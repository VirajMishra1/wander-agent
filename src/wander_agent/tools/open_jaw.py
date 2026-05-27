"""Open-jaw flight optimizer.

Fly INTO city A, travel overland, fly OUT from city B.
No OTA combines flights + ground transport for open-jaw optimization.
Composes existing search_flights + search_ground_transport tools.

Example: JFK → Rome, train Rome → Paris, Paris → JFK.
You see two cities on one trip. Never fly the same route twice.
Usually cheaper than two separate round-trips.
"""

from __future__ import annotations

import asyncio

# IATA → (city name, country, lat, lon)
_AIRPORT_INFO: dict[str, tuple[str, str, float, float]] = {
    "JFK": ("New York", "US", 40.64, -73.78),
    "EWR": ("New York", "US", 40.69, -74.17),
    "LGA": ("New York", "US", 40.78, -73.87),
    "LAX": ("Los Angeles", "US", 33.94, -118.41),
    "SFO": ("San Francisco", "US", 37.62, -122.38),
    "ORD": ("Chicago", "US", 41.98, -87.90),
    "MIA": ("Miami", "US", 25.80, -80.29),
    "BOS": ("Boston", "US", 42.37, -71.01),
    "ATL": ("Atlanta", "US", 33.64, -84.43),
    "DFW": ("Dallas", "US", 32.90, -97.04),
    "LHR": ("London", "GB", 51.48, -0.45),
    "LGW": ("London", "GB", 51.15, -0.18),
    "CDG": ("Paris", "FR", 49.01, 2.55),
    "ORY": ("Paris", "FR", 48.72, 2.38),
    "FRA": ("Frankfurt", "DE", 50.04, 8.56),
    "MUC": ("Munich", "DE", 48.35, 11.79),
    "BER": ("Berlin", "DE", 52.37, 13.52),
    "AMS": ("Amsterdam", "NL", 52.31, 4.76),
    "MAD": ("Madrid", "ES", 40.47, -3.57),
    "BCN": ("Barcelona", "ES", 41.30, 2.08),
    "FCO": ("Rome", "IT", 41.80, 12.25),
    "MXP": ("Milan", "IT", 45.63, 8.73),
    "VCE": ("Venice", "IT", 45.51, 12.35),
    "ATH": ("Athens", "GR", 37.94, 23.95),
    "LIS": ("Lisbon", "PT", 38.77, -9.13),
    "OPO": ("Porto", "PT", 41.24, -8.68),
    "ZRH": ("Zurich", "CH", 47.46, 8.55),
    "VIE": ("Vienna", "AT", 48.12, 16.57),
    "PRG": ("Prague", "CZ", 50.10, 14.26),
    "BUD": ("Budapest", "HU", 47.44, 19.26),
    "WAW": ("Warsaw", "PL", 52.17, 20.97),
    "IST": ("Istanbul", "TR", 41.28, 28.75),
    "DXB": ("Dubai", "AE", 25.25, 55.36),
    "AUH": ("Abu Dhabi", "AE", 24.44, 54.65),
    "DOH": ("Doha", "QA", 25.27, 51.61),
    "SIN": ("Singapore", "SG", 1.36, 103.99),
    "HKG": ("Hong Kong", "HK", 22.31, 113.92),
    "NRT": ("Tokyo", "JP", 35.77, 140.39),
    "HND": ("Tokyo", "JP", 35.55, 139.78),
    "KIX": ("Osaka", "JP", 34.43, 135.24),
    "ICN": ("Seoul", "KR", 37.46, 126.44),
    "TPE": ("Taipei", "TW", 25.08, 121.23),
    "BKK": ("Bangkok", "TH", 13.68, 100.75),
    "HKT": ("Phuket", "TH", 8.11, 98.32),
    "CNX": ("Chiang Mai", "TH", 18.77, 98.96),
    "KUL": ("Kuala Lumpur", "MY", 2.75, 101.71),
    "DPS": ("Bali", "ID", -8.75, 115.17),
    "CGK": ("Jakarta", "ID", -6.13, 106.65),
    "SGN": ("Ho Chi Minh City", "VN", 10.82, 106.65),
    "HAN": ("Hanoi", "VN", 21.22, 105.80),
    "DEL": ("Delhi", "IN", 28.56, 77.10),
    "BOM": ("Mumbai", "IN", 19.09, 72.87),
    "BLR": ("Bangalore", "IN", 13.20, 77.71),
    "PEK": ("Beijing", "CN", 40.08, 116.58),
    "PVG": ("Shanghai", "CN", 31.14, 121.81),
    "SYD": ("Sydney", "AU", -33.95, 151.18),
    "MEL": ("Melbourne", "AU", -37.67, 144.84),
    "YYZ": ("Toronto", "CA", 43.68, -79.63),
    "YVR": ("Vancouver", "CA", 49.19, -123.18),
    "GRU": ("São Paulo", "BR", -23.43, -46.47),
    "MEX": ("Mexico City", "MX", 19.44, -99.07),
    "BOG": ("Bogotá", "CO", 4.70, -74.15),
    "LIM": ("Lima", "PE", -12.02, -77.11),
    "EZE": ("Buenos Aires", "AR", -34.82, -58.54),
    "JNB": ("Johannesburg", "ZA", -26.13, 28.24),
    "CPT": ("Cape Town", "ZA", -33.96, 18.60),
    "NBO": ("Nairobi", "KE", -1.32, 36.93),
    "CMN": ("Casablanca", "MA", 33.36, -7.59),
    "CAI": ("Cairo", "EG", 30.12, 31.41),
    "TLV": ("Tel Aviv", "IL", 32.01, 34.89),
    "ADD": ("Addis Ababa", "ET", 8.98, 38.80),
}

