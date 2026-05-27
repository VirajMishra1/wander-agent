"""Natural and special places finder — OSM Overpass (no API key)."""
from __future__ import annotations
import math


def _dist_m(lat1, lon1, lat2, lon2):
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))


_CATEGORY_QUERIES: dict[str, list[tuple[str, str]]] = {
    "viewpoint":   [("tourism", "viewpoint"), ("tourism", "attraction")],
    "beach":       [("natural", "beach"), ("leisure", "beach_resort")],
    "hiking":      [("natural", "peak"), ("natural", "saddle"), ("route", "hiking")],
    "coworking":   [("amenity", "coworking_space")],
    "waterfall":   [("waterway", "waterfall"), ("natural", "waterfall")],
    "camping":     [("tourism", "camp_site"), ("tourism", "caravan_site")],
    "market":      [("amenity", "marketplace"), ("shop", "mall")],
    "hot_spring":  [("natural", "hot_spring"), ("amenity", "spa")],
    "museum":      [("tourism", "museum"), ("tourism", "gallery")],
    "park":        [("leisure", "nature_reserve"), ("leisure", "park"), ("boundary", "national_park")],
}


# These categories rarely have names in OSM — don't require ["name"] filter
_NO_NAME_FILTER = {"viewpoint", "beach", "waterfall", "hot_spring", "camping"}


def _build_overpass(
    tags_list: list[tuple[str, str]], radius_m: int, lat: float, lon: float,
    limit: int, require_name: bool = True,
) -> str:
    name_f = '["name"]' if require_name else ""
    parts = []
    for k, v in tags_list:
        parts.append(f'  node["{k}"="{v}"]{name_f}(around:{radius_m},{lat},{lon});')
        parts.append(f'  way["{k}"="{v}"]{name_f}(around:{radius_m},{lat},{lon});')
        parts.append(f'  relation["{k}"="{v}"]{name_f}(around:{radius_m},{lat},{lon});')
    return "[out:json][timeout:20];\n(\n" + "\n".join(parts) + f"\n);\nout body center {limit};\n"


