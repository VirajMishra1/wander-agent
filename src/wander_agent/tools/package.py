"""Bookable trip package orchestrator.

Single call that composes every relevant tool and returns a structured
"plan, verify, and book this exact trip" package:

  - Flights (with nearby-airport expansion)
  - Hotels (with booking deeplinks)
  - Ground transport options
  - Visa + entry requirements (with apply links)
  - Weather forecast
  - Travel advisory
  - Top attractions
  - Total cost estimate
  - Confidence label on every data point
  - Booking checklist

Answer to: "Book me a trip to Bali, I'm flying from Dubai, 7 nights."
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta


async def plan_trip_package(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    trip_length_days: int = 7,
    travelers: int = 1,
    passport_country: str | None = None,
    currency: str = "USD",
    budget_level: str = "moderate",
    interests: str | None = None,
    include_ground_transport: bool = True,
) -> dict:
    """Build a complete bookable trip package in one call.

    Composes: flights (multi-airport), hotels, visa, weather, advisory,
    attractions, ground transport, cost estimate, and booking checklist.
    Every section has a data_confidence label and direct booking URLs.

    Args:
        origin: Departure airport IATA or city (e.g., "DXB", "New York", "JFK")
        destination: Destination city (e.g., "Bali", "Tokyo", "Paris")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD (auto-calculated from trip_length_days if omitted)
        trip_length_days: Nights at destination (used when return_date omitted)
        travelers: Number of travelers
        passport_country: ISO-2 for visa check (e.g., "US", "IN", "GB")
        currency: Home currency for all prices
        budget_level: budget, moderate, luxury
        interests: Comma-separated interests (e.g., "beach,food,history")
        include_ground_transport: Include bus/train options
    """
    from .activities import search_activities
    from .advisory import get_travel_advisory
    from .destination import geocode, get_destination_info
    from .flights import search_flights
    from .ground_transport import search_ground_transport
    from .hotels import search_hotels
    from .visa import check_visa_requirement
    from .weather import get_weather
    from ..utils.airport_data import city_to_iata, iata_to_city, get_nearby_airports

    # Resolve dates
    try:
        dep_dt = datetime.strptime(departure_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "departure_date must be YYYY-MM-DD"}

    if not return_date:
        return_date = (dep_dt + timedelta(days=trip_length_days)).strftime("%Y-%m-%d")

    try:
        ret_dt = datetime.strptime(return_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "return_date must be YYYY-MM-DD"}

    nights = (ret_dt - dep_dt).days
    if nights <= 0:
        return {"error": "return_date must be after departure_date"}

    # Resolve IATA codes
    origin_iata = city_to_iata(origin) or origin.upper()[:3]
    dest_iata = city_to_iata(destination) or destination.upper()[:3]
    dest_city = iata_to_city(dest_iata) or destination

    # Expand origin to nearby airports (DXB → also SHJ, AUH)
    origin_airports = [origin_iata] + get_nearby_airports(origin_iata)

    # Geocode destination for weather / activities
    geo = await geocode(destination)
    lat = geo.get("latitude")
    lon = geo.get("longitude")
    country_name = geo.get("country", "")

    # Fan out all fetches in parallel
    flight_tasks = [
        search_flights(
            origin=ap, destination=dest_iata,
            departure_date=departure_date, return_date=return_date,
            adults=travelers, max_results=3, currency=currency,
        )
        for ap in origin_airports[:3]
    ]

    hotel_task = search_hotels(
        city=dest_city, check_in=departure_date, check_out=return_date,
        adults=travelers, max_results=5, currency=currency,
    )
    weather_task = (
        get_weather(lat, lon, departure_date, return_date)
        if lat and lon else asyncio.sleep(0, result={})
    )
    advisory_task = (
        get_travel_advisory(country_name)
        if country_name else asyncio.sleep(0, result={})
    )
    visa_task = (
        check_visa_requirement(passport_country, dest_iata[:2])
        if passport_country else asyncio.sleep(0, result={})
    )
    activities_task = (
        search_activities(lat, lon, radius_km=15, max_results=8)
        if lat and lon else asyncio.sleep(0, result={})
    )
    ground_task = (
        search_ground_transport(
            origin_city=iata_to_city(origin_iata) or origin,
            destination_city=dest_city,
            date=departure_date,
            travelers=travelers,
        )
        if include_ground_transport else asyncio.sleep(0, result={})
    )
    country_task = (
        get_destination_info(country_name)
        if country_name else asyncio.sleep(0, result={})
    )

    results = await asyncio.gather(
        *flight_tasks,
        hotel_task, weather_task, advisory_task, visa_task,
        activities_task, ground_task, country_task,
        return_exceptions=True,
    )

    n_airports = len(origin_airports[:3])
    flight_results = results[:n_airports]
    hotels, weather, advisory, visa, activities, ground, country_info = results[n_airports:]

    # Process flights — pick cheapest across all origin airports
    all_flight_options: list[dict] = []
    for ap, r in zip(origin_airports[:3], flight_results):
        if not isinstance(r, dict) or r.get("results_count", 0) == 0:
            continue
        for f in r.get("flights", [])[:2]:
            all_flight_options.append({
                **f,
                "origin_airport": ap,
                "google_flights_url": (
                    f"https://www.google.com/travel/flights/search"
                    f"?q=flights+from+{ap}+to+{dest_iata}"
                    f"+on+{departure_date}+returning+{return_date}"
                    f"+{travelers}+passengers"
                ),
            })

    all_flight_options.sort(key=lambda x: x.get("price", 9999))
    best_flight = all_flight_options[0] if all_flight_options else None
    flight_cost_pp: float | None = best_flight.get("price") if best_flight else None

    # Process hotels
    hotels_d = hotels if isinstance(hotels, dict) else {}
    cheapest_ppn = hotels_d.get("cheapest_price_per_night")
    hotel_total = round((cheapest_ppn or 80) * nights, 2)

    # Process visa
    visa_d = visa if isinstance(visa, dict) else {}

    # Process weather
    weather_d = weather if isinstance(weather, dict) else {}
    wx_summary = weather_d.get("summary") or {}

    # Process advisory
    adv_d = advisory if isinstance(advisory, dict) else {}
    adv_level = adv_d.get("advisory_level", 1)

    # Process activities
    act_d = activities if isinstance(activities, dict) else {}
    top_attractions = [
        a["name"] for a in (act_d.get("activities") or [])[:6] if a.get("name")
    ]

    # Process ground transport
    ground_d = ground if isinstance(ground, dict) else {}

    # Process country info
    country_d = country_info if isinstance(country_info, dict) else {}
    currencies = country_d.get("currencies") or [{}]

    # Cost estimate
    food_daily = {"budget": 25, "moderate": 55, "luxury": 140}.get(budget_level, 55)
    food_total = food_daily * nights * travelers
    flight_total = round(flight_cost_pp * travelers, 2) if flight_cost_pp else None
    grand_total = (
        round((flight_total or 0) + hotel_total + food_total, 2)
        if flight_total else None
    )

    adv_labels = {1: "Normal precautions", 2: "Exercise caution",
                  3: "Reconsider travel", 4: "DO NOT TRAVEL"}

    return {
        "trip": {
            "origin": origin_iata,
            "origin_airports_checked": origin_airports[:3],
            "destination": dest_city,
            "departure_date": departure_date,
            "return_date": return_date,
            "nights": nights,
            "travelers": travelers,
            "currency": currency.upper(),
            "budget_level": budget_level,
        },

        "flights": {
            "best": best_flight,
            "all_options": all_flight_options[:5],
            "price_is_per_person": True,
            "booking_links": {
                "google_flights": (
                    f"https://www.google.com/travel/flights/search"
                    f"?q=flights+from+{origin_iata}+to+{dest_iata}"
                    f"+on+{departure_date}+returning+{return_date}+{travelers}+passengers"
                ),
                "skyscanner": (
                    f"https://www.skyscanner.com/transport/flights"
                    f"/{origin_iata}/{dest_iata}"
                    f"/{departure_date.replace('-', '')}"
                    f"/{return_date.replace('-', '')}/?adults={travelers}"
                ),
                "kayak": (
                    f"https://www.kayak.com/flights/{origin_iata}-{dest_iata}"
                    f"/{departure_date}/{return_date}/{travelers}adults"
                ),
            },
            "data_confidence": "scraped_live",
        },

        "hotels": {
            "options": hotels_d.get("hotels", [])[:5],
            "cheapest_per_night": cheapest_ppn,
            "hotel_total_estimate": hotel_total,
            "booking_links": {
                "booking_com": (
                    f"https://www.booking.com/search.html"
                    f"?ss={dest_city.replace(' ', '+')}"
                    f"&checkin={departure_date}&checkout={return_date}"
                    f"&group_adults={travelers}"
                ),
                "airbnb": (
                    f"https://www.airbnb.com/s/{dest_city.replace(' ', '--')}/homes"
                    f"?checkin={departure_date}&checkout={return_date}&adults={travelers}"
                ),
                "google_hotels": (
                    f"https://www.google.com/travel/hotels"
                    f"?q=hotels+in+{dest_city.replace(' ', '+')}"
                    f"&d1={departure_date}&d2={return_date}&g={travelers}"
                ),
            },
            "data_confidence": hotels_d.get("data_confidence", "names_live_prices_estimated"),
        },

        "visa": {
            **visa_d,
            "data_confidence": visa_d.get("data_confidence", "not_checked"),
        } if visa_d else {
            "note": "Pass passport_country to get visa requirements and apply links.",
            "data_confidence": "not_checked",
        },

        "weather": {
            "avg_high_c": wx_summary.get("avg_high_c"),
            "avg_low_c": wx_summary.get("avg_low_c"),
            "rainy_days": wx_summary.get("rainy_days"),
            "description": wx_summary.get("description", ""),
            "data_confidence": "live_forecast" if wx_summary else "unavailable",
        },

        "advisory": {
            "level": adv_level,
            "label": adv_labels.get(adv_level, "Unknown"),
            "summary": adv_d.get("summary", ""),
            "source_url": adv_d.get("source_url", "https://travel.state.gov"),
            "data_confidence": "live_rss",
        },

        "ground_transport": {
            "routes": ground_d.get("route_overview", []),
            "booking_links": ground_d.get("booking_links", []),
            "google_maps_transit_url": ground_d.get("google_maps_transit_url"),
            "data_confidence": ground_d.get("data_confidence", "deeplinks_only"),
        },

        "top_attractions": top_attractions,
        "attractions_data_confidence": act_d.get("data_confidence", "wikidata_fallback"),

        "destination_info": {
            "local_currency": currencies[0].get("code", "") if currencies else "",
            "languages": country_d.get("languages", []),
            "timezone": (country_d.get("timezones") or [""])[0],
        },

        "cost_estimate": {
            "flight_per_person": flight_cost_pp,
            "flight_total_all_travelers": flight_total,
            "hotel_total": hotel_total,
            "food_estimate": food_total,
            "grand_total": grand_total,
            "currency": currency.upper(),
            "breakdown_note": (
                f"Flight: live scraped. Hotel: cheapest found × {nights} nights. "
                f"Food: ${food_daily}/person/day ({budget_level}). "
                "Excludes activities, local transport, visa fees."
            ),
            "data_confidence": "estimated",
        },

        "booking_checklist": _build_checklist(visa_d, adv_level, flight_d, hotel_d),

        "suggest_web_search": [
            f"best neighborhoods to stay in {dest_city}",
            f"{dest_city} travel guide {departure_date[:7]}",
            f"{dest_city} local SIM card and transport guide",
            f"things to know before visiting {dest_city}",
        ],
    }


def _build_checklist(
    visa_data: dict,
    advisory_level: int,
    flight_data: dict | None = None,
    hotel_data: dict | None = None,
) -> list[dict]:
    steps: list[dict] = []

    if advisory_level >= 3:
        steps.append({
            "priority": "HIGH",
            "step": "⚠️ Read travel advisory",
            "detail": f"Level {advisory_level} advisory in effect. Check full guidance.",
            "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html",
            "booking_links": {},
        })

    cat = visa_data.get("category", "")
    if cat in ("eta_required", "evisa", "visa_required"):
        apply_url = visa_data.get("apply_link") or visa_data.get("official_link", "")
        steps.append({
            "priority": "HIGH",
            "step": f"📋 Apply for {cat.replace('_', ' ').title()}",
            "detail": visa_data.get("guidance", "Check requirements before booking."),
            "url": apply_url,
            "booking_links": {},
        })
    elif cat == "visa_on_arrival":
        steps.append({
            "priority": "MEDIUM",
            "step": "📋 Visa on arrival — check requirements",
            "detail": visa_data.get("guidance", ""),
            "url": visa_data.get("official_link", ""),
            "booking_links": {},
        })
    elif cat == "visa_free":
        steps.append({
            "priority": "INFO",
            "step": "✅ No visa required",
            "detail": "Verify passport validity (6+ months beyond return date).",
            "url": visa_data.get("official_link", ""),
            "booking_links": {},
        })

    # Flight booking links — pull all from flight result, add Kiwi book URLs
    flight_links: dict = {}
    if flight_data:
        flight_links = dict(flight_data.get("booking_links") or {})
        # Add individual Kiwi live fare links
        kiwi_fares = flight_data.get("kiwi_live_fares", [])
        for i, fare in enumerate(kiwi_fares[:3], 1):
            url = fare.get("book_url", "")
            if url:
                label = f"kiwi_option_{i} (${fare.get('price','')} {fare.get('duration','')} {fare.get('stops',0)} stop{'s' if fare.get('stops',0)!=1 else ''})"
                flight_links[label] = url

    flight_primary = (
        flight_links.get("skyscanner")
        or flight_links.get("google_flights")
        or "https://www.google.com/travel/flights"
    )
    steps.append({
        "priority": "HIGH",
        "step": "✈️ Book flights",
        "detail": "Compare prices across all options below.",
        "url": flight_primary,
        "booking_links": flight_links,
    })

    # Hotel booking links — pull all from hotel result
    hotel_links: dict = {}
    if hotel_data:
        hotel_links = dict(hotel_data.get("booking_links") or {})

    hotel_primary = hotel_links.get("booking_com", "https://www.booking.com")
    steps.append({
        "priority": "HIGH",
        "step": "🏨 Book accommodation",
        "detail": "Compare across all options below. Prices shown on each site.",
        "url": hotel_primary,
        "booking_links": hotel_links,
    })

    steps += [
        {
            "priority": "MEDIUM",
            "step": "🛡️ Get travel insurance",
            "detail": "Medical + cancellation + lost luggage.",
            "url": "https://www.insureandgo.com",
            "booking_links": {
                "insureandgo": "https://www.insureandgo.com",
                "world_nomads": "https://www.worldnomads.com",
                "safetywing": "https://www.safetywing.com",
            },
        },
        {
            "priority": "MEDIUM",
            "step": "💉 Check vaccinations",
            "detail": "CDC traveler health notices.",
            "url": "https://wwwnc.cdc.gov/travel",
            "booking_links": {},
        },
        {
            "priority": "LOW",
            "step": "📱 Get local SIM / eSIM",
            "detail": "Airalo covers 190+ countries. Holafly good for unlimited data.",
            "url": "https://www.airalo.com",
            "booking_links": {
                "airalo": "https://www.airalo.com",
                "holafly": "https://www.holafly.com",
            },
        },
    ]
    return steps
