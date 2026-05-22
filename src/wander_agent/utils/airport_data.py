"""Curated list of popular destination airports for inspiration tools.

Used when we don't have a flight aggregator's 'anywhere' search.
We loop these in parallel and find the cheapest from a user's origin.
"""

from __future__ import annotations

# (IATA, city, country, region)
POPULAR_DESTINATIONS: list[tuple[str, str, str, str]] = [
    # Europe
    ("LHR", "London", "United Kingdom", "europe"),
    ("CDG", "Paris", "France", "europe"),
    ("FCO", "Rome", "Italy", "europe"),
    ("BCN", "Barcelona", "Spain", "europe"),
    ("AMS", "Amsterdam", "Netherlands", "europe"),
    ("BER", "Berlin", "Germany", "europe"),
    ("MAD", "Madrid", "Spain", "europe"),
    ("LIS", "Lisbon", "Portugal", "europe"),
    ("VIE", "Vienna", "Austria", "europe"),
    ("ATH", "Athens", "Greece", "europe"),
    ("PRG", "Prague", "Czech Republic", "europe"),
    ("IST", "Istanbul", "Turkey", "europe"),
    ("DUB", "Dublin", "Ireland", "europe"),
    ("CPH", "Copenhagen", "Denmark", "europe"),
    # Asia
    ("NRT", "Tokyo", "Japan", "asia"),
    ("ICN", "Seoul", "South Korea", "asia"),
    ("BKK", "Bangkok", "Thailand", "asia"),
    ("SIN", "Singapore", "Singapore", "asia"),
    ("HKG", "Hong Kong", "Hong Kong", "asia"),
    ("DEL", "Delhi", "India", "asia"),
    ("BOM", "Mumbai", "India", "asia"),
    ("KUL", "Kuala Lumpur", "Malaysia", "asia"),
    ("DPS", "Bali (Denpasar)", "Indonesia", "asia"),
    ("TPE", "Taipei", "Taiwan", "asia"),
    # Americas
    ("LAX", "Los Angeles", "United States", "americas"),
    ("SFO", "San Francisco", "United States", "americas"),
    ("MIA", "Miami", "United States", "americas"),
    ("JFK", "New York", "United States", "americas"),
    ("YYZ", "Toronto", "Canada", "americas"),
    ("MEX", "Mexico City", "Mexico", "americas"),
    ("CUN", "Cancun", "Mexico", "americas"),
    ("GRU", "Sao Paulo", "Brazil", "americas"),
    ("LIM", "Lima", "Peru", "americas"),
    # Oceania
    ("SYD", "Sydney", "Australia", "oceania"),
    ("AKL", "Auckland", "New Zealand", "oceania"),
    # Africa / Middle East
    ("DXB", "Dubai", "United Arab Emirates", "middle_east"),
    ("CAI", "Cairo", "Egypt", "africa"),
    ("CPT", "Cape Town", "South Africa", "africa"),
    ("JNB", "Johannesburg", "South Africa", "africa"),
    ("NBO", "Nairobi", "Kenya", "africa"),
]


def filter_destinations(
    regions: str | None = None,
    exclude_origin: str | None = None,
) -> list[tuple[str, str, str, str]]:
    """Get destinations, optionally filtered by region(s).

    Args:
        regions: Comma-separated regions (e.g., "europe,asia"). Omit for all.
        exclude_origin: IATA code to exclude
    """
    result = POPULAR_DESTINATIONS
    if regions:
        wanted = {r.strip().lower() for r in regions.split(",")}
        result = [d for d in result if d[3] in wanted]
    if exclude_origin:
        result = [d for d in result if d[0] != exclude_origin.upper()]
    return result


