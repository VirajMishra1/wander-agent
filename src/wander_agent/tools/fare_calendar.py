"""Fare calendar — cheapest day to fly in a given month.

Samples up to 15 days per month (every other day) and returns a full
price grid with day-of-week analysis, price tiers, and best/worst weeks.
"""

from __future__ import annotations

import asyncio
import calendar
from datetime import date, timedelta


def _days_to_sample(year: int, month: int, max_samples: int = 15) -> list[date]:
    """Return up to max_samples dates spread across the month, skipping the past."""
    today = date.today()
    days_in_month = calendar.monthrange(year, month)[1]
    step = max(1, days_in_month // max_samples)
    result = []
    d = 1
    while d <= days_in_month and len(result) < max_samples:
        candidate = date(year, month, d)
        if candidate > today:
            result.append(candidate)
        d += step
    return result


def _tier(price: float, p33: float, p67: float) -> str:
    if price <= p33:
        return "budget"
    if price <= p67:
        return "mid"
    return "expensive"


def _week_label(d: date) -> str:
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return f"{start.strftime('%b %-d')}–{end.strftime('%-d')}"


async def fare_calendar(
    origin: str,
    destination: str,
    year: int | None = None,
    month: int | None = None,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    trip_length_days: int | None = None,
) -> dict:
    """Show a full month price grid — find the cheapest day to fly.

    Samples up to 15 departure dates per month and returns prices, day-of-week
    analysis, price tiers (budget/mid/expensive), and best/worst weeks. Useful
    for flexible travelers who can shift by a few days to save money.

    Args:
        origin: Origin airport IATA code (e.g., "JFK")
        destination: Destination airport IATA code (e.g., "LHR")
        year: Year (default: next occurrence of month)
        month: Month 1-12 (default: next month)
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code (e.g., "USD", "EUR", "GBP")
        trip_length_days: If set, price as round-trip (return = departure + N days)
    """
    from .flights import search_flights

    today = date.today()

    # Resolve year/month
    if month is None:
        nxt = today.replace(day=1) + timedelta(days=32)
        month = nxt.month
        year = nxt.year
    if year is None:
        year = today.year if month > today.month else today.year + 1

    origin = origin.upper().strip()
    destination = destination.upper().strip()

    sample_dates = _days_to_sample(year, month, max_samples=15)
    if not sample_dates:
        return {
            "error": f"All dates in {year}-{month:02d} are in the past.",
            "route": f"{origin} → {destination}",
        }

    sem = asyncio.Semaphore(3)

    async def _price_date(dep: date) -> dict | None:
        async with sem:
            try:
                ret_date = (dep + timedelta(days=trip_length_days)).isoformat() if trip_length_days else None
                result = await search_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=dep.isoformat(),
                    return_date=ret_date,
                    adults=adults,
                    max_results=1,
                    currency=currency,
                    cabin_class=cabin_class,
                )
                price = result.get("cheapest_price")
                if not price:
                    return None
                return {
                    "date": dep.isoformat(),
                    "day_of_week": dep.strftime("%A"),
                    "price": price,
                    "currency": currency.upper(),
                    "week": _week_label(dep),
                }
            except Exception:
                return None

    raw = await asyncio.gather(*[_price_date(d) for d in sample_dates])
    priced = [r for r in raw if r is not None]

    if not priced:
        return {
            "error": "No prices returned for this route/month. Try a different month or check IATA codes.",
            "route": f"{origin} → {destination}",
            "month": f"{year}-{month:02d}",
        }

    prices_sorted = sorted(p["price"] for p in priced)
    n = len(prices_sorted)
    p33 = prices_sorted[n // 3]
    p67 = prices_sorted[(2 * n) // 3]
    for item in priced:
        item["tier"] = _tier(item["price"], p33, p67)

    priced.sort(key=lambda x: x["date"])

    cheapest = min(priced, key=lambda x: x["price"])
    priciest = max(priced, key=lambda x: x["price"])

    # Day-of-week analysis
    dow: dict[str, list[float]] = {}
    for item in priced:
        dow.setdefault(item["day_of_week"], []).append(item["price"])
    dow_analysis = {
        day: {
            "avg_price": round(sum(prices) / len(prices)),
            "samples": len(prices),
            "min_price": min(prices),
        }
        for day, prices in sorted(dow.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
    }

    # Week analysis
    weeks: dict[str, list[float]] = {}
    for item in priced:
        weeks.setdefault(item["week"], []).append(item["price"])
    week_avgs = {w: round(sum(p) / len(p)) for w, p in weeks.items()}
    best_week = min(week_avgs, key=week_avgs.get) if week_avgs else None
    worst_week = max(week_avgs, key=week_avgs.get) if week_avgs else None

    # Booking links for cheapest date
    cheap_date = cheapest["date"]
    ret = (date.fromisoformat(cheap_date) + timedelta(days=trip_length_days or 7)).isoformat()
    booking_links = {
        "google_flights": (
            f"https://www.google.com/flights#flt={origin}.{destination}.{cheap_date}"
            + (f"*{destination}.{origin}.{ret}" if trip_length_days else "")
            + f";c:{currency};e:1"
        ),
        "skyscanner": (
            f"https://www.skyscanner.net/transport/flights/{origin.lower()}/{destination.lower()}/"
            f"{cheap_date.replace('-', '')}"
            + (f"/{ret.replace('-', '')}" if trip_length_days else "")
            + f"/?adults={adults}&cabinclass={cabin_class}"
        ),
        "kayak": (
            f"https://www.kayak.com/flights/{origin}-{destination}/{cheap_date}"
            + (f"/{ret}" if trip_length_days else "")
            + f"/{adults}adults"
        ),
    }

    return {
        "route": f"{origin} → {destination}",
        "month": f"{year}-{month:02d}",
        "trip_type": "round_trip" if trip_length_days else "one_way",
        "trip_length_days": trip_length_days,
        "adults": adults,
        "cabin_class": cabin_class,
        "currency": currency.upper(),
        "days_sampled": len(priced),
        "price_grid": priced,
        "cheapest": {
            "date": cheapest["date"],
            "day_of_week": cheapest["day_of_week"],
            "price": cheapest["price"],
            "week": cheapest.get("week"),
        },
        "most_expensive": {
            "date": priciest["date"],
            "day_of_week": priciest["day_of_week"],
            "price": priciest["price"],
        },
        "price_spread": priciest["price"] - cheapest["price"],
        "price_tiers": {
            "budget_threshold": p33,
            "expensive_threshold": p67,
        },
        "day_of_week_analysis": dow_analysis,
        "cheapest_day_of_week": next(iter(dow_analysis)) if dow_analysis else None,
        "week_analysis": week_avgs,
        "best_week": best_week,
        "worst_week": worst_week,
        "booking_links_for_cheapest_date": booking_links,
        "data_confidence": "scraped_live",
        "note": (
            "Prices sampled every ~2 days. Mid-week departures (Tue/Wed) are typically cheapest. "
            "Book 6-8 weeks ahead for best fares on most routes."
        ),
    }
