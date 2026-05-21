"""Curated cost-of-living dataset.

Median daily traveler budget in USD for major destinations, derived from
aggregated public sources (Numbeo monthly averages, Budget Your Trip, BackPacker
Index, Expatistan). Snapshot. Re-export annually.

Bands: 'budget' = hostel + street food, 'mid' = 3-star hotel + sit-down meals,
'luxury' = 4-5 star + fine dining.
"""

from __future__ import annotations

# Daily USD budget per traveler. (budget, mid, luxury)
CITY_DAILY_BUDGET_USD: dict[str, tuple[int, int, int]] = {
    # Europe
    "london": (90, 200, 450),
    "paris": (85, 180, 420),
    "amsterdam": (80, 170, 380),
    "berlin": (60, 130, 300),
    "barcelona": (60, 130, 290),
    "madrid": (55, 125, 280),
    "rome": (65, 140, 320),
    "milan": (75, 160, 360),
    "venice": (80, 170, 400),
    "florence": (65, 140, 310),
    "vienna": (70, 150, 330),
    "prague": (40, 90, 220),
    "budapest": (35, 80, 200),
    "warsaw": (40, 85, 200),
    "krakow": (35, 75, 180),
    "lisbon": (50, 110, 250),
    "porto": (45, 100, 230),
    "athens": (45, 100, 240),
    "santorini": (75, 170, 420),
    "dublin": (80, 175, 380),
    "copenhagen": (95, 210, 470),
    "stockholm": (85, 190, 430),
    "oslo": (100, 225, 500),
    "helsinki": (80, 175, 400),
    "reykjavik": (110, 240, 540),
    "zurich": (110, 250, 580),
    "geneva": (105, 240, 560),
    "brussels": (70, 155, 350),
    "edinburgh": (75, 170, 370),
    "istanbul": (35, 80, 200),
    "moscow": (45, 100, 250),
    # Asia
    "tokyo": (65, 150, 380),
    "kyoto": (55, 130, 320),
    "osaka": (55, 130, 320),
    "seoul": (50, 120, 300),
    "beijing": (40, 100, 260),
    "shanghai": (50, 120, 300),
    "hong kong": (65, 150, 380),
    "singapore": (70, 160, 400),
    "bangkok": (25, 65, 180),
    "chiang mai": (20, 50, 140),
    "phuket": (30, 80, 230),
    "bali": (25, 70, 200),
    "denpasar": (25, 70, 200),
    "ubud": (25, 70, 200),
    "jakarta": (30, 75, 200),
    "kuala lumpur": (30, 80, 210),
    "ho chi minh city": (25, 65, 170),
    "hanoi": (22, 60, 160),
    "manila": (35, 85, 220),
    "taipei": (40, 95, 250),
    "mumbai": (25, 75, 220),
    "delhi": (22, 70, 200),
    "goa": (25, 70, 200),
    "kathmandu": (20, 50, 140),
    "colombo": (30, 75, 200),
    "male": (90, 250, 700),
    "dubai": (75, 180, 480),
    "abu dhabi": (70, 170, 450),
    "doha": (70, 170, 440),
    "tel aviv": (75, 170, 400),
    "jerusalem": (65, 150, 350),
    # Americas
    "new york": (110, 240, 550),
    "san francisco": (105, 230, 530),
    "los angeles": (90, 195, 440),
    "las vegas": (80, 175, 400),
    "chicago": (85, 180, 410),
    "miami": (90, 195, 450),
    "boston": (95, 200, 450),
    "washington": (85, 180, 410),
    "seattle": (85, 180, 410),
    "honolulu": (100, 220, 500),
    "toronto": (75, 165, 380),
    "vancouver": (80, 175, 400),
    "montreal": (65, 145, 330),
    "mexico city": (40, 95, 240),
    "cancun": (55, 130, 320),
    "tulum": (60, 145, 360),
    "guadalajara": (35, 85, 220),
    "havana": (45, 110, 280),
    "san jose": (50, 120, 290),
    "panama city": (50, 120, 290),
    "lima": (40, 95, 230),
    "cusco": (35, 85, 210),
    "bogota": (35, 85, 210),
    "cartagena": (45, 110, 260),
    "medellin": (35, 85, 210),
    "santiago": (45, 105, 260),
    "buenos aires": (40, 95, 230),
    "rio de janeiro": (50, 115, 280),
    "sao paulo": (45, 105, 260),
    "quito": (35, 85, 210),
    # Africa
    "cairo": (30, 80, 220),
    "marrakech": (35, 85, 220),
    "casablanca": (40, 95, 240),
    "cape town": (45, 110, 280),
    "johannesburg": (40, 100, 250),
    "nairobi": (45, 110, 280),
    "zanzibar": (45, 110, 280),
    "addis ababa": (35, 85, 220),
    # Oceania
    "sydney": (85, 185, 420),
    "melbourne": (80, 175, 400),
    "auckland": (75, 165, 370),
    "queenstown": (90, 195, 450),
    "fiji": (75, 175, 420),
}

# Country-level fallback medians for unlisted cities
COUNTRY_DAILY_BUDGET_USD: dict[str, tuple[int, int, int]] = {
    "switzerland": (105, 240, 560),
    "norway": (100, 220, 490),
    "iceland": (110, 240, 540),
    "denmark": (95, 210, 470),
    "japan": (60, 140, 360),
    "usa": (90, 195, 450),
    "united states": (90, 195, 450),
    "uk": (75, 170, 380),
    "united kingdom": (75, 170, 380),
    "france": (75, 165, 370),
    "germany": (60, 130, 300),
    "italy": (65, 145, 330),
    "spain": (55, 125, 280),
    "portugal": (45, 105, 240),
    "greece": (50, 110, 260),
    "czech republic": (40, 90, 220),
    "hungary": (35, 80, 200),
    "poland": (40, 85, 200),
    "thailand": (25, 65, 180),
    "vietnam": (22, 60, 160),
    "indonesia": (25, 70, 200),
    "india": (22, 65, 200),
    "philippines": (30, 75, 200),
    "malaysia": (30, 80, 210),
    "south korea": (50, 120, 300),
    "singapore": (70, 160, 400),
    "china": (45, 110, 280),
    "mexico": (40, 95, 240),
    "colombia": (35, 85, 210),
    "peru": (35, 85, 220),
    "argentina": (40, 95, 230),
    "brazil": (45, 105, 260),
    "australia": (80, 175, 400),
    "new zealand": (75, 165, 370),
    "egypt": (30, 80, 220),
    "morocco": (35, 85, 220),
    "south africa": (45, 105, 270),
    "kenya": (45, 110, 280),
    "tanzania": (45, 110, 280),
    "uae": (75, 180, 480),
    "turkey": (35, 80, 200),
}


def lookup_cost(city: str | None = None, country: str | None = None) -> dict | None:
    """Find cost data for a city, falling back to country if needed."""
    if city:
        key = city.lower().strip()
        if key in CITY_DAILY_BUDGET_USD:
            budget, mid, luxury = CITY_DAILY_BUDGET_USD[key]
            return {
                "match_type": "city",
                "matched_name": city,
                "daily_budget_usd": budget,
                "daily_mid_usd": mid,
                "daily_luxury_usd": luxury,
            }
    if country:
        key = country.lower().strip()
        if key in COUNTRY_DAILY_BUDGET_USD:
            budget, mid, luxury = COUNTRY_DAILY_BUDGET_USD[key]
            return {
                "match_type": "country_fallback",
                "matched_name": country,
                "daily_budget_usd": budget,
                "daily_mid_usd": mid,
                "daily_luxury_usd": luxury,
            }
    return None
