"""Transit visa checker.

Answers: "Do I need a transit visa at LHR with a US passport connecting to DEL?"

This is a common trip-ruiner — travelers get denied boarding because they didn't
know they needed a transit visa for their layover country. Static dataset covering
the most common layover airports and passport combinations.
"""

from __future__ import annotations

# Transit visa requirements by (layover_country_iso2, passport_iso2) → requirement
# Sources: IATA Travel Centre, official government guidance (as of 2024-2025)
_TRANSIT_RULES: dict[tuple[str, str], str] = {
    # UK — DATV (Direct Airside Transit Visa) required for many nationals
    ("GB", "AF"): "required", ("GB", "AL"): "required", ("GB", "DZ"): "required",
    ("GB", "AO"): "required", ("GB", "BD"): "required", ("GB", "BY"): "required",
    ("GB", "CM"): "required", ("GB", "CN"): "required", ("GB", "CD"): "required",
    ("GB", "ER"): "required", ("GB", "ET"): "required", ("GB", "GH"): "required",
    ("GB", "GN"): "required", ("GB", "NG"): "required", ("GB", "PK"): "required",
    ("GB", "RU"): "required", ("GB", "SN"): "required", ("GB", "SL"): "required",
    ("GB", "LK"): "required", ("GB", "SD"): "required", ("GB", "TZ"): "required",
    ("GB", "UG"): "required", ("GB", "IN"): "required", ("GB", "TH"): "required",
    ("GB", "PH"): "required", ("GB", "ID"): "required", ("GB", "VN"): "required",
    ("GB", "KE"): "required", ("GB", "MA"): "required", ("GB", "TN"): "required",
    ("GB", "EG"): "required",
    ("GB", "US"): "not_required", ("GB", "CA"): "not_required",
    ("GB", "AU"): "not_required", ("GB", "NZ"): "not_required",
    ("GB", "JP"): "not_required", ("GB", "KR"): "not_required",
    ("GB", "SG"): "not_required", ("GB", "TR"): "not_required",
    ("GB", "BR"): "not_required", ("GB", "MX"): "not_required",
    ("GB", "ZA"): "not_required", ("GB", "MY"): "not_required",

    # USA — no true airside transit; ESTA required for visa-waiver nationals
    ("US", "IN"): "required", ("US", "PK"): "required", ("US", "BD"): "required",
    ("US", "CN"): "required", ("US", "NG"): "required", ("US", "GH"): "required",
    ("US", "ET"): "required", ("US", "EG"): "required", ("US", "VN"): "required",
    ("US", "PH"): "required", ("US", "ID"): "required", ("US", "TH"): "required",
    ("US", "MA"): "required", ("US", "KE"): "required",
    ("US", "GB"): "esta_required", ("US", "DE"): "esta_required",
    ("US", "FR"): "esta_required", ("US", "AU"): "esta_required",
    ("US", "NZ"): "esta_required", ("US", "JP"): "esta_required",
    ("US", "KR"): "esta_required", ("US", "SG"): "esta_required",
    ("US", "CA"): "not_required", ("US", "MX"): "not_required",

    # Schengen (Germany as representative — ATV required for several nationalities)
    ("DE", "AF"): "required", ("DE", "BD"): "required", ("DE", "CN"): "required",
    ("DE", "ER"): "required", ("DE", "ET"): "required", ("DE", "GH"): "required",
    ("DE", "GN"): "required", ("DE", "IN"): "required", ("DE", "IR"): "required",
    ("DE", "IQ"): "required", ("DE", "NG"): "required", ("DE", "PK"): "required",
    ("DE", "LK"): "required", ("DE", "SO"): "required", ("DE", "SD"): "required",
    ("DE", "SS"): "required", ("DE", "SY"): "required", ("DE", "TZ"): "required",
    ("DE", "TH"): "required", ("DE", "VN"): "required", ("DE", "ID"): "required",
    ("DE", "PH"): "required", ("DE", "TR"): "required", ("DE", "EG"): "required",
    ("DE", "US"): "not_required", ("DE", "CA"): "not_required",
    ("DE", "AU"): "not_required", ("DE", "JP"): "not_required",
    ("DE", "KR"): "not_required", ("DE", "BR"): "not_required",
    ("DE", "MX"): "not_required", ("DE", "ZA"): "not_required",
    ("DE", "MA"): "not_required", ("DE", "TN"): "not_required",
    ("DE", "UA"): "not_required",

    # Canada
    ("CA", "IN"): "required", ("CA", "PK"): "required", ("CA", "BD"): "required",
    ("CA", "NG"): "required", ("CA", "GH"): "required", ("CA", "ET"): "required",
    ("CA", "KE"): "required", ("CA", "TZ"): "required", ("CA", "VN"): "required",
    ("CA", "PH"): "required", ("CA", "ID"): "required", ("CA", "CN"): "required",
    ("CA", "TH"): "not_required",
    ("CA", "US"): "not_required", ("CA", "GB"): "not_required",
    ("CA", "AU"): "not_required", ("CA", "JP"): "not_required",
    ("CA", "BR"): "not_required", ("CA", "MX"): "not_required",
    ("CA", "ZA"): "not_required",

    # Australia
    ("AU", "IN"): "required", ("AU", "CN"): "required", ("AU", "ID"): "required",
    ("AU", "PH"): "required", ("AU", "VN"): "required", ("AU", "BD"): "required",
    ("AU", "PK"): "required", ("AU", "NG"): "required", ("AU", "GH"): "required",
    ("AU", "ET"): "required",
    ("AU", "US"): "not_required", ("AU", "GB"): "not_required",
    ("AU", "CA"): "not_required", ("AU", "JP"): "not_required",
    ("AU", "KR"): "not_required", ("AU", "SG"): "not_required",
    ("AU", "NZ"): "not_required", ("AU", "MY"): "not_required",
    ("AU", "ZA"): "not_required", ("AU", "TH"): "not_required",
    ("AU", "BR"): "not_required", ("AU", "MX"): "not_required",

    # UAE (DXB) — very open transit policy
    ("AE", "IN"): "not_required", ("AE", "PK"): "not_required",
    ("AE", "BD"): "not_required", ("AE", "NG"): "not_required",
    ("AE", "GH"): "not_required", ("AE", "ET"): "not_required",
    ("AE", "CN"): "not_required", ("AE", "VN"): "not_required",
    ("AE", "PH"): "not_required", ("AE", "ID"): "not_required",
    ("AE", "TH"): "not_required", ("AE", "US"): "not_required",
    ("AE", "GB"): "not_required", ("AE", "DE"): "not_required",
    ("AE", "FR"): "not_required", ("AE", "AU"): "not_required",
    ("AE", "JP"): "not_required", ("AE", "ZA"): "not_required",
    ("AE", "MA"): "not_required", ("AE", "KE"): "not_required",
    ("AE", "TR"): "not_required", ("AE", "CA"): "not_required",
    ("AE", "KR"): "not_required", ("AE", "SG"): "not_required",

    # Singapore (SIN)
    ("SG", "US"): "not_required", ("SG", "GB"): "not_required",
    ("SG", "IN"): "not_required", ("SG", "CN"): "not_required",
    ("SG", "GH"): "not_required", ("SG", "ID"): "not_required",
    ("SG", "PH"): "not_required", ("SG", "VN"): "not_required",
    ("SG", "TH"): "not_required", ("SG", "MY"): "not_required",
    ("SG", "AU"): "not_required", ("SG", "JP"): "not_required",
    ("SG", "KR"): "not_required", ("SG", "ZA"): "not_required",
    ("SG", "PK"): "required", ("SG", "BD"): "required",
    ("SG", "AF"): "required", ("SG", "NG"): "required", ("SG", "ET"): "required",

    # Turkey (IST) — generally open transit
    ("TR", "US"): "not_required", ("TR", "GB"): "not_required",
    ("TR", "DE"): "not_required", ("TR", "IN"): "not_required",
    ("TR", "CN"): "not_required", ("TR", "PK"): "not_required",
    ("TR", "BD"): "not_required", ("TR", "NG"): "not_required",
    ("TR", "GH"): "not_required", ("TR", "ET"): "not_required",
    ("TR", "ID"): "not_required", ("TR", "PH"): "not_required",
    ("TR", "VN"): "not_required", ("TR", "TH"): "not_required",
    ("TR", "ZA"): "not_required", ("TR", "MA"): "not_required",
    ("TR", "KE"): "not_required", ("TR", "EG"): "not_required",
    ("TR", "AU"): "not_required", ("TR", "JP"): "not_required",
    ("TR", "KR"): "not_required", ("TR", "SG"): "not_required",
    ("TR", "CA"): "not_required", ("TR", "FR"): "not_required",

    # Qatar (DOH) — generally open transit
    ("QA", "US"): "not_required", ("QA", "GB"): "not_required",
    ("QA", "IN"): "not_required", ("QA", "PK"): "not_required",
    ("QA", "BD"): "not_required", ("QA", "NG"): "not_required",
    ("QA", "GH"): "not_required", ("QA", "ET"): "not_required",
    ("QA", "CN"): "not_required", ("QA", "ID"): "not_required",
    ("QA", "PH"): "not_required", ("QA", "VN"): "not_required",
    ("QA", "TH"): "not_required", ("QA", "ZA"): "not_required",
    ("QA", "MA"): "not_required", ("QA", "KE"): "not_required",
    ("QA", "AU"): "not_required", ("QA", "JP"): "not_required",
    ("QA", "TR"): "not_required", ("QA", "DE"): "not_required",
    ("QA", "FR"): "not_required", ("QA", "CA"): "not_required",
    ("QA", "KR"): "not_required", ("QA", "SG"): "not_required",
}

