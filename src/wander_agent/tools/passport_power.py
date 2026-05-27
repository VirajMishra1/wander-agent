"""Passport power index and comparison.

Ranks passport strength using the existing visa dataset.
Compares two passports — shows exactly what one gives you that the other doesn't.
Viral for dual-passport holders and immigration decision-making.

Zero new APIs. Uses VISA_DATA already in visa.py.
"""

from __future__ import annotations

from .visa import VISA_DATA

# Henley Passport Index 2024 — global rank (1 = strongest)
HENLEY_2024: dict[str, int] = {
    "JP": 1, "SG": 1, "DE": 1, "FR": 1, "ES": 1, "IT": 1,
    "FI": 2, "KR": 2, "AT": 2, "LU": 2, "SE": 2,
    "DK": 3, "IE": 3, "NL": 3,
    "BE": 4, "CZ": 4, "MT": 4, "NZ": 4, "NO": 4, "PT": 4, "CH": 4,
    "AU": 5, "HU": 5, "PL": 5, "GB": 5,
    "CA": 6, "GR": 6, "MY": 6,
    "US": 7, "LT": 7, "SK": 7,
    "IS": 9, "EE": 9, "LV": 9,
    "CY": 11, "HR": 11,
    "AE": 20,
    "AR": 22, "BR": 22, "CL": 22, "MX": 25,
    "IL": 28, "KW": 30,
    "UA": 30, "GE": 47,
    "TR": 38, "ZA": 55,
    "CN": 65, "IN": 80,
    "NG": 95, "PK": 100, "GH": 70,
    "ET": 103, "KE": 72,
    "AF": 108, "IQ": 107, "SY": 106, "YE": 105,
}

_ISO2_TO_NAME: dict[str, str] = {
    "US": "United States", "GB": "United Kingdom", "CA": "Canada", "AU": "Australia",
    "NZ": "New Zealand", "JP": "Japan", "KR": "South Korea", "SG": "Singapore",
    "DE": "Germany", "FR": "France", "IT": "Italy", "ES": "Spain", "PT": "Portugal",
    "NL": "Netherlands", "BE": "Belgium", "CH": "Switzerland", "AT": "Austria",
    "SE": "Sweden", "NO": "Norway", "DK": "Denmark", "FI": "Finland", "IE": "Ireland",
    "PL": "Poland", "CZ": "Czechia", "HU": "Hungary", "SK": "Slovakia", "RO": "Romania",
    "GR": "Greece", "HR": "Croatia", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia",
    "IS": "Iceland", "MT": "Malta", "LU": "Luxembourg", "CY": "Cyprus",
    "IN": "India", "CN": "China", "PK": "Pakistan", "BD": "Bangladesh",
    "TH": "Thailand", "MY": "Malaysia", "ID": "Indonesia", "VN": "Vietnam",
    "PH": "Philippines", "TW": "Taiwan", "HK": "Hong Kong",
    "BR": "Brazil", "AR": "Argentina", "MX": "Mexico", "CL": "Chile",
    "CO": "Colombia", "PE": "Peru",
    "ZA": "South Africa", "KE": "Kenya", "NG": "Nigeria", "ET": "Ethiopia", "GH": "Ghana",
    "EG": "Egypt", "MA": "Morocco", "TN": "Tunisia",
    "AE": "UAE", "SA": "Saudi Arabia", "TR": "Turkey", "IL": "Israel", "JO": "Jordan",
    "GE": "Georgia", "AM": "Armenia", "UA": "Ukraine", "RU": "Russia",
    "AF": "Afghanistan", "IQ": "Iraq", "SY": "Syria", "YE": "Yemen",
    "NP": "Nepal", "LK": "Sri Lanka", "MV": "Maldives", "BT": "Bhutan",
    "KH": "Cambodia", "LA": "Laos", "MM": "Myanmar",
    "TZ": "Tanzania", "UG": "Uganda", "RW": "Rwanda", "ZW": "Zimbabwe",
    "FJ": "Fiji", "BS": "Bahamas", "BB": "Barbados", "JM": "Jamaica",
    "DO": "Dominican Republic", "PA": "Panama", "CR": "Costa Rica",
    "EC": "Ecuador", "BO": "Bolivia", "UY": "Uruguay",
}

