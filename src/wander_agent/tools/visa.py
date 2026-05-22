"""Visa requirement check - counter to the Mery Caldass ESTA fail.

Curated dataset of passport -> destination visa requirements.
Based on IATA Timatic data + Wikipedia visa-policy tables (public).
Counters the viral AI-fail of recommending visa-free travel that isn't.
"""

from __future__ import annotations


# Compressed format: passport_iso -> {visa_free_countries: set, eta_required: set, evisa: set}
# Common ones; LLM should fall back to web search for niche passports.
VISA_DATA: dict[str, dict[str, set[str]]] = {
    "us": {
        "visa_free": {"GB", "FR", "DE", "IT", "ES", "PT", "NL", "BE", "CH", "AT",
                       "DK", "SE", "NO", "FI", "IE", "GR", "PL", "CZ", "HU", "RO",
                       "BG", "HR", "SI", "SK", "EE", "LV", "LT", "LU", "MT", "CY",
                       "JP", "KR", "TW", "HK", "SG", "MY", "TH", "PH", "ID",
                       "MX", "CA", "BS", "BB", "JM", "DO", "PA", "CR", "EC", "CO",
                       "PE", "CL", "AR", "UY", "AU", "NZ", "FJ", "ZA", "IL", "MA",
                       "EG", "TR", "GE", "AM", "AL", "RS", "ME", "BA", "MK", "IS"},
        "eta_required": {"NZ", "GB", "CA"},
        "evisa": {"IN", "VN", "CN", "RU", "SA", "KE", "TZ", "UG", "RW", "ZW"},
        "visa_on_arrival": {"NP", "LK", "MV", "ID", "TH", "KH", "LA", "BO", "JO", "LB"},
    },
    "gb": {
        "visa_free": {"US", "CA", "AU", "NZ", "JP", "KR", "SG", "MY", "TH", "ID",
                       "PH", "MX", "BR", "AR", "CL", "PE", "ZA", "IL", "TR", "AE",
                       "EG", "MA", "HK", "TW"} | {"FR", "DE", "IT", "ES", "PT", "NL", "BE",
                       "CH", "AT", "DK", "SE", "NO", "FI", "IE", "GR", "PL", "CZ", "HU",
                       "IS", "RS", "AL"},
        "eta_required": {"US"},
        "evisa": {"IN", "VN", "RU", "CN", "SA"},
        "visa_on_arrival": {"NP", "LK", "MV", "JO", "LB"},
    },
    "ca": {
        "visa_free": {"US", "GB", "FR", "DE", "IT", "ES", "JP", "KR", "AU", "NZ",
                       "MX", "BR", "AR", "CL", "PE", "ZA", "IL", "AE", "EG", "MA",
                       "HK", "TW", "SG", "MY", "TH", "ID", "PH", "TR", "RS"},
        "eta_required": {"GB", "NZ"},
        "evisa": {"IN", "VN", "RU", "CN"},
        "visa_on_arrival": {"NP", "LK", "MV", "JO"},
    },
    "au": {
        "visa_free": {"GB", "FR", "DE", "IT", "ES", "JP", "KR", "SG", "MY", "TH",
                       "ID", "PH", "NZ", "MX", "BR", "AR", "ZA", "AE", "EG", "MA",
                       "HK", "TW", "IL", "TR", "RS"},
        "eta_required": {"US", "CA", "GB"},
        "evisa": {"IN", "VN", "RU", "CN"},
        "visa_on_arrival": {"NP", "LK", "MV", "JO", "LB"},
    },
    "in": {
        "visa_free": {"NP", "BT", "MV", "OM", "MU", "BB", "JM", "TT", "HT",
                       "RS", "MA", "TN", "QA"},
        "eta_required": set(),
        "evisa": {"US", "AU", "NZ", "SG", "GB", "FR", "DE", "IT", "ES", "PT", "NL",
                   "TR", "TH", "VN", "MY", "ID", "PH", "KH", "LA", "TZ", "KE",
                   "UG", "RW", "ZW", "AZ", "GE", "AM"},
        "visa_on_arrival": {"NP", "BT", "MV", "TH", "ID", "LK", "MM", "JO", "TZ"},
    },
    "de": {
        "visa_free": {"US", "GB", "CA", "AU", "NZ", "JP", "KR", "SG", "MY", "TH",
                       "ID", "PH", "MX", "BR", "AR", "CL", "PE", "ZA", "IL", "TR",
                       "AE", "EG", "MA", "HK", "TW"} | {"FR", "IT", "ES", "PT", "NL",
                       "BE", "CH", "AT", "DK", "SE", "NO", "FI", "IE", "GR", "PL",
                       "CZ", "HU", "IS", "RS", "AL"},
        "eta_required": {"US", "GB", "NZ", "CA"},
        "evisa": {"IN", "VN", "RU", "CN", "SA"},
        "visa_on_arrival": {"NP", "LK", "MV", "JO", "LB"},
    },
    "cn": {
        "visa_free": {"SG", "MY", "TH", "AE", "RS", "MA", "MX", "AL", "ME", "RU",
                       "AZ", "AM", "GE"},
        "eta_required": set(),
        "evisa": {"US", "GB", "CA", "AU", "NZ", "JP", "KR", "DE", "FR", "IT", "ES",
                   "PT", "NL", "BE", "TR", "VN", "ID", "PH"},
        "visa_on_arrival": {"NP", "LK", "MV", "JO", "ID"},
    },
}


