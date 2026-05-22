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

    def _name_match(a: str, b: str) -> bool:
        """Strict: exact match, or full token containment with reasonable length ratio."""
        a, b = a.strip().lower(), b.strip().lower()
        if not a or not b:
            return False
        if a == b:
            return True
        if len(a) < 4 or len(b) < 4:
            return a == b
        if (a in b and len(a) / len(b) >= 0.5) or (b in a and len(b) / len(a) >= 0.5):
            return True
        return False

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
                if _name_match(g.get("name", ""), place_name) and (
                    g.get("admin1", "").lower() == city.lower() or
                    g.get("name", "").lower() == city.lower() or
                    city.lower() in (g.get("admin1") or "").lower()
                ):
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
                matching = [p for p in otm_data if _name_match(p.get("name", ""), place_name)]
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
    from datetime import date, timedelta
    from .flights import search_flights

    probe_date = (date.today() + timedelta(days=21)).isoformat()
    try:
        result = await search_flights(
            origin=origin,
            destination=destination,
            departure_date=probe_date,
            max_results=1,
        )
        has_route = result.get("results_count", 0) > 0
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": has_route,
            "probe_date": probe_date,
            "data_source": result.get("data_source", "unknown"),
        }
    except Exception as e:
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown",
            "error": str(e),
        }
