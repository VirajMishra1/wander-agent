"""Flight carbon footprint calculator.

Calculates CO2e emissions for a flight using great-circle distance and
ICAO/DEFRA emission factors. Compares to car and train alternatives.
Shows carbon offset cost (Gold Standard verified offsets ~$15-25/tonne).

No API key required — pure math + static emission factors.
"""

from __future__ import annotations

import math

# Emission factors (kg CO2e per passenger per km) — DEFRA/ICAO 2024
# Includes radiative forcing multiplier (RFI ~1.9) for high-altitude warming
_EMISSION_FACTORS: dict[str, float] = {
    "economy":         0.133,
    "premium_economy": 0.200,
    "business":        0.266,
    "first":           0.399,
}

_CAR_FACTORS: dict[str, float] = {
    "petrol": 0.171, "diesel": 0.163, "hybrid": 0.110, "electric": 0.047,
}

_TRAIN_FACTORS: dict[str, float] = {
    "high_speed": 0.014, "intercity": 0.041, "us_amtrak": 0.056,
}

_AIRPORT_COORDS: dict[str, tuple[float, float]] = {
    "JFK": (40.64, -73.78), "EWR": (40.69, -74.17), "LGA": (40.78, -73.87),
    "LAX": (33.94, -118.41), "SFO": (37.62, -122.38), "ORD": (41.98, -87.90),
    "ATL": (33.64, -84.43), "MIA": (25.80, -80.29), "DFW": (32.90, -97.04),
    "SEA": (47.45, -122.31), "BOS": (42.37, -71.01), "DEN": (39.86, -104.67),
    "LHR": (51.48, -0.45), "LGW": (51.15, -0.18), "STN": (51.88, 0.24),
    "MAN": (53.35, -2.27), "EDI": (55.95, -3.37),
    "CDG": (49.01, 2.55), "ORY": (48.72, 2.38),
    "AMS": (52.31, 4.76),
    "FRA": (50.04, 8.56), "MUC": (48.35, 11.79), "BER": (52.37, 13.52),
    "ZRH": (47.46, 8.55), "GVA": (46.24, 6.11),
    "MAD": (40.47, -3.57), "BCN": (41.30, 2.08),
    "FCO": (41.80, 12.25), "MXP": (45.63, 8.73),
    "DXB": (25.25, 55.36), "AUH": (24.44, 54.65), "SHJ": (25.33, 55.52),
    "DOH": (25.27, 51.61),
    "IST": (41.28, 28.75), "SAW": (40.90, 29.31),
    "SIN": (1.36, 103.99),
    "HKG": (22.31, 113.92),
    "NRT": (35.77, 140.39), "HND": (35.55, 139.78), "KIX": (34.43, 135.24),
    "ICN": (37.46, 126.44), "GMP": (37.56, 126.79),
    "PEK": (40.08, 116.58), "PVG": (31.14, 121.81), "CAN": (23.39, 113.30),
    "BKK": (13.68, 100.75), "DMK": (13.91, 100.61), "HKT": (8.11, 98.32),
    "KUL": (2.75, 101.71),
    "DEL": (28.56, 77.10), "BOM": (19.09, 72.87), "BLR": (13.20, 77.71),
    "MAA": (12.99, 80.17),
    "SYD": (-33.95, 151.18), "MEL": (-37.67, 144.84), "BNE": (-27.38, 153.12),
    "JNB": (-26.13, 28.24), "CPT": (-33.96, 18.60),
    "YYZ": (43.68, -79.63), "YVR": (49.19, -123.18), "YUL": (45.47, -73.74),
    "GRU": (-23.43, -46.47), "GIG": (-22.81, -43.25),
    "MEX": (19.44, -99.07),
    "NBO": (-1.32, 36.93), "ADD": (8.98, 38.80),
    "CMN": (33.36, -7.59),
    "DPS": (-8.75, 115.17), "CGK": (-6.13, 106.65),
    "SGN": (10.82, 106.65), "HAN": (21.22, 105.80),
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def calculate_flight_carbon(
    origin: str,
    destination: str,
    passengers: int = 1,
    cabin_class: str = "economy",
    trip_type: str = "round_trip",
) -> dict:
    """Calculate CO2e carbon footprint for a flight.

    Uses ICAO/DEFRA 2024 emission factors including radiative forcing (RFI ×1.9)
    for high-altitude warming. Shows per-passenger and total emissions, carbon
    offset cost at Gold Standard prices, and train/car comparison for short routes.

    No API key required.

    Args:
        origin: Origin airport IATA code (e.g., "JFK")
        destination: Destination airport IATA code (e.g., "LHR")
        passengers: Number of passengers
        cabin_class: economy | premium_economy | business | first
        trip_type: one_way | round_trip
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()
    cabin = cabin_class.lower().replace("-", "_").replace(" ", "_")
    if cabin not in _EMISSION_FACTORS:
        cabin = "economy"

    o_coords = _AIRPORT_COORDS.get(origin)
    d_coords = _AIRPORT_COORDS.get(destination)

    if not o_coords:
        return {"error": f"Airport {origin} not in dataset. Use IATA code e.g. JFK, LHR, DXB."}
    if not d_coords:
        return {"error": f"Airport {destination} not in dataset. Use IATA code e.g. JFK, LHR, DXB."}

    gc_km = _haversine_km(*o_coords, *d_coords)
    # Add ~10% for actual flight path detour vs great circle
    flight_km = gc_km * (1.10 if gc_km > 1000 else 1.05)
    legs = 2 if trip_type == "round_trip" else 1

    factor = _EMISSION_FACTORS[cabin]
    co2_per_pax = flight_km * factor * legs
    co2_total = co2_per_pax * passengers

    # Gold Standard offset ~$18/tonne midpoint
    offset_per_pax = round(co2_per_pax / 1000 * 18, 2)
    offset_total = round(co2_total / 1000 * 18, 2)

    if gc_km < 500:
        route_type = "short-haul (<500 km)"
        train_viable = True
    elif gc_km < 1500:
        route_type = "medium-haul (500-1500 km)"
        train_viable = True
    elif gc_km < 4000:
        route_type = "long-haul (1500-4000 km)"
        train_viable = False
    else:
        route_type = "ultra-long-haul (>4000 km)"
        train_viable = False

    result: dict = {
        "route": f"{origin} → {destination}" + (f" → {origin}" if trip_type == "round_trip" else ""),
        "trip_type": trip_type,
        "cabin_class": cabin,
        "passengers": passengers,
        "great_circle_km": round(gc_km),
        "actual_km_estimated": round(flight_km),
        "route_type": route_type,
        "emissions_per_passenger": {
            "kg_co2e": round(co2_per_pax, 1),
            "tonnes_co2e": round(co2_per_pax / 1000, 3),
        },
        "emissions_total_all_passengers": {
            "kg_co2e": round(co2_total, 1),
            "tonnes_co2e": round(co2_total / 1000, 3),
        },
        "carbon_offset": {
            "cost_per_passenger_usd": offset_per_pax,
            "cost_total_usd": offset_total,
            "price_per_tonne_usd": 18,
            "providers": [
                "https://www.goldstandard.org/take-action/offset-your-emissions",
                "https://atmosfair.de/en/",
                "https://www.climatecare.org/",
            ],
        },
        "context": [
            f"Equivalent to driving {round(co2_per_pax / 0.171):.0f} km in a petrol car",
            f"Equivalent to {round(co2_per_pax / 2.3):.0f} days of average EU electricity use",
            f"Equivalent to {round(co2_per_pax / 6.3):.0f} beef burgers (production emissions)",
        ],
        "methodology": (
            "ICAO/DEFRA 2024 factors. Includes radiative forcing multiplier (RFI ×1.9) "
            "for high-altitude warming effects. Economy: 0.133 kg CO2e/pax-km, "
            "Business: 0.266, First: 0.399."
        ),
        "data_confidence": "icao_defra_2024_static",
    }

    if train_viable:
        train_co2 = flight_km * _TRAIN_FACTORS["high_speed"] * legs * passengers
        car_co2_pp = flight_km * _CAR_FACTORS["petrol"] * legs / max(passengers, 2)
        saving_pct = round((1 - train_co2 / co2_total) * 100) if co2_total else 0
        result["alternatives"] = {
            "high_speed_train": {
                "kg_co2e_total": round(train_co2, 1),
                "saving_vs_flight_pct": saving_pct,
                "note": "Electric high-speed rail (TGV/Eurostar/Shinkansen class)",
            },
            "car_per_person": {
                "kg_co2e": round(car_co2_pp, 1),
                "basis": f"Petrol car, {max(passengers, 2)} occupants",
            },
            "train_search": f"https://www.thetrainline.com/book/results?origin={origin}&destination={destination}",
        }

    return result
