"""Travel advisories from US State Department RSS feed (no auth)."""

from __future__ import annotations

import re
import time
from html import unescape

# In-process cache (60 min TTL)
_cache: dict = {"data": None, "fetched_at": 0}
_CACHE_TTL = 3600


async def _fetch_advisories() -> dict:
    """Fetch and parse US State Dept advisory RSS feed. Cached 60min."""
    if _cache["data"] and time.time() - _cache["fetched_at"] < _CACHE_TTL:
        return _cache["data"]

    from ..utils.http import get_client

    client = await get_client()
    resp = await client.get(
        "https://travel.state.gov/_res/rss/TAsTWs.xml",
        headers={"User-Agent": "WanderAgent/0.1.0 (open-source travel mcp)"},
        timeout=15.0,
    )
    resp.raise_for_status()
    xml = resp.text

    advisories: dict = {}
    for item_match in re.finditer(r"<item>(.*?)</item>", xml, re.DOTALL):
        block = item_match.group(1)
        title = re.search(r"<title>([^<]+)</title>", block)
        link = re.search(r"<link>([^<]+)</link>", block)
        pub_date = re.search(r"<pubDate>([^<]+)</pubDate>", block)
        level = re.search(r'<category domain="Threat-Level">([^<]+)</category>', block)
        country_tag = re.search(r'<category domain="Country-Tag">([^<]+)</category>', block)
        desc = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", block, re.DOTALL)

        if not title:
            continue
        title_text = unescape(title.group(1))
        # Parse "Country - Level X: ..." or "Country Travel Advisory - Level X: ..."
        country_name = title_text.split(" - ")[0].strip() if " - " in title_text else title_text
        if country_name.lower().endswith(" travel advisory"):
            country_name = country_name[: -len(" travel advisory")].strip()
        level_text = level.group(1) if level else ""
        level_num = None
        m = re.search(r"Level (\d)", level_text)
        if m:
            level_num = int(m.group(1))

        desc_text = ""
        if desc:
            # Strip HTML
            raw = desc.group(1)
            clean = re.sub(r"<[^>]+>", " ", raw)
            clean = re.sub(r"\s+", " ", unescape(clean)).strip()
            desc_text = clean[:1500]

        entry = {
            "country": country_name,
            "country_code": country_tag.group(1).split(",")[0] if country_tag else "",
            "advisory_level": level_num,
            "advisory_label": level_text,
            "url": link.group(1) if link else "",
            "updated": pub_date.group(1) if pub_date else "",
            "summary": desc_text,
        }
        advisories[country_name.lower()] = entry
        if entry["country_code"]:
            advisories[entry["country_code"].lower()] = entry

    _cache["data"] = advisories
    _cache["fetched_at"] = time.time()
    return advisories


async def get_travel_advisory(country: str) -> dict:
    """Official US State Department travel advisory for a country.

    Returns advisory level (1-4), summary, and link to full advisory.
    Levels: 1=Normal Precautions, 2=Increased Caution, 3=Reconsider Travel,
    4=Do Not Travel.

    No API key required. Cached 60 minutes in-memory.

    Args:
        country: Country name in English (e.g., "Japan", "Egypt") or ISO code ("JP", "EG")
    """
    try:
        advisories = await _fetch_advisories()
        key = country.lower().strip()
        # ISO 3166-1 alpha-2 -> common country names for input convenience
        iso_to_name = {
            "jp": "japan", "fr": "france", "de": "germany", "it": "italy",
            "es": "spain", "gb": "united kingdom", "uk": "united kingdom",
            "us": "united states", "ca": "canada", "au": "australia",
            "nz": "new zealand", "br": "brazil", "ar": "argentina",
            "mx": "mexico", "co": "colombia", "pe": "peru", "cl": "chile",
            "cn": "china", "tw": "taiwan", "hk": "hong kong", "in": "india",
            "id": "indonesia", "th": "thailand", "vn": "vietnam",
            "ph": "philippines", "my": "malaysia", "sg": "singapore",
            "kr": "south korea", "ru": "russia", "tr": "turkey",
            "eg": "egypt", "ma": "morocco", "za": "south africa",
            "ke": "kenya", "ae": "united arab emirates", "il": "israel",
            "sa": "saudi arabia", "ir": "iran", "iq": "iraq", "sy": "syria",
            "ua": "ukraine", "pl": "poland", "se": "sweden", "no": "norway",
            "fi": "finland", "dk": "denmark", "nl": "netherlands",
            "be": "belgium", "ch": "switzerland", "at": "austria",
            "gr": "greece", "pt": "portugal", "ie": "ireland", "is": "iceland",
        }
        if len(key) == 2 and key in iso_to_name:
            key = iso_to_name[key]

        entry = advisories.get(key)
        if not entry:
            # Partial match by name
            for k, v in advisories.items():
                if len(k) > 2 and (key in k or k in key):
                    entry = v
                    break
        if not entry:
            return {
                "country": country,
                "error": f"No advisory found for '{country}'. Country may not be in State Dept list.",
                "available_countries_count": len({v["country"] for v in advisories.values()}),
            }

        risk_descriptors = {
            1: "Normal precautions - safe for travel",
            2: "Increased caution - elevated risks in some areas",
            3: "Reconsider travel - significant risks",
            4: "Do not travel - life-threatening risks",
        }

        return {
            "country": entry["country"],
            "country_code": entry["country_code"],
            "advisory_level": entry["advisory_level"],
            "advisory_label": entry["advisory_label"],
            "risk_description": risk_descriptors.get(entry["advisory_level"], "Unknown"),
            "updated": entry["updated"],
            "official_url": entry["url"],
            "summary": entry["summary"],
            "source": "US State Department",
        }
    except Exception as e:
        return {"error": str(e), "country": country}


async def list_advisories_by_level(min_level: int = 3) -> dict:
    """List all countries currently at or above a given advisory level.

    Useful for inspiration mode: "what countries should I avoid right now?"

    Args:
        min_level: Minimum advisory level (1-4). Default 3 = Reconsider Travel.
    """
    try:
        advisories = await _fetch_advisories()
        seen: set = set()
        results = []
        for entry in advisories.values():
            if entry["country"] in seen:
                continue
            seen.add(entry["country"])
            if entry["advisory_level"] and entry["advisory_level"] >= min_level:
                results.append({
                    "country": entry["country"],
                    "advisory_level": entry["advisory_level"],
                    "advisory_label": entry["advisory_label"],
                    "updated": entry["updated"],
                    "url": entry["url"],
                })
        results.sort(key=lambda x: -x["advisory_level"])
        return {
            "min_level": min_level,
            "results_count": len(results),
            "countries": results,
            "source": "US State Department",
        }
    except Exception as e:
        return {"error": str(e)}
