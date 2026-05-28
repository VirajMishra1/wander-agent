"""Multi-origin meetup optimizer.

N travelers in N different cities want to meet somewhere. Find the city
where total combined cost is lowest. No OTA does this. The math is
combinatorial: query each origin->candidate route, sum totals.

Pre-filters destination pool to the 45 most central candidates (by
geographic centroid of all origins) so the search completes in <60s.
"""

from __future__ import annotations

import asyncio
import math

# Coordinates for destination airports (lat, lon)
_COORDS: dict[str, tuple[float, float]] = {
    "LHR": (51.48, -0.45), "CDG": (49.01, 2.55), "FCO": (41.80, 12.25),
    "BCN": (41.30, 2.08), "AMS": (52.31, 4.76), "MAD": (40.47, -3.57),
    "FRA": (50.04, 8.56), "MUC": (48.35, 11.79), "ZRH": (47.46, 8.55),
    "VIE": (48.11, 16.57), "BRU": (50.90, 4.48), "CPH": (55.62, 12.66),
    "OSL": (60.19, 11.10), "ARN": (59.65, 17.92), "HEL": (60.32, 24.96),
    "LIS": (38.78, -9.13), "ATH": (37.94, 23.94), "IST": (41.28, 28.75),
    "WAW": (52.17, 20.97), "PRG": (50.10, 14.26), "BUD": (47.43, 19.26),
    "OTP": (44.57, 26.10), "SOF": (42.70, 23.41), "BEG": (44.82, 20.31),
    "SKG": (40.52, 22.97), "JFK": (40.64, -73.78), "LAX": (33.94, -118.41),
    "ORD": (41.98, -87.90), "MIA": (25.80, -80.29), "YYZ": (43.68, -79.63),
    "YVR": (49.19, -123.18), "MEX": (19.44, -99.07), "GRU": (-23.43, -46.47),
    "EZE": (-34.82, -58.54), "SCL": (-33.39, -70.79), "BOG": (4.70, -74.15),
    "LIM": (-12.02, -77.11), "GIG": (-22.81, -43.25), "DXB": (25.25, 55.36),
    "DOH": (25.27, 51.61), "AUH": (24.44, 54.65), "CAI": (30.12, 31.41),
    "JNB": (-26.13, 28.24), "NBO": (-1.32, 36.93), "CPT": (-33.96, 18.60),
    "CMN": (33.36, -7.59), "ADD": (8.98, 38.80), "LOS": (6.58, 3.32),
    "NRT": (35.77, 140.39), "ICN": (37.46, 126.44), "HKG": (22.31, 113.92),
    "SIN": (1.36, 103.99), "BKK": (13.68, 100.75), "KUL": (2.75, 101.71),
    "CGK": (-6.13, 106.65), "MNL": (14.51, 121.02), "DEL": (28.56, 77.10),
    "BOM": (19.09, 72.87), "BLR": (13.20, 77.71), "MAA": (12.99, 80.17),
    "SYD": (-33.95, 151.18), "MEL": (-37.67, 144.84), "AKL": (-37.01, 174.79),
    "PEK": (40.08, 116.58), "PVG": (31.14, 121.81), "CAN": (23.39, 113.30),
    "TPE": (25.08, 121.23), "KIX": (34.43, 135.24), "CTU": (30.58, 103.95),
    "DPS": (-8.75, 115.17), "SGN": (10.82, 106.65), "HAN": (21.22, 105.80),
    "RGN": (16.91, 96.13), "DAC": (23.84, 90.40), "CMB": (7.18, 79.88),
    "TBS": (41.67, 44.95), "EVN": (40.15, 44.40), "TAS": (41.26, 69.28),
    "SFO": (37.62, -122.38), "BOS": (42.37, -71.01), "DFW": (32.90, -97.04),
    "SEA": (47.45, -122.31), "ATL": (33.64, -84.43), "DEN": (39.86, -104.67),
    "LAS": (36.08, -115.15), "PHX": (33.44, -112.01), "IAH": (29.99, -95.34),
    "CUN": (21.04, -86.87),
}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _centroid(iata_list: list[str]) -> tuple[float, float]:
    coords = [_COORDS[i] for i in iata_list if i in _COORDS]
    if not coords:
        return (20.0, 0.0)
    return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))


