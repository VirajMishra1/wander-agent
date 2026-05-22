"""Hotel search.

Free APIs for hotels are scarce. This tool provides three layers:

1. Real hotel NAMES from fast_hotels (scrapes Google Hotels static HTML).
   Names work reliably. Prices/ratings don't (Google JS-renders them).
2. Constructed Booking.com + Google Hotels + Airbnb deeplink URLs for the
   user's exact dates. Click-through gives live prices.
3. Suggested web-search queries the LLM can run for live prices/reviews.

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
    """Search hotels — scrapes Google Hotels for names, returns booking deeplinks.

    No API key required. Use booking_links for live prices.

    Args:
        city: City name (e.g., "Paris", "Tokyo")
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: Number of guests
        rooms: Number of rooms
        max_results: Max hotel names to return
        currency: Currency code for display
        price_range: Ignored (kept for compatibility)
        ratings: Ignored (kept for compatibility)
    """
    try:
        nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
    except Exception:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if nights <= 0:
        return {"error": "check_out must be after check_in."}

    names = await _get_fast_hotels_names(city, check_in, check_out, adults)

    hotels = [
        {
            "name": h["name"],
            "amenities": h["amenities"],
            "price_per_night": None,
            "price_total": None,
        }
        for h in names[:max_results]
    ]
    cheapest = None
    source = "google_hotels_scrape"

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
