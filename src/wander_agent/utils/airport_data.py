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
