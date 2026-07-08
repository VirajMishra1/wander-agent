"""Test cost-of-living lookup fallback chain: city → country → region."""

from wander_agent.utils.cost_data import lookup_cost


def test_city_exact_match():
    result = lookup_cost(city="Tokyo")
    assert result is not None
    assert result["match_type"] == "city"
    assert result["daily_budget_usd"] > 0


def test_country_fallback():
    result = lookup_cost(city="nonexistent-city", country="Japan")
    assert result is not None
    assert result["match_type"] == "country_fallback"
    assert result["daily_budget_usd"] > 0


def test_regional_fallback():
    result = lookup_cost(city="nonexistent", country="Bangladesh")
    assert result is not None
    assert result["match_type"] == "regional_estimate"
    assert "south asia" in result["matched_name"].lower()
    assert result["daily_budget_usd"] > 0


def test_unknown_returns_none():
    result = lookup_cost(city="nonexistent", country="atlantis")
    assert result is None


def test_case_insensitive():
    result = lookup_cost(city="TOKYO")
    assert result is not None
    assert result["match_type"] == "city"
