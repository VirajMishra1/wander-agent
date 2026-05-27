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
            daily_mid = cost_data.get("mid_range_usd_day")

        adv_level: int | None = None
        if isinstance(adv_data, dict):
            adv_level = adv_data.get("level")

        # Weather score from cost_of_living climate data if present
        weather_sc = 6.0
        if isinstance(cost_data, dict):
            climate = cost_data.get("climate") or {}
            month_data = climate.get(str(now_month)) or {}
            avg_temp = month_data.get("avg_temp_c")
            avg_precip = month_data.get("avg_precip_mm", 0) or 0
            if avg_temp is not None:
                if 20 <= avg_temp <= 28:
                    t_sc = 10.0
                elif 15 <= avg_temp < 20 or 28 < avg_temp <= 32:
                    t_sc = 7.5
                elif 10 <= avg_temp < 15 or 32 < avg_temp <= 36:
                    t_sc = 5.0
                else:
                    t_sc = 2.5
                p_sc = max(0.0, 10.0 - avg_precip / 5)
                weather_sc = round(t_sc * 0.6 + p_sc * 0.4, 1)

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
