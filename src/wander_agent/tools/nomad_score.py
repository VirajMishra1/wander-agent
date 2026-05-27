"""Digital nomad city scorer.

Ranks cities for remote-work suitability across 6 dimensions:
cost, safety, internet, weather, visa ease, and lifestyle.
All data from existing wander-agent sources — no extra keys required.
"""

from __future__ import annotations

import asyncio
from datetime import datetime as _dt

# Static internet quality index 0-10 (Speedtest Global Index + Nomad List data)
_INTERNET: dict[str, float] = {
    "singapore": 9.2, "seoul": 9.5, "tokyo": 9.0, "taipei": 9.3, "hong kong": 9.0,
    "amsterdam": 9.1, "zurich": 9.0, "stockholm": 9.2, "copenhagen": 9.0, "helsinki": 9.1,
    "london": 8.5, "paris": 8.3, "berlin": 8.2, "barcelona": 8.4, "madrid": 8.3,
    "lisbon": 8.6, "porto": 8.4, "prague": 8.5, "budapest": 8.3, "warsaw": 8.4,
    "new york": 8.0, "san francisco": 8.2, "austin": 8.3, "miami": 7.9, "toronto": 8.1,
    "dubai": 8.8, "abu dhabi": 8.7, "tel aviv": 8.9,
    "bangkok": 7.8, "bali": 7.2, "chiang mai": 7.5, "ho chi minh city": 7.6, "hanoi": 7.4,
    "kuala lumpur": 8.0, "jakarta": 7.3, "manila": 6.8,
    "medellin": 7.5, "bogota": 7.3, "mexico city": 7.7, "buenos aires": 7.2,
    "cape town": 7.0, "nairobi": 6.5,
    "tbilisi": 8.0, "tashkent": 7.0, "yerevan": 7.8,
}

# Lifestyle score 0-10: coworking density, English usage, walkability, expat community
_LIFESTYLE: dict[str, float] = {
    "bali": 9.5, "chiang mai": 9.0, "lisbon": 9.2, "barcelona": 9.0, "medellin": 8.8,
    "tbilisi": 8.5, "mexico city": 8.7, "bangkok": 8.5, "ho chi minh city": 8.3,
    "berlin": 8.8, "amsterdam": 8.7, "prague": 8.5, "budapest": 8.5,
    "porto": 8.8, "madrid": 8.3, "tel aviv": 8.2,
    "singapore": 8.0, "taipei": 8.5, "seoul": 8.3, "tokyo": 7.8,
    "new york": 7.5, "san francisco": 7.8, "austin": 8.2, "miami": 8.0,
    "toronto": 8.0, "london": 7.8, "dubai": 7.5, "cape town": 8.0,
}

# Visa ease 1-5 (scale to 10) for short-stay remote workers
_VISA_EASE_BY_COUNTRY: dict[str, float] = {
    "germany": 5.0, "france": 5.0, "spain": 5.0, "portugal": 5.0, "italy": 5.0,
    "netherlands": 5.0, "czechia": 5.0, "hungary": 5.0, "poland": 5.0,
    "united kingdom": 4.5, "switzerland": 4.8,
    "united states": 4.0, "canada": 4.5, "australia": 4.5,
    "japan": 4.8, "south korea": 4.8, "singapore": 4.8, "taiwan": 4.8,
    "thailand": 5.0, "indonesia": 4.5, "vietnam": 4.5, "malaysia": 5.0,
    "united arab emirates": 4.8, "israel": 4.0,
    "mexico": 5.0, "colombia": 4.5, "argentina": 4.5, "brazil": 3.5,
    "south africa": 4.5, "kenya": 3.5,
    "georgia": 5.0, "armenia": 5.0, "uzbekistan": 3.5,
    "philippines": 4.5,
}

