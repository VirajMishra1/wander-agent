"""Itinerary planning - builds structured multi-day travel plans."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


async def plan_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: str | None = None,
    budget_level: str = "moderate",
    travelers: int = 1,
    include_weather: bool = True,
    include_activities: bool = True,
) -> dict:
    """Generate a structured day-by-day travel itinerary with real data.

    Fetches weather, activities, destination info, and currency data to build
    a data-backed itinerary. The AI should use this structured data to create
    a narrative itinerary for the user.

    Args:
        destination: City and country (e.g., "Paris, France", "Tokyo, Japan")
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        interests: Comma-separated interests (e.g., "food,history,nature,nightlife,art")
        budget_level: Budget level: budget, moderate, luxury
        travelers: Number of travelers
        include_weather: Fetch weather forecast for the dates
        include_activities: Fetch nearby activities and attractions
    """
    from .activities import search_activities
    from .currency import convert_currency
    from .destination import geocode, get_destination_info
    from .weather import get_weather

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    num_days = (end - start).days
    if num_days <= 0:
        return {"error": "end_date must be after start_date"}

    # Step 1: Geocode destination
    geo = await geocode(destination)
    if geo.get("error"):
        return {"error": f"Could not find '{destination}'. Try 'City, Country' format.", "detail": geo["error"]}

    lat, lon = geo["latitude"], geo["longitude"]
    country = geo.get("country", "")

    # Step 2: Fetch data in parallel
    tasks = {}

    if include_weather:
        tasks["weather"] = get_weather(lat, lon, start_date, end_date)

    if include_activities:
        interest_list = [i.strip() for i in (interests or "").split(",") if i.strip()]
        if interest_list:
            for interest in interest_list[:3]:
                tasks[f"activities_{interest}"] = search_activities(lat, lon, radius_km=15, category=interest, max_results=10)
        else:
            tasks["activities_all"] = search_activities(lat, lon, radius_km=15, max_results=20)

    if country:
        tasks["country_info"] = get_destination_info(country)

    results = {}
    gathered = await asyncio.gather(
        *[tasks[k] for k in tasks],
        return_exceptions=True,
    )
    for key, result in zip(tasks.keys(), gathered):
        if not isinstance(result, Exception):
            results[key] = result

    # Step 3: Build structured itinerary data
    all_activities = []
    for key, val in results.items():
        if key.startswith("activities") and val.get("activities"):
            all_activities.extend(val["activities"])

    # Deduplicate by name
    seen = set()
    unique_activities = []
    for a in all_activities:
        if a["name"] and a["name"] not in seen:
            seen.add(a["name"])
            unique_activities.append(a)

    # Distribute activities across days
    activities_per_day = max(len(unique_activities) // max(num_days, 1), 2)
    days = []
    activity_idx = 0

    for day_num in range(num_days):
        current_date = start + timedelta(days=day_num)
        day_activities = unique_activities[activity_idx:activity_idx + activities_per_day]
        activity_idx += activities_per_day

        weather_for_day = None
        if results.get("weather", {}).get("daily_forecasts"):
            forecasts = results["weather"]["daily_forecasts"]
            if day_num < len(forecasts):
                weather_for_day = forecasts[day_num]

        days.append({
            "day": day_num + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "weather": weather_for_day,
            "suggested_activities": [
                {
                    "name": a["name"],
                    "type": a.get("kind", ""),
                    "description": a.get("description", ""),
                    "distance_from_center_m": a.get("distance_m"),
                }
                for a in day_activities
            ],
        })

    # Country info summary
    country_info = results.get("country_info", {})
    currency_info = country_info.get("currencies", [{}])[0] if country_info.get("currencies") else {}

    return {
        "destination": destination,
        "country": country,
        "coordinates": {"latitude": lat, "longitude": lon},
        "trip_dates": {"start": start_date, "end": end_date, "nights": num_days},
        "travelers": travelers,
        "budget_level": budget_level,
        "interests": interests,
        "country_info": {
            "languages": country_info.get("languages", []),
            "currency": currency_info,
            "timezone": country_info.get("timezones", []),
            "calling_code": country_info.get("calling_code", ""),
            "drives_on": country_info.get("drives_on", ""),
        },
        "weather_summary": results.get("weather", {}).get("summary"),
        "daily_plan": days,
        "total_activities_found": len(unique_activities),
        "note": "Structured data for AI to build narrative itinerary. Activities are real.",
        "suggest_web_search": [
            f"best restaurants {destination} {(interests or 'food').split(',')[0].strip()} reddit",
            f"{destination} {start_date[:7]} festivals events",
            f"{destination} insider tips not tourist traps",
            f"{destination} neighborhoods to stay travel blog",
            f"things to know before visiting {destination} 2026",
        ],
    }
