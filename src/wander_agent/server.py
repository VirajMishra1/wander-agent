"""Wander Agent - MCP Server entry point.

20+ tools for AI-powered travel: inspiration mode (no destination yet) and
planning mode (have destination). Plus mind-blow differentiators: travel
advisories, local events, cost-of-living, multi-objective destination scoring.

Install in Claude Desktop:
  uv run mcp install src/wander_agent/server.py
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

# Persona A: Inspiration (no destination yet)
from .tools.inspiration import (
    cheap_anywhere_from,
    compare_destinations,
    find_destinations_by_budget,
)

# Persona B: Planning (have destination)
from .tools.flights import search_flights
from .tools.hotels import search_hotels
from .tools.itinerary import plan_itinerary
from .tools.budget import optimize_budget

# Enrichment (both personas)
from .tools.activities import search_activities
from .tools.currency import convert_currency, get_exchange_rates
from .tools.destination import geocode, get_destination_info
from .tools.weather import get_weather

# Mind-blow differentiators
from .tools.advisory import get_travel_advisory, list_advisories_by_level
from .tools.events import get_local_events
from .tools.cost_of_living import get_cost_of_living
from .tools.score import score_destinations
from .tools.seasons import best_month_to_visit

# Verification
from .tools.verify import verify_flight_route, verify_place

# Viral killers
from .tools.skiplagged import find_skiplagged_fares
from .tools.meetup import multi_origin_meetup
from .tools.aurora import find_aurora_destinations
from .tools.mistake_fares import find_mistake_fares
from .tools.visa import check_visa_requirement, visa_free_destinations
from .tools.restaurants import search_restaurants_bars

# New utility tools
from .tools.packing import generate_packing_list
from .tools.places import find_places
from .tools.jetlag import calculate_jet_lag
from .tools.phrasebook import get_language_phrasebook
from .tools.stopover import get_stopover_guide
from .tools.travel_news import get_travel_news
from .tools.health import check_travel_health

# Traveler profile (persistent memory)
from .tools.profile import (
    get_traveler_profile,
    onboard_traveler,
    update_traveler_profile,
    get_trip_history,
)

# Ground transport + bookable trip package
from .tools.ground_transport import search_ground_transport
from .tools.package import plan_trip_package


@dataclass
class AppContext:
    pass


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    from .utils.http import close_client
    try:
        yield AppContext()
    finally:
        await close_client()


mcp = FastMCP(
    "Wander Agent",
    instructions=(
        "You are a personal travel agent with memory. Act like a real travel agent "
        "who knows the traveler personally.\n\n"

        "== FIRST INTERACTION ==\n"
        "ALWAYS call get_traveler_profile first. If onboarded=False, greet the user "
        "warmly and walk them through onboard_traveler step by step — ask their name, "
        "home airports, passport(s), currency, travel style, interests, dietary "
        "restrictions, and any visas/ETAs they already hold. Then save with "
        "onboard_traveler. From that point on, use their profile automatically.\n\n"

        "== RETURNING USERS ==\n"
        "Call get_traveler_profile at session start. Use their home_airports, "
        "passports, home_currency, and interests automatically without asking. "
        "Reference their past trips when relevant. Address them by name.\n\n"

        "== TOOL USAGE PHILOSOPHY ==\n"
        "NEVER answer a travel question with just one tool. Compose multiple tools:\n"
        "- 'Book a trip to Tokyo' → plan_trip_package (flights+hotels+visa+weather+advisory+transport in one call)\n"
        "- 'Where should I go?' → cheap_anywhere_from + score_destinations + check_visa_requirement\n"
        "- 'Plan my itinerary' → plan_itinerary + get_local_events + get_weather + verify_place\n"
        "- 'Is X safe?' → get_travel_advisory + check_visa_requirement + get_weather\n"
        "- 'Cheapest flight' → search_flights with nearby airports + find_skiplagged_fares\n"
        "Always run suggest_web_search queries from tool outputs.\n\n"

        "== NEARBY AIRPORTS ==\n"
        "For flight searches, always consider nearby airports. DXB → also SHJ, AUH. "
        "JFK → also EWR, LGA. LHR → also LGW, STN. London-area, NYC-area, Dubai-area "
        "users should see prices from all local airports.\n\n"

        "== GROUND TRANSPORT ==\n"
        "For any trip, always call search_ground_transport for the origin→destination "
        "leg. Buses and trains are often cheaper and more convenient than flights for "
        "distances under 500km. Present bus/train links alongside flight options.\n\n"

        "== CONFIDENCE LABELS ==\n"
        "Every data point has a data_confidence field. Surface these to the user:\n"
        "- scraped_live: real-time Google Flights scrape\n"
        "- live_rss: live government feed\n"
        "- live_forecast: Open-Meteo live weather\n"
        "- curated_snapshot: our dataset (verify with official_link before booking)\n"
        "- estimated: calculated estimate\n"
        "- deeplink: link to live prices on the service's own site\n"
        "- wikidata_fallback: Wikidata attractions (no OpenTripMap key configured)\n\n"

        "== RESPONSE FORMAT ==\n"
        "Structure every travel answer as:\n"
        "1. ✈️ Flights — cheapest option with price, airline, duration, booking link\n"
        "2. 🏨 Hotels — cheapest option per night + Booking.com / Airbnb / Google Hotels links\n"
        "3. 🚌 Ground transport — bus/train options with booking links\n"
        "4. 📋 Visa — category (visa-free / e-visa / on-arrival) + apply link\n"
        "5. 🌤️ Weather — avg temp and rainy days for travel dates\n"
        "6. ⚠️ Safety — advisory level and any warnings\n"
        "7. 🏛️ Top attractions — 4-6 real verified places\n"
        "8. 💰 Total cost estimate — flight + hotel + food breakdown\n"
        "9. ✅ Booking checklist — ordered steps to actually book this trip\n\n"

        "== BOOKING LINKS ==\n"
        "Always surface direct booking URLs. Use the booking_links fields in tool "
        "outputs. Present them as clickable: '[Book on Skyscanner](url)'. "
        "For visas, always include the official apply_link. "
        "Never just say 'search Booking.com' — give the filled-in URL.\n\n"

        "== WHEN TO USE WEB SEARCH ==\n"
        "- Current mistake fares / flash deals\n"
        "- Recent destination news (strikes, closures, protests)\n"
        "- Restaurant reviews and specific recommendations\n"
        "- Local festivals not in Ticketmaster\n"
        "- Visa policy changes after May 2026\n"
        "Always run the suggest_web_search queries from tool outputs."
    ),
    lifespan=app_lifespan,
)


# ============================================================
# PERSONA A: INSPIRATION MODE (no destination yet)
# ============================================================

@mcp.tool()
async def tool_find_destinations_by_budget(
    origin: str,
    total_budget: float,
    trip_length_days: int = 7,
    departure_month: str | None = None,
    travelers: int = 1,
    interests: str | None = None,
    visa_free_only: bool = False,
    passport_country: str | None = None,
    currency: str = "USD",
    max_results: int = 10,
) -> dict:
    """INSPIRATION: Find destinations achievable within a total budget.

    "I have $1500, where can I go?" - returns ranked destinations under budget
    with flight + hotel costs calculated.

    Args:
        origin: Departure airport IATA code (e.g., "JFK")
        total_budget: Total budget for trip
        trip_length_days: Number of nights
        departure_month: YYYY-MM (e.g., "2026-08") or omit for any
        travelers: Number of travelers
        interests: Comma-separated (e.g., "beach,food,history")
        visa_free_only: Only visa-free destinations (requires passport_country)
        passport_country: ISO 2-letter code (e.g., "US")
        currency: USD, EUR, etc.
        max_results: Max destinations to return
    """
    return await find_destinations_by_budget(
        origin, total_budget, trip_length_days, departure_month, travelers,
        interests, visa_free_only, passport_country, currency, max_results,
    )


@mcp.tool()
async def tool_cheap_anywhere_from(
    origin: str,
    month: str | None = None,
    max_price: float | None = None,
    max_results: int = 20,
    currency: str = "USD",
    regions: str | None = None,
    round_trip_days: int | None = None,
) -> dict:
    """INSPIRATION: Find cheapest destinations from origin airport.

    "Show me cheap flights from NYC anywhere in March" - returns ranked
    destinations by price. Set round_trip_days for realistic round-trip budgeting.

    Args:
        origin: IATA airport code (e.g., "JFK")
        month: YYYY-MM constraint (optional)
        max_price: Filter out above this price (per-person)
        max_results: Max destinations
        currency: USD, EUR, etc.
        regions: Comma-separated (europe, asia, americas, oceania, africa, middle_east)
        round_trip_days: Days at destination for round-trip price (omit for one-way)
    """
    return await cheap_anywhere_from(origin, month, max_price, max_results, currency, regions, round_trip_days)


@mcp.tool()
async def tool_compare_destinations(
    origin: str,
    destinations: str,
    departure_date: str,
    return_date: str,
    travelers: int = 1,
    currency: str = "USD",
) -> dict:
    """INSPIRATION: Compare multiple destinations side-by-side for same dates.

    "Paris vs Rome vs Barcelona for next month" - returns flight + hotel costs
    for each, ranked by total cost.

    Args:
        origin: Departure airport IATA code
        destinations: Comma-separated (e.g., "CDG,FCO,BCN" or "Paris,Rome,Barcelona")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        travelers: Number of travelers
        currency: USD, EUR, etc.
    """
    return await compare_destinations(origin, destinations, departure_date, return_date, travelers, currency)


# ============================================================
# PERSONA B: PLANNING MODE (have destination)
# ============================================================

@mcp.tool()
async def tool_search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    max_results: int = 5,
    currency: str = "USD",
    nonstop_only: bool = False,
) -> dict:
    """PLANNING: Search flights between two airports.

    Uses Google Flights data through fast_flights. No API key required.

    Args:
        origin: IATA airport code (e.g., "JFK", "LAX", "LHR")
        destination: IATA airport code (e.g., "CDG", "NRT", "SYD")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD (omit for one-way)
        adults: 1-9
        max_results: Max results
        currency: USD, EUR, GBP, etc.
        nonstop_only: Nonstop only
    """
    return await search_flights(origin, destination, departure_date, return_date,
                                 adults, max_results, currency, nonstop_only)


@mcp.tool()
async def tool_search_hotels(
    city: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    rooms: int = 1,
    max_results: int = 10,
    currency: str = "USD",
    price_range: str | None = None,
    ratings: str | None = None,
) -> dict:
    """PLANNING: Search hotels in a city.

    Uses Google Hotels names through fast_hotels plus booking deeplinks.
    Args:
        city: City name (e.g., "Paris", "Tokyo") - NOT IATA code
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: Number of guests
        rooms: Number of rooms
        max_results: Max results
        currency: USD, EUR, etc.
        price_range: "100-300"
        ratings: "3,4,5"
    """
    return await search_hotels(city, check_in, check_out, adults, rooms,
                                max_results, currency, price_range, ratings)


@mcp.tool()
async def tool_plan_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: str | None = None,
    budget_level: str = "moderate",
    travelers: int = 1,
    include_weather: bool = True,
    include_activities: bool = True,
) -> dict:
    """PLANNING: Generate data-backed day-by-day itinerary with real activities and weather.

    Args:
        destination: City and country (e.g., "Paris, France")
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        interests: Comma-separated (e.g., "food,history,nature,art")
        budget_level: budget, moderate, luxury
        travelers: Number of travelers
        include_weather: Include forecast
        include_activities: Include nearby attractions
    """
    return await plan_itinerary(destination, start_date, end_date, interests,
                                 budget_level, travelers, include_weather, include_activities)


@mcp.tool()
async def tool_optimize_budget(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    adults: int = 1,
    currency: str = "USD",
    flexible_dates: bool = True,
    flexibility_days: int = 3,
) -> dict:
    """PLANNING: Find cheapest flight + hotel combo with flexible dates.

    Args:
        origin: Departure airport IATA code
        destination: Arrival airport IATA code
        departure_date: Preferred YYYY-MM-DD
        return_date: Preferred YYYY-MM-DD
        adults: Travelers
        currency: USD, EUR, etc.
        flexible_dates: Search nearby dates
        flexibility_days: Days to flex (1-7)
    """
    return await optimize_budget(origin, destination, departure_date, return_date,
                                  adults, currency, flexible_dates, flexibility_days)


# ============================================================
# MIND-BLOW DIFFERENTIATORS
# ============================================================

@mcp.tool()
async def tool_get_travel_advisory(country: str) -> dict:
    """Official US State Department travel advisory for a country.

    Returns advisory level (1=safe, 4=do not travel), summary, and link.
    No API key. Cached 60 min.

    Args:
        country: Country name in English (e.g., "Japan", "Egypt") or ISO code
    """
    return await get_travel_advisory(country)


@mcp.tool()
async def tool_list_advisories_by_level(min_level: int = 3) -> dict:
    """List countries currently at advisory level X or above.

    "What countries should I avoid right now?"

    Args:
        min_level: 1-4. Default 3 = Reconsider Travel. 4 = Do Not Travel.
    """
    return await list_advisories_by_level(min_level)


@mcp.tool()
async def tool_get_local_events(
    city: str,
    start_date: str,
    end_date: str,
    classification: str | None = None,
    keyword: str | None = None,
    max_results: int = 20,
) -> dict:
    """DIFFERENTIATOR: Find concerts, shows, sports during your trip dates.

    "Coldplay is in Paris while you're there." Uses Ticketmaster Discovery.

    Args:
        city: City name
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        classification: music, sports, arts, family, film, miscellaneous
        keyword: Artist, team, or show name
        max_results: Max events
    """
    return await get_local_events(city, start_date, end_date, classification, keyword, max_results)


@mcp.tool()
async def tool_get_cost_of_living(city: str, home_currency: str = "USD") -> dict:
    """DIFFERENTIATOR: Cost-of-living index + quality of life scores for a city.

    "Your $100/day = lavish in Lisbon, broke in London." Free, no auth.
    Covers ~270 cities globally with detailed quality scores.

    Args:
        city: City name (e.g., "Lisbon", "Tokyo", "San Francisco")
        home_currency: Your home currency (USD, EUR, etc.)
    """
    return await get_cost_of_living(city, home_currency)


@mcp.tool()
async def tool_score_destinations(
    destinations: str,
    travel_start: str,
    travel_end: str,
    weights: str = "cost:3,weather:3,safety:2,events:1,quality_of_life:1",
    weather_pref: str = "warm_dry",
    origin: str | None = None,
) -> dict:
    """DIFFERENTIATOR: Multi-objective destination ranking.

    Scores destinations on cost + weather + safety + events + quality of life
    simultaneously. The killer "where should I actually go?" tool.

    Args:
        destinations: Comma-separated (e.g., "Paris,Rome,Barcelona,Tokyo")
        travel_start: YYYY-MM-DD
        travel_end: YYYY-MM-DD
        weights: key:weight pairs (e.g., "cost:3,weather:2")
        weather_pref: warm_dry, cool_dry, warm_any, snow, shoulder_season
        origin: Optional origin airport
    """
    return await score_destinations(destinations, travel_start, travel_end, weights, weather_pref, origin)


@mcp.tool()
async def tool_best_month_to_visit(
    latitude: float,
    longitude: float,
    preferences: str = "warm_dry",
) -> dict:
    """DIFFERENTIATOR: Best month to visit based on 5 years of climate data.

    "When is Bali at its best?" Uses Open-Meteo historical archive. No auth.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        preferences: warm_dry, cool_dry, warm_any, snow, shoulder_season
    """
    return await best_month_to_visit(latitude, longitude, preferences)


# ============================================================
# ENRICHMENT (used by both modes)
# ============================================================

@mcp.tool()
async def tool_get_weather(
    latitude: float, longitude: float, start_date: str, end_date: str,
) -> dict:
    """Get weather forecast for travel dates. No auth required.

    Args:
        latitude: Latitude
        longitude: Longitude
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
    """
    return await get_weather(latitude, longitude, start_date, end_date)


@mcp.tool()
async def tool_convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert between currencies with live rates. No auth required.

    Args:
        amount: Amount to convert
        from_currency: Source currency (e.g., "USD")
        to_currency: Target currency (e.g., "EUR")
    """
    return await convert_currency(amount, from_currency, to_currency)


