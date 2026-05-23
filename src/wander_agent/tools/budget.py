"""Budget optimizer - finds cheapest travel combinations."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


async def optimize_budget(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    adults: int = 1,
    currency: str = "USD",
    flexible_dates: bool = True,
    flexibility_days: int = 3,
) -> dict:
    """Find the cheapest flight + hotel combination for a trip.

    Searches multiple date combinations if flexible_dates is true.
    Compares options and returns the best deal.

    Args:
        origin: Departure airport IATA code (e.g., "JFK")
        destination: Arrival airport IATA code (e.g., "CDG")
        departure_date: Preferred departure date (YYYY-MM-DD)
        return_date: Preferred return date (YYYY-MM-DD)
        adults: Number of travelers
        currency: Currency for prices
        flexible_dates: Search nearby dates for cheaper options
        flexibility_days: Days to search around preferred dates (1-7)
    """
    from .flights import search_flights
    from .hotels import search_hotels

    flexibility_days = min(max(flexibility_days, 0), 7)
    dep = datetime.strptime(departure_date, "%Y-%m-%d")
    ret = datetime.strptime(return_date, "%Y-%m-%d")
    trip_duration = (ret - dep).days

    # Generate date combinations to search
    date_combos = [{"dep": departure_date, "ret": return_date}]
    if flexible_dates and flexibility_days > 0:
        for d in range(-flexibility_days, flexibility_days + 1):
            new_dep = dep + timedelta(days=d)
            new_ret = new_dep + timedelta(days=trip_duration)
            if new_dep.date() > datetime.now().date():
                combo = {
                    "dep": new_dep.strftime("%Y-%m-%d"),
                    "ret": new_ret.strftime("%Y-%m-%d"),
                }
                if combo not in date_combos:
                    date_combos.append(combo)

    # Search flights for each date combo (parallel, max 3 to avoid rate limits)
    flight_results = []
    for batch_start in range(0, len(date_combos), 3):
        batch = date_combos[batch_start:batch_start + 3]
        tasks = [
            search_flights(
                origin=origin,
                destination=destination,
                departure_date=combo["dep"],
                return_date=combo["ret"],
                adults=adults,
                max_results=3,
                currency=currency,
            )
            for combo in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for combo, result in zip(batch, results):
            if isinstance(result, Exception):
                continue
            price = result.get("cheapest_price")
            if not price and result.get("flights"):
                price = result["flights"][0].get("price")
            if price:
                flight_results.append({
                    "departure_date": combo["dep"],
                    "return_date": combo["ret"],
                    "price": price,
                    "currency": result.get("currency", currency),
                    "booking_links": result.get("booking_links", {}),
                    "kiwi_live_fares": result.get("kiwi_live_fares", []),
                })

    # Search hotels - translate IATA destination code to city name
    from ..utils.airport_data import iata_to_city
    hotel_city = iata_to_city(destination) or destination

    hotel_result = await search_hotels(
        city=hotel_city,
        check_in=departure_date,
        check_out=return_date,
        adults=adults,
        max_results=5,
        currency=currency,
    )

    # Calculate total costs for each combination
    combinations = []
    cheapest_hotel_per_night = None
    if hotel_result.get("hotels"):
        for h in hotel_result["hotels"]:
            if h.get("price_per_night"):
                if cheapest_hotel_per_night is None or h["price_per_night"] < cheapest_hotel_per_night:
                    cheapest_hotel_per_night = h["price_per_night"]

    for flight in sorted(flight_results, key=lambda x: x["price"]):
        dep_date = datetime.strptime(flight["departure_date"], "%Y-%m-%d")
        ret_date = datetime.strptime(flight["return_date"], "%Y-%m-%d")
        nights = (ret_date - dep_date).days

        hotel_total = (cheapest_hotel_per_night or 0) * nights
        total = flight["price"] * adults + hotel_total

        combinations.append({
            "departure_date": flight["departure_date"],
            "return_date": flight["return_date"],
            "nights": nights,
            "flight_price_per_person": flight["price"],
            "flight_total": flight["price"] * adults,
            "hotel_per_night": cheapest_hotel_per_night,
            "hotel_total": hotel_total,
            "grand_total": round(total, 2),
            "currency": currency,
            "flight_booking_links": flight.get("booking_links", {}),
            "kiwi_live_fares": flight.get("kiwi_live_fares", []),
        })

    combinations.sort(key=lambda x: x["grand_total"])

    savings = 0
    if len(combinations) >= 2:
        original = next(
            (c for c in combinations if c["departure_date"] == departure_date),
            combinations[-1],
        )
        savings = round(original["grand_total"] - combinations[0]["grand_total"], 2)

    best = combinations[0] if combinations else None
    return {
        "origin": origin,
        "destination": destination,
        "preferred_dates": {"departure": departure_date, "return": return_date},
        "adults": adults,
        "dates_searched": len(date_combos),
        "best_combination": best,
        "all_combinations": combinations[:5],
        "potential_savings": savings,
        "currency": currency,
        "hotel_options": hotel_result.get("hotels", [])[:3],
        "hotel_booking_links": hotel_result.get("booking_links", {}),
        "flight_booking_links": best.get("flight_booking_links", {}) if best else {},
        "kiwi_live_fares": best.get("kiwi_live_fares", []) if best else [],
        "tip": f"You could save {currency} {savings} by shifting dates!" if savings > 0 else "Your preferred dates are already the cheapest.",
    }