_CITY_TO_COUNTRY: dict[str, str] = {
    "bali": "indonesia", "jakarta": "indonesia",
    "chiang mai": "thailand", "bangkok": "thailand", "phuket": "thailand",
    "ho chi minh city": "vietnam", "hanoi": "vietnam",
    "kuala lumpur": "malaysia", "penang": "malaysia",
    "singapore": "singapore",
    "tokyo": "japan", "osaka": "japan",
    "seoul": "south korea",
    "taipei": "taiwan",
    "hong kong": "hong kong",
    "lisbon": "portugal", "porto": "portugal",
    "barcelona": "spain", "madrid": "spain",
    "berlin": "germany", "munich": "germany",
    "amsterdam": "netherlands",
    "paris": "france",
    "london": "united kingdom",
    "prague": "czechia",
    "budapest": "hungary",
    "warsaw": "poland",
    "tbilisi": "georgia",
    "yerevan": "armenia",
    "tashkent": "uzbekistan",
    "medellin": "colombia", "bogota": "colombia",
    "mexico city": "mexico",
    "buenos aires": "argentina",
    "cape town": "south africa",
    "nairobi": "kenya",
    "dubai": "united arab emirates", "abu dhabi": "united arab emirates",
    "tel aviv": "israel",
    "new york": "united states", "san francisco": "united states",
    "austin": "united states", "miami": "united states",
    "toronto": "canada",
    "sydney": "australia", "melbourne": "australia",
    "zurich": "switzerland",
    "stockholm": "sweden",
    "copenhagen": "denmark",
    "helsinki": "finland",
    "manila": "philippines",
}

_CITY_TO_ISO2: dict[str, str] = {
    "bali": "ID", "jakarta": "ID", "chiang mai": "TH", "bangkok": "TH",
    "phuket": "TH", "ho chi minh city": "VN", "hanoi": "VN",
    "kuala lumpur": "MY", "penang": "MY", "singapore": "SG",
    "tokyo": "JP", "osaka": "JP", "seoul": "KR", "taipei": "TW",
    "hong kong": "HK", "lisbon": "PT", "porto": "PT",
    "barcelona": "ES", "madrid": "ES", "berlin": "DE", "munich": "DE",
    "amsterdam": "NL", "paris": "FR", "london": "GB", "prague": "CZ",
    "budapest": "HU", "warsaw": "PL", "tbilisi": "GE", "yerevan": "AM",
    "tashkent": "UZ", "medellin": "CO", "bogota": "CO",
    "mexico city": "MX", "buenos aires": "AR", "cape town": "ZA",
    "nairobi": "KE", "dubai": "AE", "abu dhabi": "AE", "tel aviv": "IL",
    "new york": "US", "san francisco": "US", "austin": "US", "miami": "US",
    "toronto": "CA", "sydney": "AU", "melbourne": "AU", "zurich": "CH",
    "stockholm": "SE", "copenhagen": "DK", "helsinki": "FI", "manila": "PH",
}


