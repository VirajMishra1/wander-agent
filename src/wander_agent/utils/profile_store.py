"""Traveler profile persistence.

Stores profile in ~/.wander_agent/profile.json.
Schema versioned so future fields can be added without breaking existing profiles.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROFILE_DIR = Path.home() / ".wander_agent"
_PROFILE_PATH = _PROFILE_DIR / "profile.json"
_SCHEMA_VERSION = 1

# Defaults — everything optional so first-time users see partial profiles
_DEFAULT_PROFILE: dict[str, Any] = {
    "schema_version": _SCHEMA_VERSION,
    "created_at": None,
    "updated_at": None,
    # Identity
    "name": None,
    "home_airports": [],        # e.g. ["JFK", "EWR"] — nearby airports you use
    "passports": [],            # ISO-2 codes e.g. ["US", "IN"]
    "home_currency": "USD",
    # Preferences
    "preferred_seat": "no preference",  # aisle, window, no preference
    "preferred_cabin": "economy",       # economy, business, first
    "preferred_airlines": [],           # e.g. ["UA", "AA"]
    "travel_style": None,               # budget, moderate, luxury
    "dietary": [],                      # vegetarian, vegan, halal, kosher, gluten_free
    "interests": [],                    # beach, food, history, nature, nightlife, art, adventure
    # Visa/entry status (fast lookup so agent knows what traveler already holds)
    "visas_held": [],           # ISO-2 dest codes with currently valid visas
    "eta_held": [],             # ESTA, eTA, UK ETA, NZ ETA etc.
    # Trip history
    "past_trips": [],           # [{destination, from, to, purpose, logged_at}]
    # Loyalty programs
    "loyalty": [],              # [{airline, program, tier}]
    # Onboarding state
    "onboarded": False,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_profile() -> dict[str, Any]:
    """Load profile from disk. Returns defaults if not found."""
    if not _PROFILE_PATH.exists():
        profile = dict(_DEFAULT_PROFILE)
        profile["created_at"] = _now_iso()
        return profile
    try:
        with _PROFILE_PATH.open("r", encoding="utf-8") as f:
            stored = json.load(f)
        # Merge with defaults so new keys are always present
        merged = dict(_DEFAULT_PROFILE)
        merged.update(stored)
        return merged
    except Exception:
        profile = dict(_DEFAULT_PROFILE)
        profile["created_at"] = _now_iso()
        return profile


def save_profile(profile: dict[str, Any]) -> None:
    """Persist profile to disk."""
    _PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    profile["updated_at"] = _now_iso()
    profile.setdefault("created_at", _now_iso())
    tmp = _PROFILE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _PROFILE_PATH)


def update_profile_fields(**kwargs: Any) -> dict[str, Any]:
    """Merge kwargs into stored profile and save. Returns updated profile."""
    profile = load_profile()
    for key, value in kwargs.items():
        if key in _DEFAULT_PROFILE:
            profile[key] = value
    save_profile(profile)
    return profile


def add_trip(destination: str, from_date: str, to_date: str, purpose: str = "tourism") -> dict[str, Any]:
    """Append a completed or planned trip to history."""
    profile = load_profile()
    trip = {
        "destination": destination,
        "from": from_date,
        "to": to_date,
        "purpose": purpose,
        "logged_at": _now_iso(),
    }
    trips: list = profile.get("past_trips") or []
    trips.append(trip)
    profile["past_trips"] = trips[-50:]  # cap at 50
    save_profile(profile)
    return profile
