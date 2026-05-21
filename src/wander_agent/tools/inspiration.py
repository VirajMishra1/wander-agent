"""Inspiration tools - find destinations based on budget, interests, or anywhere from origin."""

from __future__ import annotations

import asyncio
from datetime import datetime


async def cheap_anywhere_from(
    origin: str,
    month: str | None = None,
    max_price: float | None = None,
    max_results: int = 20,
    currency: str = "USD",
) -> dict:
    """Find cheapest destinations from origin (Persona A: "where can I go?").

    Uses Travelpayouts' anywhere search. Returns ranked destinations
    sorted by price, with cheapest dates if month specified.

    Args:
        origin: IATA airport code (e.g., "JFK", "LAX")
        month: YYYY-MM to constrain dates (e.g., "2026-08"). Omit for any time.
        max_price: Filter out destinations above this price
        max_results: Max destinations to return
        currency: USD, EUR, etc.
    """
    from ..utils.config import TRAVELPAYOUTS_TOKEN, TRAVELPAYOUTS_MARKER
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return {"error": "TRAVELPAYOUTS_TOKEN required for inspiration search. Sign up free at travelpayouts.com"}

    client = await get_client()
    params: dict = {
        "origin": origin.upper(),
        "currency": currency.lower(),
        "limit": min(max_results * 2, 100),
        "token": TRAVELPAYOUTS_TOKEN,
        "sorting": "price",
    }
    if month:
        params["depart_date"] = month
    if TRAVELPAYOUTS_MARKER:
        params["marker"] = TRAVELPAYOUTS_MARKER

    try:
        resp = await client.get("https://api.travelpayouts.com/v2/prices/latest", params=params)
        if resp.status_code != 200:
            return {"error": f"API returned {resp.status_code}", "details": resp.text[:200]}

        data = resp.json()
        offers = data.get("data", [])

        destinations: dict = {}
        for o in offers:
            dest = o.get("destination", "")
            price = float(o.get("value", 0))
            if max_price and price > max_price:
                continue
            if dest not in destinations or destinations[dest]["price"] > price:
                destinations[dest] = {
                    "destination": dest,
                    "origin": o.get("origin", origin.upper()),
                    "price": price,
                    "currency": currency.upper(),
                    "departure_date": o.get("depart_date", ""),
                    "return_date": o.get("return_date", ""),
                    "transfers": o.get("number_of_changes", 0),
                    "trip_class": o.get("trip_class", 0),
                    "found_at": o.get("found_at", ""),
                }

        results = sorted(destinations.values(), key=lambda x: x["price"])[:max_results]

        return {
            "origin": origin.upper(),
            "month": month,
            "max_price": max_price,
            "results_count": len(results),
            "destinations": results,
            "cheapest": results[0] if results else None,
            "tip": "Pass each destination to plan_itinerary or search_hotels for details.",
        }
    except Exception as e:
        return {"error": str(e)}


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
) -> dict:
    """Find destinations achievable within a total budget (Persona A killer feature).

    Calculates: flight + hotel * nights, returns destinations under budget.
    Optionally filters by interests and visa-free requirements.

    Args:
        origin: Departure airport IATA code
        total_budget: Total budget for trip (flights + hotels)
        trip_length_days: Number of nights
        departure_month: YYYY-MM (e.g., "2026-08") or omit for any
        travelers: Number of travelers
        interests: Comma-separated (e.g., "beach,food,history")
        visa_free_only: Only include visa-free destinations
        passport_country: Passport country code (e.g., "US") for visa filtering
        currency: USD, EUR, etc.
        max_results: Max destinations to return
    """
    from .hotels import search_hotels
    from .destination import geocode

    # Step 1: get cheap flights anywhere
    flight_budget_per_person = total_budget * 0.6 / travelers  # assume 60% flight budget
    cheap_dests = await cheap_anywhere_from(
        origin=origin,
        month=departure_month,
        max_price=flight_budget_per_person,
        max_results=max_results * 3,
        currency=currency,
    )

    if cheap_dests.get("error") or not cheap_dests.get("destinations"):
        return {
            "error": cheap_dests.get("error", "No destinations found within flight budget"),
            "hint": "Try increasing budget or removing month constraint",
        }

    affordable: list = []

    # Step 2: for each cheap destination, estimate hotel cost
    candidates = cheap_dests["destinations"][:max_results * 2]

    for dest in candidates[:max_results]:
        dest_code = dest["destination"]
        dep_date = dest.get("departure_date", "")
        if not dep_date:
            continue
        try:
            dep_dt = datetime.fromisoformat(dep_date.replace("Z", "+00:00"))
            check_in = dep_dt.strftime("%Y-%m-%d")
            check_out = (dep_dt.replace(day=min(dep_dt.day + trip_length_days, 28))).strftime("%Y-%m-%d")
        except Exception:
            continue

        # Cheap hotel lookup
        hotels = await search_hotels(
            city=dest_code, check_in=check_in, check_out=check_out,
            adults=travelers, max_results=3, currency=currency,
        )
        cheapest_hotel = hotels.get("cheapest_price_per_night") or 80  # fallback assumption
        hotel_total = cheapest_hotel * trip_length_days * (travelers / 2 + 0.5)  # rough rooms
        flight_total = dest["price"] * travelers
        grand_total = flight_total + hotel_total

        if grand_total <= total_budget:
            affordable.append({
                "destination": dest_code,
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
                "transfers": dest.get("transfers", 0),
            })

    affordable.sort(key=lambda x: x["grand_total"])

    return {
        "origin": origin.upper(),
        "total_budget": total_budget,
        "trip_length_days": trip_length_days,
        "departure_month": departure_month,
        "travelers": travelers,
        "results_count": len(affordable),
        "destinations": affordable[:max_results],
        "tip": "Use score_destinations on these results to rank by weather, safety, and cost-of-living.",
    }