# Monthly avg temp °C per city: [Jan..Dec]
_MONTHLY_TEMP: dict[str, list[float]] = {
    "bali":           [27, 27, 27, 28, 27, 26, 25, 26, 26, 27, 27, 27],
    "chiang mai":     [22, 25, 28, 31, 31, 30, 29, 29, 28, 27, 24, 21],
    "bangkok":        [27, 29, 30, 32, 31, 30, 29, 29, 29, 29, 27, 26],
    "ho chi minh city":[27, 28, 30, 32, 32, 30, 29, 29, 29, 28, 27, 26],
    "hanoi":          [17, 18, 21, 25, 28, 30, 30, 29, 27, 24, 20, 17],
    "kuala lumpur":   [27, 28, 28, 28, 28, 28, 27, 27, 27, 27, 27, 27],
    "singapore":      [26, 27, 27, 28, 28, 28, 27, 27, 27, 27, 27, 26],
    "tokyo":          [ 6,  6, 10, 15, 19, 23, 27, 28, 24, 18, 13,  8],
    "osaka":          [ 6,  7, 11, 16, 21, 25, 29, 30, 26, 20, 14,  8],
    "seoul":          [-2,  0,  6, 13, 18, 23, 27, 28, 23, 16,  8,  1],
    "taipei":         [16, 17, 19, 23, 26, 29, 32, 32, 29, 25, 22, 18],
    "hong kong":      [16, 17, 19, 23, 26, 29, 30, 30, 28, 25, 21, 17],
    "lisbon":         [13, 14, 15, 17, 19, 23, 26, 27, 25, 21, 16, 13],
    "porto":          [12, 13, 14, 15, 17, 20, 23, 24, 22, 18, 14, 12],
    "barcelona":      [10, 11, 13, 15, 18, 22, 25, 26, 23, 19, 14, 11],
    "madrid":         [ 7,  8, 11, 14, 18, 23, 27, 27, 23, 17, 11,  7],
    "berlin":         [ 1,  2,  6, 11, 16, 19, 21, 21, 17, 12,  6,  2],
    "amsterdam":      [ 4,  4,  7, 10, 14, 17, 19, 19, 16, 12,  8,  5],
    "paris":          [ 6,  7,  9, 12, 16, 19, 22, 22, 18, 14,  9,  6],
    "london":         [ 7,  7,  9, 11, 14, 17, 20, 20, 17, 13,  9,  7],
    "prague":         [ 1,  2,  6, 11, 16, 19, 21, 21, 17, 11,  6,  2],
    "budapest":       [ 2,  4,  9, 14, 19, 23, 25, 25, 21, 15,  8,  3],
    "warsaw":         [-1,  0,  4, 10, 15, 19, 21, 20, 16, 10,  5,  0],
    "tbilisi":        [ 4,  5, 10, 15, 20, 24, 27, 27, 23, 17, 10,  5],
    "dubai":          [19, 21, 24, 28, 33, 35, 37, 37, 34, 30, 25, 21],
    "abu dhabi":      [18, 20, 24, 28, 33, 36, 38, 38, 35, 31, 26, 21],
    "tel aviv":       [13, 14, 16, 19, 23, 26, 28, 29, 27, 24, 19, 14],
    "medellin":       [22, 22, 23, 23, 22, 22, 22, 22, 22, 22, 22, 22],
    "bogota":         [14, 14, 14, 14, 14, 13, 13, 13, 13, 14, 14, 14],
    "mexico city":    [16, 18, 20, 22, 23, 22, 21, 21, 20, 19, 17, 16],
    "buenos aires":   [25, 24, 22, 18, 14, 11, 11, 12, 15, 18, 22, 24],
    "cape town":      [22, 22, 21, 18, 16, 14, 13, 14, 15, 17, 19, 21],
    "nairobi":        [19, 20, 20, 19, 18, 17, 16, 17, 17, 19, 18, 18],
    "new york":       [ 1,  2,  6, 12, 18, 23, 26, 26, 22, 16,  9,  3],
    "san francisco":  [11, 12, 13, 14, 15, 16, 16, 17, 18, 17, 14, 11],
    "austin":         [12, 14, 17, 21, 25, 29, 32, 32, 28, 22, 16, 12],
    "miami":          [20, 21, 23, 25, 27, 29, 30, 31, 30, 28, 24, 21],
    "toronto":        [-3, -2,  3,  9, 15, 21, 24, 23, 19, 13,  6, -1],
    "sydney":         [23, 23, 22, 19, 16, 13, 12, 13, 15, 18, 21, 23],
    "zurich":         [ 2,  3,  7, 11, 16, 19, 22, 21, 17, 12,  6,  2],
    "stockholm":      [-2, -2,  1,  6, 12, 17, 20, 18, 14,  8,  3, -1],
    "copenhagen":     [ 2,  2,  5,  9, 14, 17, 20, 20, 16, 11,  7,  3],
    "helsinki":       [-4, -5, -1,  5, 11, 16, 19, 18, 13,  7,  2, -2],
    "manila":         [26, 27, 28, 30, 31, 30, 28, 28, 28, 28, 28, 27],
    "jakarta":        [27, 27, 27, 27, 27, 27, 27, 27, 27, 28, 28, 27],
    "yerevan":        [ 1,  3,  9, 15, 20, 25, 28, 28, 23, 16,  9,  3],
    "tashkent":       [ 3,  5, 11, 17, 22, 28, 31, 30, 25, 18, 11,  5],
}


def _weather_score(city_lower: str, month: int) -> float:
    """Score 0-10 based on typical temp for the month. Defaults to 6.0 if unknown."""
    temps = _MONTHLY_TEMP.get(city_lower)
    if not temps:
        return 6.0
    avg_temp = temps[month - 1]
    if 20 <= avg_temp <= 28:
        return 9.5
    if 15 <= avg_temp < 20 or 28 < avg_temp <= 32:
        return 7.5
    if 10 <= avg_temp < 15 or 32 < avg_temp <= 36:
        return 5.0
    return 2.5


def _internet_score(city_lower: str) -> float:
    return _INTERNET.get(city_lower, 7.5)


def _lifestyle_score(city_lower: str) -> float:
    return _LIFESTYLE.get(city_lower, 7.0)


def _visa_score(city_lower: str) -> float:
    country = _CITY_TO_COUNTRY.get(city_lower, city_lower)
    return _VISA_EASE_BY_COUNTRY.get(country, 4.0) * 2  # scale 0-10


def _cost_score(daily_budget_mid: float | None) -> float:
    """Cheaper = higher score (0-10)."""
    if not daily_budget_mid:
        return 5.0
    if daily_budget_mid <= 40:
        return 9.5
    if daily_budget_mid <= 60:
        return 8.5
    if daily_budget_mid <= 80:
        return 7.5
    if daily_budget_mid <= 100:
        return 6.5
    if daily_budget_mid <= 150:
        return 5.0
    if daily_budget_mid <= 200:
        return 3.5
    return 2.0


