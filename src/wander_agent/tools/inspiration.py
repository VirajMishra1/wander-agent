"""Inspiration tools - loop fast_flights over curated destination list.

Kiwi's public sandbox is closed (partner-only). We use fast_flights against
a curated list of ~40 popular global destinations instead. Slower but works
with zero API keys for flights.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


# Limit parallel fast_flights calls to avoid Google rate-limits.
_FLIGHT_CONCURRENCY = 5


async def _gather_with_limit(coros: list, limit: int) -> list:
    sem = asyncio.Semaphore(limit)

    async def _bounded(c):
        async with sem:
            return await c

    return await asyncio.gather(*(_bounded(c) for c in coros), return_exceptions=True)


async def cheap_anywhere_from(
    origin: str,
    month: str | None = None,
    max_price: float | None = None,
    max_results: int = 20,
    currency: str = "USD",
    regions: str | None = None,
) -> dict:
    """Find cheapest destinations from origin.

    Loops fast_flights (Google Flights) over ~40 popular global destinations.
    No API key needed. Takes ~30-60 seconds because it queries each destination.

    Args:
        origin: IATA airport code (e.g., "JFK")
        month: YYYY-MM constraint (uses 15th of month). Omit for ~30 days out.
        max_price: Filter destinations above this price
        max_results: Max destinations to return
        currency: USD, EUR, etc.
        regions: Comma-separated regions to limit search (europe, asia, americas,
                 oceania, africa, middle_east). Omit for global.
    """
    from .flights import search_flights
    from ..utils.airport_data import filter_destinations

    if month:
        try:
            year, mo = month.split("-")
            search_date = datetime(int(year), int(mo), 15)
        except Exception:
            return {"error": f"Invalid month '{month}'. Use YYYY-MM."}
    else:
        search_date = datetime.now() + timedelta(days=30)

    if search_date.date() <= datetime.now().date():
        search_date = datetime.now() + timedelta(days=14)

    departure_date = search_date.strftime("%Y-%m-%d")
    destinations = filter_destinations(regions=regions, exclude_origin=origin)

    async def _price_one(iata: str, city: str, country: str, region: str) -> dict | None:
        result = await search_flights(
            origin=origin, destination=iata, departure_date=departure_date,
            max_results=1, currency=currency,
        )
        if result.get("results_count", 0) == 0:
            return None
        cheapest = result["flights"][0]
        price = cheapest.get("price")
        if not price or (max_price and price > max_price):
            return None
        return {
            "destination_airport": iata,
            "destination_city": city,
            "destination_country": country,
            "region": region,
            "origin": origin.upper(),
            "price": price,
            "currency": currency.upper(),
            "departure_date": departure_date,
            "airline": cheapest.get("airline", ""),
            "duration": cheapest.get("duration", ""),
            "stops": cheapest.get("stops"),
            "price_signal": result.get("price_signal", "typical"),
        }

    coros = [_price_one(iata, city, country, region) for iata, city, country, region in destinations]
    raw_results = await _gather_with_limit(coros, _FLIGHT_CONCURRENCY)

    valid = [r for r in raw_results if r and not isinstance(r, Exception)]
    valid.sort(key=lambda x: x["price"])
    valid = valid[:max_results]

    return {
        "origin": origin.upper(),
        "departure_date": departure_date,
        "month": month,
        "max_price": max_price,
        "regions": regions or "global",
        "destinations_searched": len(destinations),
        "results_count": len(valid),
        "destinations": valid,
        "cheapest": valid[0] if valid else None,
        "currency": currency.upper(),
        "data_source": "google_flights (looped)",
        "tip": "Pass top destinations to plan_itinerary or score_destinations.",
        "suggest_web_search": [
            f"best places from {origin.upper()} {month or 'this year'}",
            f"hidden gem destinations under {currency.upper()} {int(max_price) if max_price else 1000}",
        ],
    }


async def find_destinations_by_budget(
    origin: str,
    total_budget: float,
    trip_length_days: int = 7,
    departure_month: str | None = None,
    travelers: int = 1,
    interests: str | None = None,
    visa_free_only: bool = False,
    passport_country: str | None = None,
    currency: str = "USD",
    max_results: int = 10,
    regions: str | None = None,
) -> dict:
    """Find destinations achievable within a total trip budget.

    Calculates flight + hotel * nights. Returns destinations under budget.

    Args:
        origin: Departure IATA code
        total_budget: Total budget for trip
        trip_length_days: Number of nights
        departure_month: YYYY-MM or omit for ~30 days out
        travelers: Number of travelers
        interests: Comma-separated (e.g., "beach,food,history")
        visa_free_only: Filter visa-free (requires passport_country)
        passport_country: ISO 2-letter (e.g., "US")
        currency: USD, EUR, etc.
        max_results: Max destinations
        regions: Limit search to regions (e.g., "europe,asia")
    """
    from .hotels import search_hotels

    # Per-person flight budget estimate (50% of total)
    flight_budget_pp = total_budget * 0.5 / travelers

    cheap = await cheap_anywhere_from(
        origin=origin,
        month=departure_month,
        max_price=flight_budget_pp,
        max_results=max_results * 2,
        currency=currency,
        regions=regions,
    )

    if cheap.get("error") or not cheap.get("destinations"):
        return {
            "error": cheap.get("error", "No destinations under flight budget"),
            "hint": "Try larger budget or different regions.",
        }

    affordable: list = []
    async def _check_destination(dest: dict) -> dict | None:
        dest_city = dest["destination_city"]
        dep_dt = datetime.strptime(dest["departure_date"], "%Y-%m-%d")
        check_in = dest["departure_date"]
        check_out = (dep_dt + timedelta(days=trip_length_days)).strftime("%Y-%m-%d")

        hotels = await search_hotels(
            city=dest_city, check_in=check_in, check_out=check_out,
            adults=travelers, max_results=3, currency=currency,
        )
        cheapest_hotel = hotels.get("cheapest_price_per_night") or 80
        hotel_total = cheapest_hotel * trip_length_days
        flight_total = dest["price"] * travelers
        grand_total = flight_total + hotel_total

        if grand_total > total_budget:
            return None
        return {
            "destination": dest_city,
            "destination_airport": dest["destination_airport"],
            "country": dest["destination_country"],
            "region": dest["region"],
            "flight_price_per_person": dest["price"],
            "flight_total": flight_total,
            "hotel_per_night": cheapest_hotel,
            "hotel_total": round(hotel_total, 2),
            "grand_total": round(grand_total, 2),
            "currency": currency.upper(),
            "departure_date": check_in,
            "return_date": check_out,
            "trip_length_days": trip_length_days,
            "budget_remaining": round(total_budget - grand_total, 2),
            "stops": dest.get("stops", 0),
            "airline": dest.get("airline", ""),
        }

    candidates = cheap["destinations"][:max_results * 2]
    raw = await _gather_with_limit([_check_destination(d) for d in candidates], 5)
    affordable = [r for r in raw if r and not isinstance(r, Exception)]
    affordable.sort(key=lambda x: x["grand_total"])

    return {
        "origin": origin.upper(),
        "total_budget": total_budget,
        "trip_length_days": trip_length_days,
        "departure_month": departure_month,
        "travelers": travelers,
        "regions": regions or "global",
        "results_count": len(affordable),
        "destinations": affordable[:max_results],
        "tip": "Run score_destinations on these to rank by weather/safety/cost-of-living.",
        "suggest_web_search": [
            f"best destinations under {currency.upper()} {int(total_budget)} {departure_month or ''}",
            f"travel deals from {origin.upper()} {departure_month or ''}",
        ],
    }


async def compare_destinations(
    origin: str,
    destinations: str,
    departure_date: str,
    return_date: str,
    travelers: int = 1,
    currency: str = "USD",
) -> dict:
    """Side-by-side cost comparison of multiple destinations.

    Args:
        origin: Departure IATA code
        destinations: Comma-separated (e.g., "CDG,FCO,BCN" or "Paris,Rome,Barcelona")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        travelers: Number of travelers
        currency: USD, EUR, etc.
    """
    from .flights import search_flights
    from .hotels import search_hotels

    dest_list = [d.strip() for d in destinations.split(",") if d.strip()]
    if len(dest_list) < 2:
        return {"error": "Provide at least 2 destinations, comma-separated"}

    from ..utils.airport_data import city_to_iata, iata_to_city

    async def _fetch(dest: str) -> dict:
        is_iata = len(dest) == 3 and dest.isalpha()
        dest_iata = dest.upper() if is_iata else (city_to_iata(dest) or dest.upper())
        dest_city = dest if not is_iata else (iata_to_city(dest) or dest)

        flight = await search_flights(
            origin=origin, destination=dest_iata, departure_date=departure_date,
            return_date=return_date, adults=travelers, max_results=3, currency=currency,
        )
        if isinstance(flight, Exception) or flight.get("results_count", 0) == 0:
            # Round-trip failed - try sum of two one-ways
            outbound = await search_flights(
                origin=origin, destination=dest_iata, departure_date=departure_date,
                adults=travelers, max_results=3, currency=currency,
            )
            inbound = await search_flights(
                origin=dest_iata, destination=origin, departure_date=return_date,
                adults=travelers, max_results=3, currency=currency,
            )
            out_p = outbound.get("cheapest_price") if isinstance(outbound, dict) else None
            in_p = inbound.get("cheapest_price") if isinstance(inbound, dict) else None
            if out_p and in_p:
                flight = {"cheapest_price": out_p + in_p, "_note": "sum of two one-ways"}
            else:
                flight = flight if isinstance(flight, dict) else {}

        hotel = await search_hotels(
            city=dest_city, check_in=departure_date, check_out=return_date,
            adults=travelers, max_results=3, currency=currency,
        )
        if isinstance(hotel, Exception):
            hotel = {}

        nights = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(departure_date, "%Y-%m-%d")).days
        flight_per_person = flight.get("cheapest_price") or 0
        flight_total = flight_per_person * travelers
        hotel_per_night = hotel.get("cheapest_price_per_night") or 0
        hotel_total = hotel_per_night * nights

        return {
            "destination": dest_city,
            "destination_airport": dest_iata,
            "flight_cheapest_per_person": flight_per_person or None,
            "flight_total": flight_total,
            "hotel_per_night": hotel_per_night or None,
            "hotel_total": hotel_total,
            "total_cost": round(flight_total + hotel_total, 2),
            "currency": currency.upper(),
            "nights": nights,
            "hotel_data_available": bool(hotel_per_night),
        }

    results = await asyncio.gather(*[_fetch(d) for d in dest_list])
    results.sort(key=lambda x: x["total_cost"] or 999999)

    return {
        "origin": origin.upper(),
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers,
        "comparisons": results,
        "cheapest": results[0] if results else None,
        "most_expensive": results[-1] if results else None,
        "savings_choosing_cheapest": round(
            (results[-1]["total_cost"] or 0) - (results[0]["total_cost"] or 0), 2
        ) if len(results) >= 2 else 0,
        "currency": currency.upper(),
        "suggest_web_search": [
            f"{' vs '.join(dest_list)} for travelers reddit",
            f"best month to visit {dest_list[0]}",
        ],
    }