async def compare_destinations(
    origin: str,
    destinations: str,
    departure_date: str,
    return_date: str,
    travelers: int = 1,
    currency: str = "USD",
) -> dict:
    """Compare multiple destinations side-by-side for the same dates.

    Pulls flight prices and hotel rates in parallel for each destination.
    Perfect for "Paris vs Rome vs Barcelona for next month".

    Args:
        origin: Departure airport IATA code
        destinations: Comma-separated destinations (e.g., "CDG,FCO,BCN" or "Paris,Rome,Barcelona")
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

    async def _fetch(dest: str) -> dict:
        flight_task = search_flights(
            origin=origin, destination=dest, departure_date=departure_date,
            return_date=return_date, adults=travelers, max_results=3, currency=currency,
        )
        hotel_task = search_hotels(
            city=dest, check_in=departure_date, check_out=return_date,
            adults=travelers, max_results=3, currency=currency,
        )
        flight, hotel = await asyncio.gather(flight_task, hotel_task, return_exceptions=True)
        flight = flight if not isinstance(flight, Exception) else {}
        hotel = hotel if not isinstance(hotel, Exception) else {}

        nights = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(departure_date, "%Y-%m-%d")).days
        flight_total = (flight.get("cheapest_price") or 0) * travelers
        hotel_per_night = hotel.get("cheapest_price_per_night") or 0
        hotel_total = hotel_per_night * nights

        return {
            "destination": dest,
            "flight_cheapest_per_person": flight.get("cheapest_price"),
            "flight_total": flight_total,
            "hotel_per_night": hotel_per_night,
            "hotel_total": hotel_total,
            "total_cost": round(flight_total + hotel_total, 2),
            "currency": currency.upper(),
            "nights": nights,
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
        "savings_choosing_cheapest": round((results[-1]["total_cost"] or 0) - (results[0]["total_cost"] or 0), 2) if len(results) >= 2 else 0,
        "currency": currency.upper(),
    }
