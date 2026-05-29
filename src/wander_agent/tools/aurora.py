"""Aurora / natural phenomenon reverse search.

"Where can I see the northern lights cheapest in next 60 days?"
Combines NOAA KP-index forecast + aurora-zone airports + flight pricing.

Reverse natural-phenomenon search. No OTA does this.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


# Aurora-viewing airports with high seasonal aurora activity (auroral oval)
AURORA_AIRPORTS: list[tuple[str, str, str, float]] = [
    # IATA, city, country, geomag latitude (~)
    ("TOS", "Tromso", "Norway", 66.7),
    ("BOO", "Bodo", "Norway", 65.5),
    ("RVN", "Rovaniemi", "Finland", 64.0),
    ("KEF", "Reykjavik", "Iceland", 64.1),
    ("FAI", "Fairbanks", "USA (Alaska)", 64.9),
    ("YZF", "Yellowknife", "Canada", 67.5),
    ("YYC", "Calgary", "Canada", 56.3),
    ("KIR", "Kiruna", "Sweden", 65.8),
    ("OUL", "Oulu", "Finland", 62.6),
    ("MMK", "Murmansk", "Russia", 65.7),
    ("ABZ", "Aberdeen", "Scotland", 57.5),
    ("INV", "Inverness", "Scotland", 58.5),
    ("YQX", "Gander", "Canada", 53.0),
]


async def find_aurora_destinations(
    origin: str,
    max_budget: float = 1500.0,
    days_ahead_min: int = 7,
    days_ahead_max: int = 60,
    currency: str = "USD",
    max_results: int = 8,
) -> dict:
    """Find cheapest flights to aurora-viewing destinations + KP forecast.

    Args:
        origin: Departure IATA code (e.g., "JFK")
        max_budget: Max total flight budget USD
        days_ahead_min: Earliest departure (days from now)
        days_ahead_max: Latest departure (days from now)
        currency: USD, EUR, etc.
        max_results: Max destinations to return
    """
    from .flights import search_flights
    from .weather import get_weather
    from ..utils.http import get_client

    today = datetime.now().date()
    # Pick a sample date in the window (middle for best forecast)
    sample_date = today + timedelta(days=(days_ahead_min + days_ahead_max) // 2)
    # Aurora season check
    aurora_season = sample_date.month in [9, 10, 11, 12, 1, 2, 3, 4]

    # Fetch NOAA 3-day KP forecast (no auth)
    kp_forecast_summary: dict = {}
    try:
        client = await get_client()
        kp_resp = await client.get(
            "https://services.swpc.noaa.gov/text/3-day-forecast.txt",
            timeout=15.0,
        )
        if kp_resp.status_code == 200:
            text = kp_resp.text
            # Pull max KP from forecast (rough parse - look for KP values 0-9)
            import re
            kp_values = [int(m) for m in re.findall(r"\b([0-9])\b", text[:2000])]
            if kp_values:
                kp_forecast_summary = {
                    "max_kp_3day": max(kp_values),
                    "avg_kp_3day": round(sum(kp_values) / len(kp_values), 1),
                    "interpretation": (
                        "Strong aurora (visible far south)" if max(kp_values) >= 6
                        else "Moderate aurora (visible at auroral oval)" if max(kp_values) >= 4
                        else "Weak aurora (only at high latitudes)"
                    ),
                    "source": "NOAA SWPC 3-day forecast",
                }
    except Exception:
        pass

    sem = asyncio.Semaphore(5)

    async def _eval_airport(iata: str, city: str, country: str, geomag_lat: float) -> dict | None:
        async with sem:
            try:
                flight = await search_flights(
                    origin=origin, destination=iata,
                    departure_date=sample_date.isoformat(),
                    max_results=1, currency=currency,
                )
                price = flight.get("cheapest_price")
                if not price or price > max_budget:
                    return None

                # Aurora visibility score: higher geomag latitude + aurora season
                aurora_score = geomag_lat - 50
                if aurora_season:
                    aurora_score += 5

                from .flights import (
                    _skyscanner_url, _google_flights_url,
                    _expedia_flight_url, _lastminute_flight_url,
                )
                booking_links = flight.get("booking_links") or {
                    "skyscanner": _skyscanner_url(origin, iata, sample_date.isoformat(), 1),
                    "google_flights": _google_flights_url(origin, iata, sample_date.isoformat(), 1),
                    "expedia": _expedia_flight_url(origin, iata, sample_date.isoformat(), 1),
                    "lastminute": _lastminute_flight_url(origin, iata, sample_date.isoformat(), 1),
                }
                return {
                    "destination": city,
                    "destination_airport": iata,
                    "country": country,
                    "geomagnetic_latitude": geomag_lat,
                    "aurora_visibility_score": round(aurora_score, 1),
                    "flight_price": price,
                    "currency": currency.upper(),
                    "sample_departure_date": sample_date.isoformat(),
                    "aurora_season": aurora_season,
                    "best_viewing_months": "Sep-Apr",
                    "booking_links": booking_links,
                    "kiwi_live_fares": flight.get("kiwi_live_fares", []),
                }
            except Exception:
                return None

    results = await asyncio.gather(*[
        _eval_airport(iata, city, country, gl) for iata, city, country, gl in AURORA_AIRPORTS
    ])
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda x: x["flight_price"])
    top = valid[:max_results]

    return {
        "origin": origin.upper(),
        "max_budget": max_budget,
        "currency": currency.upper(),
        "search_window": {
            "earliest": (today + timedelta(days=days_ahead_min)).isoformat(),
            "latest": (today + timedelta(days=days_ahead_max)).isoformat(),
            "sample_date_used": sample_date.isoformat(),
        },
        "aurora_season": aurora_season,
        "season_note": (
            "Aurora season (Sep-Apr). Long dark nights = better viewing." if aurora_season
            else "Off-season (May-Aug). Summer = midnight sun, no aurora."
        ),
        "current_kp_forecast": kp_forecast_summary,
        "results_count": len(top),
        "destinations": top,
        "cheapest": top[0] if top else None,
        "tip": "Higher geomagnetic latitude = better aurora odds. Above 64deg = consistent viewing.",
        "suggest_web_search": [
            f"aurora forecast {sample_date.isoformat()[:7]} KP index",
            f"best aurora viewing tours {top[0]['destination']}" if top else "northern lights tour",
            "aurora hotel glass roof booking",
        ],
    }
