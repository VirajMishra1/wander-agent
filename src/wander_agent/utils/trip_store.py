"""Persistent trip store at ~/.wander_agent/trips.json.

A trip is a stateful object the agent builds up over multiple sessions:
destination, dates, a booking checklist, and shortlisted flight/hotel
options. This is the memory that no OTA gives you.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

_STORE = Path.home() / ".wander_agent" / "trips.json"

_VALID_STATUS = {"planning", "booked", "completed", "cancelled"}

_DEFAULT_CHECKLIST = [
    "book_flights",
    "book_hotel",
    "check_visa",
    "travel_insurance",
    "book_ground_transport",
    "check_advisory",
    "pack",
    "notify_bank",
]


def _ensure() -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE.exists():
        _STORE.write_text("[]")


def load_trips() -> list[dict]:
    _ensure()
    try:
        return json.loads(_STORE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save(trips: list[dict]) -> None:
    _ensure()
    _STORE.write_text(json.dumps(trips, indent=2))


def _new_checklist() -> dict:
    return {k: {"done": False, "note": ""} for k in _DEFAULT_CHECKLIST}


def create_trip(
    destination: str,
    depart_date: str | None = None,
    return_date: str | None = None,
    origin: str | None = None,
    travelers: int = 1,
    passport_country: str | None = None,
    purpose: str | None = None,
    notes: str | None = None,
) -> dict:
    trips = load_trips()
    trip = {
        "id": uuid.uuid4().hex[:8],
        "destination": destination,
        "origin": origin,
        "depart_date": depart_date,
        "return_date": return_date,
        "travelers": travelers,
        "passport_country": passport_country,
        "purpose": purpose,
        "notes": notes or "",
        "status": "planning",
        "checklist": _new_checklist(),
        "shortlist": {"flights": [], "hotels": []},
    }
    trips.append(trip)
    _save(trips)
    return trip


def list_trips(status: str | None = None) -> list[dict]:
    trips = load_trips()
    if status:
        return [t for t in trips if t.get("status") == status]
    return trips


def get_trip(trip_id: str) -> dict | None:
    for t in load_trips():
        if t["id"] == trip_id:
            return t
    return None


def find_trip_by_destination(destination: str) -> dict | None:
    dl = destination.strip().lower()
    matches = [t for t in load_trips() if dl in (t.get("destination") or "").lower()]
    if not matches:
        return None
    # prefer active (non-cancelled/completed) trips
    active = [t for t in matches if t.get("status") in ("planning", "booked")]
    return (active or matches)[-1]


def update_trip(trip_id: str, **fields) -> dict | None:
    trips = load_trips()
    for t in trips:
        if t["id"] == trip_id:
            for k, v in fields.items():
                if v is None:
                    continue
                if k == "status" and v not in _VALID_STATUS:
                    continue
                t[k] = v
            _save(trips)
            return t
    return None


def set_checklist_item(trip_id: str, key: str, done: bool, note: str | None = None) -> dict | None:
    trips = load_trips()
    for t in trips:
        if t["id"] == trip_id:
            cl = t.setdefault("checklist", _new_checklist())
            item = cl.setdefault(key, {"done": False, "note": ""})
            item["done"] = done
            if note is not None:
                item["note"] = note
            _save(trips)
            return t
    return None


def attach_option(trip_id: str, kind: str, option: dict) -> dict | None:
    if kind not in ("flights", "hotels"):
        return None
    trips = load_trips()
    for t in trips:
        if t["id"] == trip_id:
            sl = t.setdefault("shortlist", {"flights": [], "hotels": []})
            sl.setdefault(kind, []).append(option)
            _save(trips)
            return t
    return None


def delete_trip(trip_id: str) -> bool:
    trips = load_trips()
    new = [t for t in trips if t["id"] != trip_id]
    if len(new) == len(trips):
        return False
    _save(new)
    return True


def checklist_progress(trip: dict) -> dict:
    cl = trip.get("checklist") or {}
    total = len(cl)
    done = sum(1 for v in cl.values() if v.get("done"))
    pct = round(100 * done / total) if total else 0
    return {
        "done": done,
        "total": total,
        "percent": pct,
        "remaining": [k for k, v in cl.items() if not v.get("done")],
    }
