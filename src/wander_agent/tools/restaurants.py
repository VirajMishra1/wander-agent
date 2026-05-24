"""Restaurant, bar, pub, and cafe search.

Primary source: OpenStreetMap Overpass API (global, no key required).
Optional enrichment: Foursquare Places API v3 (free tier, set FOURSQUARE_API_KEY).
Returns deeplinks to Google Maps, Zomato, TripAdvisor, Yelp, OpenTable, Foursquare.
"""

from __future__ import annotations

import math
import os


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _price_label(osm_level: str | None, cuisine: str) -> str:
    if osm_level:
        return {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}.get(int(osm_level), "$$")
    c = (cuisine or "").lower()
    if any(k in c for k in ["fast_food", "burger", "sandwich", "kebab", "noodle", "pizza"]):
        return "$"
    if any(k in c for k in ["french", "steak", "sushi", "seafood", "omakase", "tasting"]):
        return "$$$"
    return "$$"


def _deeplinks(name: str, lat: float, lon: float, city_hint: str, amenity: str) -> dict:
    n = name.replace(" ", "+")
    loc = city_hint.replace(" ", "+")
    links: dict = {
        "google_maps": f"https://www.google.com/maps/search/{n}/@{lat},{lon},17z",
        "google_reviews": f"https://www.google.com/search?q={n}+{loc}+restaurant+reviews",
        "zomato": f"https://www.zomato.com/search?q={n}&location={loc}",
        "tripadvisor": f"https://www.tripadvisor.com/Search?q={n}+{loc}",
        "yelp": f"https://www.yelp.com/search?find_desc={n}&find_loc={loc}",
        "foursquare": f"https://foursquare.com/explore?q={n}&near={loc}",
    }
    if amenity == "restaurant":
        links["opentable"] = f"https://www.opentable.com/s/?restaurantName={n}&metroName={loc}"
        links["resy"] = f"https://resy.com/cities/search?query={n}"
    if amenity in ("bar", "pub", "cocktail_bar", "biergarten"):
        links["untappd"] = f"https://untappd.com/search?q={n}"
    return links


_AMENITY_MAP: dict[str, list[str]] = {
    "restaurant": ["restaurant"],
    "bar": ["bar", "cocktail_bar"],
    "pub": ["pub", "biergarten"],
    "cafe": ["cafe"],
    "nightlife": ["nightclub", "bar", "cocktail_bar", "music_venue"],
    "all": ["restaurant", "bar", "pub", "cafe", "nightclub", "biergarten", "cocktail_bar"],
}

_FSQ_CATS: dict[str, str] = {
    "restaurant": "13000",
    "bar": "13003,13059",
    "pub": "13004",
    "cafe": "13034,13032",
    "nightlife": "10032,13003",
    "all": "13000,13003,13004,13034,10032,13059",
}


