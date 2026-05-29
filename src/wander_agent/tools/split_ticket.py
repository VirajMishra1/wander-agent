"""Split-ticket flight search.

Book two separate tickets through a hub instead of one through-ticket.
Saves 20-60% on many routes. OTAs are contractually forbidden from
recommending this — same philosophy as Skiplagged/hidden-city fares.

CRITICAL: Different from hidden-city. You actually fly all segments.
The saving comes from airlines pricing hub routes independently, so
origin→hub + hub→destination < origin→destination through-ticket.
"""

from __future__ import annotations

import asyncio
import math

# Major connecting hubs with coordinates
HUBS: dict[str, tuple[str, str, float, float]] = {
    # IATA: (city, country, lat, lon)
    "ATL": ("Atlanta", "US", 33.64, -84.43),
    "ORD": ("Chicago", "US", 41.98, -87.90),
    "DFW": ("Dallas", "US", 32.90, -97.04),
    "LAX": ("Los Angeles", "US", 33.94, -118.41),
    "JFK": ("New York", "US", 40.64, -73.78),
    "MIA": ("Miami", "US", 25.80, -80.29),
    "DEN": ("Denver", "US", 39.86, -104.67),
    "SEA": ("Seattle", "US", 47.45, -122.31),
    "LHR": ("London", "GB", 51.48, -0.45),
    "FRA": ("Frankfurt", "DE", 50.04, 8.56),
    "AMS": ("Amsterdam", "NL", 52.31, 4.76),
    "CDG": ("Paris", "FR", 49.01, 2.55),
    "MAD": ("Madrid", "ES", 40.47, -3.57),
    "FCO": ("Rome", "IT", 41.80, 12.25),
    "IST": ("Istanbul", "TR", 41.28, 28.75),
    "DXB": ("Dubai", "AE", 25.25, 55.36),
    "DOH": ("Doha", "QA", 25.27, 51.61),
    "AUH": ("Abu Dhabi", "AE", 24.44, 54.65),
    "SIN": ("Singapore", "SG", 1.36, 103.99),
    "HKG": ("Hong Kong", "HK", 22.31, 113.92),
    "NRT": ("Tokyo", "JP", 35.77, 140.39),
    "ICN": ("Seoul", "KR", 37.46, 126.44),
    "BKK": ("Bangkok", "TH", 13.68, 100.75),
    "KUL": ("Kuala Lumpur", "MY", 2.75, 101.71),
    "GRU": ("São Paulo", "BR", -23.43, -46.47),
    "JNB": ("Johannesburg", "ZA", -26.13, 28.24),
    "SYD": ("Sydney", "AU", -33.95, 151.18),
    "YYZ": ("Toronto", "CA", 43.68, -79.63),
    "EWR": ("Newark", "US", 40.69, -74.17),
    "ADD": ("Addis Ababa", "ET", 8.98, 38.80),
    "NBO": ("Nairobi", "KE", -1.32, 36.93),
}

_AIRPORT_COORDS: dict[str, tuple[float, float]] = {
    iata: (lat, lon) for iata, (_, _, lat, lon) in HUBS.items()
} | {
    "LGW": (51.15, -0.18), "STN": (51.88, 0.24), "MAN": (53.35, -2.27),
    "ZRH": (47.46, 8.55), "GVA": (46.24, 6.11), "BCN": (41.30, 2.08),
    "MUC": (48.35, 11.79), "BER": (52.37, 13.52),
    "SAW": (40.90, 29.31), "SHJ": (25.33, 55.52),
    "HND": (35.55, 139.78), "KIX": (34.43, 135.24), "GMP": (37.56, 126.79),
    "DMK": (13.91, 100.61),
    "DEL": (28.56, 77.10), "BOM": (19.09, 72.87), "BLR": (13.20, 77.71),
    "MAA": (12.99, 80.17),
    "PEK": (40.08, 116.58), "PVG": (31.14, 121.81),
    "SFO": (37.62, -122.38), "BOS": (42.37, -71.01), "IAD": (38.94, -77.45),
    "IAH": (29.99, -95.34), "PHX": (33.44, -112.01),
    "YVR": (49.19, -123.18), "YUL": (45.47, -73.74),
    "MEL": (-37.67, 144.84), "BNE": (-27.38, 153.12), "CPT": (-33.96, 18.60),
    "CMN": (33.36, -7.59),
    "DPS": (-8.75, 115.17), "CGK": (-6.13, 106.65),
    "SGN": (10.82, 106.65), "HAN": (21.22, 105.80),
    "MEX": (19.44, -99.07), "GIG": (-22.81, -43.25),
}

