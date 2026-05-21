"""Flight search via fast_flights (Google Flights scraper).

Primary: fast_flights — real Google Flights data, no auth.
Fallback: Kiwi Tequila — when fast_flights HTML changes or rate-limits.

Note: fast_flights scrapes Google Flights. Stability depends on Google's HTML
remaining stable. If queries start failing, the Kiwi fallback kicks in.
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
    for f in raw_flights:
        if nonstop_only and getattr(f, "stops", 0) != 0:
            continue
        price_raw = str(getattr(f, "price", "") or "")
        amount, native_curr = _parse_price(price_raw)
        if amount == 0:
            continue
        parsed.append({
            "airline": getattr(f, "name", ""),
            "departure": getattr(f, "departure", ""),
            "arrival": getattr(f, "arrival", ""),
            "arrival_time_offset": getattr(f, "arrival_time_ahead", ""),
            "duration": getattr(f, "duration", ""),
            "stops": getattr(f, "stops", 0),
            "delay": getattr(f, "delay", None),
            "is_best": bool(getattr(f, "is_best", False)),
            "price_raw": price_raw,
            "price_native": amount,
            "native_currency": native_curr,
        })

    # Convert prices to requested currency (batch — one rate lookup per source currency)
    target = currency.upper()
    rates: dict = {}
    for f in parsed:
        nc = f["native_currency"]
        if nc != target and nc not in rates:
            conv = await convert_currency(1.0, nc, target)
            if not conv.get("error"):
                rates[nc] = conv["exchange_rate"]
            else:
                rates[nc] = None

    for f in parsed:
        nc = f["native_currency"]
        if nc == target:
            f["price"] = f["price_native"]
        elif rates.get(nc):
            f["price"] = round(f["price_native"] * rates[nc], 2)
        else:
            f["price"] = f["price_native"]  # Keep native if conversion failed
        f["currency"] = target

    parsed.sort(key=lambda x: x["price"])
    return {
        "flights": parsed[:max_results],
        "source": "google_flights (via fast_flights)",
        "price_signal": getattr(result, "current_price", "typical"),
    }


async def _search_kiwi(
    origin: str, destination: str, departure_date: str, return_date: str | None,
    adults: int, currency: str, max_results: int, nonstop_only: bool,
) -> dict | None:
    from ..utils.config import KIWI_API_KEY
    from ..utils.http import get_client

    if not KIWI_API_KEY:
        return None

    client = await get_client()
    dep_kiwi = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    params: dict = {
        "fly_from": origin.upper(),
        "fly_to": destination.upper(),
        "date_from": dep_kiwi,
        "date_to": dep_kiwi,
        "adults": adults,
        "curr": currency.upper(),
        "limit": max_results,
    }
    if return_date:
        ret_kiwi = datetime.strptime(return_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        params["return_from"] = ret_kiwi
        params["return_to"] = ret_kiwi
    if nonstop_only:
        params["max_stopovers"] = 0

    try:
        resp = await client.get(
            "https://api.tequila.kiwi.com/v2/search",
            params=params,
            headers={"apikey": KIWI_API_KEY},
            timeout=20.0,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()

        flights = []
        for offer in data.get("data", [])[:max_results]:
            segments = []
            for route in offer.get("route", []):
                segments.append({
                    "airline": route.get("airline", ""),
                    "flight_number": f"{route.get('airline', '')}{route.get('flight_no', '')}",
                    "departure_airport": route.get("flyFrom", ""),
                    "departure_time": route.get("local_departure", ""),
                    "arrival_airport": route.get("flyTo", ""),
                    "arrival_time": route.get("local_arrival", ""),
                })
            flights.append({
                "price": float(offer.get("price", 0)),
                "currency": currency.upper(),
                "duration_minutes": offer.get("duration", {}).get("total", 0) // 60,
                "stops": max(len(segments) - 1, 0),
                "segments": segments,
                "booking_url": offer.get("deep_link", ""),
            })
        flights.sort(key=lambda x: x["price"])
        return {"flights": flights, "source": "kiwi_tequila"}
    except Exception:
        return None


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
    """Search flights via Google Flights (fast_flights) with Kiwi Tequila fallback.

    Args:
        origin: IATA airport code (e.g., "JFK")
        destination: IATA airport code (e.g., "CDG")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD for round trip
        adults: Passengers
        max_results: Max results
        currency: Target currency (prices converted)
        nonstop_only: Skip flights with stops
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    # Try Google Flights first
    gf = await _search_fast_flights(
        origin, destination, departure_date, return_date,
        adults, max_results, currency, nonstop_only,
    )
    if gf and gf["flights"]:
        cheapest = gf["flights"][0]["price"]
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": adults,
            "results_count": len(gf["flights"]),
            "flights": gf["flights"],
            "cheapest_price": cheapest,
            "currency": currency.upper(),
            "price_signal": gf.get("price_signal", "typical"),
            "data_source": gf["source"],
            "suggest_web_search": [
                f"{origin} to {destination} mistake fares {departure_date[:7]}",
                f"{origin} to {destination} cheap flight tips reddit",
                f"airline strikes affecting {origin} {destination} {departure_date[:7]}",
            ],
        }

    # Fallback to Kiwi
    kw = await _search_kiwi(
        origin, destination, departure_date, return_date,
        adults, currency, max_results, nonstop_only,
    )
    if kw and kw["flights"]:
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": adults,
            "results_count": len(kw["flights"]),
            "flights": kw["flights"],
            "cheapest_price": kw["flights"][0]["price"],
            "currency": currency.upper(),
            "data_source": "kiwi_tequila (fallback)",
            "note": "Google Flights scraper unavailable. Used Kiwi.",
        }

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "results_count": 0,
        "flights": [],
        "error": "Both Google Flights scraper and Kiwi fallback unavailable. Set KIWI_API_KEY in .env for fallback.",
    }
