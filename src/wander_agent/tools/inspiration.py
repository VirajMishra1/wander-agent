"""Inspiration tools - find destinations by budget/interests using Kiwi 'anywhere' search."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


async def cheap_anywhere_from(
    origin: str,
    month: str | None = None,
    max_price: float | None = None,
    max_results: int = 20,
    currency: str = "USD",
) -> dict:
    """Find cheapest destinations from origin airport.

    Uses Kiwi Tequila's 'anywhere' search. Returns ranked destinations by price.

    Args:
        origin: IATA airport code (e.g., "JFK", "LAX")
        month: YYYY-MM to constrain dates (e.g., "2026-08"). Omit for any.
        max_price: Filter out destinations above this price
        max_results: Max destinations to return
        currency: USD, EUR, etc.
    """
    from ..utils.config import KIWI_API_KEY
    from ..utils.http import get_client

    if not KIWI_API_KEY:
        return {
            "error": "KIWI_API_KEY required for inspiration search.",
            "hint": "Sign up free at https://tequila.kiwi.com for sandbox access.",
        }

    client = await get_client()

    # Build date range for Kiwi (DD/MM/YYYY)
    if month:
        try:
            year, mo = month.split("-")
            month_start = datetime(int(year), int(mo), 1)
            # Last day of month
            next_mo = month_start.replace(day=28) + timedelta(days=4)
            month_end = next_mo - timedelta(days=next_mo.day)
        except Exception:
            return {"error": f"Invalid month format '{month}'. Use YYYY-MM."}
        date_from = month_start.strftime("%d/%m/%Y")
        date_to = month_end.strftime("%d/%m/%Y")
    else:
        # Next 6 months
        today = datetime.now() + timedelta(days=14)
        date_from = today.strftime("%d/%m/%Y")
        date_to = (today + timedelta(days=180)).strftime("%d/%m/%Y")

    params: dict = {
        "fly_from": origin.upper(),
        "fly_to": "anywhere",
        "date_from": date_from,
        "date_to": date_to,
        "curr": currency.upper(),
        "limit": min(max_results * 3, 200),
        "sort": "price",
    }
    if max_price:
        params["price_to"] = int(max_price)

    try:
        resp = await client.get(
            "https://api.tequila.kiwi.com/v2/search",
            params=params,
            headers={"apikey": KIWI_API_KEY},
            timeout=30.0,
        )
        if resp.status_code != 200:
            return {"error": f"Kiwi API returned {resp.status_code}", "details": resp.text[:300]}

        data = resp.json()
        offers = data.get("data", [])

        destinations: dict = {}
        for o in offers:
            dest_code = o.get("flyTo", "")
            dest_city = o.get("cityTo", "")
            price = float(o.get("price", 0))
            key = dest_code or dest_city
            if not key:
                continue
            if key not in destinations or destinations[key]["price"] > price:
                destinations[key] = {
                    "destination_airport": dest_code,
                    "destination_city": dest_city,
                    "destination_country": o.get("countryTo", {}).get("name", ""),
                    "country_code": o.get("countryTo", {}).get("code", ""),
                    "origin": origin.upper(),
                    "price": price,
                    "currency": currency.upper(),
                    "departure_date": o.get("local_departure", "")[:10],
                    "return_date": o.get("local_arrival", "")[:10],
                    "duration_hours": round(o.get("duration", {}).get("total", 0) / 3600, 1),
                    "stops": max(len(o.get("route", [])) - 1, 0),
                    "booking_url": o.get("deep_link", ""),
                }

        results = sorted(destinations.values(), key=lambda x: x["price"])[:max_results]

        return {
            "origin": origin.upper(),
            "month": month,
            "max_price": max_price,
            "results_count": len(results),
            "destinations": results,
            "cheapest": results[0] if results else None,
            "currency": currency.upper(),
            "data_source": "kiwi_tequila",
            "tip": "Pass top destinations to plan_itinerary or score_destinations.",
            "suggest_web_search": [
                f"best places to visit from {origin.upper()} {month or 'this year'}",
                f"hidden gem destinations under {currency.upper()} {int(max_price) if max_price else 1000}",
            ],
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
    """Find destinations achievable within a total trip budget.

    Calculates flight + hotel * nights. Returns destinations under budget.

    Args:
        origin: Departure airport IATA code
        total_budget: Total budget for trip
        trip_length_days: Number of nights
        departure_month: YYYY-MM or omit for any
        travelers: Number of travelers
        interests: Comma-separated (e.g., "beach,food,history")
        visa_free_only: Only visa-free destinations (requires passport_country)
        passport_country: ISO 2-letter code (e.g., "US")
        currency: USD, EUR, etc.
        max_results: Max destinations
    """
    from .hotels import search_hotels

    flight_budget_per_person = total_budget * 0.5 / travelers
    cheap = await cheap_anywhere_from(
        origin=origin,
        month=departure_month,
        max_price=flight_budget_per_person,
        max_results=max_results * 3,
        currency=currency,
    )

    if cheap.get("error") or not cheap.get("destinations"):
        return {
            "error": cheap.get("error", "No destinations under flight budget"),
            "hint": "Try a larger budget or remove month constraint.",
        }

    affordable: list = []
    candidates = cheap["destinations"][:max_results * 2]

    for dest in candidates[:max_results]:
        dest_city = dest.get("destination_city") or dest.get("destination_airport")
        dep_date = dest.get("departure_date")
        if not dep_date:
            continue
        try:
            dep_dt = datetime.strptime(dep_date, "%Y-%m-%d")
            check_in = dep_dt.strftime("%Y-%m-%d")
            check_out = (dep_dt + timedelta(days=trip_length_days)).strftime("%Y-%m-%d")
        except Exception:
            continue

        hotels = await search_hotels(
            city=dest_city, check_in=check_in, check_out=check_out,
            adults=travelers, max_results=3, currency=currency,
        )
        cheapest_hotel = hotels.get("cheapest_price_per_night") or 80
        hotel_total = cheapest_hotel * trip_length_days
        flight_total = dest["price"] * travelers
        grand_total = flight_total + hotel_total

        if grand_total <= total_budget:
            affordable.append({
                "destination": dest_city,
                "destination_airport": dest.get("destination_airport"),
                "country": dest.get("destination_country"),
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
        "savings_choosing_cheapest": round(
            (results[-1]["total_cost"] or 0) - (results[0]["total_cost"] or 0), 2
        ) if len(results) >= 2 else 0,
        "currency": currency.upper(),
        "suggest_web_search": [
            f"{' vs '.join(dest_list)} for travelers reddit",
            f"best month to visit {dest_list[0]}",
        ],
    }
