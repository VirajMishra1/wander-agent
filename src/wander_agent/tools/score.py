"""Multi-objective destination scorer - the killer ranking tool."""

from __future__ import annotations

import asyncio


async def score_destinations(
    destinations: str,
    travel_start: str,
    travel_end: str,
    weights: str = "cost:3,weather:3,safety:2,events:1,quality_of_life:1",
    weather_pref: str = "warm_dry",
    origin: str | None = None,
) -> dict:
    """Score destinations across multiple objectives simultaneously.

    The killer ranking tool. Combines:
    - Cost (lower = better, normalized vs other destinations)
    - Weather match for travel dates (matches `weather_pref`)
    - Safety (travel advisory count, inverted)
    - Events count during travel dates
    - Quality of life (Teleport scores aggregate)

    Args:
        destinations: Comma-separated cities (e.g., "Paris,Rome,Barcelona,Tokyo")
        travel_start: YYYY-MM-DD
        travel_end: YYYY-MM-DD
        weights: Comma-separated key:weight pairs (e.g., "cost:3,weather:2")
        weather_pref: warm_dry, cool_dry, warm_any, snow, shoulder_season
        origin: Optional origin airport for cost calc (e.g., "JFK")
    """
    from .advisory import get_travel_advisory
    from .cost_of_living import get_cost_of_living
    from .destination import geocode
    from .events import get_local_events
    from .hotels import search_hotels
    from .weather import get_weather

    dest_list = [d.strip() for d in destinations.split(",") if d.strip()]
    if len(dest_list) < 2:
        return {"error": "Need at least 2 destinations to compare"}

    weight_map: dict = {"cost": 3, "weather": 3, "safety": 2, "events": 1, "quality_of_life": 1}
    for pair in weights.split(","):
        if ":" in pair:
            k, v = pair.split(":")
            weight_map[k.strip()] = float(v.strip())

    async def _score_one(dest: str) -> dict:
        geo = await geocode(dest)
        if geo.get("error"):
            return {"destination": dest, "error": geo["error"]}
        lat, lon = geo["latitude"], geo["longitude"]
        country = geo.get("country", "")

        weather_task = get_weather(lat, lon, travel_start, travel_end)
        hotels_task = search_hotels(city=dest, check_in=travel_start, check_out=travel_end, max_results=3)
        advisory_task = get_travel_advisory(country) if country else asyncio.sleep(0, result={})
        events_task = get_local_events(city=dest, start_date=travel_start, end_date=travel_end, max_results=10)
        col_task = get_cost_of_living(city=dest)

        weather, hotels, advisory, events, col = await asyncio.gather(
            weather_task, hotels_task, advisory_task, events_task, col_task,
            return_exceptions=True,
        )
        weather = weather if not isinstance(weather, Exception) else {}
        hotels = hotels if not isinstance(hotels, Exception) else {}
        advisory = advisory if not isinstance(advisory, Exception) else {}
        events = events if not isinstance(events, Exception) else {}
        col = col if not isinstance(col, Exception) else {}

        # Raw metrics
        avg_temp = (weather.get("summary") or {}).get("avg_high_c", 20)
        rainy = (weather.get("summary") or {}).get("rainy_days", 0)
        total_days = (weather.get("summary") or {}).get("total_days", 1)
        rainy_pct = rainy / max(total_days, 1)
        cost_per_night = hotels.get("cheapest_price_per_night") or 100
        advisory_count = advisory.get("advisory_count", 0)
        event_count = events.get("results_count", 0)
        qol_scores = col.get("category_scores", [])
        qol_avg = sum(s["score_out_of_10"] for s in qol_scores) / len(qol_scores) if qol_scores else 5

        # Weather match score (0-10)
        if weather_pref == "warm_dry":
            w_score = max(0, 10 - abs(avg_temp - 25) - rainy_pct * 5)
        elif weather_pref == "cool_dry":
            w_score = max(0, 10 - abs(avg_temp - 15) - rainy_pct * 5)
        elif weather_pref == "warm_any":
            w_score = max(0, min(10, avg_temp / 3))
        elif weather_pref == "snow":
            w_score = max(0, 10 - (avg_temp + 5))
        else:
            w_score = max(0, 10 - abs(avg_temp - 22) - rainy_pct * 3)

        return {
            "destination": dest,
            "country": country,
            "metrics": {
                "avg_temp_c": avg_temp,
                "rainy_days_pct": round(rainy_pct * 100, 1),
                "cost_per_night_usd": cost_per_night,
                "advisory_count": advisory_count,
                "event_count": event_count,
                "quality_of_life_score": round(qol_avg, 2),
            },
            "raw_scores": {
                "weather": round(w_score, 2),
                "cost_value": cost_per_night,
                "safety_raw": advisory_count,
                "events": event_count,
                "quality_of_life": qol_avg,
            },
        }

    results = await asyncio.gather(*[_score_one(d) for d in dest_list])
    valid = [r for r in results if "error" not in r]
    if not valid:
        return {"error": "Could not score any destination", "details": results}

    # Normalize costs (lower better)
    costs = [r["raw_scores"]["cost_value"] for r in valid]
    min_cost, max_cost = min(costs), max(costs)
    safety_raws = [r["raw_scores"]["safety_raw"] for r in valid]
    max_safety = max(safety_raws) if safety_raws else 0
    events_raws = [r["raw_scores"]["events"] for r in valid]
    max_events = max(events_raws) if events_raws else 1

    for r in valid:
        cost_norm = 10 * (1 - (r["raw_scores"]["cost_value"] - min_cost) / max(max_cost - min_cost, 1))
        safety_norm = 10 * (1 - r["raw_scores"]["safety_raw"] / max(max_safety, 1))
        events_norm = 10 * (r["raw_scores"]["events"] / max(max_events, 1))
        qol_norm = r["raw_scores"]["quality_of_life"]
        weather_norm = r["raw_scores"]["weather"]

        composite = (
            weight_map.get("cost", 0) * cost_norm
            + weight_map.get("weather", 0) * weather_norm
            + weight_map.get("safety", 0) * safety_norm
            + weight_map.get("events", 0) * events_norm
            + weight_map.get("quality_of_life", 0) * qol_norm
        )
        total_weight = sum(weight_map.values())
        r["scores"] = {
            "cost": round(cost_norm, 2),
            "weather": round(weather_norm, 2),
            "safety": round(safety_norm, 2),
            "events": round(events_norm, 2),
            "quality_of_life": round(qol_norm, 2),
            "composite": round(composite / max(total_weight, 1), 2),
        }

    valid.sort(key=lambda x: -x["scores"]["composite"])

    return {
        "travel_period": {"start": travel_start, "end": travel_end},
        "weights": weight_map,
        "weather_preference": weather_pref,
        "ranked_destinations": valid,
        "winner": valid[0]["destination"] if valid else None,
        "tip": "Composite is weighted average. Adjust weights to match what matters most to you.",
    }
