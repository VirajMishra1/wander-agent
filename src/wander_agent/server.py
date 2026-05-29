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

# New high-impact tools
from .tools.nomad_score import score_nomad_cities
from .tools.transit_visa import check_transit_visa
from .tools.flight_carbon import calculate_flight_carbon
from .tools.fare_calendar import fare_calendar
from .tools.split_ticket import find_split_ticket
from .tools.passport_power import get_passport_power
from .tools.open_jaw import find_open_jaw
from .tools.cheapest_month import find_cheapest_month
from .tools.local_sim import get_local_sim_guide

# Trip memory + fare monitoring + value reasoning
from .tools.trips import (
    save_trip,
    list_my_trips,
    get_trip_status,
    update_trip,
    delete_trip,
)
from .tools.fare_watch import (
    watch_fare,
    list_fare_watches,
    check_fare_watches,
    stop_fare_watch,
)
from .tools.value_rank import rank_trip_options


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
        "- wikidata_fallback: Wikidata attractions (no OpenTripMap key configured)\n"
        "Many results also carry a data_meta block (trust_score 0-100, trust_label, "
        "meaning, fetched_at). Quote the trust_label when a number drives a booking decision.\n\n"

        "== TRIP MEMORY ==\n"
        "When a traveler commits to a destination, call save_trip to persist it with an "
        "8-item booking checklist. On return, call list_my_trips / get_trip_status and pick "
        "up where they left off. Tick items with update_trip (mark_done) as flights/hotels/"
        "visa get sorted. This memory is the agent's edge — no OTA remembers your trip.\n\n"

        "== FARE MONITORING ==\n"
        "If a price is too high or the traveler is undecided, offer watch_fare with a "
        "target_price. Later call check_fare_watches to re-price and surface target_hit / "
        "price_drop buy signals first.\n\n"

        "== VALUE, NOT JUST PRICE ==\n"
        "When comparing 2+ flight/trip options, call rank_trip_options. The cheapest fare "
        "often hides self-transfers, hidden-city risk, no baggage, or non-refundability. "
        "Surface value_score and the winner's 'why', and call out flags (hidden-city, "
        "split-ticket, self-transfer) explicitly.\n\n"

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
    """INSPIRATION: "I have $1500, where can I go?" Ranks destinations under a total
    budget with flight + hotel costs calculated.

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
    """WEATHER timing: best month to visit by climate, not price.

    "When is Bali at its best?" Uses 5yr Open-Meteo historical archive. No auth.
    For cheapest month by airfare use find_cheapest_month; for day-level price
    grid within a month use fare_calendar.

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
    """First-time setup. Saves the traveler profile for reuse every future session.

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
    """Complete bookable trip package in one call: flights, hotels, visa, weather,
    advisory, attractions, ground transport, cost estimate + booking URLs/checklist.

    Use when the destination is decided; use score_destinations if still deciding.

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
    """Find restaurants/bars/pubs/cafes near a location: cuisine, price, hours,
    distance + links to Google Maps, Zomato, TripAdvisor, Yelp, OpenTable, Resy,
    Untappd, Foursquare. Ratings need FOURSQUARE_API_KEY (free tier).

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

@mcp.tool()
async def tool_score_nomad_cities(
    cities: str,
    month: int | None = None,
    weights: str = "cost:25,safety:20,internet:15,weather:20,visa:10,lifestyle:10",
) -> dict:
    """Score and rank cities for digital nomad / remote-work suitability.

    Combines cost of living, safety advisory, internet speed index, weather
    comfort, visa ease, and lifestyle/coworking data into a single ranked score.
    No API key required.

    Args:
        cities: Comma-separated city names (e.g., "Bali,Lisbon,Chiang Mai,Medellin")
        month: Month 1-12 to evaluate weather (default: current month)
        weights: Scoring weights as "dimension:percent" pairs summing to 100.
                 Dimensions: cost, safety, internet, weather, visa, lifestyle
    """
    return await score_nomad_cities(cities, month, weights)


@mcp.tool()
async def tool_check_transit_visa(
    passport_country: str,
    layover_airport: str,
    connecting_to: str | None = None,
) -> dict:
    """Check if you need a transit visa for a layover airport.

    Covers the most common passport + layover combinations for 40+ major hubs:
    LHR, JFK, LAX, FRA, AMS, CDG, DXB, SIN, IST, DOH, NRT, ICN, HKG, YYZ,
    SYD, and more. This is a common trip-ruiner — carriers deny boarding if
    you lack the required transit document. Check BEFORE booking.

    Args:
        passport_country: Your passport ISO2 code (e.g., "IN", "US", "NG")
        layover_airport: IATA code of layover airport (e.g., "LHR", "DXB", "JFK")
        connecting_to: Optional final destination airport IATA (for context)
    """
    return await check_transit_visa(passport_country, layover_airport, connecting_to)


@mcp.tool()
async def tool_calculate_flight_carbon(
    origin: str,
    destination: str,
    passengers: int = 1,
    cabin_class: str = "economy",
    trip_type: str = "round_trip",
) -> dict:
    """Calculate CO2e carbon footprint for a flight.

    Uses ICAO/DEFRA 2024 emission factors including radiative forcing (RFI ×1.9).
    Shows per-passenger and total emissions, carbon offset cost at Gold Standard
    prices ($18/tonne), and train/car comparison for short-to-medium routes.
    No API key required.

    Args:
        origin: Origin airport IATA code (e.g., "JFK")
        destination: Destination airport IATA code (e.g., "LHR")
        passengers: Number of passengers
        cabin_class: economy | premium_economy | business | first
        trip_type: one_way | round_trip
    """
    return await calculate_flight_carbon(origin, destination, passengers, cabin_class, trip_type)


@mcp.tool()
async def tool_fare_calendar(
    origin: str,
    destination: str,
    year: int | None = None,
    month: int | None = None,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    trip_length_days: int | None = None,
) -> dict:
    """PRICE timing (day-level): cheapest DAY to fly within ONE month.

    Samples up to 15 departure dates in one month — day-of-week analysis, price
    tiers, best/worst weeks. For cheapest MONTH across a year use
    find_cheapest_month; for best weather use best_month_to_visit.

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
    return await fare_calendar(origin, destination, year, month, adults, cabin_class, currency, trip_length_days)


