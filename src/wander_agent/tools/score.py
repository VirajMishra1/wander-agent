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

        # When origin is provided, fetch real flight cost so ranking reflects actual trip expense.
        if origin:
            from .flights import search_flights
            from ..utils.airport_data import city_to_iata
            dest_iata = city_to_iata(dest) or dest.upper()[:3]
            flight_task: object = search_flights(
                origin=origin.upper(), destination=dest_iata,
                departure_date=travel_start, return_date=travel_end,
                max_results=1,
            )
        else:
            flight_task = asyncio.sleep(0, result={})

        weather, hotels, advisory, events, col, flight_result = await asyncio.gather(
            weather_task, hotels_task, advisory_task, events_task, col_task, flight_task,
            return_exceptions=True,
        )
        weather = weather if not isinstance(weather, Exception) else {}
        hotels = hotels if not isinstance(hotels, Exception) else {}
        advisory = advisory if not isinstance(advisory, Exception) else {}
        events = events if not isinstance(events, Exception) else {}
        col = col if not isinstance(col, Exception) else {}
        flight_result = flight_result if not isinstance(flight_result, Exception) else {}

        # Raw metrics
        avg_temp = (weather.get("summary") or {}).get("avg_high_c", 20)
        rainy = (weather.get("summary") or {}).get("rainy_days", 0)
        total_days_weather = (weather.get("summary") or {}).get("total_days", 1)
        rainy_pct = rainy / max(total_days_weather, 1)

        from datetime import datetime as _dt
        trip_days = max(
            (_dt.strptime(travel_end, "%Y-%m-%d") - _dt.strptime(travel_start, "%Y-%m-%d")).days, 1
        )
        hotel_per_night = hotels.get("cheapest_price_per_night") or 80
        col_budget = (col.get("daily_budget_per_person") or {})
        col_mid = col_budget.get("mid_tier_usd")

        # flight_price_pp: per-person round-trip (search_flights contract: always per-person)
        flight_price_pp: float | None = None
        if isinstance(flight_result, dict) and flight_result.get("cheapest_price"):
            flight_price_pp = float(flight_result["cheapest_price"])

        # Cost = (flight round-trip + hotel total) / trip days — real total trip cost daily equivalent
        if flight_price_pp is not None:
            daily_cost = (flight_price_pp + hotel_per_night * trip_days) / trip_days
        elif col_mid:
            daily_cost = float(col_mid)
        else:
            daily_cost = hotel_per_night + 80

        # Safety: use advisory_level (1-4) directly, default 1 (safest) if no advisory
        advisory_level = advisory.get("advisory_level") or 1

        event_count = events.get("results_count", 0)

        # QoL proxy from cost tier (cheap=high value, expensive=low)
        if col_mid:
            qol_proxy = max(5, min(10, 10 - (col_mid - 50) / 30))
        else:
            qol_proxy = 5

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
                "daily_cost_usd_equiv": round(daily_cost, 2),
                "flight_price_per_person": flight_price_pp,
                "hotel_per_night": hotel_per_night,
                "advisory_level": advisory_level,
                "event_count": event_count,
                "value_score": round(qol_proxy, 2),
                "cost_includes_flights": flight_price_pp is not None,
            },
            "raw_scores": {
                "weather": round(w_score, 2),
                "cost_value": daily_cost,
                "safety_raw": advisory_level,
                "events": event_count,
                "quality_of_life": qol_proxy,
            },
        }

    results = await asyncio.gather(*[_score_one(d) for d in dest_list])
    valid = [r for r in results if "error" not in r]
    if not valid:
        return {"error": "Could not score any destination", "details": results}

    # Normalize costs (lower better)
    costs = [r["raw_scores"]["cost_value"] for r in valid]
    min_cost, max_cost = min(costs), max(costs)
    # Safety: advisory_level 1=best, 4=worst. Convert to 0-10 (level 1=10, level 4=0)
    for r in valid:
        r["raw_scores"]["safety_normalized"] = max(0, (4 - r["raw_scores"]["safety_raw"]) * (10 / 3))
    events_raws = [r["raw_scores"]["events"] for r in valid]
    max_events = max(events_raws) if events_raws else 1

    for r in valid:
        cost_norm = 10 * (1 - (r["raw_scores"]["cost_value"] - min_cost) / max(max_cost - min_cost, 1))
        safety_norm = r["raw_scores"]["safety_normalized"]
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

    winner = valid[0]["destination"] if valid else None
    return {
        "travel_period": {"start": travel_start, "end": travel_end},
        "weights": weight_map,
        "weather_preference": weather_pref,
        "ranked_destinations": valid,
        "winner": winner,
        "tip": "Composite is weighted average. Adjust weights to match what matters most.",
        "suggest_web_search": [
            f"why visit {winner} {travel_start[:7]}" if winner else "",
            f"{winner} vs {valid[1]['destination']}" if len(valid) >= 2 else "",
            f"best time of year for {winner}" if winner else "",
        ],
    }
