"""Offline country lookup backed by the vendored data/countries.json (from mledoze/countries)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent.parent / "data" / "countries.json"

# Countries that drive on the left. Not in the dataset, so listed here.
LEFT_DRIVING = frozenset({
    "AU", "NZ", "GB", "IE", "MT", "CY", "JP", "IN", "PK", "BD", "LK", "NP", "BT", "TH", "MY", "SG",
    "ID", "BN", "HK", "MO", "TL", "MV", "MU", "SC", "KE", "UG", "TZ", "ZM", "ZW", "BW", "NA", "ZA",
    "LS", "SZ", "MZ", "MW", "SR", "GY", "JM", "BS", "BB", "TT", "AG", "DM", "GD", "KN", "LC", "VC",
    "FJ", "PG", "SB", "WS", "TO",
})


@lru_cache(maxsize=1)
def _countries() -> list[dict]:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def find_country(query: str) -> dict | None:
    """Find a country by name, official name, alt spelling, or ISO-2/ISO-3 code."""
    q = query.strip().lower()
    if not q:
        return None
    countries = _countries()
    for c in countries:
        if q in (c["name"].lower(), c["official"].lower(), c["cca2"].lower(), c["cca3"].lower()) \
                or q in (a.lower() for a in c["alt"]):
            return c
    for c in countries:
        if q in c["name"].lower() or q in c["official"].lower():
            return c
    return None
