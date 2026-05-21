"""Verification layer - cross-check AI suggestions against real data."""

from __future__ import annotations


async def verify_place(
    place_name: str,
    city: str,
    expected_type: str | None = None,
) -> dict:
    """Verify that a place (restaurant, attraction, hotel) actually exists.

    Use this to cross-check AI-generated recommendations against real data.
    Catches hallucinations before they reach the user.

    Args:
        place_name: Name of the place to verify (e.g., "Eiffel Tower", "Le Jules Verne")
        city: City where the place should be (e.g., "Paris")
        expected_type: Expected type: restaurant, attraction, hotel, museum, park
    """
    from ..utils.config import FOURSQUARE_KEY
    from ..utils.http import get_client

    results = {"place_name": place_name, "city": city, "verified": False, "sources": []}

    # Source 1: Nominatim/OpenStreetMap (free, no auth)
    client = await get_client()
    try:
        osm_resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": f"{place_name}, {city}",
                "format": "json",
                "limit": 3,
                "addressdetails": 1,
            },
            headers={"User-Agent": "WanderAgent/0.1.0 (travel-verification)"},
        )
        if osm_resp.status_code == 200:
            osm_data = osm_resp.json()
            if osm_data:
                best = osm_data[0]
                results["sources"].append({
                    "source": "OpenStreetMap",
                    "found": True,
                    "display_name": best.get("display_name", ""),
                    "latitude": float(best.get("lat", 0)),
                    "longitude": float(best.get("lon", 0)),
                    "type": best.get("type", ""),
                })
                results["verified"] = True
                results["latitude"] = float(best.get("lat", 0))
                results["longitude"] = float(best.get("lon", 0))
    except Exception:
        pass

    # Source 2: Foursquare (if key available)
    if FOURSQUARE_KEY:
        try:
            fsq_resp = await client.get(
                "https://api.foursquare.com/v3/places/search",
                params={
                    "query": place_name,
                    "near": city,
                    "limit": 3,
                },
                headers={
                    "Authorization": FOURSQUARE_KEY,
                    "Accept": "application/json",
                },
            )
            if fsq_resp.status_code == 200:
                fsq_data = fsq_resp.json()
                places = fsq_data.get("results", [])
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
                else:
                    results["sources"].append({"source": "Foursquare", "found": False})
        except Exception:
            pass

    # Source 3: OpenTripMap (for attractions)
    from ..utils.config import OPENTRIPMAP_KEY
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

    confidence = len([s for s in results["sources"] if s.get("found", False)])
    results["confidence"] = "high" if confidence >= 2 else "medium" if confidence == 1 else "not_found"
    results["recommendation"] = (
        "Place verified across multiple sources - safe to recommend."
        if confidence >= 2
        else "Place found in one source - likely real but verify details."
        if confidence == 1
        else "Place NOT found in any source - likely hallucinated. Do not recommend."
    )

    return results


async def verify_flight_route(
    origin: str,
    destination: str,
) -> dict:
    """Verify that a flight route exists between two airports.

    Args:
        origin: Departure IATA airport code
        destination: Arrival IATA airport code
    """
    from ..utils.config import TRAVELPAYOUTS_TOKEN
    from ..utils.http import get_client

    if not TRAVELPAYOUTS_TOKEN:
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "route_exists": "unknown",
            "note": "TRAVELPAYOUTS_TOKEN required for route verification.",
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
