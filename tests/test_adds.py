"""Tests for the trip-memory, fare-watch, value-rank, freshness adds."""
from __future__ import annotations

import json

import pytest

from wander_agent.utils import freshness, trip_store, watch_store
from wander_agent.tools import value_rank


@pytest.fixture(autouse=True)
def tmp_stores(tmp_path, monkeypatch):
    monkeypatch.setattr(trip_store, "_STORE", tmp_path / "trips.json")
    monkeypatch.setattr(watch_store, "_STORE", tmp_path / "fare_watches.json")
    yield


# ---- freshness ----

def test_confidence_meta_known():
    m = freshness.confidence_meta("scraped_live")
    assert m["trust_score"] == 80
    assert m["trust_label"] == "Live scrape"


def test_confidence_meta_unknown_falls_back():
    m = freshness.confidence_meta("nonsense")
    assert m["trust_score"] == 30


def test_stamp_adds_meta_and_backcompat():
    r = freshness.stamp({}, "estimated", source="model")
    assert r["data_meta"]["confidence"] == "estimated"
    assert r["data_meta"]["source"] == "model"
    assert r["data_confidence"] == "estimated"
    assert "fetched_at" in r["data_meta"]


# ---- trip_store ----

def test_create_and_progress():
    t = trip_store.create_trip("Tokyo", "2026-08-01", "2026-08-10")
    assert len(t["id"]) == 8
    p = trip_store.checklist_progress(t)
    assert p["total"] == 8 and p["done"] == 0 and p["percent"] == 0


def test_checklist_tick_persists():
    t = trip_store.create_trip("Bali")
    trip_store.set_checklist_item(t["id"], "book_flights", True, "Emirates")
    reloaded = trip_store.get_trip(t["id"])
    assert reloaded["checklist"]["book_flights"]["done"] is True
    assert reloaded["checklist"]["book_flights"]["note"] == "Emirates"
    assert trip_store.checklist_progress(reloaded)["percent"] == 12


def test_find_by_destination_prefers_active():
    trip_store.create_trip("Rome")
    a = trip_store.create_trip("Rome")
    trip_store.update_trip(a["id"], status="cancelled")
    found = trip_store.find_trip_by_destination("rome")
    assert found["id"] != a["id"]


def test_attach_and_delete():
    t = trip_store.create_trip("Lisbon")
    trip_store.attach_option(t["id"], "flights", {"price": 400})
    assert trip_store.get_trip(t["id"])["shortlist"]["flights"][0]["price"] == 400
    assert trip_store.delete_trip(t["id"]) is True
    assert trip_store.get_trip(t["id"]) is None


# ---- watch_store ----

def test_watch_triggers_on_threshold():
    w = watch_store.create_watch("JFK", "LHR", "2026-09-01", threshold=900, baseline_price=1100)
    assert w["status"] == "active"
    updated = watch_store.record_price(w["id"], 880)
    assert updated["status"] == "triggered"
    assert updated["low_price"] == 880


def test_watch_no_trigger_above_threshold():
    w = watch_store.create_watch("JFK", "CDG", "2026-09-01", threshold=500, baseline_price=700)
    updated = watch_store.record_price(w["id"], 650)
    assert updated["status"] == "active"
    assert updated["last_price"] == 650


def test_watch_history_capped():
    w = watch_store.create_watch("JFK", "FCO", "2026-09-01")
    for i in range(watch_store._MAX_HISTORY + 10):
        watch_store.record_price(w["id"], 500 + i)
    assert len(watch_store.get_watch(w["id"])["history"]) == watch_store._MAX_HISTORY


# ---- value_rank ----

@pytest.mark.asyncio
async def test_rank_cheapest_picks_low_price():
    opts = [
        {"label": "A", "price": 1000, "stops": 0, "refundable": True},
        {"label": "B", "price": 400, "stops": 1, "split_ticket": True},
    ]
    r = await value_rank.rank_trip_options(json.dumps(opts), priority="cheapest")
    assert r["winner"] == "B"


@pytest.mark.asyncio
async def test_rank_easiest_avoids_hassle():
    opts = [
        {"label": "cheap_messy", "price": 400, "stops": 2, "self_transfer": True, "hidden_city": True},
        {"label": "clean", "price": 600, "stops": 0, "refundable": True, "checked_bag_included": True},
    ]
    r = await value_rank.rank_trip_options(json.dumps(opts), priority="easiest")
    assert r["winner"] == "clean"
    flags = [o["flags"] for o in r["ranked"] if o["label"] == "cheap_messy"][0]
    assert any("hidden-city" in f for f in flags)


@pytest.mark.asyncio
async def test_rank_rejects_bad_input():
    assert "error" in await value_rank.rank_trip_options("[]")
    assert "error" in await value_rank.rank_trip_options("not json")
