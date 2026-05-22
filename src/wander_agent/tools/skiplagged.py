"""Skiplagged hidden-city ticketing - the killer travel-hacker feature.

Hidden-city tickets exploit the fact that connecting flights are often
cheaper than the connection leg itself. Buy NYC->Mexico via Houston,
deplane in Houston, skip the last leg. Airlines hate this. Skyscanner
and Kayak can't legally surface these. Skiplagged is the only OTA that
does, and they have no public API or AI integration. We do.

Uses Skiplagged's undocumented JSON endpoint. No auth.
Direct competitor to Kayak/Skyscanner/Expedia for budget travelers.
"""

from __future__ import annotations

from datetime import datetime


async def find_skiplagged_fares(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    max_results: int = 10,
) -> dict:
    """Find hidden-city fares between airports.

    These are flights cheaper than direct because you exit at the layover
    instead of the ticketed destination. Carry-on only (no checked bags
    that go to final destination). No frequent flyer credit if AA. Don't
    book round-trips this way (return will be canceled).

    Args:
        origin: IATA airport code (e.g., "JFK")
        destination: IATA airport code (e.g., "LAX")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD for round-trip comparison (book separately)
        max_results: Max fares to return
    """
    from ..utils.http import get_client

    client = await get_client()
    params: dict = {
        "from": origin.upper(),
        "to": destination.upper(),
        "depart": departure_date,
        "format": "v3",
        "counts[adults]": 1,
    }
    if return_date:
        params["return"] = return_date

    try:
        resp = await client.get(
            "https://skiplagged.com/api/search.php",
            params=params,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "application/json,*/*",
                "Referer": "https://skiplagged.com/",
            },
            timeout=20.0,
        )
        if resp.status_code != 200:
            return {
                "error": f"Skiplagged returned {resp.status_code}",
                "note": "Skiplagged may be temporarily blocking or down.",
            }

        data = resp.json()
        itineraries = data.get("itineraries", {})
        if not itineraries:
            return {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date,
                "results_count": 0,
                "hidden_city_fares": [],
                "direct_fares": [],
                "note": "No fares found. Try different dates or airports.",
            }

        outbound = itineraries.get("outbound", [])
        flights_data = data.get("flights", {})
        airlines_data = data.get("airlines", {})

        def _format_itin(itin: dict) -> dict | None:
            flight_id = itin.get("flight", "")
            price_cents = itin.get("one_way_price", 0)
            if not flight_id or not price_cents:
                return None
            flight = flights_data.get(flight_id, {})
            segs_raw = flight.get("segments", [])
            if not segs_raw:
                return None

            segments = []
            for s in segs_raw:
                airline_code = s.get("airline", "")
                airline_info = airlines_data.get(airline_code, {})
                airline_name = airline_info.get("name", airline_code) if isinstance(airline_info, dict) else airline_code
                segments.append({
                    "from": s.get("departure", {}).get("airport", ""),
                    "to": s.get("arrival", {}).get("airport", ""),
                    "airline": airline_name,
                    "airline_code": airline_code,
                    "flight_number": f"{airline_code}{s.get('flight_number', '')}",
                    "departure_time": s.get("departure", {}).get("time", ""),
                    "arrival_time": s.get("arrival", {}).get("time", ""),
                    "duration_minutes": (s.get("duration", 0) or 0) // 60,
                })

            ticketed_dest = segments[-1]["to"] if segments else destination.upper()
            is_hidden = ticketed_dest != destination.upper()

            return {
                "price": price_cents / 100,
                "currency": "USD",
                "is_hidden_city": is_hidden,
                "ticketed_destination": ticketed_dest,
                "actual_destination": destination.upper(),
                "exit_at": destination.upper() if is_hidden else None,
                "stops": max(len(segments) - 1, 0),
                "segments": segments,
                "duration_minutes": (flight.get("duration", 0) or 0) // 60,
                "booking_url": (
                    f"https://skiplagged.com/flights/{origin.upper()}/{destination.upper()}"
                    f"/{departure_date}/?adults=1"
                ),
            }

        formatted = []
        for i in outbound:
            f = _format_itin(i)
            if f and f["price"] > 0:
                formatted.append(f)
        formatted.sort(key=lambda x: x["price"])

        hidden_fares = [f for f in formatted if f["is_hidden_city"]][:max_results]
        direct_fares = [f for f in formatted if not f["is_hidden_city"]][:max_results]

        cheapest_direct = direct_fares[0]["price"] if direct_fares else None
        cheapest_hidden = hidden_fares[0]["price"] if hidden_fares else None
        savings = 0.0
        if cheapest_direct and cheapest_hidden and cheapest_hidden < cheapest_direct:
            savings = cheapest_direct - cheapest_hidden

        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "results_count": len(formatted),
            "hidden_city_fares": hidden_fares,
            "direct_fares": direct_fares,
            "cheapest_direct": cheapest_direct,
            "cheapest_hidden_city": cheapest_hidden,
            "potential_savings_usd": round(savings, 2),
            "data_source": "skiplagged",
            "important_warnings": [
                "CARRY-ON ONLY. Checked bags go to ticketed destination.",
                "Do NOT book round-trips this way - airline will cancel return leg if you skip outbound.",
                "Do NOT add frequent flyer number (some airlines penalize).",
                "Do NOT do this on the same airline more than occasionally.",
                "Airlines (United, AA) have sued Skiplagged before. Use at own risk.",
            ],
            "suggest_web_search": [
                f"hidden city ticketing {origin.upper()} {destination.upper()} risks",
                f"airline crackdown skiplagged 2026",
            ],
        }
    except Exception as e:
        return {"error": str(e)}
