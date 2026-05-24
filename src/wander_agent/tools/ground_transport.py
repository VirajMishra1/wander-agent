"""Ground transport search — the missing leg of every trip.

Covers buses, trains, and ferries between cities via booking deeplinks.

Sources (all deeplinks, no API keys):
  - Amtrak (US rail)
  - Greyhound (US bus)
  - Megabus (US + UK)
  - OurBus (US Northeast)
  - FlixBus (Europe + select US)
  - BlaBlaCar Bus (Europe)
  - Busbud (global, 50+ countries)
  - Trainline (Europe/UK rail)
  - IRCTC (India rail)
  - 12Go (Southeast Asia)
  - Rome2Rio (global multi-modal overview)
  - Google Maps Transit
"""

from __future__ import annotations

import urllib.parse
from datetime import datetime


# Deeplink templates
_DEEPLINKS = {
    "flixbus": "https://shop.flixbus.com/search?departureCity={origin_city}&arrivalCity={dest_city}&rideDate={date}&adult={travelers}",
    "amtrak": "https://www.amtrak.com/buy/station/{origin_code}/{dest_code}.html?departDate={date}&numberOfAdults={travelers}",
    "greyhound": "https://www.greyhound.com/en/results?origin={origin_city}&destination={dest_city}&outboundDate={date}&pax={travelers}",
    "megabus": "https://us.megabus.com/journey-planner/journeys?originId={origin_city}&destinationId={dest_city}&outboundDepartureDate={date}&totalPassengers={travelers}",
    "ourbus": "https://www.ourbus.com/booknow?origin={origin_city}&destination={dest_city}&date={date}&passengers={travelers}",
    "blablacar_bus": "https://www.blablacar.com/bus/search?departure_city={origin_city}&arrival_city={dest_city}&departure_date={date}&passengers={travelers}",
    "busbud": "https://www.busbud.com/en/bus-schedules/{origin_city}/{dest_city}/{date}?adult={travelers}",
    "trainline": "https://www.thetrainline.com/book/results?origin={origin_city}&destination={dest_city}&outwardDate={date}&passengers[]=26{extra_adults}",
    "irctc": "https://www.irctc.co.in/nget/train-search?fromStation={origin_code}&toStation={dest_code}&journeyDate={date}&journeyQuota=GN&adult={travelers}",
    "12go": "https://12go.asia/en/travel/{origin_city}/{dest_city}?from_date={date}&passengers={travelers}",
    "rome2rio": "https://www.rome2rio.com/s/{origin_slug}/{dest_slug}",
    "google_maps_transit": "https://www.google.com/maps/dir/?api=1&origin={origin_city}&destination={dest_city}&travelmode=transit",
}

# Which services to show per region
_REGIONAL_SERVICES = {
    "us": ["amtrak", "greyhound", "megabus", "ourbus", "flixbus", "busbud"],
    "europe": ["flixbus", "blablacar_bus", "trainline", "busbud"],
    "india": ["irctc", "busbud"],
    "sea": ["12go", "busbud"],
    "global": ["busbud"],
}

# City -> Amtrak station code
_AMTRAK_CODES: dict[str, str] = {
    "new york": "NYP", "nyc": "NYP", "new york city": "NYP",
    "washington dc": "WAS", "washington": "WAS", "dc": "WAS",
    "philadelphia": "PHL", "boston": "BOS", "baltimore": "BAL",
    "chicago": "CHI", "los angeles": "LAX", "san francisco": "EMY",
    "seattle": "SEA", "portland": "PDX", "denver": "DEN",
    "state college": "HAR",  # nearest Amtrak: Harrisburg, PA
    "harrisburg": "HAR", "pittsburgh": "PGH",
    "miami": "MIA", "orlando": "ORL", "atlanta": "ATL",
    "new orleans": "NOL", "dallas": "DAL", "houston": "HOU",
    "minneapolis": "MSP", "kansas city": "KCY", "st. louis": "STL",
    "raleigh": "RAG", "richmond": "RVR", "charlotte": "CLT",
}

# City -> IRCTC station code
_IRCTC_CODES: dict[str, str] = {
    "mumbai": "CSTM", "delhi": "NDLS", "new delhi": "NDLS",
    "bangalore": "SBC", "bengaluru": "SBC",
    "chennai": "MAS", "kolkata": "KOAA", "hyderabad": "HYB",
    "pune": "PUNE", "ahmedabad": "ADI", "jaipur": "JP",
    "goa": "MAO", "kochi": "ERS", "agra": "AGC",
    "varanasi": "BSB", "lucknow": "LKO", "bhopal": "BPL",
    "surat": "ST", "amritsar": "ASR", "chandigarh": "CDG",
}


def _slugify(city: str) -> str:
    return city.lower().strip().replace(" ", "-").replace(",", "").replace(".", "")


