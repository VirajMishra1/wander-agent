"""Timezone converter and sunrise/sunset fetcher."""
from __future__ import annotations


async def convert_timezone(
    datetime_str: str,
    from_timezone: str,
    to_timezone: str,
) -> dict:
    """Convert a date/time from one timezone to another.

    Args:
        datetime_str: Date and time, e.g. "2026-08-15 14:30" or "2026-08-15T14:30:00"
        from_timezone: IANA timezone name, e.g. "America/New_York", "Europe/London", "Asia/Tokyo"
        to_timezone: Target IANA timezone, e.g. "Asia/Bangkok", "UTC"
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    datetime_str = datetime_str.strip().replace("T", " ")
    dt_naive = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt_naive = datetime.strptime(datetime_str, fmt)
            break
        except ValueError:
            continue
    if dt_naive is None:
        return {"error": f"Cannot parse datetime '{datetime_str}'. Use YYYY-MM-DD HH:MM format."}

    try:
        tz_from = ZoneInfo(from_timezone)
        tz_to = ZoneInfo(to_timezone)
    except ZoneInfoNotFoundError as e:
        return {"error": f"Unknown timezone: {e}. Use IANA names like 'America/New_York'."}

    dt_from = dt_naive.replace(tzinfo=tz_from)
    dt_to = dt_from.astimezone(tz_to)

    offset_from = dt_from.utcoffset()
    offset_to = dt_to.utcoffset()
    diff_hours = (offset_to.total_seconds() - offset_from.total_seconds()) / 3600

    return {
        "input": {
            "datetime": datetime_str,
            "timezone": from_timezone,
            "utc_offset": str(offset_from),
        },
        "output": {
            "datetime": dt_to.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": to_timezone,
            "utc_offset": str(offset_to),
            "day_of_week": dt_to.strftime("%A"),
        },
        "difference_hours": round(diff_hours, 1),
        "note": (
            f"{to_timezone} is {abs(diff_hours):.0f}h {'ahead of' if diff_hours > 0 else 'behind'} {from_timezone}"
            if diff_hours != 0 else f"{to_timezone} is the same time as {from_timezone}"
        ),
        "data_confidence": "calculated",
    }


async def get_sunrise_sunset(
    latitude: float,
    longitude: float,
    date: str = "today",
) -> dict:
    """Get sunrise, sunset, solar noon, and day length for any location and date.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        date: Date in YYYY-MM-DD format, or "today"
    """
    from ..utils.http import get_client
    from datetime import date as date_cls

    client = await get_client()

    if date == "today":
        date = date_cls.today().isoformat()

    url = (
        f"https://api.sunrise-sunset.org/json"
        f"?lat={latitude}&lng={longitude}&date={date}&formatted=0"
    )

    try:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code != 200:
            return {"error": "Sunrise-sunset API unavailable", "date": date}
        data = resp.json()
        if data.get("status") != "OK":
            return {"error": data.get("status", "API error"), "date": date}

        r = data["results"]

        def _fmt(iso_str: str) -> str:
            from datetime import datetime, timezone
            try:
                dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
                return dt.astimezone(timezone.utc).strftime("%H:%M UTC")
            except Exception:
                return iso_str

        day_len_secs = r.get("day_length", 0)
        hours, rem = divmod(int(day_len_secs), 3600)
        minutes = rem // 60

        return {
            "date": date,
            "location": {"latitude": latitude, "longitude": longitude},
            "sunrise_utc": _fmt(r.get("sunrise", "")),
            "sunset_utc": _fmt(r.get("sunset", "")),
            "solar_noon_utc": _fmt(r.get("solar_noon", "")),
            "civil_twilight_begin_utc": _fmt(r.get("civil_twilight_begin", "")),
            "civil_twilight_end_utc": _fmt(r.get("civil_twilight_end", "")),
            "day_length": f"{hours}h {minutes}m",
            "day_length_seconds": day_len_secs,
            "note": "All times in UTC. Convert to local timezone using convert_timezone tool.",
            "data_confidence": "live_api",
            "data_source": "sunrise-sunset.org",
        }
    except Exception as e:
        return {"error": str(e), "date": date}
