"""Jet lag calculator — science-based sleep schedule to minimise jet lag."""
from __future__ import annotations
from datetime import datetime, timedelta


_TZ_OFFSETS: dict[str, float] = {
    # Americas
    "LAX": -8, "SFO": -8, "SEA": -8, "LAS": -8, "PHX": -7,
    "DEN": -7, "ORD": -6, "DAL": -6, "DFW": -6, "HOU": -6,
    "MIA": -5, "JFK": -5, "EWR": -5, "BOS": -5, "ATL": -5,
    "YYZ": -5, "YUL": -5, "YVR": -8, "YYC": -7,
    "MEX": -6, "CUN": -6, "BOG": -5, "SCL": -4, "EZE": -3,
    "GRU": -3, "GIG": -3, "LIM": -5, "UIO": -5, "HAV": -5,
    "SJU": -4, "SDQ": -4, "SJO": -6, "PTY": -5,
    # Europe
    "LHR": 0, "LGW": 0, "STN": 0, "MAN": 0, "EDI": 0, "DUB": 0,
    "CDG": 1, "ORY": 1, "AMS": 1, "BRU": 1, "FCO": 1, "MXP": 1,
    "BCN": 1, "MAD": 1, "LIS": 0, "OPO": 0, "FRA": 1, "MUC": 1,
    "BER": 1, "HAM": 1, "ZRH": 1, "VIE": 1, "CPH": 1, "ARN": 1,
    "OSL": 1, "HEL": 2, "WAW": 1, "BUD": 1, "PRG": 1, "ATH": 2,
    "IST": 3, "SAW": 3, "KEF": 0, "DBV": 1, "SKG": 2, "SOF": 2,
    # Middle East / Africa
    "DXB": 4, "AUH": 4, "SHJ": 4, "DOH": 3, "RUH": 3, "AMM": 2,
    "TLV": 2, "CAI": 2, "CMN": 1, "RAK": 1, "CPT": 2, "JNB": 2,
    "NBO": 3, "ADD": 3, "DAR": 3, "ZNZ": 3, "KGL": 2, "LOS": 1,
    # Asia
    "DEL": 5.5, "BOM": 5.5, "MAA": 5.5, "CMB": 5.5,
    "KTM": 5.75,
    "KUL": 8, "SIN": 8, "BKK": 7, "DMK": 7, "SGN": 7, "HAN": 7,
    "REP": 7, "PNH": 7, "DAD": 7, "MNL": 8, "CGK": 7, "DPS": 8,
    "HKG": 8, "MLE": 5, "TPE": 8,
    "PEK": 8, "PVG": 8, "SHA": 8, "CTU": 8, "CAN": 8,
    "NRT": 9, "HND": 9, "KIX": 9, "FUK": 9, "OKA": 9, "CTS": 9,
    "ICN": 9, "GMP": 9, "TBS": 4, "BAK": 4,
    # Oceania
    "SYD": 11, "MEL": 11, "BNE": 10, "PER": 8, "AKL": 13, "CHC": 13, "NAN": 12,
    # Common city aliases
    "NYC": -5, "LON": 0, "PAR": 1, "ROM": 1, "MIL": 1,
}

def _get_offset(code: str) -> float | None:
    return _TZ_OFFSETS.get(code.upper())


def _direction(delta_h: float) -> str:
    if delta_h > 0:
        return "eastward"
    elif delta_h < 0:
        return "westward"
    return "same_timezone"


