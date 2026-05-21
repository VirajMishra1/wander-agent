"""Cost of living estimates from curated dataset.

Uses public-source-aggregated estimates for 100+ major destinations.
Falls back to country-level medians for unlisted cities.
"""

from __future__ import annotations


async def get_cost_of_living(
    city: str,
    home_currency: str = "USD",
    trip_days: int | None = None,
) -> dict:
    """Cost of living estimate for a travel destination.

    Returns daily traveler budgets at three tiers: budget (hostel/street food),
    mid (3-star hotel/sit-down meals), luxury (4-5 star/fine dining).

    Args:
        city: City name (e.g., "Lisbon", "Tokyo", "Reykjavik")
        home_currency: Currency to convert estimates to (USD, EUR, etc.)
        trip_days: If given, multiplies daily budgets by trip length
    """
    from ..utils.cost_data import lookup_cost
    from .destination import geocode
    from .currency import convert_currency

    # First try direct city lookup
    cost = lookup_cost(city=city)

    # If no match, geocode to get country and try country fallback
    country = None
    if not cost:
        geo = await geocode(city)
        if not geo.get("error"):
            country = geo.get("country", "")
            cost = lookup_cost(city=geo.get("name", city), country=country)

    if not cost:
        return {
            "city": city,
            "error": f"No cost data for '{city}'. Dataset covers 100+ major destinations.",
            "hint": "Try a major nearby city (e.g., 'Barcelona' instead of small village)",
        }

    budget_usd = cost["daily_budget_usd"]
    mid_usd = cost["daily_mid_usd"]
    luxury_usd = cost["daily_luxury_usd"]

    # Convert if not USD
    converted = {}
    if home_currency.upper() != "USD":
        try:
            b_conv = await convert_currency(budget_usd, "USD", home_currency)
            m_conv = await convert_currency(mid_usd, "USD", home_currency)
            l_conv = await convert_currency(luxury_usd, "USD", home_currency)
            if not b_conv.get("error"):
                converted = {
                    "budget": b_conv["converted_amount"],
                    "mid": m_conv["converted_amount"],
                    "luxury": l_conv["converted_amount"],
                    "currency": home_currency.upper(),
                }
        except Exception:
            pass

    result = {
        "city": city,
        "match_type": cost["match_type"],
        "matched_name": cost["matched_name"],
        "daily_budget_per_person": {
            "budget_tier_usd": budget_usd,
            "mid_tier_usd": mid_usd,
            "luxury_tier_usd": luxury_usd,
            "description": {
                "budget": "Hostel/Airbnb shared, street food, public transport",
                "mid": "3-star hotel, mid-range restaurants, mix of transit + taxis",
                "luxury": "4-5 star hotel, fine dining, taxis/rentals",
            },
        },
        "in_local_currency": converted,
        "source": "Curated from public aggregators (Numbeo, Budget Your Trip, Expatistan)",
        "snapshot_year": 2026,
    }

    if trip_days and trip_days > 0:
        result["trip_total_estimates_usd"] = {
            "budget": budget_usd * trip_days,
            "mid": mid_usd * trip_days,
            "luxury": luxury_usd * trip_days,
            "trip_days": trip_days,
        }

    return result
