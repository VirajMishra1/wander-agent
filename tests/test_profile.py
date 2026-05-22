"""Tests for profile store persistence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_load_profile_returns_defaults_when_missing(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    profile = ps.load_profile()
    assert profile["onboarded"] is False
    assert profile["home_airports"] == []
    assert "schema_version" in profile


def test_save_and_reload_profile(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    p = ps.load_profile()
    p["name"] = "Alice"
    p["home_airports"] = ["JFK"]
    ps.save_profile(p)

    reloaded = ps.load_profile()
    assert reloaded["name"] == "Alice"
    assert reloaded["home_airports"] == ["JFK"]


def test_update_profile_fields_merges(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    ps.update_profile_fields(home_currency="EUR", travel_style="budget")

    profile = ps.load_profile()
    assert profile["home_currency"] == "EUR"
    assert profile["travel_style"] == "budget"
    # Other defaults untouched
    assert profile["onboarded"] is False


def test_update_profile_fields_ignores_unknown_keys(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    ps.update_profile_fields(nonexistent_key="value")
    profile = ps.load_profile()
    assert "nonexistent_key" not in profile


def test_add_trip_appends(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    ps.add_trip("Tokyo", "2025-03-01", "2025-03-10", "leisure")
    ps.add_trip("Paris", "2025-06-01", "2025-06-07", "conference")

    profile = ps.load_profile()
    trips = profile["past_trips"]
    assert len(trips) == 2
    assert trips[0]["destination"] == "Tokyo"
    assert trips[1]["destination"] == "Paris"


def test_add_trip_caps_at_50(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    for i in range(55):
        ps.add_trip(f"City{i}", "2025-01-01", "2025-01-07")

    profile = ps.load_profile()
    assert len(profile["past_trips"]) == 50


def test_save_sets_updated_at(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    p = ps.load_profile()
    ps.save_profile(p)
    reloaded = ps.load_profile()
    assert reloaded["updated_at"] is not None


@pytest.mark.asyncio
async def test_onboard_traveler_sets_onboarded(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    from wander_agent.tools.profile import onboard_traveler

    result = await onboard_traveler(
        name="Bob",
        home_airports="JFK,EWR",
        passports="US",
        home_currency="USD",
        travel_style="moderate",
    )
    assert result.get("status") == "onboarded"
    assert "profile_summary" in result
    # Verify persisted
    reloaded = ps.load_profile()
    assert reloaded["name"] == "Bob"
    assert reloaded["onboarded"] is True


@pytest.mark.asyncio
async def test_get_trip_history_limit(tmp_profile, monkeypatch):
    import wander_agent.utils.profile_store as ps
    from wander_agent.tools.profile import get_trip_history

    for i in range(5):
        ps.add_trip(f"City{i}", "2025-01-01", "2025-01-07")

    result = await get_trip_history(limit=3)
    assert len(result["trips"]) <= 3
