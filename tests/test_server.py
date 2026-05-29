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
    "tool_calculate_flight_carbon",
    "tool_calculate_jet_lag",
    "tool_check_transit_visa",
    "tool_check_travel_health",
    "tool_fare_calendar",
    "tool_find_cheapest_month",
    "tool_find_open_jaw",
    "tool_find_places",
    "tool_find_split_ticket",
    "tool_generate_packing_list",
    "tool_get_language_phrasebook",
    "tool_get_local_sim_guide",
    "tool_get_passport_power",
    "tool_get_stopover_guide",
    "tool_get_travel_news",
    "tool_score_nomad_cities",
    "tool_search_restaurants_bars",
    "tool_save_trip",
    "tool_list_my_trips",
    "tool_get_trip_status",
    "tool_update_trip",
    "tool_delete_trip",
    "tool_watch_fare",
    "tool_list_fare_watches",
    "tool_check_fare_watches",
    "tool_stop_fare_watch",
    "tool_rank_trip_options",
]


def test_server_file_exists():
    assert SERVER_FILE.exists(), f"server.py not found at {SERVER_FILE}"


def test_tool_count():
    content = SERVER_FILE.read_text()
    count = len(re.findall(r"@mcp\.tool\(\)", content))
    assert count == len(EXPECTED_TOOLS), (
        f"Expected {len(EXPECTED_TOOLS)} @mcp.tool() decorators, found {count}"
    )


def test_all_expected_tools_present():
    content = SERVER_FILE.read_text()
    missing = [t for t in EXPECTED_TOOLS if t not in content]
    assert missing == [], f"Missing tools in server.py: {missing}"