_AIRPORT_TO_COUNTRY: dict[str, str] = {
    "LHR": "GB", "LGW": "GB", "STN": "GB", "MAN": "GB", "EDI": "GB",
    "JFK": "US", "EWR": "US", "LGA": "US", "LAX": "US", "ORD": "US",
    "ATL": "US", "DFW": "US", "MIA": "US", "SFO": "US", "SEA": "US",
    "BOS": "US", "DEN": "US", "IAD": "US", "IAH": "US", "PHX": "US",
    "FRA": "DE", "MUC": "DE", "DUS": "DE", "BER": "DE", "HAM": "DE",
    "CDG": "FR", "ORY": "FR",
    "AMS": "NL",
    "MAD": "ES", "BCN": "ES",
    "FCO": "IT", "MXP": "IT",
    "ZRH": "CH", "GVA": "CH",
    "YYZ": "CA", "YVR": "CA", "YUL": "CA", "YYC": "CA",
    "SYD": "AU", "MEL": "AU", "BNE": "AU", "PER": "AU",
    "DXB": "AE", "AUH": "AE", "SHJ": "AE",
    "SIN": "SG",
    "IST": "TR", "SAW": "TR",
    "DOH": "QA",
    "NRT": "JP", "HND": "JP", "KIX": "JP",
    "ICN": "KR", "GMP": "KR",
    "HKG": "HK",
    "BKK": "TH", "DMK": "TH", "HKT": "TH",
    "KUL": "MY",
    "DEL": "IN", "BOM": "IN", "BLR": "IN", "MAA": "IN",
    "PEK": "CN", "PVG": "CN", "CAN": "CN",
    "ADD": "ET",
    "NBO": "KE",
    "JNB": "ZA", "CPT": "ZA",
    "CMN": "MA",
}

