"""Travel advisories - safety, health, visa info via travelbriefing.org (no auth)."""

from __future__ import annotations


async def get_travel_advisory(country: str) -> dict:
    """Get safety, visa, health, currency, and electrical info for a country.

    Sources: travelbriefing.org (pulls from official government advisories).
    No API key required.

    Args:
        country: Country name in English (e.g., "Japan", "Egypt", "Mexico")
    """
    from ..utils.http import get_client

    client = await get_client()
    try:
        resp = await client.get(
            f"https://travelbriefing.org/{country}",
            params={"format": "json"},
        )
        if resp.status_code != 200:
            return {"error": f"No advisory found for '{country}'. Try the official English name."}

        data = resp.json()

        advisories = data.get("advisories", {})
        advisory_summary = []
        for src, info in advisories.items() if isinstance(advisories, dict) else []:
            advisory_summary.append({
                "source": src,
                "advice": info.get("advice", "") if isinstance(info, dict) else str(info),
                "updated": info.get("updated", "") if isinstance(info, dict) else "",
                "url": info.get("url", "") if isinstance(info, dict) else "",
            })

        vaccinations = data.get("vaccinations", [])
        if isinstance(vaccinations, list):
            vacc_list = [
                {
                    "name": v.get("name", "") if isinstance(v, dict) else str(v),
                    "message": v.get("message", "") if isinstance(v, dict) else "",
                }
                for v in vaccinations
            ]
        else:
            vacc_list = []

        return {
            "country": data.get("names", {}).get("name", country),
            "iso_code": data.get("names", {}).get("iso2", ""),
            "advisories": advisory_summary,
            "advisory_count": len(advisory_summary),
            "vaccinations": vacc_list,
            "currency": data.get("currency", {}),
            "language": data.get("language", {}),
            "electricity": data.get("electricity", {}),
            "telephone": data.get("telephone", {}),
            "timezone": data.get("timezone", {}),
            "water": data.get("water", {}),
            "neighbors": data.get("neighbors", []),
            "source": "travelbriefing.org",
        }
    except Exception as e:
        return {"error": str(e), "country": country}
