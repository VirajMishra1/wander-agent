"""Best month to visit using Open-Meteo historical climate data (no auth)."""

from __future__ import annotations

import asyncio
from datetime import date


async def best_month_to_visit(
    latitude: float,
    longitude: float,
    preferences: str = "warm_dry",
) -> dict:
    """Find the best month to visit a location based on historical climate.

    Uses 5 years of historical weather data to recommend months.
    No API key required.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        preferences: "warm_dry" (default), "cool_dry", "warm_any", "snow", "shoulder_season"
    """
    from ..utils.http import get_client

    client = await get_client()
    today = date.today()
    start = f"{today.year - 5}-01-01"
    end = f"{today.year - 1}-12-31"

    try:
        resp = await client.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start,
                "end_date": end,
                "daily": "temperature_2m_mean,precipitation_sum",
                "timezone": "auto",
            },
        )
        if resp.status_code != 200:
            return {"error": f"Climate API returned {resp.status_code}"}

        data = resp.json()
        dates = data.get("daily", {}).get("time", [])
        temps = data.get("daily", {}).get("temperature_2m_mean", [])
        precip = data.get("daily", {}).get("precipitation_sum", [])

        monthly: dict = {m: {"temps": [], "precip": []} for m in range(1, 13)}
        for d, t, p in zip(dates, temps, precip):
            month = int(d[5:7])
            if t is not None:
                monthly[month]["temps"].append(t)
            if p is not None:
                monthly[month]["precip"].append(p)

        month_stats = []
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for m in range(1, 13):
            temps_m = monthly[m]["temps"]
            precip_m = monthly[m]["precip"]
            avg_temp = sum(temps_m) / len(temps_m) if temps_m else None
            rainy_days = sum(1 for p in precip_m if p > 1)
            total_days = len(precip_m)
            month_stats.append({
                "month": m,
                "name": month_names[m],
                "avg_temp_c": round(avg_temp, 1) if avg_temp is not None else None,
                "avg_temp_f": round(avg_temp * 9/5 + 32, 1) if avg_temp is not None else None,
                "rainy_days_pct": round(rainy_days / max(total_days, 1) * 100, 1),
                "total_precip_mm": round(sum(precip_m), 0),
            })

        # Scoring
        def score(m: dict) -> float:
            t = m["avg_temp_c"] or 0
            r = m["rainy_days_pct"]
            if preferences == "warm_dry":
                return -(abs(t - 25) + r * 0.5)
            if preferences == "cool_dry":
                return -(abs(t - 15) + r * 0.5)
            if preferences == "warm_any":
                return t - r * 0.1
            if preferences == "snow":
                return -t - r * 0.1
            if preferences == "shoulder_season":
                return -(abs(t - 20) + r * 0.3 + (1 if m["month"] in [6, 7, 8, 12] else 0) * 10)
            return -(abs(t - 22) + r * 0.4)

        ranked = sorted(month_stats, key=score, reverse=True)

        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "preferences": preferences,
            "based_on_years": f"{today.year - 5} to {today.year - 1}",
            "best_months": [m["name"] for m in ranked[:3]],
            "worst_months": [m["name"] for m in ranked[-3:][::-1]],
            "monthly_stats": month_stats,
            "tip": f"Top recommendation: {ranked[0]['name']} ({ranked[0]['avg_temp_c']}C, {ranked[0]['rainy_days_pct']}% rainy days)",
        }
    except Exception as e:
        return {"error": str(e)}