@mcp.tool()
async def tool_get_exchange_rates(base_currency: str, target_currencies: str | None = None) -> dict:
    """Get exchange rates. No auth required.

    Args:
        base_currency: Base (e.g., "USD")
        target_currencies: Comma-separated targets or omit for all
    """
    return await get_exchange_rates(base_currency, target_currencies)


@mcp.tool()
async def tool_search_activities(
    latitude: float, longitude: float, radius_km: int = 10,
    category: str | None = None, max_results: int = 15,
) -> dict:
    """Search activities and attractions near a location.

    Args:
        latitude: Latitude
        longitude: Longitude
        radius_km: 1-50
        category: culture, nature, food, shopping, nightlife, architecture, historic, museums, religion, sport
        max_results: 1-50
    """
    return await search_activities(latitude, longitude, radius_km, category, max_results)


@mcp.tool()
async def tool_get_destination_info(country_name: str) -> dict:
    """Essential country info (currency, language, timezone). No auth required.

    Args:
        country_name: Country name (e.g., "Japan")
    """
    return await get_destination_info(country_name)


@mcp.tool()
async def tool_geocode(place_name: str) -> dict:
    """City or place -> coordinates. No auth required.

    Args:
        place_name: City or place (e.g., "Paris, France")
    """
    return await geocode(place_name)


