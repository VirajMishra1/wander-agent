"""Activities and attractions via Wikidata SPARQL (no API key required)."""

from __future__ import annotations


# Descriptions that indicate administrative divisions, not tourist attractions
# Name patterns that indicate non-tourist items (matched against name, not description)
_BAD_NAME_KEYWORDS = frozenset({
    "post office", "bus company", "bus depot", "city bus", "taxi",
    "hospital", "clinic", "pharmacy", "police station", "fire station",
    "elementary school", "junior high", "high school", "primary school",
    "art college", "university hospital", "katsura hospital",
    "city hall", "ward office", "government office",
})

_ADMIN_DESC_KEYWORDS = frozenset({
    "municipality", "civil parish", "parish", "commune", "borough",
    "county", "district", "arrondissement", "township", "province",
    "prefecture", "ward", "neighbourhood", "neighborhood", "suburb",
    "administrative", "populated place", "human settlement",
    "urban district", "rural district", "local government",
    # Transport infrastructure
    "railway station", "train station", "metro station", "subway station",
    "bus station", "bus stop", "tram stop", "airport", "ferry terminal",
    "interchange station", "underground station",
    # Educational / civic
    "university", "college", "school", "high school", "primary school",
    "elementary school", "kindergarten",
    # Natural features (too generic)
    "river in", "stream in", "canal in", "lake in",
    # Other non-tourist
    "post office", "fire station", "police station", "hospital in",
})

CATEGORIES = {
    "culture": "Q570116",
    "nature": "Q1286517",
    "food": "Q571",
    "shopping": "Q1311958",
    "nightlife": "Q1627595",
    "architecture": "Q811979",
    "historic": "Q16970",   # place of worship — broader than Q210272 (historic district)
    "museums": "Q33506",
    "religion": "Q24398318",
    "art": "Q3305213",
    "parks": "Q22698",
    "sport": "Q941594",
}


async def search_activities(
    latitude: float,
    longitude: float,
    radius_km: int = 10,
    category: str | None = None,
    max_results: int = 15,
) -> dict:
    """Search for activities and attractions near a location using Wikidata.

    No API key required.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        radius_km: Search radius in kilometers (1-50)
        category: Filter: culture, nature, food, shopping, nightlife,
                  architecture, historic, museums, religion, art, parks, sport
        max_results: Maximum number of results (1-50)
    """
    from ..utils.http import get_client

    client = await get_client()
    radius_km = min(int(radius_km), 50)

    kind_filter = ""
    if category and category.lower() in CATEGORIES:
        qid = CATEGORIES[category.lower()]
        kind_filter = f"?item wdt:P31/wdt:P279* wd:{qid} ."

    sparql = f"""
    SELECT ?item ?itemLabel ?coord ?desc WHERE {{
      SERVICE wikibase:around {{
        ?item wdt:P625 ?coord .
        bd:serviceParam wikibase:center "Point({longitude} {latitude})"^^geo:wktLiteral .
        bd:serviceParam wikibase:radius "{radius_km}" .
      }}
      {kind_filter}
      OPTIONAL {{ ?item schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }} LIMIT {min(max_results * 4, 80)}
    """
    try:
        resp = await client.get(
            "https://query.wikidata.org/sparql",
            params={"query": sparql, "format": "json"},
            headers={
                "Accept": "application/sparql-results+json",
                "User-Agent": "WanderAgent/0.2.0 (open-source travel mcp)",
            },
            timeout=15.0,
        )
        if resp.status_code == 200:
            bindings = resp.json().get("results", {}).get("bindings", [])
            # If category filter returned nothing, retry without it
            if not bindings and kind_filter:
                sparql_broad = sparql.replace(kind_filter, "")
                resp2 = await client.get(
                    "https://query.wikidata.org/sparql",
                    params={"query": sparql_broad, "format": "json"},
                    headers={
                        "Accept": "application/sparql-results+json",
                        "User-Agent": "WanderAgent/0.2.0 (open-source travel mcp)",
                    },
                    timeout=15.0,
                )
                if resp2.status_code == 200:
                    bindings = resp2.json().get("results", {}).get("bindings", [])
            results = []
            for b in bindings:
                name = b.get("itemLabel", {}).get("value", "")
                if not name or name.startswith("Q"):
                    continue
                desc = b.get("desc", {}).get("value", "")
                # Skip administrative divisions (municipalities, parishes, etc.)
                desc_lower = desc.lower()
                if any(kw in desc_lower for kw in _ADMIN_DESC_KEYWORDS):
                    continue
                # Skip non-tourist items by name patterns
                name_lower = name.lower()
                if any(kw in name_lower for kw in _BAD_NAME_KEYWORDS):
                    continue
                # Skip items with generic transport/infrastructure names
                if (name_lower.endswith(" bus") or name_lower.endswith(" buses")
                        or " post office" in name_lower
                        or " hospital" in name_lower
                        or " school" in name_lower and "art school" not in name_lower
                        or "healthcare" in desc_lower
                        or desc_lower.startswith("healthcare")):
                    continue
                coord_str = b.get("coord", {}).get("value", "")
                lat_r = lon_r = None
                if coord_str.startswith("Point("):
                    parts = coord_str[6:-1].split()
                    if len(parts) == 2:
                        lon_r, lat_r = float(parts[0]), float(parts[1])
                results.append({
                    "name": name,
                    "kind": category or "attraction",
                    "distance_m": None,
                    "latitude": lat_r,
                    "longitude": lon_r,
                    "description": desc[:300],
                    "website": "",
                    "image": "",
                    "rating": None,
                    "data_confidence": "wikidata",
                })
                if len(results) >= max_results:
                    break
            return {
                "location": {"latitude": latitude, "longitude": longitude},
                "radius_km": radius_km,
                "category": category,
                "results_count": len(results),
                "activities": results,
                "data_source": "wikidata_sparql",
                "data_confidence": "wikidata",
            }
    except Exception:
        pass

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "category": category,
        "results_count": 0,
        "activities": [],
        "data_source": "none",
        "suggest_web_search": [
            f"top attractions near {latitude},{longitude}",
            f"things to do {category or 'sightseeing'} near me",
        ],
    }
