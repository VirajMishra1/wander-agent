"""Destination info using REST Countries + geocoding."""

from __future__ import annotations


async def get_destination_info(
    country_name: str,
) -> dict:
    """Get essential travel info about a country.

    Args:
        country_name: Country name (e.g., "Japan", "France", "Brazil")

    Returns currency, languages, timezone, visa-free info, calling code, etc.
    No API key required.
    """
    from ..utils.http import get_client

    client = await get_client()

    resp = await client.get(
        f"https://restcountries.com/v3.1/name/{country_name}",
        params={"fields": "name,currencies,languages,timezones,capital,population,region,subregion,flags,cca2,idd,car"},
    )

    if resp.status_code == 404:
        return {"error": f"Country '{country_name}' not found. Try the full English name."}

    resp.raise_for_status()
    countries = resp.json()

    if not countries:
        return {"error": f"No results for '{country_name}'"}

    c = countries[0]
    currencies = c.get("currencies", {})
    currency_info = []
    for code, info in currencies.items():
        currency_info.append({
            "code": code,
            "name": info.get("name", ""),
            "symbol": info.get("symbol", ""),
        })

    languages = c.get("languages", {})

    return {
        "name": c.get("name", {}).get("common", country_name),
        "official_name": c.get("name", {}).get("official", ""),
        "country_code": c.get("cca2", ""),
        "capital": c.get("capital", [None])[0] if c.get("capital") else None,
        "region": c.get("region", ""),
        "subregion": c.get("subregion", ""),
        "population": c.get("population"),
        "currencies": currency_info,
        "languages": list(languages.values()),
        "timezones": c.get("timezones", []),
        "calling_code": c.get("idd", {}).get("root", "") + (c.get("idd", {}).get("suffixes", [""])[0] if c.get("idd", {}).get("suffixes") else ""),
        "drives_on": c.get("car", {}).get("side", ""),
        "flag_emoji": c.get("flags", {}).get("emoji", ""),
        "flag_url": c.get("flags", {}).get("png", ""),
    }


async def geocode(
    place_name: str,
) -> dict:
    """Get coordinates for a place name.

    Args:
        place_name: City or place name (e.g., "Paris, France", "Tokyo")

    Returns latitude, longitude, and display name. No API key required.
    Uses OpenStreetMap Nominatim (free).
    """
    from ..utils.http import get_client

    client = await get_client()
    resp = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": place_name,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        },
        headers={"User-Agent": "WanderAgent/0.1.0 (travel-planning-mcp)"},
    )
    resp.raise_for_status()
    results = resp.json()

    if not results:
        return {"error": f"Could not geocode '{place_name}'. Try a more specific name."}

    r = results[0]
    return {
        "place": place_name,
        "display_name": r.get("display_name", ""),
        "latitude": float(r.get("lat", 0)),
        "longitude": float(r.get("lon", 0)),
        "country": r.get("address", {}).get("country", ""),
        "country_code": r.get("address", {}).get("country_code", "").upper(),
        "type": r.get("type", ""),
    }