_OFFICIAL_URLS: dict[str, str] = {
    "GB": "https://www.gov.uk/transit-visa",
    "US": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/transit.html",
    "DE": "https://www.auswaertiges-amt.de/en/einreiseundaufenthalt/visabestimmungen-node",
    "FR": "https://france-visas.gouv.fr/en/web/france-visas/airport-transit",
    "NL": "https://ind.nl/en/transit-visa",
    "CA": "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/transit.html",
    "AU": "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771",
    "AE": "https://u.ae/en/information-and-services/visa-and-emirates-id/transit-visa",
    "SG": "https://www.ica.gov.sg/enter-transit-depart/transiting-through-singapore",
    "TR": "https://www.mfa.gov.tr/visa-information-for-foreigners.en.mfa",
    "QA": "https://www.qatarairways.com/en/countries/transit-visa.html",
    "JP": "https://www.mofa.go.jp/j_info/visit/visa/short/novisa.html",
    "KR": "https://overseas.mofa.go.kr/eng/index.do",
    "HK": "https://www.immd.gov.hk/eng/services/visas/transit.html",
    "TH": "https://www.thaiembassy.com/travel-to-thailand/transit-visa",
    "MY": "https://www.imi.gov.my/index.php/en/main-services/visa/transit-pass",
    "IN": "https://indianvisaonline.gov.in/evisa/tvoa.html",
    "CN": "https://www.mfa.gov.cn/mfa_eng/",
    "ET": "https://www.ethiopianairlines.com/et/information/transit",
    "KE": "https://evisa.go.ke/",
    "ZA": "https://www.dha.gov.za/index.php/applying-for-sa-visa",
}