_REGION: dict[str, str] = {
    "US": "Americas", "CA": "Americas", "MX": "Americas", "BR": "Americas",
    "AR": "Americas", "CL": "Americas", "CO": "Americas", "PE": "Americas",
    "EC": "Americas", "BO": "Americas", "UY": "Americas",
    "PA": "Americas", "CR": "Americas", "DO": "Americas", "JM": "Americas",
    "BS": "Americas", "BB": "Americas",
    "GB": "Europe", "DE": "Europe", "FR": "Europe", "IT": "Europe", "ES": "Europe",
    "PT": "Europe", "NL": "Europe", "BE": "Europe", "CH": "Europe", "AT": "Europe",
    "SE": "Europe", "NO": "Europe", "DK": "Europe", "FI": "Europe", "IE": "Europe",
    "PL": "Europe", "CZ": "Europe", "HU": "Europe", "SK": "Europe", "RO": "Europe",
    "GR": "Europe", "HR": "Europe", "TR": "Europe", "RS": "Europe", "AL": "Europe",
    "IS": "Europe", "MT": "Europe", "LU": "Europe", "CY": "Europe",
    "LT": "Europe", "LV": "Europe", "EE": "Europe", "SI": "Europe", "BG": "Europe",
    "MK": "Europe", "ME": "Europe", "BA": "Europe",
    "JP": "Asia Pacific", "KR": "Asia Pacific", "CN": "Asia Pacific",
    "TW": "Asia Pacific", "HK": "Asia Pacific",
    "SG": "Asia Pacific", "MY": "Asia Pacific", "TH": "Asia Pacific",
    "VN": "Asia Pacific", "PH": "Asia Pacific", "ID": "Asia Pacific",
    "IN": "Asia Pacific", "PK": "Asia Pacific", "BD": "Asia Pacific",
    "NP": "Asia Pacific", "LK": "Asia Pacific", "MV": "Asia Pacific",
    "KH": "Asia Pacific", "LA": "Asia Pacific", "MM": "Asia Pacific",
    "AU": "Asia Pacific", "NZ": "Asia Pacific", "FJ": "Asia Pacific",
    "AE": "Middle East", "SA": "Middle East", "IL": "Middle East",
    "JO": "Middle East", "LB": "Middle East", "KW": "Middle East",
    "EG": "Africa", "MA": "Africa", "TN": "Africa",
    "ZA": "Africa", "KE": "Africa", "NG": "Africa", "ET": "Africa",
    "GH": "Africa", "TZ": "Africa", "UG": "Africa", "RW": "Africa", "ZW": "Africa",
    "GE": "Caucasus / Central Asia", "AM": "Caucasus / Central Asia",
    "UA": "Eastern Europe", "RU": "Eastern Europe",
}

_TOTAL_DESTINATIONS = 199


def _get_data(iso2: str) -> dict | None:
    return VISA_DATA.get(iso2.lower())


def _access_sets(data: dict) -> tuple[set, set, set, set]:
    vf = set(data.get("visa_free", set()))
    eta = set(data.get("eta_required", set()))
    ev = set(data.get("evisa", set()))
    voa = set(data.get("visa_on_arrival", set()))
    return vf, eta, ev, voa


def _summarize(iso2: str, data: dict) -> dict:
    vf, eta, ev, voa = _access_sets(data)
    friction = vf | eta | ev | voa
    region_vf = _region_breakdown(vf)
    return {
        "passport": iso2,
        "country": _ISO2_TO_NAME.get(iso2, iso2),
        "henley_rank_2024": HENLEY_2024.get(iso2),
        "visa_free_count": len(vf),
        "eta_evisa_count": len(eta | ev),
        "visa_on_arrival_count": len(voa),
        "frictionless_total": len(friction),
        "frictionless_pct": round(len(friction) / _TOTAL_DESTINATIONS * 100, 1),
        "visa_required_approx": max(0, _TOTAL_DESTINATIONS - len(friction)),
        "visa_free_by_region": region_vf,
        "strongest_regions": list(region_vf.keys())[:3],
        "visa_free_countries": sorted(_ISO2_TO_NAME.get(c, c) for c in vf),
    }