RISKS = [
    "🚨 MISSED CONNECTION: If your first flight is delayed, the second airline WON'T wait. "
    "You'll need to buy a replacement ticket at full walk-up price.",
    "🧳 LUGGAGE: You MUST collect and re-check bags at the hub — budget 60-90 min minimum.",
    "📋 NO LEGAL PROTECTION: Unlike a through-ticket, airlines have zero obligation to "
    "rebook you on missed connections between separate tickets.",
    "🛡️ BUY TRAVEL INSURANCE that explicitly covers missed connections on separate tickets "
    "(World Nomads, Allianz, or credit card travel protection).",
    "⏰ BUFFER TIME: Allow ≥3h between tickets at major hubs, ≥4h at smaller airports.",
    "💳 CREDIT CARD BOOKING: Pay on a card with travel protection — some cover missed "
    "connections up to $500.",
]

RULES = [
    "Book each ticket separately — don't reference the connection when booking.",
    "Carry-on only eliminates the luggage re-check problem entirely.",
    "Best hub choices: DXB, IST, LHR, FRA, SIN, AMS — frequent onward flights if rebook needed.",
    "Confirm both legs depart from the same terminal, or add terminal-transfer time.",
    "This strategy works best when hub→destination has LCC competition driving prices down.",
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _candidate_hubs(
    origin: str, destination: str, max_hubs: int = 10, max_detour: float = 1.6
) -> list[tuple[str, float]]:
    o = _AIRPORT_COORDS.get(origin)
    d = _AIRPORT_COORDS.get(destination)
    if not o or not d:
        return [(iata, 1.0) for iata in list(HUBS)[:max_hubs]]
    direct_km = _haversine_km(*o, *d)
    candidates = []
    for iata, (_, _, hlat, hlon) in HUBS.items():
        if iata in (origin, destination):
            continue
        leg1 = _haversine_km(*o, hlat, hlon)
        leg2 = _haversine_km(hlat, hlon, *d)
        detour = (leg1 + leg2) / max(direct_km, 1)
        if detour > max_detour:
            continue
        # Exclude hubs trivially close to one endpoint — those produce one micro-leg
        # and one near-full-price leg, leaving no room for split-ticket savings.
        # 12% floor: both legs must be at least 12% of the total split distance.
        total_split = leg1 + leg2
        if leg1 / total_split < 0.12 or leg2 / total_split < 0.12:
            continue
        candidates.append((round(detour, 2), iata))
    candidates.sort()
    return [(iata, detour) for detour, iata in candidates[:max_hubs]]


async def find_split_ticket(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    min_connection_hours: float = 3.0,
) -> dict:
    """Find savings by booking two separate tickets through a hub airport.

    OTAs are contractually forbidden from recommending this. Savings of
    20-60% are common on long-haul routes with strong hub competition.

    Works by pricing origin→hub and hub→destination independently —
    often far cheaper than the bundled through-ticket price.

    ⚠️ Read ALL risks before booking. Not recommended for inexperienced travelers
    or anyone who can't absorb the cost of a missed connection.

    Args:
        origin: Origin airport IATA code (e.g., "SFO")
        destination: Destination airport IATA code (e.g., "DEL")
        departure_date: YYYY-MM-DD departure date
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code (e.g., "USD", "EUR")
        min_connection_hours: Minimum buffer hours between tickets at hub
    """
    from .flights import search_flights

    origin = origin.upper().strip()
    destination = destination.upper().strip()

    direct_task = asyncio.create_task(
        search_flights(
            origin=origin, destination=destination,
            departure_date=departure_date,
            adults=adults, max_results=1,
            currency=currency,
        )
    )

    candidate_hubs = _candidate_hubs(origin, destination)
    sem = asyncio.Semaphore(3)

    async def _price_via(hub_iata: str, detour: float) -> dict | None:
        async with sem:
            try:
                r1, r2 = await asyncio.gather(
                    search_flights(
                        origin=origin, destination=hub_iata,
                        departure_date=departure_date,
                        adults=adults, max_results=1,
                        currency=currency,
                    ),
                    search_flights(
                        origin=hub_iata, destination=destination,
                        departure_date=departure_date,
                        adults=adults, max_results=1,
                        currency=currency,
                    ),
                )
                p1, p2 = r1.get("cheapest_price"), r2.get("cheapest_price")
                if not p1 or not p2:
                    return None
                city, country, _, _ = HUBS[hub_iata]
                return {
                    "hub": hub_iata,
                    "hub_city": city,
                    "hub_country": country,
                    "detour_factor": detour,
                    "leg1": {
                        "route": f"{origin} → {hub_iata}",
                        "price": p1,
                        "currency": currency.upper(),
                        "booking_links": r1.get("booking_links", {}),
                    },
                    "leg2": {
                        "route": f"{hub_iata} → {destination}",
                        "price": p2,
                        "currency": currency.upper(),
                        "booking_links": r2.get("booking_links", {}),
                    },
                    "split_total": round(p1 + p2, 2),
                    "min_connection_hours_recommended": min_connection_hours,
                }
            except Exception:
                return None

    splits_raw, direct_result = await asyncio.gather(
        asyncio.gather(*[_price_via(h, df) for h, df in candidate_hubs]),
        direct_task,
    )

    direct_price = direct_result.get("cheapest_price")
    options = [r for r in splits_raw if r is not None]

    for opt in options:
        if direct_price:
            saving = round(direct_price - opt["split_total"], 2)
            opt["saving_vs_direct"] = saving
            opt["saving_pct"] = round((saving / direct_price) * 100, 1)
        else:
            opt["saving_vs_direct"] = None
            opt["saving_pct"] = None

    if direct_price:
        options.sort(key=lambda x: x.get("saving_vs_direct") or -9999, reverse=True)
    else:
        options.sort(key=lambda x: x["split_total"])

    best = options[0] if options else None
    has_saving = best and direct_price and (best.get("saving_vs_direct") or 0) > 0

    return {
        "route": f"{origin} → {destination}",
        "departure_date": departure_date,
        "adults": adults,
        "cabin_class": cabin_class,
        "currency": currency.upper(),
        "direct_price": direct_price,
        "direct_booking_links": direct_result.get("booking_links", {}),
        "split_options": options,
        "best_split": best,
        "best_saving": best["saving_vs_direct"] if best else None,
        "best_saving_pct": best["saving_pct"] if best else None,
        "hubs_tested": len(candidate_hubs),
        "hubs_priced": len(options),
        "verdict": (
            f"✅ Split via {best['hub_city']} saves ${best['saving_vs_direct']:.0f} "
            f"({best['saving_pct']:.0f}% cheaper). Read ALL risks before booking."
            if has_saving else
            "No split-ticket saving found for this route on this date."
        ),
        "risks": RISKS,
        "rules": RULES,
        "data_confidence": "scraped_live",
        "note": (
            "OTAs are contractually prevented from recommending split-ticket bookings. "
            "This tool reveals the pricing gap the industry conceals. "
            "Book each leg independently on the airline's own site."
        ),
    }
