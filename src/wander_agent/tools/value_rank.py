"""Value ranking — score trip options on price + convenience, not price alone.

Pure scoring, no I/O. Feed it a JSON list of options (flights, packages,
whatever) and a priority preset; it returns a ranked list with a 0-100
value_score and a plain-English reason for the winner.
"""

from __future__ import annotations

import json

_DEFAULT_WEIGHTS = {
    "price": 0.40,
    "duration": 0.20,
    "convenience": 0.15,
    "flexibility": 0.10,
    "baggage": 0.08,
    "hassle": 0.07,
}

_PRESETS: dict[str, dict] = {
    "cheapest": {"price": 0.70, "duration": 0.10, "convenience": 0.08, "flexibility": 0.04, "baggage": 0.04, "hassle": 0.04},
    "fastest": {"price": 0.15, "duration": 0.55, "convenience": 0.15, "flexibility": 0.05, "baggage": 0.05, "hassle": 0.05},
    "easiest": {"price": 0.20, "duration": 0.15, "convenience": 0.30, "flexibility": 0.08, "baggage": 0.07, "hassle": 0.20},
    "flexible": {"price": 0.25, "duration": 0.12, "convenience": 0.13, "flexibility": 0.35, "baggage": 0.05, "hassle": 0.10},
    "balanced": _DEFAULT_WEIGHTS,
}


def _norm_cheaper_better(values: list[float | None]) -> list[float]:
    nums = [v for v in values if v is not None]
    if not nums:
        return [0.5 for _ in values]
    lo, hi = min(nums), max(nums)
    if hi == lo:
        return [1.0 if v is not None else 0.0 for v in values]
    out = []
    for v in values:
        if v is None:
            out.append(0.0)
        else:
            out.append((hi - v) / (hi - lo))
    return out


def _convenience_score(opt: dict) -> float:
    stops = opt.get("stops", 0) or 0
    score = max(0.0, 1.0 - 0.25 * stops)
    if opt.get("self_transfer") or opt.get("hidden_city") or opt.get("split_ticket"):
        score -= 0.30
    return max(0.0, min(1.0, score))


def _bool_score(opt: dict, key: str) -> float:
    return 1.0 if opt.get(key) else 0.4


def _hassle_score(opt: dict) -> float:
    score = 1.0
    if opt.get("visa_required"):
        score -= 0.4
    if opt.get("transit_visa_required"):
        score -= 0.3
    if opt.get("self_transfer"):
        score -= 0.2
    return max(0.0, min(1.0, score))


def _flags(opt: dict) -> list[str]:
    flags = []
    if opt.get("hidden_city"):
        flags.append("hidden-city (against airline T&Cs, no checked bags)")
    if opt.get("split_ticket"):
        flags.append("split ticket (missed-connection risk is on you)")
    if opt.get("self_transfer"):
        flags.append("self-transfer (re-check bags, re-clear security)")
    if opt.get("visa_required"):
        flags.append("visa required")
    if opt.get("transit_visa_required"):
        flags.append("transit visa required")
    return flags


def _winner_reason(opt: dict, priority: str) -> str:
    bits = []
    if opt.get("price") is not None:
        bits.append(f"price {opt.get('currency', '')}{opt['price']}".strip())
    stops = opt.get("stops")
    if stops is not None:
        bits.append("nonstop" if stops == 0 else f"{stops} stop(s)")
    if opt.get("refundable"):
        bits.append("refundable")
    base = ", ".join(bits) if bits else "best overall blend"
    return f"Best for '{priority}': {base}."


async def rank_trip_options(
    options_json: str,
    priority: str = "balanced",
    currency: str = "USD",
) -> dict:
    try:
        options = json.loads(options_json) if isinstance(options_json, str) else options_json
    except (json.JSONDecodeError, TypeError):
        return {"error": "options_json must be a JSON array of option objects."}
    if not isinstance(options, list) or not options:
        return {"error": "Provide a non-empty JSON array of options."}

    weights = _PRESETS.get(priority, _DEFAULT_WEIGHTS)

    price_norm = _norm_cheaper_better([o.get("price") for o in options])
    dur_norm = _norm_cheaper_better([o.get("duration_minutes") for o in options])

    ranked = []
    for i, opt in enumerate(options):
        sub = {
            "price": price_norm[i],
            "duration": dur_norm[i],
            "convenience": _convenience_score(opt),
            "flexibility": _bool_score(opt, "refundable"),
            "baggage": _bool_score(opt, "checked_bag_included"),
            "hassle": _hassle_score(opt),
        }
        score = sum(weights[k] * sub[k] for k in weights)
        ranked.append({
            "label": opt.get("label") or opt.get("name") or f"option_{i + 1}",
            "value_score": round(100 * score, 1),
            "price": opt.get("price"),
            "stops": opt.get("stops"),
            "subscores": {k: round(v, 2) for k, v in sub.items()},
            "flags": _flags(opt),
            "raw": opt,
        })

    ranked.sort(key=lambda x: x["value_score"], reverse=True)
    winner = ranked[0]
    return {
        "priority": priority,
        "weights": weights,
        "currency": currency.upper(),
        "ranked": ranked,
        "winner": winner["label"],
        "why": _winner_reason(winner["raw"], priority),
        "tip": "value_score blends price with duration, stops, refundability and hassle — not price alone.",
    }
