"""Flight search with fallback chain: Travelpayouts -> Kiwi Tequila -> mock."""

from __future__ import annotations

from datetime import datetime


async def _search_travelpayouts(
    origin: str, destination: str, departure_date: str,
    return_date: str | None, currency: str,
) -> dict | None:
    from ..utils.config import TRAVELPAYOUTS_TOKEN, TRAVELPAYOUTS_MARKER
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return None

    client = await get_client()
    params: dict = {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "depart_date": departure_date,
        "currency": currency.lower(),
        "token": TRAVELPAYOUTS_TOKEN,
    }
    if return_date:
        params["return_date"] = return_date
    if TRAVELPAYOUTS_MARKER:
        params["marker"] = TRAVELPAYOUTS_MARKER

    try:
        resp = await client.get("https://api.travelpayouts.com/v1/prices/cheap", params=params)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("success"):
            return None

        flights = []
        for dest_code, offers in (data.get("data") or {}).items():
            for trip_id, offer in offers.items():
                flights.append({
                    "price": float(offer.get("price", 0)),
                    "currency": currency.upper(),
                    "airline": offer.get("airline", ""),
                    "flight_number": f"{offer.get('airline', '')}{offer.get('flight_number', '')}",
                    "departure_at": offer.get("departure_at", ""),
                    "return_at": offer.get("return_at", ""),
                    "expires_at": offer.get("expires_at", ""),
                    "origin": origin.upper(),
                    "destination": dest_code,
                    "booking_url": f"https://www.aviasales.com/search/{origin.upper()}{datetime.strptime(departure_date, '%Y-%m-%d').strftime('%d%m')}{dest_code}{('1' if not return_date else datetime.strptime(return_date, '%Y-%m-%d').strftime('%d%m'))}",
                    "source": "travelpayouts",
                })
        flights.sort(key=lambda x: x["price"])
        return {"flights": flights, "source": "travelpayouts"}
    except Exception:
        return None


async def _search_kiwi(
    origin: str, destination: str, departure_date: str,
    return_date: str | None, adults: int, currency: str, max_results: int,
    nonstop_only: bool,
) -> dict | None:
    from ..utils.config import KIWI_API_KEY
    from ..utils.http import get_client

    if not KIWI_API_KEY:
        return None

    client = await get_client()
    # Kiwi uses DD/MM/YYYY format
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
                "source": "kiwi",
            })

        flights.sort(key=lambda x: x["price"])
        return {"flights": flights, "source": "kiwi"}
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
    """Search flights with Travelpayouts (primary) -> Kiwi (fallback) chain.

    Args:
        origin: IATA airport code (e.g., "JFK")
        destination: IATA airport code (e.g., "CDG")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD for round trip (omit for one-way)
        adults: 1-9
        max_results: results to return
        currency: USD, EUR, etc.
        nonstop_only: nonstop flights only
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    # Try Travelpayouts first
    tp = await _search_travelpayouts(origin, destination, departure_date, return_date, currency)
    if tp and tp["flights"]:
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": adults,
            "results_count": len(tp["flights"][:max_results]),
            "flights": tp["flights"][:max_results],
            "cheapest_price": tp["flights"][0]["price"],
            "currency": currency.upper(),
            "data_source": "travelpayouts",
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
            "data_source": "kiwi_tequila",
        }

    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "results_count": 0,
        "flights": [],
        "error": "No flight data sources available. Configure TRAVELPAYOUTS_TOKEN or KIWI_API_KEY in .env",
    }