# Convenience maps for IATA <-> city translation
_IATA_TO_CITY = {iata: city for iata, city, _, _ in POPULAR_DESTINATIONS}
_CITY_TO_IATA = {city.lower(): iata for iata, city, _, _ in POPULAR_DESTINATIONS}
# Common aliases
_CITY_TO_IATA.update({
    "tokyo": "NRT", "nyc": "JFK", "new york city": "JFK", "san francisco": "SFO",
    "los angeles": "LAX", "rome": "FCO", "milan": "MXP", "venice": "VCE",
    "florence": "FLR", "naples": "NAP", "frankfurt": "FRA", "munich": "MUC",
    "hamburg": "HAM", "zurich": "ZRH", "geneva": "GVA", "edinburgh": "EDI",
    "manchester": "MAN", "stockholm": "ARN", "oslo": "OSL", "helsinki": "HEL",
    "reykjavik": "KEF", "warsaw": "WAW", "budapest": "BUD", "moscow": "SVO",
    "st petersburg": "LED", "kiev": "KBP", "kyiv": "KBP", "tel aviv": "TLV",
    "doha": "DOH", "abu dhabi": "AUH", "riyadh": "RUH", "casablanca": "CMN",
    "marrakech": "RAK", "lagos": "LOS", "manila": "MNL", "jakarta": "CGK",
    "ho chi minh": "SGN", "saigon": "SGN", "hanoi": "HAN", "yangon": "RGN",
    "phnom penh": "PNH", "kathmandu": "KTM", "colombo": "CMB", "male": "MLE",
    "kyoto": "KIX", "osaka": "KIX", "fukuoka": "FUK", "sapporo": "CTS",
    "beijing": "PEK", "shanghai": "PVG", "guangzhou": "CAN", "chengdu": "CTU",
    "chicago": "ORD", "boston": "BOS", "washington dc": "IAD", "washington": "IAD",
    "seattle": "SEA", "denver": "DEN", "atlanta": "ATL", "houston": "IAH",
    "dallas": "DFW", "phoenix": "PHX", "las vegas": "LAS", "orlando": "MCO",
    "honolulu": "HNL", "vancouver": "YVR", "montreal": "YUL", "calgary": "YYC",
    "havana": "HAV", "san jose": "SJO", "panama city": "PTY", "bogota": "BOG",
    "santiago": "SCL", "buenos aires": "EZE", "rio de janeiro": "GIG",
    "rio": "GIG", "salvador": "SSA", "quito": "UIO", "la paz": "LPB",
    "auckland": "AKL", "wellington": "WLG", "christchurch": "CHC",
    "perth": "PER", "brisbane": "BNE", "melbourne": "MEL",
})


def city_to_iata(name: str) -> str | None:
    """Look up IATA code for a city name. None if not in our map."""
    if not name:
        return None
    s = name.strip()
    # If already an IATA code
    if len(s) == 3 and s.isalpha() and s.isupper():
        return s
    return _CITY_TO_IATA.get(s.lower())


def iata_to_city(iata: str) -> str | None:
    """Look up city name for an IATA code."""
    if not iata:
        return None
    return _IATA_TO_CITY.get(iata.upper())


# ---------------------------------------------------------------------------
# Nearby airports: primary IATA -> [alternative IATAs in same metro area]
# ---------------------------------------------------------------------------
NEARBY_AIRPORTS: dict[str, list[str]] = {
    # New York
    "JFK": ["EWR", "LGA"],
    "EWR": ["JFK", "LGA"],
    "LGA": ["JFK", "EWR"],
    # London
    "LHR": ["LGW", "STN", "LTN", "LCY"],
    "LGW": ["LHR", "STN", "LTN"],
    "STN": ["LHR", "LGW", "LTN"],
    # Washington DC
    "IAD": ["DCA", "BWI"],
    "DCA": ["IAD", "BWI"],
    "BWI": ["IAD", "DCA"],
    # Los Angeles
    "LAX": ["BUR", "LGB", "ONT", "SNA"],
    "BUR": ["LAX", "LGB"],
    # San Francisco Bay Area
    "SFO": ["OAK", "SJC"],
    "OAK": ["SFO", "SJC"],
    "SJC": ["SFO", "OAK"],
    # Chicago
    "ORD": ["MDW"],
    "MDW": ["ORD"],
    # Dallas
    "DFW": ["DAL"],
    "DAL": ["DFW"],
    # Miami
    "MIA": ["FLL", "PBI"],
    "FLL": ["MIA", "PBI"],
    # Houston
    "IAH": ["HOU"],
    "HOU": ["IAH"],
    # Dubai
    "DXB": ["SHJ", "AUH"],
    "SHJ": ["DXB", "AUH"],
    "AUH": ["DXB", "SHJ"],
    # Tokyo
    "NRT": ["HND"],
    "HND": ["NRT"],
    # Osaka
    "KIX": ["ITM"],
    "ITM": ["KIX"],
    # Paris
    "CDG": ["ORY", "BVA"],
    "ORY": ["CDG"],
    # Rome
    "FCO": ["CIA"],
    "CIA": ["FCO"],
    # Milan
    "MXP": ["LIN", "BGY"],
    "BGY": ["MXP", "LIN"],
    # Seoul
    "ICN": ["GMP"],
    "GMP": ["ICN"],
    # Beijing
    "PEK": ["PKX"],
    # Shanghai
    "PVG": ["SHA"],
    "SHA": ["PVG"],
    # Bangkok
    "BKK": ["DMK"],
    "DMK": ["BKK"],
    # Toronto
    "YYZ": ["YTZ"],
    # Stockholm
    "ARN": ["BMA", "NYO"],
}


def get_nearby_airports(iata: str) -> list[str]:
    """Return alternative airports in the same metro area.

    Used to expand searches so "JFK" also checks EWR and LGA.

    Args:
        iata: Primary IATA code (e.g., "DXB")
    Returns:
        List of nearby IATA codes, not including the primary.
    """
    return NEARBY_AIRPORTS.get(iata.upper(), [])
