"""Smoke test — verifies Google Flights scraper returns real data.

Hits live Google Flights. Run after dependency upgrades to catch breakage.
Skip in CI with: pytest -m "not smoke"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_google_flights_returns_data():
    from wander_agent.tools.flights import _search_fast_flights

    result = await _search_fast_flights(
        "JFK", "CDG", "2026-08-15", None, 1, 5, "USD", False,
    )
    assert result is not None, "Google Flights returned None — scraper may be broken"
    flights = result.get("flights", [])
    assert len(flights) >= 1, f"Expected flights, got {len(flights)}"
    assert flights[0]["price"] > 0, "Price should be positive"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_google_flights_has_airline_names():
    from wander_agent.tools.flights import _search_fast_flights

    result = await _search_fast_flights(
        "JFK", "CDG", "2026-08-15", None, 1, 5, "USD", False,
    )
    if result is None:
        pytest.skip("Scraper returned None")
    flights = result.get("flights", [])
    named = [f for f in flights if f.get("airline")]
    assert len(named) >= 1, (
        f"No flights with airline names — primp impersonation may be broken. "
        f"Got {len(flights)} flights, all unnamed."
    )


@pytest.mark.smoke
def test_primp_has_valid_chrome_profile():
    """Verify at least one of our preferred Chrome profiles works."""
    from primp import Client
    from wander_agent.tools.flights import _CHROME_PROFILES

    for profile in _CHROME_PROFILES:
        try:
            client = Client(impersonate=profile)
            assert client.impersonate == profile
            return
        except (RuntimeError, Exception):
            continue
    pytest.fail(
        f"None of {_CHROME_PROFILES} are valid — "
        f"primp may have dropped all Chrome profiles in a new version"
    )
