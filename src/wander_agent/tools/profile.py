"""Traveler profile management.

Persistent profile so the agent acts like a real travel agent:
- Knows home airport, passport(s), currency on every call
- Remembers past trips and visa holdings
- First-use onboarding: ask once, remember forever
"""

from __future__ import annotations

from typing import Any


# Questions shown to new users during onboarding
_ONBOARDING_QUESTIONS = [
    {
        "id": "name",
        "question": "What's your first name? (so I can address you personally)",
        "type": "text",
        "example": "Alex",
    },
    {
        "id": "home_airports",
        "question": "What airport(s) do you usually fly from? List nearby ones too.",
        "type": "list",
        "example": ["JFK", "EWR", "LGA"],
        "note": "NYC area: JFK/EWR/LGA. London: LHR/LGW/STN. Dubai: DXB/SHJ/AUH.",
    },
    {
        "id": "passports",
        "question": "Which passport(s) do you hold? (ISO 2-letter country codes)",
        "type": "list",
        "example": ["US"],
        "note": "US=United States, GB=UK, IN=India, DE=Germany, AU=Australia, CA=Canada",
    },
    {
        "id": "home_currency",
        "question": "What's your home currency?",
        "type": "text",
        "example": "USD",
        "options": ["USD", "EUR", "GBP", "INR", "AUD", "CAD", "SGD", "AED"],
    },
    {
        "id": "travel_style",
        "question": "What's your travel style?",
        "type": "choice",
        "options": ["budget", "moderate", "luxury"],
    },
    {
        "id": "interests",
        "question": "What are your travel interests? Pick all that apply.",
        "type": "list",
        "options": ["beach", "food", "history", "nature", "nightlife", "art", "adventure", "wellness", "shopping"],
        "example": ["food", "history", "nature"],
    },
    {
        "id": "dietary",
        "question": "Any dietary restrictions? (optional — skip if none)",
        "type": "list",
        "options": ["vegetarian", "vegan", "halal", "kosher", "gluten_free", "none"],
    },
    {
        "id": "preferred_cabin",
        "question": "Preferred cabin class?",
        "type": "choice",
        "options": ["economy", "premium_economy", "business", "first"],
    },
    {
        "id": "visas_held",
        "question": "Do you currently hold any valid visas? (ISO-2 destination country codes)",
        "type": "list",
        "example": ["IN", "CN"],
        "note": "Skip if none. Lets me skip visa warnings for countries you already have access to.",
    },
    {
        "id": "eta_held",
        "question": "Any active electronic travel authorizations?",
        "type": "list",
        "options": ["ESTA (US)", "eTA (Canada)", "UK ETA", "NZ ETA", "Australia ETA"],
        "example": ["ESTA (US)"],
    },
    {
        "id": "loyalty",
        "question": "Any airline loyalty programs? (optional — helps me prioritize your airline)",
        "type": "list_of_objects",
        "example": [{"airline": "United Airlines", "program": "MileagePlus", "tier": "Gold"}],
    },
]


async def get_traveler_profile() -> dict:
    """Get the stored traveler profile.

    Call this at the start of every travel planning session to load
    home airports, passports, preferences, visa holdings, and trip history.
    If onboarded=False in the response, ask the user to run onboard_traveler first.
    """
    from ..utils.profile_store import load_profile

    profile = load_profile()
    result: dict[str, Any] = dict(profile)

    if not profile.get("onboarded"):
        result["status"] = "not_onboarded"
        result["message"] = (
            "Profile not set up yet. Run onboard_traveler to set your home airports, "
            "passport, and preferences. This only needs to be done once."
        )
        result["onboarding_questions"] = _ONBOARDING_QUESTIONS
    else:
        result["status"] = "ready"
        airports = profile.get("home_airports") or []
        passports = profile.get("passports") or []
        trips = profile.get("past_trips") or []
        result["summary"] = (
            f"Welcome back, {profile.get('name') or 'traveler'}! "
            f"Home airports: {', '.join(airports) if airports else 'not set'}. "
            f"Passport(s): {', '.join(passports) if passports else 'not set'}. "
            f"Currency: {profile.get('home_currency', 'USD')}. "
            f"Trips logged: {len(trips)}."
        )

    return result