async def search_restaurants_bars(
    latitude: float,
    longitude: float,
    category: str = "all",
    radius_m: int = 1000,
    max_results: int = 15,
    cuisine: str | None = None,
    city: str | None = None,
) -> dict:
    """Find restaurants, bars, pubs, cafes near a location with ratings and booking links.

    Returns real venues with cuisine, price level, opening hours, distance,
    ratings (if FOURSQUARE_API_KEY set), and direct links to Google Maps,
    Zomato, TripAdvisor, Yelp, OpenTable, Resy, Foursquare.

    Data source: OpenStreetMap (global, no key). Ratings: Foursquare (optional key).

    Args:
        latitude: Location latitude
        longitude: Location longitude
        category: restaurant | bar | pub | cafe | nightlife | all
        radius_m: Search radius in metres (100-5000). Default 1000m = ~10min walk.
        max_results: Max venues to return (1-30)
        cuisine: Optional cuisine filter e.g. "italian", "japanese", "indian", "thai"
        city: City name for better search links (e.g. "Tokyo", "Paris")
    """
    from ..utils.http import get_client

    client = await get_client()
    radius_m = max(100, min(int(radius_m), 5000))
    max_results = max(1, min(int(max_results), 30))
    cat = category.lower()
    amenities = _AMENITY_MAP.get(cat, _AMENITY_MAP["all"])
    amenity_re = "|".join(amenities)
    city_hint = city or f"{latitude:.4f},{longitude:.4f}"
    fsq_key = os.environ.get("FOURSQUARE_API_KEY", "")

    # --- OSM Overpass ---
    overpass_q = (
        f"[out:json][timeout:20];\n"
        f"(\n"
        f'  node["amenity"~"{amenity_re}"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  way["amenity"~"{amenity_re}"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f");\n"
        f"out body center {max_results * 6};\n"
    )

    places: list[dict] = []
    try:
        resp = await client.post(
            "https://overpass-api.de/api/interpreter",
            content=overpass_q,
            headers={"Content-Type": "text/plain"},
            timeout=20.0,
        )
        if resp.status_code == 200:
            for el in resp.json().get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name", "").strip()
                if not name:
                    continue
                lat_p = el["lat"] if el.get("type") == "node" else el.get("center", {}).get("lat")
                lon_p = el["lon"] if el.get("type") == "node" else el.get("center", {}).get("lon")
                if not lat_p or not lon_p:
                    continue
                el_cuisine = tags.get("cuisine", "").replace(";", ", ").replace("_", " ")
                # cuisine filter
                if cuisine and cuisine.lower() not in (el_cuisine + " " + name).lower():
                    continue
                addr = " ".join(filter(None, [
                    tags.get("addr:housenumber", ""),
                    tags.get("addr:street", ""),
                    tags.get("addr:city", ""),
                ])).strip()
                amenity = tags.get("amenity", cat)
                places.append({
                    "name": name,
                    "type": amenity,
                    "cuisine": el_cuisine or None,
                    "address": addr or None,
                    "phone": tags.get("phone") or tags.get("contact:phone"),
                    "website": tags.get("website") or tags.get("contact:website"),
                    "opening_hours": tags.get("opening_hours"),
                    "price_level": _price_label(tags.get("price_level"), el_cuisine),
                    "features": {
                        "outdoor_seating": tags.get("outdoor_seating") == "yes",
                        "takeaway": tags.get("takeaway") in ("yes", "only"),
                        "delivery": tags.get("delivery") == "yes",
                        "wheelchair": tags.get("wheelchair") in ("yes", "limited"),
                        "wifi": tags.get("internet_access") in ("wlan", "yes", "wifi"),
                        "reservations": tags.get("reservation") in ("yes", "recommended", "required"),
                    },
                    "latitude": lat_p,
                    "longitude": lon_p,
                    "distance_m": round(_haversine_m(latitude, longitude, lat_p, lon_p)),
                    "rating": None,
                    "rating_out_of": None,
                    "rating_source": None,
                    "booking_links": _deeplinks(name, lat_p, lon_p, city_hint, amenity),
                    "data_confidence": "osm_live",
                })
    except Exception:
        pass

    # --- Foursquare enrichment / fallback ---
    if fsq_key:
        fsq_cat = _FSQ_CATS.get(cat, "13000")
        try:
            fsq_resp = await client.get(
                "https://api.foursquare.com/v3/places/search",
                headers={"Authorization": fsq_key, "Accept": "application/json"},
                params={
                    "ll": f"{latitude},{longitude}",
                    "radius": radius_m,
                    "categories": fsq_cat,
                    "limit": min(max_results * 2, 50),
                    "sort": "RATING",
                    **({"query": cuisine} if cuisine else {}),
                },
                timeout=10.0,
            )
            if fsq_resp.status_code == 200:
                fsq_results = fsq_resp.json().get("results", [])
                fsq_by_name = {r["name"].lower(): r for r in fsq_results if r.get("name")}

                if not places:
                    # Use Foursquare as primary source
                    for r in fsq_results[:max_results * 2]:
                        name = r.get("name", "")
                        if not name:
                            continue
                        geo = r.get("geocodes", {}).get("main", {})
                        lat_p, lon_p = geo.get("latitude"), geo.get("longitude")
                        if not lat_p:
                            continue
                        loc = r.get("location", {})
                        addr = ", ".join(filter(None, [
                            loc.get("address"), loc.get("locality"), loc.get("country")
                        ]))
                        cats = r.get("categories", [{}])
                        type_name = cats[0].get("name", category) if cats else category
                        price_num = r.get("price")
                        price_lbl = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}.get(price_num, "$$")
                        rating = r.get("rating")
                        places.append({
                            "name": name,
                            "type": type_name,
                            "cuisine": None,
                            "address": addr or None,
                            "phone": r.get("tel"),
                            "website": r.get("website"),
                            "opening_hours": None,
                            "price_level": price_lbl,
                            "features": {},
                            "latitude": lat_p,
                            "longitude": lon_p,
                            "distance_m": round(_haversine_m(latitude, longitude, lat_p, lon_p)),
                            "rating": rating,
                            "rating_out_of": 10.0 if rating else None,
                            "rating_source": "foursquare",
                            "booking_links": _deeplinks(name, lat_p, lon_p, city_hint, "restaurant"),
                            "data_confidence": "foursquare_live",
                        })
                else:
                    # Enrich OSM places with Foursquare ratings + price
                    for p in places:
                        match = fsq_by_name.get(p["name"].lower())
                        if match:
                            p["rating"] = match.get("rating")
                            p["rating_out_of"] = 10.0 if match.get("rating") else None
                            p["rating_source"] = "foursquare"
                            if match.get("price"):
                                p["price_level"] = {1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}.get(
                                    match["price"], p["price_level"]
                                )
                            p["data_confidence"] = "osm_live+foursquare_ratings"
        except Exception:
            pass

    # Sort: rated first (desc rating), then by distance
    places.sort(key=lambda x: (-(x["rating"] or 0), x["distance_m"]))
    places = places[:max_results]

    # Highlights
    rated = [p for p in places if p.get("rating")]
    budget = [p for p in places if p.get("price_level") == "$"]
    closest = sorted(places, key=lambda x: x["distance_m"])

    has_ratings = any(p.get("rating") for p in places)
    data_src = "openstreetmap" + ("+foursquare" if fsq_key else " (set FOURSQUARE_API_KEY for ratings)")

    return {
        "location": {"latitude": latitude, "longitude": longitude, "city": city_hint},
        "category": category,
        "cuisine_filter": cuisine,
        "radius_m": radius_m,
        "results_count": len(places),
        "sorted_by": "rating then distance" if has_ratings else "distance",
        "places": places,
        "highlights": {
            "top_rated": rated[0]["name"] if rated else None,
            "top_rated_score": f"{rated[0]['rating']}/10 ({rated[0]['rating_source']})" if rated else None,
            "budget_pick": budget[0]["name"] if budget else None,
            "closest": closest[0]["name"] if closest else None,
            "closest_distance_m": closest[0]["distance_m"] if closest else None,
        },
        "data_source": data_src,
        "data_confidence": "osm_live" if not fsq_key else "osm_live+foursquare",
        "tip": (
            "Add FOURSQUARE_API_KEY env var for real ratings. "
            "All booking_links open live reviews. "
            "Google Maps link shows exact location + hours."
        ),
        "suggest_web_search": [
            f"best {cuisine or category} {city_hint} 2026 reddit",
            f"hidden gem {category} {city_hint} locals recommend",
        ],
    }
