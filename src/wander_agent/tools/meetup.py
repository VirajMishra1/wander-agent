"""Multi-origin meetup optimizer.

N travelers in N different cities want to meet somewhere. Find the city
where total combined cost is lowest. No OTA does this. The math is
combinatorial: query each origin->candidate route, sum totals.

Loops over curated destinations. Concurrency-limited to avoid rate-limits.
"""

from __future__ import annotations

import asyncio
from datetime import datetime


async def multi_origin_meetup(
    origins: str,
    departure_date: str,
    return_date: str,
    max_results: int = 10,
    currency: str = "USD",
    regions: str | None = None,
) -> dict:
    """Find the cheapest common meeting destination for travelers in different cities.

    "3 friends - NYC, Berlin, Tokyo - cheapest weekend they can all meet."

    Sums round-trip flights for every traveler to ~40 popular destinations,
    ranks by total. Skips any destination that is one of the origins.

    Args:
        origins: Comma-separated IATA codes (e.g., "JFK,BER,NRT")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        max_results: Max destinations to return
        currency: USD, EUR, etc.
        regions: Limit candidates to regions (e.g., "europe,asia")
    """
    from .flights import search_flights
    from ..utils.airport_data import filter_destinations

    origin_list = [o.strip().upper() for o in origins.split(",") if o.strip()]
    if len(origin_list) < 2:
        return {"error": "Need at least 2 origin airports, comma-separated"}

    destinations = filter_destinations(regions=regions)
    # Exclude any destination that's also an origin
    destinations = [d for d in destinations if d[0] not in origin_list]

    sem = asyncio.Semaphore(5)

    async def _cost_for_traveler(origin: str, dest_iata: str) -> dict:
        async with sem:
            try:
                r = await search_flights(
                    origin=origin, destination=dest_iata,
                    departure_date=departure_date,
                    max_results=1, currency=currency,
                )
                outbound = r.get("cheapest_price")
                r2 = await search_flights(
                    origin=dest_iata, destination=origin,
                    departure_date=return_date,
                    max_results=1, currency=currency,
                )
                inbound = r2.get("cheapest_price")
                if outbound and inbound:
                    return {"origin": origin, "round_trip": outbound + inbound}
                return {"origin": origin, "round_trip": None}
            except Exception:
                return {"origin": origin, "round_trip": None}

    async def _eval_destination(iata: str, city: str, country: str, region: str) -> dict | None:
        traveler_costs = await asyncio.gather(*[
            _cost_for_traveler(o, iata) for o in origin_list
        ])
        # All travelers must have a valid round-trip price
        if any(t["round_trip"] is None for t in traveler_costs):
            return None
        total = sum(t["round_trip"] for t in traveler_costs)
        return {
            "destination": city,
            "destination_airport": iata,
            "country": country,
            "region": region,
            "total_combined_cost": round(total, 2),
            "per_traveler_breakdown": [
                {"origin": t["origin"], "round_trip_cost": round(t["round_trip"], 2)}
                for t in traveler_costs
            ],
            "average_per_traveler": round(total / len(origin_list), 2),
            "currency": currency.upper(),
        }

    results = await asyncio.gather(*[
        _eval_destination(iata, city, country, region)
        for iata, city, country, region in destinations
    ])
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda x: x["total_combined_cost"])
    top = valid[:max_results]

    return {
        "travelers": origin_list,
        "traveler_count": len(origin_list),
        "departure_date": departure_date,
        "return_date": return_date,
        "destinations_evaluated": len(destinations),
        "destinations_with_full_pricing": len(valid),
        "regions": regions or "global",
        "results_count": len(top),
        "destinations": top,
        "winner": top[0] if top else None,
        "currency": currency.upper(),
        "tip": "Show per_traveler_breakdown so each person sees their cost.",
        "suggest_web_search": [
            f"weekend trip {top[0]['destination']}" if top else "",
            f"things to do in {top[0]['destination']} group of {len(origin_list)}" if top else "",
        ],
    }