async def multi_origin_meetup(
    origins: str,
    departure_date: str,
    return_date: str,
    max_results: int = 10,
    currency: str = "USD",
    regions: str | None = None,
) -> dict:
    """Find the cheapest common meeting destination for travelers in different cities.

    "4 friends in NYC, London, Dubai, Tokyo — where's cheapest to meet?"

    Computes geographic centroid of all origins, evaluates the 45 most central
    candidate destinations, sums round-trip costs per traveler, ranks by total.
    No OTA does this. Completes in ~30-60 seconds.

    Args:
        origins: Comma-separated IATA codes (e.g., "JFK,LHR,DXB,NRT")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        max_results: Top N destinations to return (default 10)
        currency: USD, EUR, etc.
        regions: Optionally limit to regions: europe, asia, americas, middle_east, africa
    """
    from .flights import search_flights
    from ..utils.airport_data import filter_destinations

    origin_list = [o.strip().upper() for o in origins.split(",") if o.strip()]
    if len(origin_list) < 2:
        return {"error": "Need at least 2 origin airports, comma-separated"}

    all_destinations = filter_destinations(regions=regions)
    all_destinations = [d for d in all_destinations if d[0] not in origin_list]

    # Pre-filter: keep 45 destinations closest to geographic centroid of all origins
    MAX_CANDIDATES = 45
    if len(all_destinations) > MAX_CANDIDATES:
        clat, clon = _centroid(origin_list)
        scored = []
        for iata, city, country, region in all_destinations:
            if iata in _COORDS:
                dist = _haversine(clat, clon, *_COORDS[iata])
            else:
                dist = 9999.0
            scored.append((dist, iata, city, country, region))
        scored.sort()
        all_destinations = [
            (iata, city, country, region)
            for _, iata, city, country, region in scored[:MAX_CANDIDATES]
        ]

    sem = asyncio.Semaphore(10)

    async def _cost_for_traveler(origin: str, dest_iata: str) -> dict:
        async with sem:
            try:
                r = await search_flights(
                    origin=origin, destination=dest_iata,
                    departure_date=departure_date,
                    max_results=1, currency=currency,
                )
                outbound = r.get("cheapest_price")
                r2 = await search_flights(
                    origin=dest_iata, destination=origin,
                    departure_date=return_date,
                    max_results=1, currency=currency,
                )
                inbound = r2.get("cheapest_price")
                if outbound and inbound:
                    return {"origin": origin, "round_trip": outbound + inbound}
                return {"origin": origin, "round_trip": None}
            except Exception:
                return {"origin": origin, "round_trip": None}

    async def _eval_destination(iata: str, city: str, country: str, region: str) -> dict | None:
        traveler_costs = await asyncio.gather(*[
            _cost_for_traveler(o, iata) for o in origin_list
        ])
        if any(t["round_trip"] is None for t in traveler_costs):
            return None
        total = sum(t["round_trip"] for t in traveler_costs)
        return {
            "destination": city,
            "destination_airport": iata,
            "country": country,
            "region": region,
            "total_combined_cost": round(total, 2),
            "per_traveler_breakdown": [
                {"origin": t["origin"], "round_trip_cost": round(t["round_trip"], 2)}
                for t in traveler_costs
            ],
            "average_per_traveler": round(total / len(origin_list), 2),
            "currency": currency.upper(),
        }

    results = await asyncio.gather(*[
        _eval_destination(iata, city, country, region)
        for iata, city, country, region in all_destinations
    ])
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda x: x["total_combined_cost"])
    top = valid[:max_results]

    return {
        "travelers": origin_list,
        "traveler_count": len(origin_list),
        "departure_date": departure_date,
        "return_date": return_date,
        "destinations_evaluated": len(all_destinations),
        "destinations_with_full_pricing": len(valid),
        "regions": regions or "global",
        "results_count": len(top),
        "destinations": top,
        "winner": top[0] if top else None,
        "currency": currency.upper(),
        "tip": "Show per_traveler_breakdown so each person sees their own cost.",
        "suggest_web_search": [
            f"weekend trip {top[0]['destination']}" if top else "",
            f"things to do in {top[0]['destination']} group of {len(origin_list)}" if top else "",
        ],
    }
