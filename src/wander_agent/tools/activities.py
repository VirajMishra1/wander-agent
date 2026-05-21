"""Activities and attractions using OpenTripMap API."""

from __future__ import annotations


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
        return {"error": "OPENTRIPMAP_API_KEY not configured in .env"}

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
