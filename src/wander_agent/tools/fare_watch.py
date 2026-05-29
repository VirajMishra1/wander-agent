"""Fare-watch tools — save a flight query + target price, re-price on demand."""

from __future__ import annotations

import asyncio

from ..utils import watch_store


def _delta(baseline: float | None, current: float | None) -> dict:
    if baseline is None or current is None:
        return {"abs": None, "pct": None}
    abs_change = round(current - baseline, 2)
    pct = round(100 * (current - baseline) / baseline, 1) if baseline else None
    return {"abs": abs_change, "pct": pct}


async def watch_fare(
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str | None = None,
    adults: int = 1,
    currency: str = "USD",
    target_price: float | None = None,
) -> dict:
    from .flights import search_flights

    baseline = None
    try:
        r = await search_flights(
            origin=origin,
            destination=destination,
            departure_date=depart_date,
            return_date=return_date,
            adults=adults,
            max_results=1,
            currency=currency,
        )
        baseline = r.get("cheapest_price")
    except Exception:
        baseline = None

    watch = watch_store.create_watch(
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        return_date=return_date,
        adults=adults,
        currency=currency,
        threshold=target_price,
        baseline_price=baseline,
    )
    return {
        "watching": True,
        "watch_id": watch["id"],
        "baseline_price": baseline,
        "target_price": target_price,
        "currency": currency.upper(),
        "tip": "Call check_fare_watches later to re-price. Triggers when price <= target.",
    }


async def list_fare_watches(status: str | None = None) -> dict:
    watches = watch_store.list_watches(status=status)
    return {
        "count": len(watches),
        "status_filter": status or "all",
        "watches": [
            {
                "watch_id": w["id"],
                "route": f"{w['origin']}->{w['destination']}",
                "depart_date": w.get("depart_date"),
                "return_date": w.get("return_date"),
                "baseline_price": w.get("baseline_price"),
                "last_price": w.get("last_price"),
                "low_price": w.get("low_price"),
                "target_price": w.get("threshold"),
                "status": w.get("status"),
                "currency": w.get("currency"),
            }
            for w in watches
        ],
    }


async def check_fare_watches(watch_id: str | None = None) -> dict:
    from .flights import search_flights

    if watch_id:
        watches = [w for w in watch_store.list_watches() if w["id"] == watch_id]
    else:
        watches = watch_store.list_watches(status="active")

    if not watches:
        return {"checked": 0, "alerts": [], "note": "No matching watches."}

    sem = asyncio.Semaphore(5)

    async def _reprice(w: dict) -> dict:
        async with sem:
            baseline = w.get("baseline_price")
            try:
                r = await search_flights(
                    origin=w["origin"],
                    destination=w["destination"],
                    departure_date=w["depart_date"],
                    return_date=w.get("return_date"),
                    adults=w.get("adults", 1),
                    max_results=1,
                    currency=w.get("currency", "USD"),
                )
                current = r.get("cheapest_price")
            except Exception:
                current = None

            if current is None:
                return {
                    "watch_id": w["id"],
                    "route": f"{w['origin']}->{w['destination']}",
                    "alert": "no_price",
                    "current_price": None,
                }

            updated = watch_store.record_price(w["id"], current)
            thr = w.get("threshold")
            delta = _delta(baseline, current)

            if thr is not None and current <= thr:
                alert = "target_hit"
            elif baseline is not None and current < baseline:
                alert = "price_drop"
            elif baseline is not None and current > baseline:
                alert = "price_rise"
            else:
                alert = "no_change"

            return {
                "watch_id": w["id"],
                "route": f"{w['origin']}->{w['destination']}",
                "alert": alert,
                "baseline_price": baseline,
                "current_price": current,
                "low_price": (updated or {}).get("low_price"),
                "target_price": thr,
                "change": delta,
                "status": (updated or {}).get("status"),
                "currency": w.get("currency"),
            }

    alerts = await asyncio.gather(*[_reprice(w) for w in watches])
    return {
        "checked": len(alerts),
        "alerts": alerts,
        "tip": "Surface target_hit and price_drop alerts first — those are buy signals.",
    }


async def stop_fare_watch(watch_id: str, delete: bool = False) -> dict:
    if delete:
        ok = watch_store.delete_watch(watch_id)
        return {"deleted": ok, "watch_id": watch_id}
    w = watch_store.set_status(watch_id, "paused")
    if not w:
        return {"error": f"No watch with id {watch_id}"}
    return {"paused": True, "watch_id": watch_id, "status": w["status"]}
