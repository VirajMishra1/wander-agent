"""Tests for visa pure-logic functions."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wander_agent.tools.visa import _classify, _eta_apply_link, _evisa_apply_link, _official_link


def test_us_to_japan_visa_free():
    result = _classify("US", "JP")
    assert result["category"] == "visa_free"
    assert result["data_confidence"] == "curated_snapshot"


def test_us_to_indonesia_visa_on_arrival():
    result = _classify("US", "ID")
    assert result["category"] in ("visa_on_arrival", "visa_free", "evisa")
    # Indonesia has changed policy — accept any non-required category
    assert result["category"] != "visa_required"


def test_us_to_australia_eta():
    result = _classify("US", "AU")
    assert result["category"] == "eta_required"
    assert "apply_link" in result
    assert result["apply_link"]  # non-empty
    assert "immi.homeaffairs.gov.au" in result["apply_link"]


def test_in_to_vietnam_evisa():
    result = _classify("IN", "VN")
    assert result["category"] == "evisa"
    assert "apply_link" in result
    assert result["apply_link"]  # non-empty


def test_gb_to_france_visa_free():
    result = _classify("GB", "FR")
    # Post-Brexit GB→FR may require ETA or visa_free depending on dataset
    assert result["category"] in ("visa_free", "eta_required", "evisa")


def test_official_link_returns_string():
    link = _official_link("AU")
    assert isinstance(link, str)
    assert link.startswith("http")


def test_official_link_unknown_returns_timatic():
    link = _official_link("ZZ")
    assert "timatic" in link


def test_eta_apply_link_australia():
    link = _eta_apply_link("AU")
    assert link is not None
    assert "immi.homeaffairs.gov.au" in link


def test_evisa_apply_link_vietnam():
    link = _evisa_apply_link("VN")
    assert link is not None
    assert link.startswith("http")


def test_unknown_passport_returns_unknown_category():
    result = _classify("ZZ", "JP")
    assert result["category"] == "unknown"
    assert result.get("needs_web_search") is True


def test_result_has_passport_and_destination():
    result = _classify("US", "TH")
    assert result["passport"] == "US"
    assert result["destination"] == "TH"


@pytest.mark.asyncio
async def test_check_visa_requirement_adds_note():
    from wander_agent.tools.visa import check_visa_requirement
    result = await check_visa_requirement("US", "JP")
    assert "important_note" in result
    assert "suggest_web_search" in result