# ============================================================
# VERIFICATION (anti-hallucination)
# ============================================================

@mcp.tool()
async def tool_verify_place(
    place_name: str, city: str, expected_type: str | None = None,
) -> dict:
    """Verify a place exists. Cross-checks OSM + Foursquare + OpenTripMap.

    Catches AI hallucinations before they reach the user.

    Args:
        place_name: Place name (e.g., "Eiffel Tower")
        city: City (e.g., "Paris")
        expected_type: restaurant, attraction, hotel, museum, park
    """
    return await verify_place(place_name, city, expected_type)


@mcp.tool()
async def tool_verify_flight_route(origin: str, destination: str) -> dict:
    """Verify a flight route exists between two airports.

    Args:
        origin: IATA code
        destination: IATA code
    """
    return await verify_flight_route(origin, destination)


# ============================================================
# VIRAL KILLERS — features no other OTA has
# ============================================================

@mcp.tool()
async def tool_find_skiplagged_fares(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    max_results: int = 10,
) -> dict:
    """KILLER: Find hidden-city ticketing fares (cheaper than direct).

    Buy NYC->Mexico via Houston, get off in Houston, save 60%. Skyscanner
    and Kayak are CONTRACTUALLY FORBIDDEN from showing these. We pull
    them direct from Skiplagged.

    CAVEATS: Carry-on only. One-way only. No frequent flyer credit.
    Tool returns warnings.

    Args:
        origin: IATA code (e.g., "JFK")
        destination: IATA code (e.g., "LAX")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD (compare round-trip; book separately)
        max_results: max fares to return
    """
    return await find_skiplagged_fares(origin, destination, departure_date, return_date, max_results)