@mcp.tool()
async def tool_find_split_ticket(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    min_connection_hours: float = 3.0,
) -> dict:
    """Find savings by booking two separate tickets through a hub (prices origin→hub
    and hub→destination independently). 20-60% off on competitive long-haul routes.
    ⚠️ Missed-connection risk is on the traveler — surface result risks before booking.

    Args:
        origin: Origin airport IATA code (e.g., "SFO")
        destination: Destination airport IATA code (e.g., "DEL")
        departure_date: YYYY-MM-DD departure date
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code
        min_connection_hours: Minimum buffer hours between tickets at hub
    """
    return await find_split_ticket(origin, destination, departure_date, adults, cabin_class, currency, min_connection_hours)


@mcp.tool()
async def tool_get_passport_power(
    passport_country: str,
    compare_with: str | None = None,
) -> dict:
    """Rank passport strength, optionally compare two head-to-head: visa-free count,
    frictionless %, regional breakdown, Henley 2024 rank. With compare_with, shows
    which destinations each passport unlocks that the other doesn't.

    Args:
        passport_country: Your passport ISO2 code (e.g., "US", "IN", "NG", "CN")
        compare_with: Optional second passport ISO2 for comparison (e.g., "GB")
    """
    return await get_passport_power(passport_country, compare_with)


@mcp.tool()
async def tool_find_open_jaw(
    origin: str,
    fly_into: str,
    fly_out_from: str,
    outbound_date: str,
    return_date: str,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
) -> dict:
    """Plan an open-jaw trip: fly into one city, overland, fly out from another
    (e.g. JFK→Rome, train to Paris, Paris→JFK). Shows total vs simple round-trip.
    Accepts IATA codes or city names.

    Args:
        origin: Home airport IATA or city (e.g., "JFK" or "New York")
        fly_into: First destination IATA or city (e.g., "FCO" or "Rome")
        fly_out_from: Final departure IATA or city (e.g., "CDG" or "Paris")
        outbound_date: YYYY-MM-DD — fly origin → fly_into
        return_date: YYYY-MM-DD — fly fly_out_from → origin
        adults: Number of passengers
        cabin_class: economy | premium_economy | business | first
        currency: Currency code
    """
    return await find_open_jaw(origin, fly_into, fly_out_from, outbound_date, return_date, adults, cabin_class, currency)


