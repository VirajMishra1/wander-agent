"""Integration tests for multi-tool orchestration (all HTTP mocked)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import respx
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ── shared fake responses ──────────────────────────────────────────────────

GEOCODE_RESPONSE = {
    "latitude": -8.4095,
    "longitude": 115.1889,
    "country": "Indonesia",
    "city": "Bali",
}

HOTELS_RESPONSE = {
    "hotels": [
        {"name": "Fake Resort", "price_per_night": 80, "currency": "USD"},
    ],
    "cheapest_price_per_night": 80,
    "data_confidence": "names_live_prices_estimated",
}

WEATHER_RESPONSE = {
    "summary": {
        "avg_high_c": 30,
        "avg_low_c": 24,
        "rainy_days": 2,
        "total_days": 7,
        "description": "Warm and mostly dry",
    }
}

ADVISORY_RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<item><title>Indonesia - Level 1: Exercise Normal Precautions</title>
<description>Exercise normal precautions.</description>
<link>https://travel.state.gov</link></item>
</channel></rss>"""

VISA_ESTA_MOCK = {}  # _classify is pure logic, no HTTP

ACTIVITIES_WIKIDATA = {
    "results": {
        "bindings": [
            {
                "itemLabel": {"value": "Tanah Lot"},
                "coord": {"value": "Point(115.0865 -8.6211)"},
                "desc": {"value": "Temple on a rock island"},
            }
        ]
    }
}


def _mock_all(router: respx.MockRouter) -> None:
    """Register mocks for all external HTTP calls used by plan_trip_package."""
    # Geocode (Open-Meteo geocoding or Nominatim)
    router.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(200, json=[{
            "lat": "-8.4095", "lon": "115.1889",
            "display_name": "Bali, Indonesia",
            "address": {"country": "Indonesia", "country_code": "id"},
        }])
    )
    # Weather
    router.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json={"daily": {
            "time": ["2025-08-01"],
            "temperature_2m_max": [30],
            "temperature_2m_min": [24],
            "precipitation_sum": [0],
        }})
    )
    router.get("https://archive-api.open-meteo.com/v1/archive").mock(
        return_value=httpx.Response(200, json={"daily": {
            "time": ["2024-08-01"],
            "temperature_2m_max": [30],
            "temperature_2m_min": [24],
            "precipitation_sum": [0],
        }})
    )
    # Advisory RSS
    router.get("https://travel.state.gov/_res/rss/TAsTWs.xml").mock(
        return_value=httpx.Response(200, text=ADVISORY_RSS)
    )
    # Hotels (fast-hotels or scraper) — catch-all for booking.com-style
    router.get(url__regex=r".*booking\.com.*").mock(
        return_value=httpx.Response(200, json=HOTELS_RESPONSE)
    )
    # Wikidata SPARQL
    router.get("https://query.wikidata.org/sparql").mock(
        return_value=httpx.Response(200, json=ACTIVITIES_WIKIDATA)
    )
    # Google Flights — catch-all
    router.get(url__regex=r".*google\.com/travel/flights.*").mock(
        return_value=httpx.Response(200, text="<html></html>")
    )
    # Rome2Rio
    router.get("https://www.rome2rio.com/api/1.4/json/Search").mock(
        return_value=httpx.Response(404)
    )
    # Teleport / cost-of-living
    router.get(url__regex=r".*teleport\.org.*").mock(
        return_value=httpx.Response(200, json={"_embedded": {"city:urban_areas": []}})
    )
    # Catch-all for anything else
    router.route(url__regex=r".*").mock(
        return_value=httpx.Response(200, json={})
    )


@pytest.mark.asyncio
async def test_plan_trip_package_returns_all_sections(reset_http_client):
    from wander_agent.tools.package import plan_trip_package

    with respx.mock(assert_all_called=False) as router:
        _mock_all(router)
        result = await plan_trip_package(
            origin="DXB",
            destination="Bali",
            departure_date="2025-08-01",
            trip_length_days=7,
            travelers=2,
            passport_country="US",
        )

    required_keys = [
        "trip", "flights", "hotels", "visa", "weather",
        "advisory", "ground_transport", "cost_estimate", "booking_checklist",
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_plan_trip_package_trip_metadata(reset_http_client):
    from wander_agent.tools.package import plan_trip_package

    with respx.mock(assert_all_called=False) as router:
        _mock_all(router)
        result = await plan_trip_package(
            origin="DXB",
            destination="Bali",
            departure_date="2025-08-01",
            trip_length_days=7,
            travelers=2,
        )

    trip = result["trip"]
    assert trip["nights"] == 7
    assert trip["travelers"] == 2
    assert trip["origin"] == "DXB"


@pytest.mark.asyncio
async def test_plan_trip_package_has_booking_links(reset_http_client):
    from wander_agent.tools.package import plan_trip_package

    with respx.mock(assert_all_called=False) as router:
        _mock_all(router)
        result = await plan_trip_package(
            origin="JFK",
            destination="Paris",
            departure_date="2025-09-01",
            trip_length_days=5,
            travelers=1,
        )

    # Must have booking links in flights section
    assert "booking_links" in result["flights"]
    assert "google_flights" in result["flights"]["booking_links"]
    assert "booking_links" in result["hotels"]


@pytest.mark.asyncio
async def test_plan_trip_package_invalid_date(reset_http_client):
    from wander_agent.tools.package import plan_trip_package

    result = await plan_trip_package(
        origin="JFK",
        destination="Tokyo",
        departure_date="not-a-date",
    )
    assert "error" in result


@pytest.mark.asyncio
async def test_plan_trip_package_return_before_departure(reset_http_client):
    from wander_agent.tools.package import plan_trip_package

    result = await plan_trip_package(
        origin="JFK",
        destination="Tokyo",
        departure_date="2025-09-10",
        return_date="2025-09-05",
    )
    assert "error" in result