async def onboard_traveler(
    name: str | None = None,
    home_airports: str | None = None,
    passports: str | None = None,
    home_currency: str = "USD",
    travel_style: str | None = None,
    interests: str | None = None,
    dietary: str | None = None,
    preferred_cabin: str = "economy",
    visas_held: str | None = None,
    eta_held: str | None = None,
) -> dict:
    """Set up traveler profile. Run once — remembered forever.

    After onboarding, every tool call automatically uses home airport,
    passport, currency, and preferences without repeating them.

    Args:
        name: First name
        home_airports: Comma-separated IATA codes (e.g., "JFK,EWR,LGA")
        passports: Comma-separated ISO-2 codes (e.g., "US" or "US,IN")
        home_currency: Home currency code (e.g., "USD", "EUR")
        travel_style: budget, moderate, or luxury
        interests: Comma-separated (e.g., "food,history,beach")
        dietary: Comma-separated restrictions (e.g., "vegetarian,halal")
        preferred_cabin: economy, premium_economy, business, first
        visas_held: ISO-2 dest codes with currently valid visas (e.g., "IN,CN")
        eta_held: ETAs held (e.g., "ESTA (US),UK ETA")
    """
    from ..utils.profile_store import load_profile, save_profile

    def _split(s: str | None) -> list[str]:
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]

    profile = load_profile()
    if name:
        profile["name"] = name.strip()
    if home_airports:
        profile["home_airports"] = [x.upper() for x in _split(home_airports)]
    if passports:
        profile["passports"] = [x.upper() for x in _split(passports)]
    if home_currency:
        profile["home_currency"] = home_currency.upper()
    if travel_style:
        profile["travel_style"] = travel_style.lower()
    if interests:
        profile["interests"] = _split(interests)
    if dietary:
        profile["dietary"] = _split(dietary)
    if preferred_cabin:
        profile["preferred_cabin"] = preferred_cabin.lower()
    if visas_held:
        profile["visas_held"] = [x.upper() for x in _split(visas_held)]
    if eta_held:
        profile["eta_held"] = _split(eta_held)

    profile["onboarded"] = True
    save_profile(profile)

    airports = profile.get("home_airports") or []
    passports_list = profile.get("passports") or []
    return {
        "status": "onboarded",
        "message": (
            f"Welcome, {profile.get('name') or 'traveler'}! Profile saved. "
            "From now on I'll remember your home airport, passport, currency, "
            "and preferences automatically."
        ),
        "profile_summary": {
            "name": profile.get("name"),
            "home_airports": airports,
            "passports": passports_list,
            "home_currency": profile.get("home_currency"),
            "travel_style": profile.get("travel_style"),
            "interests": profile.get("interests"),
            "preferred_cabin": profile.get("preferred_cabin"),
            "visas_held": profile.get("visas_held"),
            "eta_held": profile.get("eta_held"),
        },
        "next_steps": [
            "Try: 'Find me flights to Tokyo next month' — I'll use your home airports automatically.",
            "Try: 'What countries can I visit visa-free?' — I'll use your passport.",
            "Try: 'Plan a 5-day trip to Paris' — I'll match your travel style.",
            "Try: 'Book a trip to Bali under $2000' — I'll pull flights, hotels, visa, weather in one go.",
        ],
    }


async def update_traveler_profile(
    name: str | None = None,
    home_airports: str | None = None,
    passports: str | None = None,
    home_currency: str | None = None,
    travel_style: str | None = None,
    interests: str | None = None,
    dietary: str | None = None,
    preferred_cabin: str | None = None,
    visas_held: str | None = None,
    eta_held: str | None = None,
    add_visa: str | None = None,
    add_trip_destination: str | None = None,
    add_trip_from: str | None = None,
    add_trip_to: str | None = None,
    add_trip_purpose: str = "tourism",
) -> dict:
    """Update one or more fields in the stored traveler profile.

    Pass only the fields you want to change. Use add_visa / add_trip_* to
    append without replacing the full list.

    Args:
        name: Update name
        home_airports: Replace home airports (comma-separated IATA)
        passports: Replace passports (comma-separated ISO-2)
        home_currency: Update home currency
        travel_style: budget, moderate, luxury
        interests: Replace interests (comma-separated)
        dietary: Replace dietary restrictions
        preferred_cabin: economy, premium_economy, business, first
        visas_held: Replace full visa list (comma-separated ISO-2 dest codes)
        eta_held: Replace ETA list
        add_visa: Append one ISO-2 destination code to visas_held
        add_trip_destination: Log a trip — city/country (e.g., "Tokyo, Japan")
        add_trip_from: Trip start date YYYY-MM-DD
        add_trip_to: Trip end date YYYY-MM-DD
        add_trip_purpose: tourism, business, family, other
    """
    from ..utils.profile_store import add_trip, load_profile, save_profile

    def _split(s: str | None) -> list[str]:
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x.strip()]

    profile = load_profile()
    changed: list[str] = []

    if name is not None:
        profile["name"] = name.strip()
        changed.append("name")
    if home_airports is not None:
        profile["home_airports"] = [x.upper() for x in _split(home_airports)]
        changed.append("home_airports")
    if passports is not None:
        profile["passports"] = [x.upper() for x in _split(passports)]
        changed.append("passports")
    if home_currency is not None:
        profile["home_currency"] = home_currency.upper()
        changed.append("home_currency")
    if travel_style is not None:
        profile["travel_style"] = travel_style.lower()
        changed.append("travel_style")
    if interests is not None:
        profile["interests"] = _split(interests)
        changed.append("interests")
    if dietary is not None:
        profile["dietary"] = _split(dietary)
        changed.append("dietary")
    if preferred_cabin is not None:
        profile["preferred_cabin"] = preferred_cabin.lower()
        changed.append("preferred_cabin")
    if visas_held is not None:
        profile["visas_held"] = [x.upper() for x in _split(visas_held)]
        changed.append("visas_held")
    if eta_held is not None:
        profile["eta_held"] = _split(eta_held)
        changed.append("eta_held")
    if add_visa:
        existing: list[str] = profile.get("visas_held") or []
        code = add_visa.upper().strip()
        if code not in existing:
            existing.append(code)
        profile["visas_held"] = existing
        changed.append(f"visas_held (added {code})")

    if add_trip_destination and add_trip_from and add_trip_to:
        save_profile(profile)
        add_trip(add_trip_destination, add_trip_from, add_trip_to, add_trip_purpose)
        return {
            "status": "updated",
            "changed": changed + [f"past_trips (added {add_trip_destination})"],
            "profile": load_profile(),
        }

    save_profile(profile)
    return {
        "status": "updated",
        "changed": changed,
        "profile": profile,
    }


async def get_trip_history(limit: int = 20) -> dict:
    """Get past trips logged in the traveler profile.

    Args:
        limit: Max trips to return (most recent first, max 50)
    """
    from ..utils.profile_store import load_profile

    profile = load_profile()
    trips: list[dict[str, Any]] = list(reversed(profile.get("past_trips") or []))
    countries = sorted({
        t.get("destination", "").split(",")[-1].strip()
        for t in trips if t.get("destination")
    })
    return {
        "traveler": profile.get("name") or "traveler",
        "total_trips_logged": len(trips),
        "trips": trips[:limit],
        "countries_visited": countries,
    }
