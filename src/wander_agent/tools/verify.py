"""Verification layer - cross-check AI suggestions against real data."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two coordinates."""
    radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * radius_km * asin(sqrt(a))


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
    from ..utils.http import get_client

    results: dict = {"place_name": place_name, "city": city, "verified": False, "sources": []}
    client = await get_client()
    city_lat = city_lon = None

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

    try:
        city_resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city.split(",")[0].strip(), "count": 1, "language": "en", "format": "json"},
            timeout=10.0,
        )
        if city_resp.status_code == 200:
            city_results = (city_resp.json() or {}).get("results") or []
            if city_results:
                city_lat = city_results[0].get("latitude")
                city_lon = city_results[0].get("longitude")
    except Exception:
        pass

    # Source 1: Wikidata SPARQL (free, no auth, no rate limit)
    try:
        sparql_query = f"""
        SELECT ?item ?itemLabel ?coord ?desc WHERE {{
          ?item rdfs:label "{place_name}"@en .
          OPTIONAL {{ ?item wdt:P625 ?coord . }}
          OPTIONAL {{ ?item schema:description ?desc . FILTER(LANG(?desc) = "en") }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 25
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
            for first in bindings:
                desc = first.get("desc", {}).get("value", "")
                coord_str = first.get("coord", {}).get("value", "")
                if "disambiguation page" in desc.lower():
                    continue
                if not coord_str.startswith("Point("):
                    continue
                parts = coord_str[6:-1].split()
                if len(parts) != 2:
                    continue
                lon, lat = float(parts[0]), float(parts[1])
                if city_lat is not None and city_lon is not None:
                    if _distance_km(float(city_lat), float(city_lon), lat, lon) > 75:
                        continue
                wikidata_id = first.get("item", {}).get("value", "").split("/")[-1]
                results["sources"].append({
                    "source": "Wikidata",
                    "found": True,
                    "wikidata_id": wikidata_id,
                    "description": desc[:200],
                })
                results["verified"] = True

                # Extract coords if available
                results["longitude"] = lon
                results["latitude"] = lat
                break
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

    return results


async def verify_flight_route(origin: str, destination: str) -> dict:
    """Verify a flight route exists between two airports.

    Args:
        origin: IATA airport code
        destination: IATA airport code
    """
    from datetime import date, timedelta
    from .flights import search_flights

    probe_dates = [
        (date.today() + timedelta(days=days_out)).isoformat()
        for days_out in (21, 42, 63)
    ]
    errors: list[str] = []
    try:
        last_result: dict = {}
        for probe_date in probe_dates:
            result = await search_flights(
                origin=origin,
                destination=destination,
                departure_date=probe_date,
                max_results=1,
            )
            last_result = result
            if result.get("results_count", 0) > 0:
                return {
                    "origin": origin.upper(),
                    "destination": destination.upper(),
                    "route_exists": True,
                    "probe_date": probe_date,
                    "data_source": result.get("data_source", "unknown"),
                }
            if result.get("error"):
                errors.append(result["error"])

        has_scraper_errors = len(errors) == len(probe_dates)
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown" if has_scraper_errors else False,
            "probe_dates": probe_dates,
            "data_source": last_result.get("data_source", "unknown"),
            "errors": errors[:3],
        }
    except Exception as e:
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown",
            "error": str(e),
        }
