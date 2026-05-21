"""Weather forecasts using Open-Meteo API (free, no auth)."""

from __future__ import annotations


async def get_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """Get weather forecast for travel dates at a location.

    Args:
        latitude: Location latitude (e.g., 48.8566 for Paris)
        longitude: Location longitude (e.g., 2.3522 for Paris)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns daily temperature, precipitation, and conditions.
    No API key required.
    """
    from ..utils.http import get_client

    client = await get_client()
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
    )
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    forecasts = []

    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }

    for i, d in enumerate(dates):
        code = daily.get("weathercode", [None])[i]
        forecasts.append({
            "date": d,
            "temp_high_c": daily.get("temperature_2m_max", [None])[i],
            "temp_low_c": daily.get("temperature_2m_min", [None])[i],
            "temp_high_f": round(daily["temperature_2m_max"][i] * 9/5 + 32, 1) if daily.get("temperature_2m_max", [None])[i] is not None else None,
            "temp_low_f": round(daily["temperature_2m_min"][i] * 9/5 + 32, 1) if daily.get("temperature_2m_min", [None])[i] is not None else None,
            "precipitation_mm": daily.get("precipitation_sum", [None])[i],
            "wind_speed_kmh": daily.get("wind_speed_10m_max", [None])[i],
            "condition": wmo_codes.get(code, f"Code {code}"),
        })

    avg_high = sum(f["temp_high_c"] for f in forecasts if f["temp_high_c"]) / max(len(forecasts), 1)
    rainy_days = sum(1 for f in forecasts if (f["precipitation_mm"] or 0) > 1)

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "timezone": data.get("timezone", ""),
        "period": {"start": start_date, "end": end_date},
        "daily_forecasts": forecasts,
        "summary": {
            "avg_high_c": round(avg_high, 1),
            "avg_high_f": round(avg_high * 9/5 + 32, 1),
            "rainy_days": rainy_days,
            "total_days": len(forecasts),
            "pack_umbrella": rainy_days > len(forecasts) * 0.3,
        },
    }