async def calculate_jet_lag(
    origin: str,
    destination: str,
    departure_date: str,
    flight_duration_hours: float = 0,
) -> dict:
    """Calculate jet lag impact and generate a recovery sleep schedule.

    Based on circadian rhythm science:
    - Eastward travel (losing time) is harder than westward
    - Recovery takes ~1 day per hour of timezone difference
    - Light exposure timing is the #1 jet lag fix

    Args:
        origin: Origin IATA airport code or city (e.g. "JFK", "London")
        destination: Destination IATA code or city (e.g. "NRT", "Tokyo")
        departure_date: YYYY-MM-DD departure date
        flight_duration_hours: Flight duration in hours (0 = auto-estimate from tz diff)
    """
    origin_offset = _get_offset(origin)
    dest_offset = _get_offset(destination)

    if origin_offset is None or dest_offset is None:
        # Try common city names
        city_map = {
            "london": 0, "paris": 1, "new york": -5, "nyc": -5, "tokyo": 9,
            "dubai": 4, "singapore": 8, "sydney": 11, "los angeles": -8,
            "chicago": -6, "miami": -5, "toronto": -5, "bangkok": 7,
            "hong kong": 8, "seoul": 9, "beijing": 8, "shanghai": 8,
            "delhi": 5.5, "mumbai": 5.5, "istanbul": 3, "amsterdam": 1,
            "berlin": 1, "rome": 1, "madrid": 1, "lisbon": 0, "athens": 2,
        }
        if origin_offset is None:
            origin_offset = city_map.get(origin.lower())
        if dest_offset is None:
            dest_offset = city_map.get(destination.lower())

    if origin_offset is None or dest_offset is None:
        return {
            "error": f"Unknown timezone for {origin if origin_offset is None else destination}. "
                     "Provide IATA code (e.g. JFK, NRT, DXB).",
            "supported_airports": list(_TZ_OFFSETS.keys()),
        }

    tz_diff = dest_offset - origin_offset
    # Handle date line wrap
    if tz_diff > 12:
        tz_diff -= 24
    elif tz_diff < -12:
        tz_diff += 24

    abs_diff = abs(tz_diff)
    direction = _direction(tz_diff)

    # Severity: eastward harder
    if abs_diff <= 2:
        severity = "minimal"
        recovery_days = 1
    elif abs_diff <= 5:
        severity = "moderate" if direction == "westward" else "significant"
        recovery_days = int(abs_diff * 0.8) if direction == "westward" else int(abs_diff)
    else:
        severity = "severe" if direction == "eastward" else "significant"
        recovery_days = int(abs_diff) if direction == "eastward" else int(abs_diff * 0.75)

    dep_dt = datetime.strptime(departure_date, "%Y-%m-%d")

    # --- Sleep schedule recommendation ---
    # Adjust bedtime 1-2 days before departure
    pre_departure = []
    if abs_diff >= 4:
        if direction == "eastward":
            pre_departure.append("2 nights before: go to bed 1 hour earlier than usual.")
            pre_departure.append("Night before: go to bed 2 hours earlier than usual.")
        else:
            pre_departure.append("2 nights before: go to bed 1 hour later than usual.")
            pre_departure.append("Night before: go to bed 2 hours later than usual.")

    # On the plane
    on_plane = []
    arrival_local = dep_dt + timedelta(hours=(flight_duration_hours or abs_diff + 4))
    if direction == "eastward":
        on_plane.append("Set watch to destination time immediately on boarding.")
        on_plane.append("Sleep during destination's night time, even if daytime at origin.")
        on_plane.append("Avoid alcohol and caffeine — they disrupt sleep quality.")
        on_plane.append("Stay hydrated: drink 250ml water per hour of flight.")
        if flight_duration_hours > 8:
            on_plane.append("Take 0.5mg melatonin 90min before destination bedtime on plane.")
    else:
        on_plane.append("Stay awake during the flight if arriving in the morning.")
        on_plane.append("Sleep only if arriving at night at destination.")
        on_plane.append("Eat according to destination meal times.")

    # After arrival schedule
    after_arrival = []
    after_arrival.append(f"Day 1: Stay awake until 10pm local time regardless of tiredness.")
    after_arrival.append(f"Day 1: Get bright light exposure (go outside) between 8am-12pm local.")
    if direction == "eastward":
        after_arrival.append("Days 1-3: Take 1mg melatonin at destination bedtime.")
        after_arrival.append("Avoid naps longer than 20 mins during day 1-2.")
        after_arrival.append("Schedule lighter activities for the first 2 days.")
    else:
        after_arrival.append("Days 1-2: Get evening light exposure (sunset walk).")
        after_arrival.append("Short 20-min nap ok if you feel exhausted, before 3pm.")

    for i in range(1, min(recovery_days + 1, 4)):
        d = dep_dt + timedelta(days=i)
        after_arrival.append(f"Day {i+1} ({d.strftime('%b %d')}): Bedtime {int(22 + tz_diff * 0.3) % 24}:00 local — gradually shifting.")

    return {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "departure_date": departure_date,
        "timezone": {
            "origin_utc_offset": origin_offset,
            "destination_utc_offset": dest_offset,
            "difference_hours": round(tz_diff, 2),
            "direction": direction,
        },
        "jet_lag": {
            "severity": severity,
            "estimated_recovery_days": recovery_days,
            "eastward_note": "Eastward travel (losing time) is ~50% harder than westward.",
        },
        "schedule": {
            "before_departure": pre_departure,
            "on_the_plane": on_plane,
            "after_arrival": after_arrival,
        },
        "quick_tips": [
            "Melatonin (0.5-1mg) taken at destination bedtime is the most evidence-based jet lag treatment.",
            "Bright light exposure in the morning at destination resets your circadian clock fastest.",
            "Fasting 12-16 hours then eating at destination meal times also helps reset body clock.",
            "Avoid alcohol on the plane — it halves sleep quality even if it makes you feel sleepy.",
            f"{'Book lighter activities for first 2 days — cognitive performance drops ~30% with severe jet lag.' if severity in ('severe','significant') else 'Mild jet lag — you should feel normal within 1-2 days.'}",
        ],
    }
