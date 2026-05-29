"""Persistent fare-watch store at ~/.wander_agent/fare_watches.json.

A watch is a saved flight query plus a target price. On each check we
re-price and append to a price history, flipping status to "triggered"
when the live price falls to/below the threshold.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from .freshness import now_iso

_STORE = Path.home() / ".wander_agent" / "fare_watches.json"

_MAX_HISTORY = 60
_VALID_STATUS = {"active", "paused", "triggered"}


def _ensure() -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE.exists():
        _STORE.write_text("[]")


def load_watches() -> list[dict]:
    _ensure()
    try:
        return json.loads(_STORE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save(watches: list[dict]) -> None:
    _ensure()
    _STORE.write_text(json.dumps(watches, indent=2))


def create_watch(
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str | None = None,
    adults: int = 1,
    currency: str = "USD",
    threshold: float | None = None,
    baseline_price: float | None = None,
) -> dict:
    watches = load_watches()
    ts = now_iso()
    history = []
    if baseline_price is not None:
        history.append({"at": ts, "price": baseline_price})
    watch = {
        "id": uuid.uuid4().hex[:8],
        "origin": origin.upper(),
        "destination": destination.upper(),
        "depart_date": depart_date,
        "return_date": return_date,
        "adults": adults,
        "currency": currency.upper(),
        "threshold": threshold,
        "baseline_price": baseline_price,
        "last_price": baseline_price,
        "low_price": baseline_price,
        "status": "active",
        "created_at": ts,
        "history": history,
    }
    watches.append(watch)
    _save(watches)
    return watch


def list_watches(status: str | None = None) -> list[dict]:
    watches = load_watches()
    if status:
        return [w for w in watches if w.get("status") == status]
    return watches


def get_watch(watch_id: str) -> dict | None:
    for w in load_watches():
        if w["id"] == watch_id:
            return w
    return None


def record_price(watch_id: str, price: float) -> dict | None:
    watches = load_watches()
    for w in watches:
        if w["id"] == watch_id:
            w["last_price"] = price
            if w.get("low_price") is None or price < w["low_price"]:
                w["low_price"] = price
            if w.get("baseline_price") is None:
                w["baseline_price"] = price
            hist = w.setdefault("history", [])
            hist.append({"at": now_iso(), "price": price})
            if len(hist) > _MAX_HISTORY:
                del hist[: len(hist) - _MAX_HISTORY]
            thr = w.get("threshold")
            if thr is not None and price <= thr and w.get("status") == "active":
                w["status"] = "triggered"
            _save(watches)
            return w
    return None


def set_status(watch_id: str, status: str) -> dict | None:
    if status not in _VALID_STATUS:
        return None
    watches = load_watches()
    for w in watches:
        if w["id"] == watch_id:
            w["status"] = status
            _save(watches)
            return w
    return None


def delete_watch(watch_id: str) -> bool:
    watches = load_watches()
    new = [w for w in watches if w["id"] != watch_id]
    if len(new) == len(watches):
        return False
    _save(new)
    return True
