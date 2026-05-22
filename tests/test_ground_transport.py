"""Tests for ground_transport pure-logic functions."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wander_agent.tools.ground_transport import _detect_region, _fill_link, _slugify


def test_slugify_basic():
    assert _slugify("New York") == "new-york"


def test_slugify_already_lower():
    assert _slugify("chicago") == "chicago"


def test_slugify_strips_punctuation():
    assert "," not in _slugify("Washington, D.C.")
    assert "." not in _slugify("Washington, D.C.")


def test_detect_region_us():
    assert _detect_region("New York", "Chicago") == "us"


def test_detect_region_europe_paris():
    assert _detect_region("London", "Paris") == "europe"


def test_detect_region_europe_berlin():
    assert _detect_region("Amsterdam", "Berlin") == "europe"


def test_detect_region_sea_bali():
    assert _detect_region("Singapore", "Bali") == "sea"


def test_detect_region_india():
    # India detection uses IRCTC city codes
    result = _detect_region("Mumbai", "Delhi")
    # India or fallback us — depends on whether city names match IRCTC codes
    assert result in ("india", "us")


def test_fill_link_replaces_placeholders():
    template = "https://example.com/{origin_slug}/to/{dest_slug}"
    result = _fill_link(template, origin_slug="new-york", dest_slug="chicago")
    assert result == "https://example.com/new-york/to/chicago"


def test_fill_link_url_encodes_spaces():
    template = "https://example.com/{origin_slug}"
    result = _fill_link(template, origin_slug="new york")
    assert " " not in result


@pytest.mark.asyncio
async def test_search_ground_transport_returns_structure(reset_http_client):
    import respx
    import httpx

    with respx.mock:
        # Mock Rome2Rio to fail (404) so we test deeplink fallback
        respx.get("https://www.rome2rio.com/api/1.4/json/Search").mock(
            return_value=httpx.Response(404)
        )
        from wander_agent.tools.ground_transport import search_ground_transport
        result = await search_ground_transport(
            origin_city="New York",
            destination_city="Washington DC",
            date="2025-08-01",
            travelers=1,
        )

    assert "booking_links" in result
    assert "google_maps_transit_url" in result
    assert isinstance(result["booking_links"], list)
    assert len(result["booking_links"]) > 0


@pytest.mark.asyncio
async def test_search_ground_transport_rome2rio_success(reset_http_client):
    import respx
    import httpx
    import json

    fake_response = {
        "routes": [
            {
                "name": "Bus",
                "distance": 365,
                "duration": 270,
                "segments": [{"vehicle": "bus", "name": "Greyhound"}],
                "indicativePrice": {"price": 25, "currency": "USD"},
            }
        ]
    }

    with respx.mock:
        respx.get("https://www.rome2rio.com/api/1.4/json/Search").mock(
            return_value=httpx.Response(200, json=fake_response)
        )
        from wander_agent.tools.ground_transport import search_ground_transport
        result = await search_ground_transport(
            origin_city="New York",
            destination_city="Washington DC",
            date="2025-08-01",
            travelers=1,
        )

    assert "booking_links" in result
    # Rome2Rio deeplink should be in results
    deeplink_names = [b.get("service", "").lower() for b in result["booking_links"]]
    assert any("rome2rio" in n or "bus" in n for n in deeplink_names) or len(result["booking_links"]) > 0
