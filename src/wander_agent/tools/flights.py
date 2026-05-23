"""Flight search — Google Flights + Kiwi.com live prices.

Runs both sources in parallel:
  - fast_flights: Google Flights scraper (airline names, typical prices)
  - kiwi_client: Kiwi MCP live search (real bookable prices + deeplinks)

Kiwi results appear as kiwi_live_fares in the response.
If Google Flights is blocked, Kiwi results promote to primary.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime


# Currency symbols to ISO codes (Google geo-detects, we normalize)
SYMBOL_TO_CODE = {
    "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR",
    "₩": "KRW", "₽": "RUB", "₺": "TRY", "R$": "BRL", "C$": "CAD",
    "A$": "AUD", "HK$": "HKD", "S$": "SGD", "NZ$": "NZD", "CHF": "CHF",
    "MX$": "MXN", "kr": "SEK", "zł": "PLN", "₪": "ILS",
}


def _parse_price(raw: str) -> tuple[float, str]:
    """Extract (amount, currency_code) from strings like '₹17180' or 'US$300'."""
    if not raw or raw.lower() in ("free", "n/a"):
        return (0.0, "USD")
    # Find currency symbol/prefix
    code = "USD"
    for sym, c in SYMBOL_TO_CODE.items():
        if raw.startswith(sym) or raw.startswith(sym + " "):
            code = c
            raw = raw[len(sym):].strip()
            break
    # Strip non-numeric except commas/dots
    nums = re.sub(r"[^\d.,]", "", raw).replace(",", "")
    try:
        return (float(nums) if nums else 0.0, code)
    except ValueError:
        return (0.0, code)


async def _parse_flight_time(time_str: str, base_date: str) -> str:
    """Convert '9:40 PM on Tue, Jul 21' to ISO-ish format."""
    return time_str  # Keep raw — LLM handles natural language fine


async def _search_fast_flights(
    origin: str, destination: str, departure_date: str, return_date: str | None,
    adults: int, max_results: int, currency: str, nonstop_only: bool,
) -> dict | None:
    try:
        from fast_flights import FlightData, Passengers, get_flights
    except ImportError:
        return None

    flight_data = [FlightData(date=departure_date, from_airport=origin.upper(), to_airport=destination.upper())]
    trip = "one-way"
    if return_date:
        flight_data.append(FlightData(date=return_date, from_airport=destination.upper(), to_airport=origin.upper()))
        trip = "round-trip"

    # fast_flights is sync; run in thread to avoid blocking
    def _run(mode: str):
        return get_flights(
            flight_data=flight_data,
            trip=trip,
            seat="economy",
            passengers=Passengers(adults=adults),
            fetch_mode=mode,
        )

    # Try common first, then fallback. Google sometimes serves stripped HTML
    # with empty airline names; retry handles that.
    result = None
    for mode in ("common", "fallback"):
        try:
            result = await asyncio.to_thread(_run, mode)
        except Exception:
            continue
        flights_attr = getattr(result, "flights", []) or []
        has_data = any(str(getattr(f, "name", "")).strip() for f in flights_attr[:5])
        if flights_attr and has_data:
            break
        result = None

    if not result:
        return None
    raw_flights = getattr(result, "flights", []) or []
    raw_flights = [f for f in raw_flights if str(getattr(f, "name", "")).strip()]
    if not raw_flights:
        return None

    # Need currency conversion if Google returned non-target currency
    from .currency import convert_currency

    parsed = []
    seen_keys = set()
    for f in raw_flights:
        if nonstop_only and getattr(f, "stops", 0) != 0:
            continue
        price_raw = str(getattr(f, "price", "") or "")
        amount, native_curr = _parse_price(price_raw)
        if amount == 0:
            continue
        airline = getattr(f, "name", "")
        departure = getattr(f, "departure", "")
        arrival = getattr(f, "arrival", "")
        # Dedupe by (airline, departure, arrival, price)
        dedup_key = (airline, departure, arrival, round(amount, 2))
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)
        parsed.append({
            "airline": airline,
            "departure": departure,
            "arrival": arrival,
            "arrival_time_offset": getattr(f, "arrival_time_ahead", ""),
            "duration": getattr(f, "duration", ""),
            "stops": getattr(f, "stops", 0),
            "delay": getattr(f, "delay", None),
            "is_best": bool(getattr(f, "is_best", False)),
            "_price_native": amount,
            "_native_currency": native_curr,
        })

    # Convert prices to requested currency (batch — one rate lookup per source currency)
    target = currency.upper()
    rates: dict = {}
    for f in parsed:
        nc = f["_native_currency"]
        if nc != target and nc not in rates:
            conv = await convert_currency(1.0, nc, target)
            if not conv.get("error"):
                rates[nc] = conv["exchange_rate"]
            else:
                rates[nc] = None

    for f in parsed:
        nc = f["_native_currency"]
        if nc == target:
            f["price"] = f["_price_native"]
        elif rates.get(nc):
            f["price"] = round(f["_price_native"] * rates[nc], 2)
        else:
            f["price"] = f["_price_native"]
        f["currency"] = target
        # Strip internal scaffolding from output
        del f["_price_native"]
        del f["_native_currency"]

    parsed.sort(key=lambda x: x["price"])
    return {
        "flights": parsed[:max_results],
        "source": "google_flights (via fast_flights)",
        "price_signal": getattr(result, "current_price", "typical"),
    }


async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    max_results: int = 5,
    currency: str = "USD",
    nonstop_only: bool = False,
) -> dict:
    """Search flights via Google Flights + Kiwi.com live prices.

    Runs both sources in parallel. Returns merged results:
    - flights[]: Google Flights data (airline names, scraper)
    - kiwi_live_fares[]: Kiwi live prices with direct booking links

    Args:
        origin: IATA airport code (e.g., "JFK")
        destination: IATA airport code (e.g., "CDG")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD for round trip
        adults: Passengers
        max_results: Max results per source
        currency: Target currency (prices converted)
        nonstop_only: Skip flights with stops
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    from ..utils.kiwi_client import search_kiwi_flights

    # Run Google Flights + Kiwi in parallel
    gf_task = _search_fast_flights(
        origin, destination, departure_date, return_date,
        adults, max_results, currency, nonstop_only,
    )
    kiwi_task = search_kiwi_flights(
        origin, destination, departure_date, return_date,
        adults, currency, max_results, nonstop_only,
    )
    gf, kiwi_fares = await asyncio.gather(gf_task, kiwi_task, return_exceptions=True)

    # Coerce exceptions to None / []
    if isinstance(gf, Exception):
        gf = None
    if isinstance(kiwi_fares, Exception):
        kiwi_fares = []
    kiwi_fares = kiwi_fares or []

    gf_flights = (gf or {}).get("flights", [])
    has_gf = bool(gf_flights)
    has_kiwi = bool(kiwi_fares)

    if not has_gf and not has_kiwi:
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "results_count": 0,
            "flights": [],
            "kiwi_live_fares": [],
            "error": (
                "Both Google Flights scraper and Kiwi.com are unavailable. "
                "Try again in a few minutes."
            ),
        }

    # If Google Flights failed, promote Kiwi as primary
    if not has_gf and has_kiwi:
        cheapest = kiwi_fares[0]["price"]
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": adults,
            "results_count": len(kiwi_fares),
            "flights": [],
            "kiwi_live_fares": kiwi_fares,
            "cheapest_price": cheapest,
            "cheapest_price_total": round(cheapest * adults, 2),
            "price_is_per_person": True,
            "currency": currency.upper(),
            "data_confidence": "live",
            "data_source": "kiwi.com",
            "note": "Google Flights unavailable. Showing Kiwi.com live fares only.",
            "suggest_web_search": [
                f"{origin} to {destination} mistake fares {departure_date[:7]}",
                f"{origin} to {destination} cheap flight tips reddit",
                f"airline strikes affecting {origin} {destination} {departure_date[:7]}",
            ],
        }

    cheapest_gf = gf_flights[0]["price"] if gf_flights else None
    cheapest_kiwi = kiwi_fares[0]["price"] if kiwi_fares else None

    if cheapest_gf is not None and cheapest_kiwi is not None:
        cheapest = min(cheapest_gf, cheapest_kiwi)
    else:
        cheapest = cheapest_gf or cheapest_kiwi or 0

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "passengers": adults,
        "results_count": len(gf_flights),
        "flights": gf_flights,
        "kiwi_live_fares": kiwi_fares,
        # cheapest_price is ALWAYS per-person regardless of adults count.
        # Use cheapest_price_total for the full group cost.
        "cheapest_price": cheapest,
        "cheapest_price_total": round(cheapest * adults, 2),
        "price_is_per_person": True,
        "currency": currency.upper(),
        "data_confidence": "scraped_live",
        "price_signal": (gf or {}).get("price_signal", "typical"),
        "data_source": "google_flights + kiwi.com",
        "suggest_web_search": [
            f"{origin} to {destination} mistake fares {departure_date[:7]}",
            f"{origin} to {destination} cheap flight tips reddit",
            f"airline strikes affecting {origin} {destination} {departure_date[:7]}",
        ],
    }
