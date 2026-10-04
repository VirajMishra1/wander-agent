"""Country facts — RestCountries API (free, no auth)."""
from __future__ import annotations


async def get_country_facts(country: str) -> dict:
    """Fetch key facts about a country: capital, languages, population, timezone, currency, calling code.

    Args:
        country: Country name or ISO 2/3-letter code (e.g., "Japan", "JP", "JPN")
    """
    from ..utils.http import get_client

    client = await get_client()
    country_clean = country.strip()

    if len(country_clean) in (2, 3) and country_clean.isalpha():
        url = f"https://restcountries.com/v3.1/alpha/{country_clean.upper()}"
    else:
        url = f"https://restcountries.com/v3.1/name/{country_clean}?fullText=false"

    try:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code != 200:
            return {"error": f"Country '{country}' not found", "data_confidence": "live_api"}
        data = resp.json()
        if not data:
            return {"error": f"No data for '{country}'", "data_confidence": "live_api"}
        c = data[0] if isinstance(data, list) else data

        name = c.get("name", {}).get("common", country)
        official_name = c.get("name", {}).get("official", name)
        capital = c.get("capital", [None])[0]
        region = c.get("region", "")
        subregion = c.get("subregion", "")
        population = c.get("population")
        area_km2 = c.get("area")
        timezones = c.get("timezones", [])
        languages = list(c.get("languages", {}).values())
        iso2 = c.get("cca2", "")
        iso3 = c.get("cca3", "")

        root = c.get("idd", {}).get("root", "")
        suffixes = c.get("idd", {}).get("suffixes", [""])
        calling_codes = [f"{root}{s}" for s in suffixes] if root else []

        currencies = {code: info.get("name", code) for code, info in c.get("currencies", {}).items()}
        currency_symbols = {code: info.get("symbol", "") for code, info in c.get("currencies", {}).items()}

        flag_emoji = c.get("flag", "")
        maps = c.get("maps", {})
        landlocked = c.get("landlocked", False)
        borders = c.get("borders", [])
        tld = c.get("tld", [])

        return {
            "name": name,
            "official_name": official_name,
            "iso2": iso2,
            "iso3": iso3,
            "flag": flag_emoji,
            "capital": capital,
            "region": region,
            "subregion": subregion,
            "population": population,
            "area_km2": area_km2,
            "landlocked": landlocked,
            "borders": borders,
            "languages": languages,
            "currencies": currencies,
            "currency_symbols": currency_symbols,
            "timezones": timezones,
            "calling_codes": calling_codes,
            "tld": tld,
            "maps": {
                "google": maps.get("googleMaps"),
                "openstreet": maps.get("openStreetMaps"),
            },
            "data_confidence": "live_api",
            "data_source": "restcountries.com",
            "suggest_web_search": [
                f"{name} travel guide 2026",
                f"visa requirements for {name}",
                f"best time to visit {name}",
            ],
        }
    except Exception as e:
        return {"error": str(e), "data_confidence": "live_api"}
