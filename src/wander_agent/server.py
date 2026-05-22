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
        "Travel agent with two modes: INSPIRATION (find destinations by budget) "
        "and PLANNING (search specific flights/hotels/itineraries). Includes "
        "advisories, events, cost-of-living, multi-objective scoring, verification. "
        "All free APIs.\n\n"
        "WHEN TO USE THESE TOOLS vs YOUR OWN WEB SEARCH:\n"
        "- Use these tools for: flight prices, hotel rates, structured weather, "
        "  cached advisories, deterministic scoring, place verification, "
        "  cost-of-living lookups, multi-destination comparison.\n"
        "- Use YOUR WEB SEARCH for: current mistake fares and flash deals, "
        "  recent destination news (strikes/closures/protests), restaurant reviews "
        "  and subjective recommendations, visa policy changes since 2025, "
        "  local festivals not in Ticketmaster (Asia/LatAm coverage gap), "
        "  trip-report blogs.\n"
        "- Many tool outputs include a 'suggest_web_search' field with concrete "
        "  query suggestions. Run them when present.\n"
        "- Compose freely: pull structured data here, then web-search to "
        "  enrich. Cross-check important claims with verify_place."
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
) -> dict:
    """INSPIRATION: Find cheapest destinations from origin airport.

    "Show me cheap flights from NYC anywhere in March" - returns ranked
    destinations by price.

    Args:
        origin: IATA airport code (e.g., "JFK")
        month: YYYY-MM constraint (optional)
        max_price: Filter out above this price
        max_results: Max destinations
        currency: USD, EUR, etc.
    """
    return await cheap_anywhere_from(origin, month, max_price, max_results, currency)


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
    Optional Hotellook prices are returned when TRAVELPAYOUTS_TOKEN is set.

    Args:
        city: City name (e.g., "Paris", "Tokyo") - NOT IATA code
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
        adults: Number of guests
        rooms: Number of rooms
        max_results: Max results
        currency: USD, EUR, etc.
        price_range: "100-300" (Hotellook only)
        ratings: "3,4,5" (Hotellook only)
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


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
