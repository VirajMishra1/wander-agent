"""Weather: forecast for near-term dates, climatology for far-future dates.

Open-Meteo forecast horizon ~16 days. Beyond that, uses historical archive
to provide climate-typical conditions for those dates.
"""

from __future__ import annotations

from datetime import date as date_cls, datetime, timedelta


WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


async def get_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """Weather forecast or climatology for a date range.

    For dates within 16 days: live forecast.
    For further dates: climatology (typical conditions, averaged from 5 years
    of historical data for those same calendar days).

    No API key required.

    Args:
        latitude: Latitude
        longitude: Longitude
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """
    from ..utils.http import get_client

    today = date_cls.today()
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    days_out = (start - today).days

    client = await get_client()

    # If start date is within forecast horizon, use forecast
    if -1 <= days_out <= 14:
        try:
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,wind_speed_10m_max",
                    "timezone": "auto",
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            return _format_forecast(resp.json(), latitude, longitude, start_date, end_date, "live_forecast")
        except Exception:
            pass  # Fall through to climatology

    # Climatology: average historical data for same calendar dates across last 5 years
    try:
        years_back = 5
        # Build query dates from past years matching the same month/day
        forecasts_by_md: dict = {}

        for year_offset in range(1, years_back + 1):
            hist_start = start.replace(year=today.year - year_offset)
            hist_end = end.replace(year=today.year - year_offset)

            resp = await client.get(
                "https://archive-api.open-meteo.com/v1/archive",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": hist_start.isoformat(),
                    "end_date": hist_end.isoformat(),
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto",
                },
                timeout=15.0,
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            dates = data.get("daily", {}).get("time", [])
            tmax = data.get("daily", {}).get("temperature_2m_max", [])
            tmin = data.get("daily", {}).get("temperature_2m_min", [])
            psum = data.get("daily", {}).get("precipitation_sum", [])

            for d, mx, mn, p in zip(dates, tmax, tmin, psum):
                md = d[5:]  # MM-DD
                if md not in forecasts_by_md:
                    forecasts_by_md[md] = {"tmax": [], "tmin": [], "precip": [], "rainy_years": 0, "sample_years": 0}
                if mx is not None:
                    forecasts_by_md[md]["tmax"].append(mx)
                if mn is not None:
                    forecasts_by_md[md]["tmin"].append(mn)
                if p is not None:
                    forecasts_by_md[md]["precip"].append(p)
                    forecasts_by_md[md]["sample_years"] += 1
                    if p > 1.0:  # >1mm = rainy day
                        forecasts_by_md[md]["rainy_years"] += 1

        # Build daily climatology array
        forecasts = []
        day = start
        while day <= end:
            md = day.strftime("%m-%d")
            stats = forecasts_by_md.get(md, {})
            tmax_vals = stats.get("tmax", [])
            tmin_vals = stats.get("tmin", [])
            precip_vals = stats.get("precip", [])

            avg_tmax = sum(tmax_vals) / len(tmax_vals) if tmax_vals else None
            avg_tmin = sum(tmin_vals) / len(tmin_vals) if tmin_vals else None
            avg_precip = sum(precip_vals) / len(precip_vals) if precip_vals else None
            # "Rainy" = rain occurred in majority of historical years on this date
            rainy_years = stats.get("rainy_years", 0)
            sample_years = stats.get("sample_years", 0)
            is_typically_rainy = sample_years > 0 and (rainy_years / sample_years) > 0.5

            forecasts.append({
                "date": day.isoformat(),
                "temp_high_c": round(avg_tmax, 1) if avg_tmax is not None else None,
                "temp_low_c": round(avg_tmin, 1) if avg_tmin is not None else None,
                "temp_high_f": round(avg_tmax * 9/5 + 32, 1) if avg_tmax is not None else None,
                "temp_low_f": round(avg_tmin * 9/5 + 32, 1) if avg_tmin is not None else None,
                "precipitation_mm": round(avg_precip, 1) if avg_precip is not None else None,
                "rain_probability_pct": round(rainy_years / sample_years * 100) if sample_years else None,
                "wind_speed_kmh": None,
                "condition": "Typical for this date (climatology)",
                "is_typically_rainy": is_typically_rainy,
            })
            day += timedelta(days=1)

        if not forecasts:
            return {"error": "Could not retrieve climatology data"}

        valid_highs = [f["temp_high_c"] for f in forecasts if f["temp_high_c"] is not None]
        avg_high = sum(valid_highs) / len(valid_highs) if valid_highs else 0
        rainy_days = sum(1 for f in forecasts if f.get("is_typically_rainy", False))

        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "period": {"start": start_date, "end": end_date},
            "forecast_type": "climatology",
            "based_on_years": f"last {years_back} years for same calendar dates",
            "daily_forecasts": forecasts,
            "summary": {
                "avg_high_c": round(avg_high, 1),
                "avg_high_f": round(avg_high * 9/5 + 32, 1),
                "rainy_days": rainy_days,
                "total_days": len(forecasts),
                "pack_umbrella": rainy_days > len(forecasts) * 0.3,
            },
            "note": "Live forecast only available within 16 days. This is historical average for the requested dates.",
        }
    except Exception as e:
        return {"error": "Weather service unavailable. Try again later."}


def _format_forecast(data: dict, lat: float, lon: float, start: str, end: str, ftype: str) -> dict:
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    forecasts = []

    for i, d in enumerate(dates):
        code = daily.get("weathercode", [None])[i]
        tmax = daily.get("temperature_2m_max", [None])[i]
        tmin = daily.get("temperature_2m_min", [None])[i]
        forecasts.append({
            "date": d,
            "temp_high_c": tmax,
            "temp_low_c": tmin,
            "temp_high_f": round(tmax * 9/5 + 32, 1) if tmax is not None else None,
            "temp_low_f": round(tmin * 9/5 + 32, 1) if tmin is not None else None,
            "precipitation_mm": daily.get("precipitation_sum", [None])[i],
            "wind_speed_kmh": daily.get("wind_speed_10m_max", [None])[i],
            "condition": WMO_CODES.get(code, f"Code {code}"),
        })

    valid_highs = [f["temp_high_c"] for f in forecasts if f["temp_high_c"] is not None]
    avg_high = sum(valid_highs) / len(valid_highs) if valid_highs else 0
    rainy_days = sum(1 for f in forecasts if (f["precipitation_mm"] or 0) > 1)

    return {
        "location": {"latitude": lat, "longitude": lon},
        "timezone": data.get("timezone", ""),
        "period": {"start": start, "end": end},
        "forecast_type": ftype,
        "daily_forecasts": forecasts,
        "summary": {
            "avg_high_c": round(avg_high, 1),
            "avg_high_f": round(avg_high * 9/5 + 32, 1),
            "rainy_days": rainy_days,
            "total_days": len(forecasts),
            "pack_umbrella": rainy_days > len(forecasts) * 0.3,
        },
    }
