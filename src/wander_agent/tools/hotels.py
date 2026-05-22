"""Hotel search.

Free APIs for hotels are scarce. This tool provides three layers:

1. Real hotel NAMES from fast_hotels (scrapes Google Hotels static HTML).
   Names work reliably. Prices/ratings don't (Google JS-renders them).
2. Constructed Booking.com + Google Hotels + Airbnb deeplink URLs for the
   user's exact dates. Click-through gives live prices.
3. Suggested web-search queries the LLM can run for live prices/reviews.

If TRAVELPAYOUTS_TOKEN is set, Hotellook prices are also returned. Optional.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from urllib.parse import quote_plus


def _booking_url(city: str, check_in: str, check_out: str, adults: int) -> str:
    return (
        f"https://www.booking.com/searchresults.html"
        f"?ss={quote_plus(city)}"
        f"&checkin={check_in}&checkout={check_out}&group_adults={adults}"
    )


def _google_hotels_url(city: str, check_in: str, check_out: str, adults: int) -> str:
    return (
        f"https://www.google.com/travel/hotels/{quote_plus(city)}"
        f"?q={quote_plus(city)}&checkin={check_in}&checkout={check_out}&adults={adults}"
    )


def _airbnb_url(city: str, check_in: str, check_out: str, adults: int) -> str:
    return (
        f"https://www.airbnb.com/s/{quote_plus(city)}/homes"
        f"?checkin={check_in}&checkout={check_out}&adults={adults}"
    )


async def _get_fast_hotels_names(city: str, check_in: str, check_out: str, adults: int) -> list[dict]:
    """Get real hotel names from Google Hotels via fast_hotels."""
    try:
        from fast_hotels import get_hotels
        from fast_hotels.hotels_impl import Guests, HotelData
    except ImportError:
        return []

    def _run():
        try:
            return get_hotels(
                hotel_data=[HotelData(checkin_date=check_in, checkout_date=check_out, location=city)],
                guests=Guests(adults=adults, children=0),
                fetch_mode="common",
                limit=15,
            )
        except Exception:
            return None

    result = await asyncio.to_thread(_run)
    if not result:
        return []

    hotels = []
    import html as html_mod
    for h in (getattr(result, "hotels", []) or []):
        name = html_mod.unescape(str(getattr(h, "name", "")).strip())
        if not name or "Set your dates" in name:
            continue
        hotels.append({
            "name": name,
            "amenities": list(getattr(h, "amenities", []) or []),
        })
    return hotels[:10]


async def _hotellook_prices(city: str, check_in: str, check_out: str, adults: int,
                             currency: str, max_results: int) -> list[dict]:
    """Optional: if TRAVELPAYOUTS_TOKEN is set, fetch live prices via Hotellook."""
    from ..utils.config import TRAVELPAYOUTS_TOKEN, TRAVELPAYOUTS_MARKER
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return []

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
            return []
        data = resp.json()
        if not isinstance(data, list):
            return []

        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        hotels = []
        for h in data[:max_results]:
            price_from = float(h.get("priceFrom", 0))
            if not price_from:
                continue
            hotels.append({
                "name": h.get("hotelName", "Unknown"),
                "stars": h.get("stars"),
                "price_total": price_from,
                "price_per_night": round(price_from / max(nights, 1), 2),
                "currency": currency.upper(),
                "booking_url": f"https://search.hotellook.com/hotels?hotelId={h.get('hotelId')}&checkIn={check_in}&checkOut={check_out}&adults={adults}",
            })
        hotels.sort(key=lambda x: x["price_total"])
        return hotels
    except Exception:
        return []


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
    """Search hotels with hybrid strategy.

    Returns: real hotel names (Google Hotels scrape) + deeplinks to
    Booking.com / Google Hotels / Airbnb for live prices + suggested web
    searches the LLM can run for reviews. Live prices from Hotellook only
    if TRAVELPAYOUTS_TOKEN is configured (optional).

    Args:
        city: City name (e.g., "Paris", "Tokyo")
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: Number of guests
        rooms: Number of rooms (passed to deeplinks)
        max_results: Max hotel names to return
        currency: USD, EUR, etc. (Hotellook only)
        price_range: "100-300" (Hotellook only)
        ratings: "3,4,5" (Hotellook only)
    """
    try:
        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
    except Exception:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if nights <= 0:
        return {"error": "check_out must be after check_in."}

    names_task = _get_fast_hotels_names(city, check_in, check_out, adults)
    prices_task = _hotellook_prices(city, check_in, check_out, adults, currency, max_results)
    names, hotellook_hotels = await asyncio.gather(names_task, prices_task)

    # Merge: if hotellook has data, prefer it; otherwise use scraped names
    if hotellook_hotels:
        hotels = hotellook_hotels[:max_results]
        cheapest = hotels[0]["price_per_night"]
        source = "hotellook (live prices)"
    else:
        hotels = [
            {
                "name": h["name"],
                "amenities": h["amenities"],
                "price_per_night": None,
                "price_total": None,
                "note": "Live prices not available — set TRAVELPAYOUTS_TOKEN or use the booking_links below.",
            }
            for h in names[:max_results]
        ]
        cheapest = None
        source = "google_hotels (names only — use deeplinks for live prices)"

    return {
        "city": city,
        "check_in": check_in,
        "check_out": check_out,
        "guests": adults,
        "nights": nights,
        "results_count": len(hotels),
        "hotels": hotels,
        "cheapest_price_per_night": cheapest,
        "currency": currency.upper(),
        "data_source": source,
        "booking_links": {
            "booking_com": _booking_url(city, check_in, check_out, adults),
            "google_hotels": _google_hotels_url(city, check_in, check_out, adults),
            "airbnb": _airbnb_url(city, check_in, check_out, adults),
        },
        "suggest_web_search": [
            f"best hotels {city} under ${'200' if not price_range else price_range.split('-')[-1]} {check_in[:7]}",
            f"{city} hotels {check_in[:7]} reddit recommendations",
            f"{city} where to stay neighborhood guide",
            f"{hotels[0]['name'] if hotels else city + ' hotels'} reviews",
        ],
        "note": (
            "Hotel price scraping is unreliable. Use the booking_links to see live prices, "
            "or run the suggest_web_search queries for reviews and current rates."
        ),
    }