@mcp.tool()
async def tool_multi_origin_meetup(
    origins: str,
    departure_date: str,
    return_date: str,
    max_results: int = 10,
    currency: str = "USD",
    regions: str | None = None,
) -> dict:
    """KILLER: Find cheapest meeting point for travelers from N different cities.

    "3 friends in SF, London, Tokyo - cheapest weekend they can all meet."
    No OTA does this. Math is combinatorial — we loop curated destinations
    and sum round-trip costs per traveler.

    Args:
        origins: Comma-separated IATA codes (e.g., "JFK,LHR,NRT")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        max_results: max destinations to return
        currency: USD, EUR, etc.
        regions: limit candidates (e.g., "europe,asia")
    """
    return await multi_origin_meetup(origins, departure_date, return_date, max_results, currency, regions)


@mcp.tool()
async def tool_find_aurora_destinations(
    origin: str,
    max_budget: float = 1500.0,
    days_ahead_min: int = 7,
    days_ahead_max: int = 60,
    currency: str = "USD",
    max_results: int = 8,
) -> dict:
    """KILLER: Reverse search - "where to see northern lights cheapest, next 60 days?"

    Combines NOAA KP-index forecast + aurora-zone airports + flight prices.
    Returns ranked destinations with aurora visibility scores.

    Args:
        origin: Departure IATA code
        max_budget: Max flight budget
        days_ahead_min: Earliest departure (days from now)
        days_ahead_max: Latest departure
        currency: USD, EUR, etc.
        max_results: max destinations
    """
    return await find_aurora_destinations(origin, max_budget, days_ahead_min, days_ahead_max, currency, max_results)


