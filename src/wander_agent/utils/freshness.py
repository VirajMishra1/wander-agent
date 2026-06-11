"""Data-freshness and trust metadata helpers.

Every tool result carries a `data_confidence` string. This module turns
that label into a structured `data_meta` block so the agent can tell the
traveler how much to trust each number and when it was fetched.
"""

from __future__ import annotations

from datetime import datetime, timezone

# label -> (trust_score 0-100, short label, plain-English meaning)
_CONFIDENCE: dict[str, dict] = {
    "scraped_live": {
        "trust": 80,
        "label": "Live scrape",
        "meaning": "Scraped from Google Flights just now. Real but can shift minute to minute.",
    },
    "live_rss": {
        "trust": 85,
        "label": "Live feed",
        "meaning": "Pulled live from an official government RSS feed.",
    },
    "live_forecast": {
        "trust": 85,
        "label": "Live forecast",
        "meaning": "Open-Meteo live weather forecast.",
    },
    "live_api": {
        "trust": 90,
        "label": "Live API",
        "meaning": "Fetched live from an official API (e.g. ECB rates, NOAA).",
    },
    "deeplink": {
        "trust": 95,
        "label": "Direct link",
        "meaning": "A booking/search deeplink — opens the live provider page.",
    },
    "curated_snapshot": {
        "trust": 55,
        "label": "Curated snapshot",
        "meaning": "Hand-curated dataset. Accurate at curation time, not real-time.",
    },
    "estimated": {
        "trust": 35,
        "label": "Estimate",
        "meaning": "Modeled/estimated figure. Use as a rough guide only.",
    },
    "wikidata_fallback": {
        "trust": 50,
        "label": "Wikidata fallback",
        "meaning": "Derived from Wikidata when no primary source was available.",
    },
    "unknown": {
        "trust": 30,
        "label": "Unverified",
        "meaning": "Source unknown — treat with caution.",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def confidence_meta(confidence: str) -> dict:
    info = _CONFIDENCE.get(confidence, _CONFIDENCE["unknown"])
    return {
        "confidence": confidence,
        "trust_score": info["trust"],
        "trust_label": info["label"],
        "meaning": info["meaning"],
    }


def stamp(
    result: dict,
    confidence: str,
    source: str | None = None,
    fetched_at: str | None = None,
) -> dict:
    """Attach a `data_meta` trust block to a tool result.

    Back-compat: also sets top-level `data_confidence` if absent so older
    callers keep working.
    """
    meta = confidence_meta(confidence)
    meta["fetched_at"] = fetched_at or now_iso()
    if source:
        meta["source"] = source
    result["data_meta"] = meta
    result.setdefault("data_confidence", confidence)
    return result
