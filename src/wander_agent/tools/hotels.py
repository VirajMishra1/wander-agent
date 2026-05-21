"""Hotel search with fallback chain: Travelpayouts (Hotellook) -> Xotelo."""

from __future__ import annotations

from datetime import datetime


async def _search_hotellook(
    location: str, check_in: str, check_out: str,
    adults: int, currency: str, max_results: int,
) -> dict | None:
    from ..utils.config import TRAVELPAYOUTS_TOKEN, TRAVELPAYOUTS_MARKER
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return None

    client = await get_client()
    params: dict = {
        "location": location,
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
        resp = await client.get("https://engine.hotellook.com/api/v2/cache.json", params=params)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, list):
            return None

        hotels = []
        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        for h in data[:max_results]:
            price_from = float(h.get("priceFrom", 0))
            hotels.append({
                "name": h.get("hotelName", "Unknown"),
                "hotel_id": h.get("hotelId"),
                "stars": h.get("stars"),
                "price_total": price_from,
                "price_per_night": round(price_from / max(nights, 1), 2),
                "currency": currency.upper(),
                "location_id": h.get("locationId"),
                "location_name": h.get("location", {}).get("name", ""),
                "country": h.get("location", {}).get("country", ""),
                "latitude": h.get("location", {}).get("geo", {}).get("lat"),
                "longitude": h.get("location", {}).get("geo", {}).get("lon"),
                "price_percentile": h.get("pricePercentile", {}),
                "booking_url": f"https://search.hotellook.com/hotels?hotelId={h.get('hotelId')}&checkIn={check_in}&checkOut={check_out}&adults={adults}",
                "source": "hotellook",
            })
        hotels.sort(key=lambda x: x["price_total"] or 999999)
        return {"hotels": hotels, "source": "hotellook"}
    except Exception:
        return None


async def _search_xotelo(
    location: str, check_in: str, check_out: str,
    adults: int, max_results: int,
) -> dict | None:
    """Xotelo - free, no auth. Needs TripAdvisor location_key first."""
    from ..utils.http import get_client

    client = await get_client()
    try:
        # Step 1: find location key
        loc_resp = await client.get(
            "https://data.xotelo.com/api/list_locations",
            params={"query": location, "limit": 1},
        )
        if loc_resp.status_code != 200:
            return None
        loc_data = loc_resp.json()
        results = loc_data.get("result", {}).get("locations", [])
        if not results:
            return None
        location_key = results[0].get("location_key")
        if not location_key:
            return None

        # Step 2: get hotel list
        list_resp = await client.get(
            "https://data.xotelo.com/api/list",
            params={
                "location_key": location_key,
                "check_in": check_in,
                "check_out": check_out,
                "limit": max_results,
                "sort": "best_value",
            },
        )
        if list_resp.status_code != 200:
            return None
        hotels_raw = list_resp.json().get("result", {}).get("list", [])

        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        hotels = []
        for h in hotels_raw[:max_results]:
            price = h.get("price")
            hotels.append({
                "name": h.get("name", "Unknown"),
                "hotel_id": h.get("key"),
                "rating": h.get("review_summary", {}).get("rating"),
                "review_count": h.get("review_summary", {}).get("count"),
                "price_total": float(price) if price else None,
                "price_per_night": round(float(price) / max(nights, 1), 2) if price else None,
                "currency": "USD",
                "geo": h.get("geo", {}),
                "amenities": h.get("amenities", []),
                "source": "xotelo",
            })
        hotels.sort(key=lambda x: x["price_total"] or 999999)
        return {"hotels": hotels, "source": "xotelo"}
    except Exception:
        return None


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
    """Search hotels with Hotellook (primary) -> Xotelo (fallback).

    Args:
        city: City name (e.g., "Paris", "Tokyo") - NOT IATA code
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: number of guests
        rooms: number of rooms
        max_results: max results to return
        currency: USD, EUR, etc.
        price_range: "100-300" (Hotellook only)
        ratings: "3,4,5" (Hotellook only)
    """
    # Try Hotellook first
    hl = await _search_hotellook(city, check_in, check_out, adults, currency, max_results)
    if hl and hl["hotels"]:
        return {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "guests": adults,
            "results_count": len(hl["hotels"]),
            "hotels": hl["hotels"],
            "cheapest_price_per_night": hl["hotels"][0]["price_per_night"],
            "currency": currency.upper(),
            "data_source": "hotellook",
        }

    # Fallback to Xotelo
    xo = await _search_xotelo(city, check_in, check_out, adults, max_results)
    if xo and xo["hotels"]:
        return {
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "guests": adults,
            "results_count": len(xo["hotels"]),
            "hotels": xo["hotels"],
            "cheapest_price_per_night": xo["hotels"][0]["price_per_night"],
            "currency": "USD",
            "data_source": "xotelo",
        }

    return {
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "results_count": 0,
        "hotels": [],
        "error": "No hotel sources available. Configure TRAVELPAYOUTS_TOKEN in .env (free signup) or rely on Xotelo (no auth needed but city must be on TripAdvisor)",
    }