def _classify(passport: str, dest_code: str) -> dict:
    p = passport.lower()
    d = dest_code.upper()

    data = VISA_DATA.get(p)
    if not data:
        return {
            "passport": passport.upper(),
            "destination": d,
            "category": "unknown",
            "guidance": "No data for this passport in our dataset. Verify via official source.",
            "needs_web_search": True,
        }

    if d in data["visa_free"]:
        return {"passport": passport.upper(), "destination": d, "category": "visa_free",
                 "guidance": "No visa required for tourism (typical 30-90 day stays)."}
    if d in data.get("eta_required", set()):
        return {"passport": passport.upper(), "destination": d, "category": "eta_required",
                 "guidance": f"Electronic travel authorization REQUIRED. Apply online before departure (e.g., ESTA for US, ETA for Australia/Canada/UK)."}
    if d in data.get("visa_on_arrival", set()):
        return {"passport": passport.upper(), "destination": d, "category": "visa_on_arrival",
                 "guidance": "Visa issued on arrival at airport. Bring USD cash + passport photo typically."}
    if d in data.get("evisa", set()):
        return {"passport": passport.upper(), "destination": d, "category": "evisa",
                 "guidance": "Electronic visa REQUIRED. Apply online before travel."}
    return {"passport": passport.upper(), "destination": d, "category": "visa_required",
             "guidance": "Visa REQUIRED. Apply at consulate before travel. Allow 1-8 weeks."}


async def check_visa_requirement(
    passport_country: str,
    destination_country: str,
) -> dict:
    """Check visa requirements for travel between two countries.

    Returns category (visa_free, eta_required, visa_on_arrival, evisa,
    visa_required) plus guidance. Counters AI-hallucinated visa advice
    that caused viral travel-denied-boarding incidents.

    Args:
        passport_country: ISO 2-letter code (e.g., "US", "GB", "IN")
        destination_country: ISO 2-letter code (e.g., "JP", "TH", "BR")
    """
    result = _classify(passport_country, destination_country)
    result["important_note"] = (
        "This is a SNAPSHOT from public data. Visa policies change. "
        "ALWAYS verify with the official embassy website before booking. "
        "Required documents (passport validity, blank pages, return tickets, funds) "
        "may apply even in visa-free cases."
    )
    result["suggest_web_search"] = [
        f"visa requirements {passport_country.upper()} passport to {destination_country.upper()} 2026",
        f"{destination_country.upper()} entry requirements official site",
        f"ESTA ETA Schengen requirements {passport_country.upper()} 2026" if result.get("category") in ["eta_required", "visa_free"] else "",
    ]
    return result


async def visa_free_destinations(
    passport_country: str,
    include_categories: str = "visa_free,visa_on_arrival,evisa,eta_required",
) -> dict:
    """List all destinations accessible without a traditional visa.

    Args:
        passport_country: ISO 2-letter code (e.g., "US")
        include_categories: Comma-separated: visa_free, visa_on_arrival, evisa, eta_required
    """
    p = passport_country.lower()
    data = VISA_DATA.get(p)
    if not data:
        return {
            "passport": passport_country.upper(),
            "error": "No data for this passport. Verify via official source or web search.",
            "supported_passports": list(VISA_DATA.keys()),
            "suggest_web_search": [
                f"visa requirements {passport_country.upper()} passport 2026 list"
            ],
        }

    cats = [c.strip() for c in include_categories.split(",") if c.strip()]
    result: dict = {"passport": passport_country.upper(), "destinations_by_category": {}}
    total = 0
    for cat in cats:
        countries = sorted(data.get(cat, set()))
        result["destinations_by_category"][cat] = countries
        total += len(countries)
    result["total_destinations"] = total
    result["note"] = "Snapshot from curated dataset. Verify before booking."
    return result