def _fill_link(template: str, **kwargs: str) -> str:
    result = template
    for key, val in kwargs.items():
        result = result.replace(f"{{{key}}}", urllib.parse.quote(str(val), safe=""))
    return result


def _detect_region(origin: str, dest: str) -> str:
    combined = (origin + " " + dest).lower()
    india = set(_IRCTC_CODES.keys())
    if any(c in combined for c in india):
        return "india"
    sea_cities = {"bangkok", "singapore", "kuala lumpur", "ho chi minh", "hanoi",
                  "bali", "jakarta", "yangon", "phnom penh", "vientiane", "colombo"}
    if any(c in combined for c in sea_cities):
        return "sea"
    europe_hints = {"paris", "london", "berlin", "rome", "barcelona", "amsterdam",
                    "madrid", "lisbon", "vienna", "prague", "brussels", "zurich",
                    "stockholm", "oslo", "copenhagen", "warsaw", "budapest", "athens"}
    if any(c in combined for c in europe_hints):
        return "europe"
    return "us"


async def search_ground_transport(
    origin_city: str,
    destination_city: str,
    date: str,
    travelers: int = 1,
    region: str | None = None,
) -> dict:
    """Search bus, train, and ferry options between two cities.

    Returns direct booking deeplinks for all relevant services
    (Amtrak, FlixBus, Greyhound, Megabus, Trainline, etc.).
    No API key required.

    Args:
        origin_city: Departure city (e.g., "State College", "Paris", "Mumbai")
        destination_city: Destination city (e.g., "New York", "London", "Delhi")
        date: Departure date YYYY-MM-DD
        travelers: Number of travelers
        region: us, europe, india, sea — auto-detected if omitted
    """
    origin = origin_city.strip()
    dest = destination_city.strip()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"error": "date must be YYYY-MM-DD"}

    if not region:
        region = _detect_region(origin, dest)

    services = _REGIONAL_SERVICES.get(region, _REGIONAL_SERVICES["global"])

    origin_key = origin.lower()
    dest_key = dest.lower()
    amtrak_origin = _AMTRAK_CODES.get(origin_key, origin_key.upper()[:3])
    amtrak_dest = _AMTRAK_CODES.get(dest_key, dest_key.upper()[:3])
    irctc_origin = _IRCTC_CODES.get(origin_key, origin_key.upper()[:4])
    irctc_dest = _IRCTC_CODES.get(dest_key, dest_key.upper()[:4])

    booking_links: list[dict] = []
    for service in services:
        template = _DEEPLINKS.get(service)
        if not template:
            continue
        # Trainline encodes each extra adult as an additional passengers[]=26 param
        extra_adults = "".join("&passengers[]=26" for _ in range(travelers - 1))
        link = _fill_link(
            template,
            origin_city=origin,
            dest_city=dest,
            date=date,
            origin_slug=_slugify(origin),
            dest_slug=_slugify(dest),
            origin_code=amtrak_origin if service == "amtrak" else irctc_origin,
            dest_code=amtrak_dest if service == "amtrak" else irctc_dest,
            travelers=str(travelers),
            extra_adults=extra_adults,
        )
        booking_links.append({
            "service": service.replace("_", " ").title(),
            "url": link,
            "coverage": _SERVICE_COVERAGE.get(service, "varies"),
            "data_confidence": "deeplink",
        })

    # Rome2Rio deeplink (always add — global multi-modal overview)
    booking_links.append({
        "service": "Rome2Rio",
        "url": _fill_link(
            _DEEPLINKS["rome2rio"],
            origin_slug=_slugify(origin),
            dest_slug=_slugify(dest),
        ),
        "coverage": "Global multi-modal overview",
        "data_confidence": "deeplink",
    })

    maps_url = _fill_link(
        _DEEPLINKS["google_maps_transit"],
        origin_city=origin,
        dest_city=dest,
    )

    return {
        "origin": origin,
        "destination": dest,
        "date": date,
        "travelers": travelers,
        "region": region,
        "route_overview": [],
        "booking_links": booking_links,
        "google_maps_transit_url": maps_url,
        "data_confidence": "deeplinks_only",
        "note": (
            "Click any booking_link URL to see live prices and availability. "
            "Rome2Rio shows all transport modes in one view."
        ),
        "suggest_web_search": [
            f"bus from {origin} to {dest} {date[:7]}",
            f"train from {origin} to {dest} schedule",
            f"cheapest way {origin} to {dest}",
        ],
    }


_SERVICE_COVERAGE: dict[str, str] = {
    "flixbus": "Europe + select US routes",
    "amtrak": "United States rail",
    "greyhound": "United States bus",
    "megabus": "US + UK bus",
    "ourbus": "US Northeast bus",
    "blablacar_bus": "Europe bus + carpooling",
    "busbud": "Global bus (50+ countries)",
    "trainline": "Europe + UK rail",
    "irctc": "India rail",
    "12go": "Southeast Asia (bus/ferry/train)",
    "rome2rio": "Global multi-modal",
}
