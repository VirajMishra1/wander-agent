"""Tests for airport_data pure-logic functions."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wander_agent.utils.airport_data import city_to_iata, get_nearby_airports, iata_to_city


def test_city_to_iata_new_york():
    assert city_to_iata("New York") == "JFK"


def test_city_to_iata_london():
    assert city_to_iata("London") == "LHR"


def test_city_to_iata_tokyo():
    assert city_to_iata("Tokyo") == "NRT"


def test_city_to_iata_case_insensitive():
    assert city_to_iata("new york") == city_to_iata("New York")


def test_city_to_iata_unknown_returns_none():
    assert city_to_iata("Nonexistent City ZZZZZZ") is None


def test_iata_to_city_jfk():
    result = iata_to_city("JFK")
    assert result is not None
    assert "york" in result.lower() or "new york" in result.lower()


def test_nearby_airports_jfk():
    nearby = get_nearby_airports("JFK")
    assert "EWR" in nearby
    assert "LGA" in nearby


def test_nearby_airports_dxb():
    nearby = get_nearby_airports("DXB")
    assert "SHJ" in nearby
    assert "AUH" in nearby


def test_nearby_airports_lhr():
    nearby = get_nearby_airports("LHR")
    assert len(nearby) >= 2


def test_nearby_airports_unknown_returns_empty():
    assert get_nearby_airports("ZZZ") == []


def test_nearby_airports_no_self_reference():
    nearby = get_nearby_airports("JFK")
    assert "JFK" not in nearby
