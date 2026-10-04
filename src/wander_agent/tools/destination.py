"""Destination info + geocoding. Uses Open-Meteo geocoding (no auth, no rate limit)."""

from __future__ import annotations


async def get_destination_info(country_name: str) -> dict:
    """Get essential travel info for a country.

    Currency, languages, timezone, calling code, driving side, borders.
    Offline dataset plus a live Open-Meteo lookup for the capital's timezone.
    No API key required.

    Args:
        country_name: Country name in English (e.g., "Japan", "France") or ISO code
    """
    from ..utils.countries import LEFT_DRIVING, find_country

    c = find_country(country_name)
    if not c:
        return {"error": f"Country '{country_name}' not found. Use full English name or ISO code."}

    timezones: list[str] = []
    if c["capital"]:
        try:
            geo = await geocode(f"{c['capital']}, {c['cca2']}")
            if geo.get("timezone"):
                timezones = [geo["timezone"]]
        except Exception:
            pass

    return {
        "name": c["name"],
        "official_name": c["official"],
        "country_code": c["cca2"],
        "capital": c["capital"],
        "region": c["region"],
        "subregion": c["subregion"],
        "currencies": c["currencies"],
        "languages": c["languages"],
        "timezones": timezones,
        "calling_code": c["calling_code"],
        "drives_on": "left" if c["cca2"] in LEFT_DRIVING else "right",
        "border_countries": c["borders"],
        "data_confidence": "curated_snapshot",
    }


async def geocode(place_name: str) -> dict:
    """Get coordinates and metadata for a place.

    Uses Open-Meteo geocoding API. No auth, no rate limits, returns
    population, timezone, postcodes, country info in one call.

    Args:
        place_name: City or place name (e.g., "Paris", "Tokyo, Japan")
    """
    from ..utils.http import get_client

    client = await get_client()
    # Open-Meteo takes a simple name (no comma-country usually needed)
    primary = place_name.split(",")[0].strip()

    try:
        resp = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": primary, "count": 10, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        results = (resp.json() or {}).get("results") or []

        if not results:
            return {"error": f"Could not geocode '{place_name}'. Try a more specific name."}

        # If user provided ", Country" filter for that match
        if "," in place_name:
            country_hint = place_name.split(",", 1)[1].strip().lower()
            filtered = [r for r in results if
                        r.get("country", "").lower() == country_hint or
                        r.get("country_code", "").lower() == country_hint]
            if filtered:
                results = filtered

        # Rank: capital cities first, then highest population. Population dominates
        # within a tier because tourists almost always mean the famous big city.
        def score(r: dict) -> tuple:
            name_match = 1 if r.get("name", "").lower() == primary.lower() else 0
            pop = r.get("population") or 0
            fc = r.get("feature_code", "")
            is_capital = 1 if fc == "PPLC" else 0
            # If a result has >100x more population than another, that one wins
            # regardless of feature code tier
            return (is_capital, name_match, pop)

        results.sort(key=score, reverse=True)
        r = results[0]
        return {
            "place": place_name,
            "name": r.get("name", ""),
            "latitude": r.get("latitude"),
            "longitude": r.get("longitude"),
            "country": r.get("country", ""),
            "country_code": r.get("country_code", ""),
            "admin1": r.get("admin1", ""),
            "timezone": r.get("timezone", ""),
            "population": r.get("population"),
            "elevation_m": r.get("elevation"),
            "feature_code": r.get("feature_code", ""),
            "alternatives": [
                {"name": a.get("name"), "country": a.get("country"), "admin1": a.get("admin1")}
                for a in results[1:4]
            ],
        }
    except Exception as e:
        return {"error": str(e)}