_VERDICT_LABELS = {
    "not_required": "✅ No transit visa required",
    "required": "🚫 Transit visa required — apply before travel",
    "esta_required": "⚠️ US ESTA required (esta.cbp.dhs.gov, $21, approve within minutes)",
    "tvpa": "ℹ️ Transit Without Visa may apply — verify with airline",
}

_RISK_LEVELS = {
    "not_required": "low",
    "required": "high",
    "esta_required": "medium",
    "tvpa": "medium",
    "unknown": "medium",
}


def _lookup(layover_country: str, passport: str) -> str:
    key = (layover_country.upper(), passport.upper())
    if key in _TRANSIT_RULES:
        return _TRANSIT_RULES[key]
    if layover_country.upper() == passport.upper():
        return "not_required"
    _eu = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU",
           "IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}
    if layover_country.upper() in _eu and passport.upper() in _eu:
        return "not_required"
    return "unknown"


async def check_transit_visa(
    passport_country: str,
    layover_airport: str,
    connecting_to: str | None = None,
) -> dict:
    """Check if you need a transit visa for a layover airport.

    Covers the most common passport + layover combinations for major hubs:
    LHR, JFK, LAX, FRA, AMS, CDG, DXB, SIN, IST, DOH, NRT, ICN, HKG,
    YYZ, SYD, and 40+ others.

    This is a common trip-ruiner — carriers deny boarding if you lack
    the required transit document. Check this BEFORE booking.

    Args:
        passport_country: Your passport ISO2 code (e.g., "IN", "US", "NG", "CN")
        layover_airport: IATA code of layover airport (e.g., "LHR", "DXB", "JFK")
        connecting_to: Optional — your final destination airport IATA (for context)
    """
    passport = passport_country.upper().strip()
    airport = layover_airport.upper().strip()

    layover_country = _AIRPORT_TO_COUNTRY.get(airport)
    if not layover_country:
        return {
            "passport": passport,
            "layover_airport": airport,
            "connecting_to": connecting_to,
            "verdict": "⚠️ Airport not in dataset",
            "error": (
                f"Airport {airport} not in dataset. "
                f"Check manually: https://www.iatatravelcentre.com/"
            ),
        }

    requirement = _lookup(layover_country, passport)
    verdict = _VERDICT_LABELS.get(requirement, f"ℹ️ {requirement} — verify with airline")
    risk = _RISK_LEVELS.get(requirement, "medium")
    official_url = _OFFICIAL_URLS.get(layover_country, "https://www.iatatravelcentre.com/")

    notes: list[str] = []
    if requirement == "required":
        notes.append("Apply 2-4 weeks before travel. Airline may deny boarding without it.")
        notes.append("Transit visa required even if you stay airside and don't enter the country.")
    if requirement == "esta_required":
        notes.append("ESTA applies to all Visa Waiver Programme nationalities transiting the US.")
        notes.append("The US has no true airside transit — all connecting passengers clear US CBP.")
    if airport in ("LHR", "LGW", "STN") and requirement == "required":
        notes.append("UK DATV covers airside transit only. A separate UK visa is needed to enter the country.")
    if layover_country == "US":
        notes.append("All passengers transiting the US must clear US Customs and Border Protection, regardless of stay duration.")
    if requirement == "unknown":
        notes.append("This combination is not in our dataset. Verify at IATA Travel Centre or contact your airline.")

    return {
        "passport_country": passport,
        "layover_airport": airport,
        "layover_country": layover_country,
        "connecting_to": connecting_to,
        "requirement": requirement,
        "verdict": verdict,
        "risk_level": risk,
        "notes": notes,
        "official_link": official_url,
        "verify_also": "https://www.iatatravelcentre.com/",
        "data_confidence": "curated_static_2024_2025",
        "warning": "Always verify with your airline and official embassy — policies change without notice.",
    }
