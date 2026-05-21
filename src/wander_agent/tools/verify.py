"""Verification layer - cross-check AI suggestions against real data."""

from __future__ import annotations


async def verify_place(
    place_name: str,
    city: str,
    expected_type: str | None = None,
) -> dict:
    """Verify a place exists. Cross-checks Open-Meteo geocoder, Wikidata,
    Foursquare (if key), and OpenTripMap (if key).

    Catches AI hallucinations. Returns confidence level.

    Args:
        place_name: Place name (e.g., "Eiffel Tower", "Le Jules Verne")
        city: City context (e.g., "Paris")
        expected_type: restaurant, attraction, hotel, museum, park
    """
    from ..utils.config import FOURSQUARE_KEY, OPENTRIPMAP_KEY
    from ..utils.http import get_client

    results: dict = {"place_name": place_name, "city": city, "verified": False, "sources": []}
    client = await get_client()

    # Source 1: Wikidata SPARQL (free, no auth, no rate limit)
    try:
        sparql_query = f"""
        SELECT ?item ?itemLabel ?coord ?desc WHERE {{
          ?item rdfs:label "{place_name}"@en .
          OPTIONAL {{ ?item wdt:P625 ?coord . }}
          OPTIONAL {{ ?item schema:description ?desc . FILTER(LANG(?desc) = "en") }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 5
        """
        wd_resp = await client.get(
            "https://query.wikidata.org/sparql",
            params={"query": sparql_query, "format": "json"},
            headers={
                "Accept": "application/sparql-results+json",
                "User-Agent": "WanderAgent/0.1.0 (open-source travel mcp)",
            },
            timeout=15.0,
        )
        if wd_resp.status_code == 200:
            bindings = wd_resp.json().get("results", {}).get("bindings", [])
            if bindings:
                first = bindings[0]
                desc = first.get("desc", {}).get("value", "")
                wikidata_id = first.get("item", {}).get("value", "").split("/")[-1]
                results["sources"].append({
                    "source": "Wikidata",
                    "found": True,
                    "wikidata_id": wikidata_id,
                    "description": desc[:200],
                })
                results["verified"] = True

                # Extract coords if available
                coord_str = first.get("coord", {}).get("value", "")
                if coord_str.startswith("Point("):
                    parts = coord_str[6:-1].split()
                    if len(parts) == 2:
                        results["longitude"] = float(parts[0])
                        results["latitude"] = float(parts[1])
    except Exception:
        pass

    # Source 2: Open-Meteo geocoding (free, no auth, no rate limit)
    try:
        geo_resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place_name, "count": 3, "language": "en", "format": "json"},
            timeout=10.0,
        )
        if geo_resp.status_code == 200:
            geo_results = (geo_resp.json() or {}).get("results") or []
            for g in geo_results:
                # Must be in the right city or nearby
                if (g.get("admin1", "").lower() == city.lower() or
                    g.get("name", "").lower() == city.lower() or
                    place_name.lower() in g.get("name", "").lower()):
                    results["sources"].append({
                        "source": "Open-Meteo Geocoding",
                        "found": True,
                        "name": g.get("name", ""),
                        "country": g.get("country", ""),
                        "feature_code": g.get("feature_code", ""),
                    })
                    if not results.get("latitude"):
                        results["latitude"] = g.get("latitude")
                        results["longitude"] = g.get("longitude")
                    break
    except Exception:
        pass

    # Source 3: Foursquare (if key)
    if FOURSQUARE_KEY:
        try:
            fsq_resp = await client.get(
                "https://api.foursquare.com/v3/places/search",
                params={"query": place_name, "near": city, "limit": 3},
                headers={"Authorization": FOURSQUARE_KEY, "Accept": "application/json"},
                timeout=10.0,
            )
            if fsq_resp.status_code == 200:
                places = fsq_resp.json().get("results", [])
                if places:
                    p = places[0]
                    results["sources"].append({
                        "source": "Foursquare",
                        "found": True,
                        "name": p.get("name", ""),
                        "address": p.get("location", {}).get("formatted_address", ""),
                        "categories": [c.get("name", "") for c in p.get("categories", [])],
                    })
                    results["verified"] = True
        except Exception:
            pass

    # Source 4: OpenTripMap (if key + coords)
    if OPENTRIPMAP_KEY and results.get("latitude"):
        try:
            otm_resp = await client.get(
                "https://api.opentripmap.com/0.1/en/places/radius",
                params={
                    "lat": results["latitude"],
                    "lon": results["longitude"],
                    "radius": 500,
                    "limit": 5,
                    "apikey": OPENTRIPMAP_KEY,
                    "format": "json",
                },
                timeout=10.0,
            )
            if otm_resp.status_code == 200:
                otm_data = otm_resp.json()
                matching = [p for p in otm_data if place_name.lower() in (p.get("name", "").lower())]
                if matching:
                    results["sources"].append({
                        "source": "OpenTripMap",
                        "found": True,
                        "name": matching[0].get("name", ""),
                        "kinds": matching[0].get("kinds", ""),
                    })
        except Exception:
            pass

    confidence_count = len([s for s in results["sources"] if s.get("found", False)])
    if confidence_count >= 2:
        results["confidence"] = "high"
        results["recommendation"] = "Place verified across multiple sources. Safe to recommend."
    elif confidence_count == 1:
        results["confidence"] = "medium"
        results["recommendation"] = "Place found in one source. Verify details before recommending."
    else:
        results["confidence"] = "not_found"
        results["recommendation"] = "Place NOT found in any source. Likely hallucinated. Do not recommend."

    return results


async def verify_flight_route(origin: str, destination: str) -> dict:
    """Verify a flight route exists between two airports.

    Args:
        origin: IATA airport code
        destination: IATA airport code
    """
    from ..utils.config import TRAVELPAYOUTS_TOKEN
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown",
            "note": "TRAVELPAYOUTS_TOKEN required.",
        }

    client = await get_client()
    try:
        resp = await client.get(
            "https://api.travelpayouts.com/v1/prices/direct",
            params={
                "origin": origin.upper(),
                "destination": destination.upper(),
                "token": TRAVELPAYOUTS_TOKEN,
            },
        )
        if resp.status_code != 200:
            return {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "route_exists": "unknown",
                "note": f"API returned {resp.status_code}",
            }
        data = resp.json()
        has_route = bool(data.get("data"))

        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": has_route,
            "has_direct_flights": has_route,
            "source": "travelpayouts",
        }
    except Exception as e:
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown",
            "error": str(e),
        }