async def find_places(
    latitude: float,
    longitude: float,
    category: str = "viewpoint",
    radius_km: int = 15,
    max_results: int = 12,
    city: str | None = None,
) -> dict:
    """Find natural and special places near a location using OpenStreetMap.

    No API key required. Categories:
    - viewpoint: Scenic viewpoints, photo spots, panoramas
    - beach: Public beaches and beach resorts
    - hiking: Mountain peaks, hiking trailheads, saddles
    - coworking: Coworking spaces for digital nomads
    - waterfall: Waterfalls and natural water features
    - camping: Campsites and caravan parks
    - market: Local markets and bazaars
    - hot_spring: Hot springs and natural spas
    - museum: Museums and art galleries
    - park: Nature reserves and national parks

    Args:
        latitude: Location latitude
        longitude: Location longitude
        category: See categories above
        radius_km: Search radius in km (1-50)
        max_results: Max results (1-30)
        city: City name for better links
    """
    from ..utils.http import get_client

    client = await get_client()
    radius_m = max(1000, min(int(radius_km) * 1000, 50000))
    max_results = max(1, min(int(max_results), 30))
    cat = category.lower()
    tags = _CATEGORY_QUERIES.get(cat, _CATEGORY_QUERIES["viewpoint"])
    city_hint = city or f"{latitude:.4f},{longitude:.4f}"
    query = _build_overpass(tags, radius_m, latitude, longitude, max_results * 5,
                             require_name=cat not in _NO_NAME_FILTER)

    places = []
    try:
        resp = await client.post(
            "https://overpass-api.de/api/interpreter",
            content=query,
            headers={"Content-Type": "text/plain"},
            timeout=20.0,
        )
        if resp.status_code == 200:
            for el in resp.json().get("elements", []):
                t = el.get("tags", {})
                name = t.get("name", "").strip()
                if not name:
                    if cat in _NO_NAME_FILTER:
                        # Use natural:name, nat_name, or fall back to type label
                        name = (t.get("nat_name") or t.get("natural") or
                                t.get("tourism") or t.get("waterway") or
                                t.get("leisure") or cat).strip().title()
                    else:
                        continue
                lat_p = el.get("lat") if el.get("type") == "node" else el.get("center", {}).get("lat")
                lon_p = el.get("lon") if el.get("type") == "node" else el.get("center", {}).get("lon")
                if not lat_p or not lon_p:
                    continue

                dist = _dist_m(latitude, longitude, lat_p, lon_p)
                n = name.replace(" ", "+")
                loc = city_hint.replace(" ", "+")
                elevation = t.get("ele")
                desc = t.get("description") or t.get("note") or t.get("wikipedia", "")

                place = {
                    "name": name,
                    "category": cat,
                    "description": desc[:300] if desc else None,
                    "latitude": lat_p,
                    "longitude": lon_p,
                    "distance_m": dist,
                    "elevation_m": int(elevation) if elevation and str(elevation).isdigit() else None,
                    "website": t.get("website") or t.get("contact:website"),
                    "opening_hours": t.get("opening_hours"),
                    "fee": t.get("fee"),  # "yes"/"no"
                    "access": t.get("access"),
                    "surface": t.get("surface"),  # for hiking: gravel/rock/dirt
                    "links": {
                        "google_maps": f"https://www.google.com/maps?q={lat_p},{lon_p}&ll={lat_p},{lon_p}&z=16",
                        "google_maps_search": f"https://www.google.com/maps/search/{n}/@{lat_p},{lon_p},16z",
                        "google_photos": f"https://www.google.com/search?q={n}+{loc}&tbm=isch",
                        "alltrails": f"https://www.alltrails.com/explore?q={n}" if cat == "hiking" else None,
                        "wikiloc": f"https://www.wikiloc.com/trails/hiking?q={n}" if cat == "hiking" else None,
                        "wikidata": f"https://www.wikidata.org/wiki/{t.get('wikidata')}" if t.get("wikidata") else None,
                        "tripadvisor": f"https://www.tripadvisor.com/Search?q={n}+{loc}",
                    },
                    "data_source": "openstreetmap",
                    "data_confidence": "osm_live",
                }
                # Remove None links
                place["links"] = {k: v for k, v in place["links"].items() if v}
                places.append(place)
                if len(places) >= max_results:
                    break
    except Exception:
        pass

    places.sort(key=lambda x: x["distance_m"])

    # Category-specific tips
    tips = {
        "viewpoint": "Arrive at sunrise/sunset for best photography light.",
        "beach": "Check local tide times. Blue Flag beaches are safest.",
        "hiking": "Tell someone your route. Carry 2L water + emergency snack.",
        "coworking": "Call ahead to check availability and day-pass prices.",
        "waterfall": "Best flow after rainy season. Slippery — wear grip shoes.",
        "camping": "Book peak season sites weeks ahead. Check fire restrictions.",
        "market": "Mornings are freshest. Bargain respectfully — start at 60% of asking.",
        "hot_spring": "Check temperature (safe = 36-42°C). Avoid if pregnant.",
        "museum": "Most offer free entry on first Sunday of the month.",
        "park": "Download offline map. Rangers can advise on trail conditions.",
    }.get(cat, "Verify opening hours before visiting.")

    return {
        "location": {"latitude": latitude, "longitude": longitude, "city": city_hint},
        "category": cat,
        "radius_km": radius_km,
        "results_count": len(places),
        "places": places,
        "closest": places[0]["name"] if places else None,
        "tip": tips,
        "data_source": "openstreetmap_overpass",
        "suggest_web_search": [
            f"best {cat} near {city_hint} 2026",
            f"{city_hint} {cat} hidden gems local guide",
        ],
    }