def _advisory_score(level: int | None) -> float:
    return {1: 9.0, 2: 7.0, 3: 4.0, 4: 1.0}.get(level or 1, 7.0)


async def score_nomad_cities(
    cities: str,
    month: int | None = None,
    weights: str = "cost:25,safety:20,internet:15,weather:20,visa:10,lifestyle:10",
) -> dict:
    """Score and rank cities for digital nomad / remote-work suitability.

    Combines cost of living, US State Dept safety advisory, internet speed
    index, weather comfort, visa ease, and lifestyle/coworking data into a
    single ranked score. No API key required.

    Args:
        cities: Comma-separated city names (e.g., "Bali,Lisbon,Chiang Mai,Medellin")
        month: Month 1-12 to evaluate (default: current month)
        weights: Scoring weights as "dimension:percent" pairs summing to 100.
                 Dimensions: cost, safety, internet, weather, visa, lifestyle
    """
    from .cost_of_living import get_cost_of_living
    from .advisory import get_travel_advisory

    now_month = month or _dt.now().month

    # Parse weights
    w: dict[str, float] = {}
    for pair in weights.split(","):
        if ":" in pair:
            try:
                k, v = pair.split(":", 1)
                w[k.strip()] = float(v.strip()) / 100
            except (ValueError, TypeError):
                pass
    defaults = {"cost": 0.25, "safety": 0.20, "internet": 0.15,
                "weather": 0.20, "visa": 0.10, "lifestyle": 0.10}
    for k, v in defaults.items():
        w.setdefault(k, v)

    city_list = [c.strip() for c in cities.split(",") if c.strip()]
    if not city_list:
        return {"error": "Provide at least one city name"}

    async def _score_city(city: str) -> dict:
        cl = city.lower()
        iso2 = _CITY_TO_ISO2.get(cl)

        # Run cost + advisory in parallel
        cost_fut = asyncio.create_task(get_cost_of_living(city))
        async def _empty_adv() -> dict:
            return {}

        adv_fut = asyncio.create_task(
            get_travel_advisory(iso2) if iso2 else _empty_adv()
        )
        cost_data, adv_data = await asyncio.gather(cost_fut, adv_fut, return_exceptions=True)

        daily_mid: float | None = None
        if isinstance(cost_data, dict) and not cost_data.get("error"):
            daily_mid = cost_data.get("daily_budget_per_person", {}).get("mid_tier_usd")

        adv_level: int | None = None
        if isinstance(adv_data, dict):
            adv_level = adv_data.get("advisory_level")

        # Weather score from static monthly temp table
        weather_sc = _weather_score(cl, now_month)

        dim_scores = {
            "cost":      _cost_score(daily_mid),
            "safety":    _advisory_score(adv_level),
            "internet":  _internet_score(cl),
            "weather":   weather_sc,
            "visa":      _visa_score(cl),
            "lifestyle": _lifestyle_score(cl),
        }
        total = round(sum(dim_scores[k] * w.get(k, 0) for k in dim_scores), 1)

        return {
            "city": city,
            "total_score": total,
            "max_score": 10.0,
            "scores": {k: round(v, 1) for k, v in dim_scores.items()},
            "daily_budget_mid_usd": daily_mid,
            "advisory_level": adv_level,
            "links": {
                "nomadlist":  f"https://nomadlist.com/{cl.replace(' ', '-')}",
                "coworker":   f"https://www.coworker.com/search/{cl.replace(' ', '-')}",
                "airbnb_monthly": (
                    f"https://www.airbnb.com/s/{city.replace(' ', '-')}/homes"
                    f"?adults=1&min_nights=28"
                ),
            },
        }

    results = await asyncio.gather(*[_score_city(c) for c in city_list], return_exceptions=True)
    valid = [r for r in results if isinstance(r, dict) and "error" not in r]
    valid.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "cities_scored": len(valid),
        "month_evaluated": now_month,
        "weights_used": {k: f"{int(v * 100)}%" for k, v in w.items()},
        "ranking": valid,
        "winner": valid[0]["city"] if valid else None,
        "winner_score": valid[0]["total_score"] if valid else None,
        "data_sources": "cost_of_living (static), US State Dept advisory (live RSS), internet (Speedtest index static), visa ease (static), lifestyle (Nomad List static)",
        "suggest_web_search": [
            f"digital nomad {valid[0]['city']} 2026 monthly cost" if valid else "best digital nomad cities 2026",
            "digital nomad visa countries 2026 no tax",
        ],
    }
