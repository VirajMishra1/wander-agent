"""Hotel search via Hotellook (Travelpayouts). Free API key required."""

from __future__ import annotations

from datetime import datetime


async def search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = 1,
    max_results: int = 10,
    currency: str = "USD",
    price_range: str | None = None,
    ratings: str | None = None,
) -> dict:
    """Search hotels in a city via Hotellook (Travelpayouts).

    Args:
        city: City name (e.g., "Paris", "Tokyo") - NOT IATA code
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: Number of guests
        rooms: Number of rooms
        max_results: Max results
        currency: USD, EUR, etc.
        price_range: "100-300" filter
        ratings: "3,4,5" star filter
    """
    from ..utils.config import TRAVELPAYOUTS_TOKEN, TRAVELPAYOUTS_MARKER
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "results_count": 0,
            "hotels": [],
            "error": "TRAVELPAYOUTS_TOKEN required. Free signup: https://www.travelpayouts.com",
        }

    client = await get_client()
    params: dict = {
        "location": city,
        "checkIn": check_in,
        "checkOut": check_out,
        "currency": currency.lower(),
        "adults": adults,
        "limit": max_results,
        "token": TRAVELPAYOUTS_TOKEN,
    }
    if TRAVELPAYOUTS_MARKER:
        params["marker"] = TRAVELPAYOUTS_MARKER

    try:
        resp = await client.get(
            "https://engine.hotellook.com/api/v2/cache.json",
            params=params,
            timeout=20.0,
        )
        if resp.status_code != 200:
            return {
                "city": city,
                "results_count": 0,
                "hotels": [],
                "error": f"Hotellook returned {resp.status_code}",
            }

        data = resp.json()
        if not isinstance(data, list):
            return {
                "city": city,
                "results_count": 0,
                "hotels": [],
                "error": "Unexpected response format from Hotellook",
            }

        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        hotels = []
        for h in data[:max_results]:
            price_from = float(h.get("priceFrom", 0))
            if not price_from:
                continue

            stars = h.get("stars")
            if ratings and stars is not None:
                allowed = [int(r.strip()) for r in ratings.split(",") if r.strip().isdigit()]
                if stars not in allowed:
                    continue

            per_night = round(price_from / max(nights, 1), 2)
            if price_range:
                try:
                    lo, hi = price_range.split("-")
                    if not (float(lo) <= per_night <= float(hi)):
                        continue
                except Exception:
                    pass

            hotels.append({
                "name": h.get("hotelName", "Unknown"),
                "hotel_id": h.get("hotelId"),
                "stars": stars,
                "price_total": price_from,
                "price_per_night": per_night,
                "currency": currency.upper(),
                "location_id": h.get("locationId"),
                "location_name": h.get("location", {}).get("name", ""),
                "country": h.get("location", {}).get("country", ""),
                "latitude": h.get("location", {}).get("geo", {}).get("lat"),
                "longitude": h.get("location", {}).get("geo", {}).get("lon"),
                "price_percentile": h.get("pricePercentile", {}),
                "booking_url": f"https://search.hotellook.com/hotels?hotelId={h.get('hotelId')}&checkIn={check_in}&checkOut={check_out}&adults={adults}",
            })

        hotels.sort(key=lambda x: x["price_total"])

        return {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "guests": adults,
            "nights": nights,
            "results_count": len(hotels),
            "hotels": hotels,
            "cheapest_price_per_night": hotels[0]["price_per_night"] if hotels else None,
            "currency": currency.upper(),
            "source": "hotellook (travelpayouts)",
        }
    except Exception as e:
        return {
            "city": city,
            "results_count": 0,
            "hotels": [],
            "error": str(e),
        }
