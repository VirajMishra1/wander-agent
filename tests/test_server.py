"""Verify all expected tools are registered in server.py — static grep, no import needed."""
from __future__ import annotations

import re
import sys
from pathlib import Path

SERVER_FILE = Path(__file__).parent.parent / "src" / "wander_agent" / "server.py"

EXPECTED_TOOLS = [
    "tool_find_destinations_by_budget",
    "tool_cheap_anywhere_from",
    "tool_compare_destinations",
    "tool_search_flights",
    "tool_search_hotels",
    "tool_plan_itinerary",
    "tool_optimize_budget",
    "tool_get_travel_advisory",
    "tool_list_advisories_by_level",
    "tool_get_local_events",
    "tool_get_cost_of_living",
    "tool_score_destinations",
    "tool_best_month_to_visit",
    "tool_get_weather",
    "tool_convert_currency",
    "tool_get_exchange_rates",
    "tool_search_activities",
    "tool_get_destination_info",
    "tool_geocode",
    "tool_verify_place",
    "tool_verify_flight_route",
    "tool_find_skiplagged_fares",
    "tool_multi_origin_meetup",
    "tool_find_aurora_destinations",
    "tool_find_mistake_fares",
    "tool_check_visa_requirement",
    "tool_visa_free_destinations",
    "tool_get_traveler_profile",
    "tool_onboard_traveler",
    "tool_update_traveler_profile",
    "tool_get_trip_history",
    "tool_search_ground_transport",
    "tool_plan_trip_package",
]


def test_server_file_exists():
    assert SERVER_FILE.exists(), f"server.py not found at {SERVER_FILE}"


def test_tool_count():
    content = SERVER_FILE.read_text()
    count = len(re.findall(r"@mcp\.tool\(\)", content))
    assert count == 33, f"Expected 33 @mcp.tool() decorators, found {count}"


def test_all_expected_tools_present():
    content = SERVER_FILE.read_text()
    missing = [t for t in EXPECTED_TOOLS if t not in content]
    assert missing == [], f"Missing tools in server.py: {missing}"