def _region_breakdown(countries: set[str]) -> dict[str, int]:
    bd: dict[str, int] = {}
    for c in countries:
        r = _REGION.get(c, "Other")
        bd[r] = bd.get(r, 0) + 1
    return dict(sorted(bd.items(), key=lambda x: x[1], reverse=True))


def _names(codes: set[str]) -> list[str]:
    return sorted(_ISO2_TO_NAME.get(c, c) for c in codes)


async def get_passport_power(
    passport_country: str,
    compare_with: str | None = None,
) -> dict:
    """Rank passport strength and optionally compare two passports.

    Shows visa-free access count, frictionless travel percentage, regional
    breakdown, and Henley Index 2024 rank. When compare_with is provided,
    shows a head-to-head diff — which destinations each passport unlocks
    that the other doesn't. Critical for dual-passport holders.

    No API key required — uses built-in visa dataset.

    Args:
        passport_country: Your passport ISO2 code (e.g., "US", "IN", "NG", "CN")
        compare_with: Optional second passport ISO2 for comparison (e.g., "GB")
    """
    iso_a = passport_country.upper().strip()
    data_a = _get_data(iso_a)

    if not data_a:
        return {
            "error": (
                f"Passport '{iso_a}' not in dataset. "
                f"Supported: {', '.join(sorted(k.upper() for k in VISA_DATA))}"
            ),
        }

    summary_a = _summarize(iso_a, data_a)
    vf_a, eta_a, ev_a, voa_a = _access_sets(data_a)
    friction_a = vf_a | eta_a | ev_a | voa_a

    result: dict = {
        **summary_a,
        "tier": (
            "Tier 1 — Top 10 global (near-universal access)" if (summary_a["henley_rank_2024"] or 99) <= 10 else
            "Tier 2 — Strong (150+ frictionless)" if summary_a["frictionless_total"] >= 150 else
            "Tier 3 — Average (100-149 frictionless)" if summary_a["frictionless_total"] >= 100 else
            "Tier 4 — Limited (<100 frictionless)"
        ),
        "data_confidence": "static_henley_2024 + wander_visa_dataset",
        "note": "Frictionless = visa-free + ETA + eVisa + visa-on-arrival. Does not include full visa required.",
    }

    if compare_with:
        iso_b = compare_with.upper().strip()
        data_b = _get_data(iso_b)
        if not data_b:
            result["comparison_error"] = f"Passport '{iso_b}' not in dataset."
            return result

        summary_b = _summarize(iso_b, data_b)
        vf_b, eta_b, ev_b, voa_b = _access_sets(data_b)
        friction_b = vf_b | eta_b | ev_b | voa_b

        a_only = friction_a - friction_b
        b_only = friction_b - friction_a
        both = friction_a & friction_b

        net = len(friction_a) - len(friction_b)
        stronger = iso_a if net >= 0 else iso_b

        recs: list[str] = []
        if a_only:
            top_a = _names(a_only)[:6]
            recs.append(f"Use {iso_a} passport for: {', '.join(top_a)}{'...' if len(a_only) > 6 else ''}")
        if b_only:
            top_b = _names(b_only)[:6]
            recs.append(f"Use {iso_b} passport for: {', '.join(top_b)}{'...' if len(b_only) > 6 else ''}")
        if not a_only and not b_only:
            recs.append(f"Identical frictionless access in this dataset — use either passport.")

        result["comparison"] = {
            "passport_b": iso_b,
            "country_b": summary_b["country"],
            "henley_rank_b": summary_b["henley_rank_2024"],
            "frictionless_b": summary_b["frictionless_total"],
            "frictionless_a": summary_a["frictionless_total"],
            f"{iso_a}_only_destinations": len(a_only),
            f"{iso_b}_only_destinations": len(b_only),
            "shared_frictionless": len(both),
            "stronger_passport": stronger,
            "net_advantage": (
                f"{iso_a} covers {abs(net)} more frictionless destinations" if net > 0 else
                f"{iso_b} covers {abs(net)} more frictionless destinations" if net < 0 else
                "Equal frictionless access"
            ),
            f"{iso_a}_only_countries": _names(a_only),
            f"{iso_b}_only_countries": _names(b_only),
            "recommendations": recs,
        }

    return result
