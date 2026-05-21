"""Destination info + geocoding. Uses Open-Meteo geocoding (no auth, no rate limit)."""

from __future__ import annotations


async def get_destination_info(country_name: str) -> dict:
    """Get essential travel info for a country.

    Currency, languages, timezone, calling code, visa-free travel info.
    No API key required.

    Args:
        country_name: Country name in English (e.g., "Japan", "France")
    """
    from ..utils.http import get_client

    client = await get_client()
    resp = await client.get(
        f"https://restcountries.com/v3.1/name/{country_name}",
        params={"fields": "name,currencies,languages,timezones,capital,population,region,subregion,flags,cca2,idd,car,maps,borders"},
    )

    if resp.status_code == 404:
        return {"error": f"Country '{country_name}' not found. Use full English name."}

    resp.raise_for_status()
    countries = resp.json()
    if not countries:
        return {"error": f"No results for '{country_name}'"}

    c = countries[0]
    currencies = c.get("currencies", {})
    languages = c.get("languages", {})

    return {
        "name": c.get("name", {}).get("common", country_name),
        "official_name": c.get("name", {}).get("official", ""),
        "country_code": c.get("cca2", ""),
        "capital": (c.get("capital") or [None])[0],
        "region": c.get("region", ""),
        "subregion": c.get("subregion", ""),
        "population": c.get("population"),
        "currencies": [
            {"code": code, "name": info.get("name", ""), "symbol": info.get("symbol", "")}
            for code, info in currencies.items()
        ],
        "languages": list(languages.values()),
        "timezones": c.get("timezones", []),
        "calling_code": (c.get("idd", {}).get("root", "") +
                         (c.get("idd", {}).get("suffixes", [""])[0] if c.get("idd", {}).get("suffixes") else "")),
        "drives_on": c.get("car", {}).get("side", ""),
        "border_countries": c.get("borders", []),
        "google_maps_url": c.get("maps", {}).get("googleMaps", ""),
        "flag_url": c.get("flags", {}).get("png", ""),
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
