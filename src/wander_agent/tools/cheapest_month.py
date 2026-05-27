"""Find the cheapest month to fly a given route.

Scans the next 12 months by sampling the first Tuesday of each month
(statistically cheapest booking day). 12 calls max — polite to scrapers.
Returns months ranked by price with season labels and booking links.
"""

from __future__ import annotations

import asyncio
import calendar
from datetime import date, timedelta


def _first_tuesday(year: int, month: int) -> date:
    """Return the date of the first Tuesday in a given month."""
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        if week[calendar.TUESDAY] != 0:
            return date(year, month, week[calendar.TUESDAY])
    return date(year, month, 1)


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def _demand_label(month: int) -> str:
    if month in (6, 7, 8):
        return "peak — summer school holidays"
    if month == 12:
        return "peak — Christmas/New Year"
    if month in (3, 4):
        return "shoulder — spring travel"
    if month in (1, 2):
        return "off-peak — post-holiday quiet"
    if month in (9, 10, 11):
        return "shoulder — autumn off-peak"
    return "standard"


async def find_cheapest_month(
    origin: str,
    destination: str,
    months_ahead: int = 12,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    trip_length_days: int = 7,
    trip_type: str = "round_trip",
) -> dict:
    """Find the cheapest month to fly a route over the next N months.

    Samples the first Tuesday of each month (statistically cheapest booking day).
    Returns all months ranked by price with season analysis. Flexible travelers
    can save hundreds by shifting their trip by just one or two months.

    Complements fare_calendar (day-level within one month — this is month-level
    across a full year).

    Args:
        origin: Origin airport IATA code (e.g., "JFK")
        destination: Destination airport IATA code (e.g., "BCN")
        months_ahead: Future months to scan (1-12, default 12)
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code
        trip_length_days: Days for round-trip return leg (departure + N)
        trip_type: round_trip | one_way
    """
    from .flights import search_flights

    origin = origin.upper().strip()
    destination = destination.upper().strip()
    months_ahead = max(1, min(int(months_ahead), 12))

    today = date.today()
    months_to_scan: list[tuple[int, int, date]] = []
    y, m = today.year, today.month
    for _ in range(months_ahead):
        m += 1
        if m > 12:
            m = 1
            y += 1
        sample = _first_tuesday(y, m)
        if sample > today:
            months_to_scan.append((y, m, sample))

    if not months_to_scan:
        return {"error": "No future months to scan.", "route": f"{origin} → {destination}"}

    sem = asyncio.Semaphore(3)

    async def _price_month(yr: int, mo: int, dep: date) -> dict | None:
        async with sem:
            try:
                ret = (
                    (dep + timedelta(days=trip_length_days)).isoformat()
                    if trip_type == "round_trip" else None
                )
                result = await search_flights(
                    origin=origin, destination=destination,
                    departure_date=dep.isoformat(),
                    return_date=ret,
                    adults=adults, max_results=1,
                    currency=currency, cabin_class=cabin_class,
                )
                price = result.get("cheapest_price")
                if not price:
                    return None
                return {
                    "month": f"{yr}-{mo:02d}",
                    "month_name": dep.strftime("%B %Y"),
                    "sample_date": dep.isoformat(),
                    "sample_day": dep.strftime("%A"),
                    "price": price,
                    "currency": currency.upper(),
                    "season": _season(mo),
                    "demand": _demand_label(mo),
                }
            except Exception:
                return None

    raw = await asyncio.gather(*[_price_month(y, m, d) for y, m, d in months_to_scan])
    priced = [r for r in raw if r is not None]

    if not priced:
        return {
            "error": "No prices returned. Check IATA codes or try a different route.",
            "route": f"{origin} → {destination}",
        }

    prices_sorted = sorted(p["price"] for p in priced)
    n = len(prices_sorted)
    p33, p67 = prices_sorted[n // 3], prices_sorted[(2 * n) // 3]
    for item in priced:
        item["tier"] = "budget" if item["price"] <= p33 else "mid" if item["price"] <= p67 else "expensive"

    ranked = sorted(priced, key=lambda x: x["price"])
    cheapest = ranked[0]
    priciest = ranked[-1]

    season_avgs: dict[str, list[float]] = {}
    for item in priced:
        season_avgs.setdefault(item["season"], []).append(item["price"])
    season_summary = {
        s: round(sum(v) / len(v))
        for s, v in sorted(season_avgs.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
    }

    cheap_dep = cheapest["sample_date"]
    cheap_ret = (date.fromisoformat(cheap_dep) + timedelta(days=trip_length_days)).isoformat()
    booking_links = {
        "google_flights": (
            f"https://www.google.com/flights#flt={origin}.{destination}.{cheap_dep}"
            + (f"*{destination}.{origin}.{cheap_ret}" if trip_type == "round_trip" else "")
            + f";c:{currency};e:1"
        ),
        "skyscanner": (
            f"https://www.skyscanner.net/transport/flights/{origin.lower()}/{destination.lower()}/"
            f"{cheap_dep.replace('-', '')}"
            + (f"/{cheap_ret.replace('-', '')}" if trip_type == "round_trip" else "")
            + f"/?adults={adults}&cabinclass={cabin_class}"
        ),
        "kayak": (
            f"https://www.kayak.com/flights/{origin}-{destination}/{cheap_dep}"
            + (f"/{cheap_ret}" if trip_type == "round_trip" else "")
            + f"/{adults}adults"
        ),
    }

    return {
        "route": f"{origin} → {destination}",
        "trip_type": trip_type,
        "trip_length_days": trip_length_days if trip_type == "round_trip" else None,
        "adults": adults,
        "cabin_class": cabin_class,
        "currency": currency.upper(),
        "months_scanned": len(priced),
        "ranking": ranked,
        "cheapest_month": cheapest["month_name"],
        "cheapest_price": cheapest["price"],
        "cheapest_sample_date": cheapest["sample_date"],
        "most_expensive_month": priciest["month_name"],
        "most_expensive_price": priciest["price"],
        "price_spread": priciest["price"] - cheapest["price"],
        "potential_saving_vs_peak": round(priciest["price"] - cheapest["price"], 2),
        "season_avg_prices": season_summary,
        "cheapest_season": next(iter(season_summary)) if season_summary else None,
        "booking_links_for_cheapest_month": booking_links,
        "data_confidence": "scraped_live",
        "note": (
            "Sampled on first Tuesday of each month — statistically cheapest booking day. "
            "Book 6-8 weeks before departure for most routes. "
            "Use fare_calendar to pinpoint the cheapest day within your chosen month."
        ),
    }
