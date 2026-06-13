"""Tests for credit card points/miles tools."""
from __future__ import annotations

import pytest

from wander_agent.data import points_data
from wander_agent.tools import points


@pytest.fixture(autouse=True)
def mock_profile(monkeypatch):
    monkeypatch.setattr(
        points, "load_profile",
        lambda: {
            "cards": [
                {"card_key": "chase_sapphire_reserve", "program": "chase_ur", "balance": 80000},
                {"card_key": "amex_gold", "program": "amex_mr", "balance": 60000},
            ]
        },
    )


# ---- data module ----

def test_program_valuations_has_major_programs():
    for key in ("chase_ur", "amex_mr", "hyatt_woh", "united_mp"):
        assert key in points_data.PROGRAM_VALUATIONS


def test_transfer_partners_chase():
    partners = points_data.TRANSFER_PARTNERS["chase_ur"]
    partner_keys = {p["partner"] for p in partners}
    assert "hyatt_woh" in partner_keys
    assert "united_mp" in partner_keys


def test_find_programs_for_partner():
    progs = points_data.find_programs_for_partner("hyatt_woh")
    assert "chase_ur" in progs
    assert "bilt" in progs


def test_find_sweet_spots_for_programs():
    spots = points_data.find_sweet_spots_for_programs(["chase_ur"])
    assert any("Hyatt" in s["name"] for s in spots)


def test_cards_have_required_fields():
    for key, card in points_data.CARDS.items():
        assert "name" in card
        assert "program" in card
        assert "annual_fee" in card
        assert "base_earn" in card


# ---- estimate_points_value ----

@pytest.mark.asyncio
async def test_estimate_points_value_good():
    result = await points.estimate_points_value(
        points_cost=60000, cash_price=1200.0, program="chase_ur"
    )
    assert result["verdict"] == "good"
    assert result["cents_per_point"] == 2.0


@pytest.mark.asyncio
async def test_estimate_points_value_poor():
    result = await points.estimate_points_value(
        points_cost=60000, cash_price=300.0, program="chase_ur"
    )
    assert result["verdict"] == "poor"


@pytest.mark.asyncio
async def test_estimate_points_value_unknown_program():
    result = await points.estimate_points_value(
        points_cost=10000, cash_price=100.0, program="fake_program"
    )
    assert "error" in result


# ---- find_transfer_partners ----

@pytest.mark.asyncio
async def test_find_transfer_partners():
    result = await points.find_transfer_partners("chase_ur")
    assert result["total_partners"] > 5
    partner_names = [p["partner"] for p in result["partners"]]
    assert any("Hyatt" in n for n in partner_names)


@pytest.mark.asyncio
async def test_find_transfer_partners_airline_program():
    result = await points.find_transfer_partners("united_mp")
    assert result["partners"] == []


# ---- calculate_points_or_cash ----

@pytest.mark.asyncio
async def test_points_or_cash_use_points():
    result = await points.calculate_points_or_cash(
        cash_price=800.0, points_price=30000, program="chase_ur"
    )
    assert result["recommendation"] == "use_points"
    assert result["cents_per_point"] > 1.5


@pytest.mark.asyncio
async def test_points_or_cash_pay_cash():
    result = await points.calculate_points_or_cash(
        cash_price=100.0, points_price=50000, program="chase_ur"
    )
    assert result["recommendation"] == "pay_cash"


# ---- estimate_points_earning ----

@pytest.mark.asyncio
async def test_estimate_earning_dining():
    result = await points.estimate_points_earning(
        amount=100.0, card_key="chase_sapphire_reserve", category="dining"
    )
    assert result["points_earned"] == 300
    assert result["multiplier"] == "3x"


@pytest.mark.asyncio
async def test_estimate_earning_base():
    result = await points.estimate_points_earning(
        amount=500.0, card_key="amex_gold", category="general"
    )
    assert result["points_earned"] == 500


@pytest.mark.asyncio
async def test_estimate_earning_unknown_card():
    result = await points.estimate_points_earning(
        amount=100.0, card_key="fake_card"
    )
    assert "error" in result


# ---- find_sweet_spot_awards ----

@pytest.mark.asyncio
async def test_sweet_spots_from_profile():
    result = await points.find_sweet_spot_awards()
    assert result["total_sweet_spots"] > 0
    assert any("ANA" in s["name"] for s in result["sweet_spots"])


@pytest.mark.asyncio
async def test_sweet_spots_filtered_by_cabin():
    result = await points.find_sweet_spot_awards(
        programs="chase_ur", cabin="business"
    )
    for s in result["sweet_spots"]:
        assert "business" in s["cabin"].lower()


@pytest.mark.asyncio
async def test_sweet_spots_filtered_by_max_points():
    result = await points.find_sweet_spot_awards(
        programs="chase_ur,amex_mr", max_points=50000
    )
    for s in result["sweet_spots"]:
        assert s["points_required"] <= 50000


@pytest.mark.asyncio
async def test_sweet_spots_filtered_by_route():
    result = await points.find_sweet_spot_awards(
        programs="amex_mr", route_keyword="Japan"
    )
    assert result["total_sweet_spots"] >= 1


# ---- compare_points_programs ----

@pytest.mark.asyncio
async def test_compare_programs_from_profile():
    result = await points.compare_points_programs(cash_price=1000.0)
    assert result["programs_compared"] == 2
    assert "recommendation" in result


@pytest.mark.asyncio
async def test_compare_programs_explicit():
    result = await points.compare_points_programs(
        cash_price=500.0, programs="chase_ur,citi_typ,bilt"
    )
    assert result["programs_compared"] == 3
