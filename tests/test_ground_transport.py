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
    result = _detect_region("Mumbai", "Delhi")
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
async def test_search_ground_transport_returns_structure():
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
    assert result["data_confidence"] == "deeplinks_only"


@pytest.mark.asyncio
async def test_search_ground_transport_no_hardcoded_keys():
    """Confirm no API call is made — purely deeplinks."""
    from wander_agent.tools.ground_transport import search_ground_transport
    # No respx mock needed — no HTTP calls should be made
    result = await search_ground_transport(
        origin_city="London",
        destination_city="Paris",
        date="2025-09-01",
        travelers=2,
    )
    assert result["region"] == "europe"
    assert len(result["booking_links"]) >= 3
    # Rome2Rio deeplink always present
    services = [b["service"].lower() for b in result["booking_links"]]
    assert any("rome2rio" in s for s in services)


@pytest.mark.asyncio
async def test_search_ground_transport_invalid_date():
    from wander_agent.tools.ground_transport import search_ground_transport
    result = await search_ground_transport("NYC", "Boston", "not-a-date")
    assert "error" in result


@pytest.mark.asyncio
async def test_search_ground_transport_route_overview_empty():
    """route_overview is always [] — no API dependency."""
    from wander_agent.tools.ground_transport import search_ground_transport
    result = await search_ground_transport("New York", "Chicago", "2025-08-01")
    assert result["route_overview"] == []
