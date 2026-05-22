"""Tests for flights price parsing and output contract."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wander_agent.tools.flights import _parse_price


def test_parse_price_usd():
    amount, code = _parse_price("$1,234")
    assert amount == 1234.0
    assert code == "USD"


def test_parse_price_gbp():
    amount, code = _parse_price("£850")
    assert amount == 850.0
    assert code == "GBP"


def test_parse_price_eur():
    amount, code = _parse_price("€450")
    assert amount == 450.0
    assert code == "EUR"


def test_parse_price_inr():
    amount, code = _parse_price("₹17,180")
    assert amount == 17180.0
    assert code == "INR"


def test_parse_price_free():
    amount, code = _parse_price("free")
    assert amount == 0.0


def test_parse_price_na():
    amount, code = _parse_price("n/a")
    assert amount == 0.0


def test_parse_price_plain_number():
    amount, code = _parse_price("$299")
    assert amount == 299.0
    assert code == "USD"


def test_parse_price_with_decimals():
    amount, code = _parse_price("$1,299.99")
    assert amount == pytest.approx(1299.99, rel=1e-3)
    assert code == "USD"


def test_parse_price_us_prefix():
    # "US$300" — not in SYMBOL_TO_CODE, strips non-numeric, defaults to USD
    amount, code = _parse_price("US$300")
    assert amount == 300.0
    assert code == "USD"


def test_parse_price_returns_tuple():
    result = _parse_price("$500")
    assert isinstance(result, tuple)
    assert len(result) == 2
