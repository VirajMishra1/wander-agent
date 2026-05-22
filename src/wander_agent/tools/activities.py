"""Activities and attractions using OpenTripMap API."""

from __future__ import annotations


async def _search_activities_wikidata(
    latitude: float,
    longitude: float,
    radius_km: int,
    category: str | None,
    max_results: int,
) -> dict:
    """Wikidata SPARQL fallback for attractions near a location. No API key needed."""
    from ..utils.http import get_client

    client = await get_client()
    radius_m = min(radius_km, 50) * 1000

    # Map our category labels to Wikidata instance-of values
    _WD_KINDS: dict[str, str] = {
        "museums": "Q33506",
        "historic": "Q210272",
        "culture": "Q570116",
        "religion": "Q24398318",
        "architecture": "Q811979",
        "nature": "Q1286517",
        "parks": "Q22698",
        "art": "Q3305213",
    }
    kind_filter = ""
    if category and category.lower() in _WD_KINDS:
        qid = _WD_KINDS[category.lower()]
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
    }} LIMIT {min(max_results * 2, 40)}
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
            results = []
            for b in bindings:
                name = b.get("itemLabel", {}).get("value", "")
                if not name or name.startswith("Q"):  # skip unnamed items
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
                    "description": b.get("desc", {}).get("value", "")[:300],
                    "website": "",
                    "image": "",
                    "rating": None,
                    "data_confidence": "wikidata_fallback",
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
                "data_confidence": "wikidata_fallback",
                "note": "Set OPENTRIPMAP_API_KEY for richer attraction data.",
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
        "note": "Set OPENTRIPMAP_API_KEY for attraction data. Wikidata query also failed.",
        "suggest_web_search": [
            f"top attractions near {latitude},{longitude}",
            f"things to do {category or 'sightseeing'} near me",
        ],
    }


CATEGORIES = {
    "culture": "cultural",
    "nature": "natural",
    "food": "foods",
    "shopping": "shops",
    "nightlife": "amusements",
    "architecture": "architecture",
    "historic": "historic",
    "museums": "museums",
    "religion": "religion",
    "sport": "sport",
}


async def search_activities(
    latitude: float,
    longitude: float,
    radius_km: int = 10,
    category: str | None = None,
    max_results: int = 15,
) -> dict:
    """Search for activities and attractions near a location.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        radius_km: Search radius in kilometers (1-50)
        category: Filter by category: culture, nature, food, shopping, nightlife, architecture, historic, museums, religion, sport
        max_results: Maximum number of results (1-50)
    """
    from ..utils.config import OPENTRIPMAP_KEY
    from ..utils.http import get_client

    if not OPENTRIPMAP_KEY:
        # Wikidata SPARQL fallback — no API key needed, returns real attractions
        return await _search_activities_wikidata(latitude, longitude, radius_km, category, max_results)

    client = await get_client()
    base = "https://api.opentripmap.com/0.1/en/places"

    params: dict = {
        "lat": latitude,
        "lon": longitude,
        "radius": min(radius_km, 50) * 1000,
        "limit": min(max_results, 50),
        "apikey": OPENTRIPMAP_KEY,
        "rate": 3,  # minimum rating
        "format": "json",
    }
    if category and category.lower() in CATEGORIES:
        params["kinds"] = CATEGORIES[category.lower()]

    resp = await client.get(f"{base}/radius", params=params)
    resp.raise_for_status()
    places = resp.json()

    results = []
    for place in places:
        if not place.get("name"):
            continue

        # Get details for top results
        detail = {}
        if place.get("xid") and len(results) < max_results:
            try:
                detail_resp = await client.get(
                    f"{base}/xid/{place['xid']}",
                    params={"apikey": OPENTRIPMAP_KEY},
                )
                if detail_resp.status_code == 200:
                    detail = detail_resp.json()
            except Exception:
                pass

        results.append({
            "name": place.get("name", ""),
            "kind": place.get("kinds", "").split(",")[0] if place.get("kinds") else "",
            "distance_m": place.get("dist"),
            "latitude": place.get("point", {}).get("lat"),
            "longitude": place.get("point", {}).get("lon"),
            "description": (detail.get("wikipedia_extracts") or {}).get("text", "")[:300] if detail else "",
            "website": detail.get("url", ""),
            "image": detail.get("image", ""),
            "rating": place.get("rate"),
        })

    results.sort(key=lambda x: -(x.get("rating") or 0))

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "category": category,
        "results_count": len(results),
        "activities": results[:max_results],
    }