@mcp.tool()
async def tool_find_mistake_fares(
    origin: str | None = None,
    days_lookback: int = 14,
    max_results: int = 20,
) -> dict:
    """KILLER: Recent mistake fares + deal alerts from Secret Flying + Flight Deal RSS.

    The signal Going.com charges $49/yr for, free.

    Args:
        origin: City name filter (e.g., "New York") or omit for all
        days_lookback: Only posts from last N days
        max_results: max deals
    """
    return await find_mistake_fares(origin, days_lookback, max_results)


@mcp.tool()
async def tool_check_visa_requirement(
    passport_country: str,
    destination_country: str,
) -> dict:
    """KILLER: Check visa requirements (counters viral AI-fail ESTA incidents).

    Returns category (visa_free, eta_required, visa_on_arrival, evisa,
    visa_required) plus guidance. Direct response to the Mery Caldass
    incident where ChatGPT told a traveler she didn't need ESTA -
    she got denied boarding (millions of views).

    Args:
        passport_country: ISO 2-letter (e.g., "US", "GB", "IN")
        destination_country: ISO 2-letter (e.g., "JP", "TH")
    """
    return await check_visa_requirement(passport_country, destination_country)


@mcp.tool()
async def tool_visa_free_destinations(
    passport_country: str,
    include_categories: str = "visa_free,visa_on_arrival,evisa,eta_required",
) -> dict:
    """KILLER: All destinations a passport can enter without a traditional visa.

    "I'm Indian passport, show every country I can fly to with e-visa or visa-on-arrival."

    Args:
        passport_country: ISO 2-letter code
        include_categories: Comma-separated category filter
    """
    return await visa_free_destinations(passport_country, include_categories)