_CITY_TO_IATA: dict[str, str] = {
    "new york": "JFK", "london": "LHR", "paris": "CDG", "frankfurt": "FRA",
    "rome": "FCO", "milan": "MXP", "venice": "VCE", "athens": "ATH",
    "tokyo": "NRT", "osaka": "KIX", "seoul": "ICN", "taipei": "TPE",
    "bangkok": "BKK", "phuket": "HKT", "chiang mai": "CNX",
    "kuala lumpur": "KUL", "bali": "DPS", "jakarta": "CGK",
    "ho chi minh city": "SGN", "ho chi minh": "SGN", "saigon": "SGN",
    "hanoi": "HAN", "delhi": "DEL", "mumbai": "BOM", "bangalore": "BLR",
    "beijing": "PEK", "shanghai": "PVG", "hong kong": "HKG",
    "singapore": "SIN", "dubai": "DXB", "abu dhabi": "AUH", "doha": "DOH",
    "istanbul": "IST", "amsterdam": "AMS", "lisbon": "LIS", "porto": "OPO",
    "madrid": "MAD", "barcelona": "BCN", "berlin": "BER", "munich": "MUC",
    "vienna": "VIE", "prague": "PRG", "budapest": "BUD", "warsaw": "WAW",
    "zurich": "ZRH", "toronto": "YYZ", "vancouver": "YVR",
    "sydney": "SYD", "melbourne": "MEL", "johannesburg": "JNB",
    "cape town": "CPT", "nairobi": "NBO", "cairo": "CAI", "tel aviv": "TLV",
    "san francisco": "SFO", "los angeles": "LAX", "chicago": "ORD",
    "miami": "MIA", "boston": "BOS", "atlanta": "ATL", "dallas": "DFW",
    "mexico city": "MEX", "sao paulo": "GRU", "buenos aires": "EZE",
    "lima": "LIM", "bogota": "BOG", "casablanca": "CMN",
    "addis ababa": "ADD",
}


def _resolve(city_or_iata: str) -> tuple[str, str]:
    """Return (iata, city_name). Accepts IATA codes or city names."""
    s = city_or_iata.strip()
    if len(s) == 3 and s.upper() in _AIRPORT_INFO:
        iata = s.upper()
        return iata, _AIRPORT_INFO[iata][0]
    iata = _CITY_TO_IATA.get(s.lower())
    if iata:
        return iata, _AIRPORT_INFO[iata][0]
    return s.upper(), s.title()


