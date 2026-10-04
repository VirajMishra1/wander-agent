"""Regression tests for the tool-audit fixes (stores, packing, points, overpass, countries, kiwi)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest
import respx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_trip_store_reads_legacy_dict_format(tmp_path, monkeypatch):
    import wander_agent.utils.trip_store as ts

    store = tmp_path / "trips.json"
    store.write_text(json.dumps({"schema_version": 1, "trips": []}))
    monkeypatch.setattr(ts, "_STORE", store)

    assert ts.load_trips() == []
    trip = ts.create_trip("Lisbon")
    assert [t["id"] for t in ts.list_trips()] == [trip["id"]]


def test_watch_store_reads_legacy_dict_format(tmp_path, monkeypatch):
    import wander_agent.utils.watch_store as ws

    store = tmp_path / "fare_watches.json"
    store.write_text(json.dumps({"schema_version": 1, "watches": []}))
    monkeypatch.setattr(ws, "_STORE", store)

    assert ws.load_watches() == []
    assert ws.list_watches() == []


@pytest.mark.asyncio
async def test_packing_list_without_activities():
    from wander_agent.tools.packing import generate_packing_list

    # The MCP wrapper passes activities=None when the caller omits it
    result = await generate_packing_list("Lisbon", "2026-12-10", "2026-12-13", activities=None, latitude=38.7, longitude=-9.1)
    assert "error" not in result


@pytest.mark.asyncio
async def test_points_earning_dining_maps_to_restaurants():
    from wander_agent.tools.points import estimate_points_earning

    result = await estimate_points_earning(100, "amex_gold", "dining")
    assert result["matched_category"] == "restaurants"
    assert result["points_earned"] == 400


def test_find_country_by_name_code_and_alt():
    from wander_agent.utils.countries import find_country

    assert find_country("Japan")["cca2"] == "JP"
    assert find_country("jp")["cca2"] == "JP"
    assert find_country("USA")["cca2"] == "US"
    assert find_country("Atlantis") is None


@pytest.mark.asyncio
@respx.mock
async def test_overpass_retries_after_504(monkeypatch):
    import wander_agent.utils.overpass as op

    monkeypatch.setattr(op, "_RETRY_DELAY", 0)
    route = respx.post(op._ENDPOINT).mock(side_effect=[
        httpx.Response(504),
        httpx.Response(200, json={"elements": [{"id": 1}]}),
    ])
    async with httpx.AsyncClient() as client:
        elements, error = await op.overpass_elements(client, "[out:json];")
    assert elements == [{"id": 1}]
    assert error is None
    assert route.call_count == 2


@pytest.mark.asyncio
@respx.mock
async def test_overpass_reports_error_when_retries_exhausted(monkeypatch):
    import wander_agent.utils.overpass as op

    monkeypatch.setattr(op, "_RETRY_DELAY", 0)
    respx.post(op._ENDPOINT).mock(return_value=httpx.Response(504))
    async with httpx.AsyncClient() as client:
        elements, error = await op.overpass_elements(client, "[out:json];")
    assert elements == []
    assert "504" in error


@pytest.mark.asyncio
async def test_kiwi_circuit_breaker_skips_after_repeated_failures(monkeypatch):
    import wander_agent.utils.kiwi_client as kc

    monkeypatch.setattr(kc, "_failures", 0)
    monkeypatch.setattr(kc, "_skip_until", 0.0)
    for _ in range(kc._MAX_FAILURES):
        kc._record_failure()

    assert await kc.search_kiwi_flights("JFK", "LHR", "2026-12-10") == []