# ============================================================
# TRAVELER PROFILE (persistent memory — real travel agent UX)
# ============================================================

@mcp.tool()
async def tool_get_traveler_profile() -> dict:
    """Load the stored traveler profile (home airports, passports, history).

    ALWAYS call this at the start of a session. If onboarded=False,
    walk the user through onboard_traveler before doing anything else.
    """
    return await get_traveler_profile()


@mcp.tool()
async def tool_onboard_traveler(
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
    """First-time setup. Saves profile so the agent remembers you forever.

    Run this once when the user is new. After this, get_traveler_profile
    returns their stored preferences on every future session.

    Args:
        name: First name
        home_airports: Comma-separated IATA (e.g., "JFK,EWR")
        passports: Comma-separated ISO-2 (e.g., "US" or "US,IN")
        home_currency: USD, EUR, GBP, INR, etc.
        travel_style: budget, moderate, luxury
        interests: Comma-separated (e.g., "food,history,beach")
        dietary: Comma-separated restrictions
        preferred_cabin: economy, premium_economy, business, first
        visas_held: ISO-2 dest codes with active visas (e.g., "IN,CN")
        eta_held: Active ETAs (e.g., "ESTA (US),UK ETA")
    """
    return await onboard_traveler(
        name, home_airports, passports, home_currency,
        travel_style, interests, dietary, preferred_cabin,
        visas_held, eta_held,
    )


@mcp.tool()
async def tool_update_traveler_profile(
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
    """Update profile fields or log a completed trip. Pass only what changed.

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
        add_visa: Append one ISO-2 dest code to visas_held
        add_trip_destination: Log a trip — destination name
        add_trip_from: Trip start YYYY-MM-DD
        add_trip_to: Trip end YYYY-MM-DD
        add_trip_purpose: tourism, business, family, other
    """
    return await update_traveler_profile(
        name, home_airports, passports, home_currency, travel_style,
        interests, dietary, preferred_cabin, visas_held, eta_held,
        add_visa, add_trip_destination, add_trip_from, add_trip_to, add_trip_purpose,
    )


@mcp.tool()
async def tool_get_trip_history(limit: int = 20) -> dict:
    """View logged trip history for this traveler.

    Args:
        limit: Max trips to return (most recent first)
    """
    return await get_trip_history(limit)


# ============================================================
# GROUND TRANSPORT (bus, train, ferry)
# ============================================================

@mcp.tool()
async def tool_search_ground_transport(
    origin_city: str,
    destination_city: str,
    date: str,
    travelers: int = 1,
    region: str | None = None,
) -> dict:
    """Search bus, train, and ferry options between two cities.

    Returns multi-modal route overview + direct booking links for
    Amtrak, FlixBus, Greyhound, Megabus, OurBus, BlaBlaCar,
    Busbud, Trainline, IRCTC, 12Go, and Rome2Rio.
    No API key required.

    Args:
        origin_city: Departure city (e.g., "State College", "Paris", "Mumbai")
        destination_city: Destination city (e.g., "New York", "London", "Delhi")
        date: Departure date YYYY-MM-DD
        travelers: Number of travelers
        region: us, europe, india, sea — auto-detected if omitted
    """
    return await search_ground_transport(origin_city, destination_city, date, travelers, region)


# ============================================================
# BOOKABLE TRIP PACKAGE (orchestrates everything in one call)
# ============================================================

@mcp.tool()
async def tool_plan_trip_package(
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
    """THE KILLER TOOL: Complete bookable trip package in one call.

    Simultaneously fetches and composes: flights (multi-airport),
    hotels, visa requirements, weather, safety advisory, attractions,
    ground transport, and a cost estimate — with direct booking URLs
    for every section and a step-by-step booking checklist.

    Use this when the user has a specific trip in mind.
    Use score_destinations first if they're still deciding where to go.

    Args:
        origin: Departure airport IATA or city (e.g., "DXB", "JFK", "New York")
        destination: Destination city (e.g., "Bali", "Tokyo", "Paris")
        departure_date: YYYY-MM-DD
        return_date: YYYY-MM-DD (auto-calculated from trip_length_days if omitted)
        trip_length_days: Nights (used when return_date omitted)
        travelers: Number of travelers
        passport_country: ISO-2 for visa check (e.g., "US", "IN", "GB")
        currency: Home currency for all prices
        budget_level: budget, moderate, luxury
        interests: Comma-separated (e.g., "beach,food,history")
        include_ground_transport: Also search buses/trains
    """
    return await plan_trip_package(
        origin, destination, departure_date, return_date,
        trip_length_days, travelers, passport_country, currency,
        budget_level, interests, include_ground_transport,
    )



@mcp.tool()
async def tool_search_restaurants_bars(
    latitude: float,
    longitude: float,
    category: str = "all",
    radius_m: int = 1000,
    max_results: int = 15,
    cuisine: str | None = None,
    city: str | None = None,
) -> dict:
    """Find restaurants, bars, pubs, cafes near a location with ratings and booking links.

    Returns real venues with cuisine, price level, opening hours, distance,
    and direct links to Google Maps, Zomato, TripAdvisor, Yelp, OpenTable,
    Resy (restaurants), Untappd (bars/pubs), and Foursquare.

    Ratings available if FOURSQUARE_API_KEY env var is set (free tier).

    Args:
        latitude: Location latitude
        longitude: Location longitude
        category: restaurant | bar | pub | cafe | nightlife | all
        radius_m: Walk radius in metres (default 1000 = ~12min walk)
        max_results: Max venues (1-30)
        cuisine: Filter by cuisine e.g. "italian", "japanese", "thai", "indian"
        city: City name for better search links e.g. "Tokyo", "Paris"
    """
    return await search_restaurants_bars(
        latitude, longitude, category, radius_m, max_results, cuisine, city,
    )



# ============================================================
# NEW UTILITY TOOLS
# ============================================================

@mcp.tool()
async def tool_generate_packing_list(
    destination: str,
    start_date: str,
    end_date: str,
    activities: str | None = None,
    budget_level: str = "moderate",
    travelers: int = 1,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    """Generate a smart packing list tailored to destination, weather, and activities.

    Fetches live weather to adapt clothing and gear suggestions.

    Args:
        destination: City or country name
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        activities: Comma-separated (e.g., "beach,hiking,business,nightlife")
        budget_level: budget, moderate, luxury
        travelers: Number of travelers
        latitude: Optional — auto-fetched if omitted
        longitude: Optional — auto-fetched if omitted
    """
    return await generate_packing_list(
        destination, start_date, end_date, activities,
        budget_level, travelers, latitude, longitude,
    )


@mcp.tool()
async def tool_find_places(
    latitude: float,
    longitude: float,
    category: str,
    radius_km: int = 20,
    max_results: int = 15,
    city: str | None = None,
) -> dict:
    """Find viewpoints, beaches, hiking trails, coworking spaces, and more.

    Uses OpenStreetMap — no API key required.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        category: viewpoint | beach | hiking | coworking | waterfall | camping | market | hot_spring | museum | park
        radius_km: Search radius in km (1-100)
        max_results: Max places to return
        city: City name for richer search links (e.g., "Bali", "Cape Town")
    """
    return await find_places(latitude, longitude, category, radius_km, max_results, city)


@mcp.tool()
async def tool_calculate_jet_lag(
    origin: str,
    destination: str,
    departure_date: str,
    flight_duration_hours: float = 0.0,
) -> dict:
    """Calculate jet lag severity and give a science-based recovery schedule.

    Covers pre-departure schedule shift, on-plane tips, melatonin timing,
    and post-arrival light exposure strategy.

    Args:
        origin: City or IATA code (e.g., "New York", "JFK")
        destination: City or IATA code (e.g., "Tokyo", "NRT")
        departure_date: YYYY-MM-DD
        flight_duration_hours: Flight time in hours (0 = auto-estimated)
    """
    return await calculate_jet_lag(origin, destination, departure_date, flight_duration_hours)


@mcp.tool()
async def tool_get_language_phrasebook(
    destination: str,
    language_code: str | None = None,
    category: str | None = None,
) -> dict:
    """Get a phrasebook for the local language at a destination.

    Covers 17 languages with pronunciation guides and essential phrases.

    Args:
        destination: City or country name (e.g., "Tokyo", "France", "Bangkok")
        language_code: Override language (ja, fr, es, it, de, pt, th, zh, ar, ko, hi, vi, id, tr, ms, sw)
        category: greeting | essential | food | transport | shopping | emergency | accommodation | numbers
    """
    return await get_language_phrasebook(destination, language_code, category)


@mcp.tool()
async def tool_get_stopover_guide(
    airport: str,
    layover_hours: float,
    passport_country: str | None = None,
) -> dict:
    """What to do during a layover at a major hub airport.

    Covers in-terminal activities, city excursions, and transit visa info
    for IST, DXB, SIN, DOH, NRT, HND, CDG, HKG, ICN, AMS.

    Args:
        airport: IATA code (e.g., "DXB", "SIN", "IST")
        layover_hours: Total layover duration in hours
        passport_country: ISO-2 code for transit visa check (e.g., "IN", "US")
    """
    return await get_stopover_guide(airport, layover_hours, passport_country)


@mcp.tool()
async def tool_get_travel_news(
    destination: str,
    days_lookback: int = 7,
    max_results: int = 10,
) -> dict:
    """Get recent travel news and disruption alerts for a destination.

    Scans Google News RSS for strikes, airport closures, entry bans, protests.
    No API key required.

    Args:
        destination: City or country name (e.g., "Paris", "Thailand")
        days_lookback: Only news from last N days (1-30)
        max_results: Max articles to return
    """
    return await get_travel_news(destination, days_lookback, max_results)


@mcp.tool()
async def tool_check_travel_health(
    destination_iso2: str,
    trip_duration_days: int = 14,
) -> dict:
    """Health requirements, vaccine recommendations, and safety tips for a destination.

    Covers required vaccines, CDC/WHO recommendations, water safety, mosquito risk,
    altitude sickness, food safety, and a pre-departure preparation timeline.

    Args:
        destination_iso2: ISO 2-letter country code OR IATA airport code (e.g., "TH", "JP", "BKK", "DPS")
        trip_duration_days: Trip length (affects malaria prophylaxis advice etc.)
    """
    return await check_travel_health(destination_iso2, trip_duration_days)

def main():
    import os
    transport = os.environ.get("WANDER_TRANSPORT", "stdio")
    host = os.environ.get("WANDER_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)


if __name__ == "__main__":
    main()