@mcp.tool()
async def tool_find_cheapest_month(
    origin: str,
    destination: str,
    months_ahead: int = 12,
    adults: int = 1,
    cabin_class: str = "economy",
    currency: str = "USD",
    trip_length_days: int = 7,
    trip_type: str = "round_trip",
) -> dict:
    """PRICE timing (month-level): cheapest MONTH to fly across the next N months.

    Samples the first Tuesday of each month, ranks months by price with season
    analysis. For cheapest DAY within one month use fare_calendar; for best
    weather use best_month_to_visit.

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
    return await find_cheapest_month(origin, destination, months_ahead, adults, cabin_class, currency, trip_length_days, trip_type)


@mcp.tool()
async def tool_get_local_sim_guide(
    country: str,
    trip_duration_days: int = 7,
    data_heavy: bool = False,
) -> dict:
    """Local SIM/eSIM guide for a country: operators, cost, data, where to buy,
    activation, tethering policy, duration advice. 25+ countries; falls back to
    Airalo/Holafly otherwise.

    Args:
        country: Country name (e.g., "Thailand"), ISO2 code (e.g., "TH"), or city (e.g., "Bangkok")
        trip_duration_days: Trip length in days — affects local SIM vs eSIM recommendation
        data_heavy: True if you stream video, work remotely, or need constant hotspot
    """
    return await get_local_sim_guide(country, trip_duration_days, data_heavy)


# ============================================================
# TRIP MEMORY (persistent across sessions)
# ============================================================

@mcp.tool()
async def tool_save_trip(
    destination: str,
    depart_date: str | None = None,
    return_date: str | None = None,
    origin: str | None = None,
    travelers: int = 1,
    passport_country: str | None = None,
    purpose: str | None = None,
    notes: str | None = None,
) -> dict:
    """Save a trip the traveler is planning. Returns a trip_id + 8-item booking checklist.

    Use when a traveler commits to a destination so progress persists across sessions.

    Args:
        destination: City or country
        depart_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        origin: Home airport IATA
        travelers: Headcount
        passport_country: ISO2 for visa context
        purpose: leisure/business/etc
        notes: Free text
    """
    return await save_trip(destination, depart_date, return_date, origin,
                           travelers, passport_country, purpose, notes)


@mcp.tool()
async def tool_list_my_trips(status: str | None = None) -> dict:
    """List the traveler's saved trips with checklist progress.

    Args:
        status: Filter by planning/booked/completed/cancelled (omit for all)
    """
    return await list_my_trips(status)


@mcp.tool()
async def tool_get_trip_status(
    trip_id: str | None = None,
    destination: str | None = None,
) -> dict:
    """Get a saved trip's full state + checklist progress. Look up by id or destination.

    Args:
        trip_id: 8-char trip id
        destination: City/country if id unknown
    """
    return await get_trip_status(trip_id, destination)


@mcp.tool()
async def tool_update_trip(
    trip_id: str,
    status: str | None = None,
    depart_date: str | None = None,
    return_date: str | None = None,
    notes: str | None = None,
    mark_done: str | None = None,
    mark_undone: str | None = None,
    checklist_note: str | None = None,
    shortlist_flight: dict | None = None,
    shortlist_hotel: dict | None = None,
) -> dict:
    """Update a saved trip: change status/dates, tick checklist items, shortlist options.

    Checklist keys: book_flights, book_hotel, check_visa, travel_insurance,
    book_ground_transport, check_advisory, pack, notify_bank.

    Args:
        trip_id: 8-char trip id
        status: planning/booked/completed/cancelled
        depart_date: YYYY-MM-DD
        return_date: YYYY-MM-DD
        notes: Replace notes
        mark_done: Checklist key to mark done
        mark_undone: Checklist key to un-mark
        checklist_note: Note for the marked item
        shortlist_flight: Flight option dict to save
        shortlist_hotel: Hotel option dict to save
    """
    return await update_trip(trip_id, status, depart_date, return_date, notes,
                             mark_done, mark_undone, checklist_note,
                             shortlist_flight, shortlist_hotel)


@mcp.tool()
async def tool_delete_trip(trip_id: str) -> dict:
    """Delete a saved trip.

    Args:
        trip_id: 8-char trip id
    """
    return await delete_trip(trip_id)


# ============================================================
# FARE MONITORING
# ============================================================

@mcp.tool()
async def tool_watch_fare(
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str | None = None,
    adults: int = 1,
    currency: str = "USD",
    target_price: float | None = None,
) -> dict:
    """Start watching a flight route. Records a baseline price and a target to alert at.

    Args:
        origin: IATA
        destination: IATA
        depart_date: YYYY-MM-DD
        return_date: YYYY-MM-DD for round trip
        adults: Passengers
        currency: USD/EUR/etc
        target_price: Alert when price falls to/below this
    """
    return await watch_fare(origin, destination, depart_date, return_date,
                            adults, currency, target_price)


@mcp.tool()
async def tool_list_fare_watches(status: str | None = None) -> dict:
    """List saved fare watches with baseline/last/low prices.

    Args:
        status: Filter active/paused/triggered (omit for all)
    """
    return await list_fare_watches(status)


@mcp.tool()
async def tool_check_fare_watches(watch_id: str | None = None) -> dict:
    """Re-price watched routes now and return buy-signal alerts.

    Alerts: target_hit, price_drop, price_rise, no_change.

    Args:
        watch_id: Check one watch, or omit to check all active watches
    """
    return await check_fare_watches(watch_id)


@mcp.tool()
async def tool_stop_fare_watch(watch_id: str, delete: bool = False) -> dict:
    """Pause or delete a fare watch.

    Args:
        watch_id: Watch id
        delete: True deletes; False just pauses
    """
    return await stop_fare_watch(watch_id, delete)


# ============================================================
# VALUE REASONING (price is not everything)
# ============================================================

@mcp.tool()
async def tool_rank_trip_options(
    options_json: str,
    priority: str = "balanced",
    currency: str = "USD",
) -> dict:
    """Rank flight/trip options on a 0-100 value score — price plus stops, duration,
    refundability, baggage and hassle — not price alone.

    Pass a JSON array of option objects with any of: price, duration_minutes, stops,
    refundable, checked_bag_included, self_transfer, hidden_city, split_ticket,
    visa_required, transit_visa_required, label.

    Args:
        options_json: JSON array of option objects
        priority: cheapest/fastest/easiest/flexible/balanced
        currency: Display currency
    """
    return await rank_trip_options(options_json, priority, currency)


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