async def find_open_jaw(
    origin: str,
    fly_into: str,
    fly_out_from: str,
    outbound_date: str,
    return_date: str,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
) -> dict:
    """Plan an open-jaw trip: fly into one city, travel overland, fly out from another.

    No OTA combines flight search + ground transport for open-jaw routing.
    This composes both tools: prices inbound flight, outbound flight, and the
    overland segment between the two cities.

    Example: origin=JFK, fly_into=Rome, fly_out_from=Paris, outbound=Sep 1,
    return=Sep 15. Returns JFK→Rome flight + Rome→Paris train + Paris→JFK
    flight, with total cost and comparison vs a round-trip to Rome only.

    Accepts both IATA codes (FCO, CDG) and city names (Rome, Paris).

    Args:
        origin: Home airport IATA or city (e.g., "JFK" or "New York")
        fly_into: First destination IATA or city (e.g., "FCO" or "Rome")
        fly_out_from: Final departure IATA or city (e.g., "CDG" or "Paris")
        outbound_date: YYYY-MM-DD — fly origin → fly_into
        return_date: YYYY-MM-DD — fly fly_out_from → origin
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code
    """
    from .flights import search_flights
    from .ground_transport import search_ground_transport

    origin_iata, origin_city = _resolve(origin)
    in_iata, in_city = _resolve(fly_into)
    out_iata, out_city = _resolve(fly_out_from)

    if in_iata == out_iata:
        return {"error": "fly_into and fly_out_from are the same city. Use search_flights for a round-trip."}

    f_in_t = asyncio.create_task(search_flights(
        origin=origin_iata, destination=in_iata,
        departure_date=outbound_date, adults=adults,
        max_results=3, currency=currency, cabin_class=cabin_class,
    ))
    f_out_t = asyncio.create_task(search_flights(
        origin=out_iata, destination=origin_iata,
        departure_date=return_date, adults=adults,
        max_results=3, currency=currency, cabin_class=cabin_class,
    ))
    ground_t = asyncio.create_task(search_ground_transport(
        origin_city=in_city, destination_city=out_city,
        departure_date=outbound_date, passengers=adults, currency=currency,
    ))
    baseline_t = asyncio.create_task(search_flights(
        origin=origin_iata, destination=in_iata,
        departure_date=outbound_date, return_date=return_date,
        adults=adults, max_results=1, currency=currency, cabin_class=cabin_class,
    ))

    f_in, f_out, ground, baseline = await asyncio.gather(
        f_in_t, f_out_t, ground_t, baseline_t, return_exceptions=True,
    )

    p_in = f_in.get("cheapest_price") if isinstance(f_in, dict) else None
    p_out = f_out.get("cheapest_price") if isinstance(f_out, dict) else None
    p_baseline = baseline.get("cheapest_price") if isinstance(baseline, dict) else None
    total_flights = round(p_in + p_out, 2) if (p_in and p_out) else None

    ground_summary = None
    if isinstance(ground, dict) and ground.get("options"):
        opts = ground["options"]
        if opts:
            best_g = min(opts, key=lambda x: x.get("price_usd") or 9999)
            ground_summary = {
                "type": best_g.get("type"),
                "operator": best_g.get("operator"),
                "duration": best_g.get("duration"),
                "price_usd": best_g.get("price_usd"),
                "booking_link": best_g.get("booking_link"),
            }

    comparison: dict = {}
    if total_flights and p_baseline:
        premium = round(total_flights - p_baseline, 2)
        comparison = {
            "round_trip_to_first_city_only": p_baseline,
            "open_jaw_flights_total": total_flights,
            "open_jaw_premium_usd": premium,
            "cities_gained": 1,
            "verdict": (
                f"Pay ${premium:.0f} more to also visit {out_city} (vs round-trip to {in_city} only)"
                if premium > 0 else
                f"Open-jaw is ${abs(premium):.0f} CHEAPER than a round-trip — and you see {out_city} too!"
            ),
        }

    checklist = [
        f"1. Book {origin_iata} → {in_iata} one-way for {outbound_date}",
        f"2. Book {out_iata} → {origin_iata} one-way for {return_date}",
        (
            f"3. Book {in_city} → {out_city} {ground_summary['type']} "
            f"(~{ground_summary['duration']}, ~${ground_summary['price_usd']})"
            if ground_summary else
            f"3. Book {in_city} → {out_city} overland — try Omio, Trainline, FlixBus, or BlaBlaCar"
        ),
    ]

    return {
        "trip": f"{origin_iata} → {in_iata} · {in_city}→{out_city} · {out_iata} → {origin_iata}",
        "outbound_date": outbound_date,
        "return_date": return_date,
        "adults": adults,
        "cabin_class": cabin_class,
        "currency": currency.upper(),
        "legs": {
            "inbound_flight": {
                "route": f"{origin_iata} → {in_iata} ({in_city})",
                "date": outbound_date,
                "price": p_in,
                "currency": currency.upper(),
                "flights": f_in.get("flights", [])[:3] if isinstance(f_in, dict) else [],
                "booking_links": f_in.get("booking_links", {}) if isinstance(f_in, dict) else {},
            },
            "ground_segment": {
                "route": f"{in_city} → {out_city}",
                "cheapest_option": ground_summary,
                "all_options": ground.get("options", []) if isinstance(ground, dict) else [],
                "booking_links": ground.get("booking_links", {}) if isinstance(ground, dict) else {},
            },
            "outbound_flight": {
                "route": f"{out_iata} ({out_city}) → {origin_iata}",
                "date": return_date,
                "price": p_out,
                "currency": currency.upper(),
                "flights": f_out.get("flights", [])[:3] if isinstance(f_out, dict) else [],
                "booking_links": f_out.get("booking_links", {}) if isinstance(f_out, dict) else {},
            },
        },
        "total_flight_cost": total_flights,
        "cities_visited": [in_city, out_city],
        "comparison_vs_round_trip": comparison,
        "booking_checklist": checklist,
        "pro_tips": [
            "Book one-way tickets separately — more flexibility if plans change.",
            "Use Omio.com or Trainline.com to compare train vs bus for overland segment.",
            "Open-jaw avoids backtracking — every mile takes you somewhere new.",
            "Consider an extra night mid-trip before the ground segment.",
        ],
        "data_confidence": "scraped_live (flights) + live (ground transport)",
    }
