"""Credit card points/miles static dataset.

Covers major transferable currency programs, airline/hotel partners,
baseline valuations (cents per point), bonus categories, and curated
sweet-spot award redemptions. All data is editorial/crowd-sourced —
treat as guidance, not gospel.
"""

from __future__ import annotations

# ── Baseline CPP valuations (cents per point) ──────────────────────
# Source: The Points Guy, NerdWallet, One Mile at a Time averages.
# These are "fair" values for typical redemptions; sweet spots can be 3-10×.

PROGRAM_VALUATIONS: dict[str, dict] = {
    # Bank transferable currencies
    "chase_ur": {
        "name": "Chase Ultimate Rewards",
        "issuer": "Chase",
        "currency": "Ultimate Rewards points",
        "cpp_low": 1.25,
        "cpp_mid": 1.8,
        "cpp_high": 2.5,
        "cpp_portal": 1.25,
        "notes": "1.25cpp via portal (CSP), 1.5cpp (CSR). Transfers unlock 2cpp+ on partners.",
    },
    "amex_mr": {
        "name": "Amex Membership Rewards",
        "issuer": "Amex",
        "currency": "Membership Rewards points",
        "cpp_low": 1.0,
        "cpp_mid": 1.6,
        "cpp_high": 2.5,
        "cpp_portal": 1.0,
        "notes": "Portal value is weak (1cpp). Transfer to ANA/Virgin Atlantic for outsized value.",
    },
    "citi_typ": {
        "name": "Citi ThankYou Points",
        "issuer": "Citi",
        "currency": "ThankYou points",
        "cpp_low": 1.0,
        "cpp_mid": 1.5,
        "cpp_high": 2.0,
        "cpp_portal": 1.0,
        "notes": "Transfers to JetBlue, Turkish, Singapore are strong.",
    },
    "capital_one": {
        "name": "Capital One Miles",
        "issuer": "Capital One",
        "currency": "Capital One miles",
        "cpp_low": 1.0,
        "cpp_mid": 1.4,
        "cpp_high": 2.0,
        "cpp_portal": 1.0,
        "notes": "Travel portal gives 1cpp floor. Transfer partners expanding.",
    },
    "bilt": {
        "name": "Bilt Rewards",
        "issuer": "Bilt",
        "currency": "Bilt points",
        "cpp_low": 1.25,
        "cpp_mid": 1.7,
        "cpp_high": 2.5,
        "cpp_portal": 1.25,
        "notes": "Earn on rent. Strong Hyatt/AA/United/Turkish transfer partners.",
    },
    # Airline miles
    "united_mp": {
        "name": "United MileagePlus",
        "issuer": "United Airlines",
        "currency": "MileagePlus miles",
        "cpp_low": 1.0,
        "cpp_mid": 1.3,
        "cpp_high": 2.0,
        "cpp_portal": None,
        "notes": "Dynamic pricing. Excursionist Perk adds free stopover.",
    },
    "aa_aadvantage": {
        "name": "American AAdvantage",
        "issuer": "American Airlines",
        "currency": "AAdvantage miles",
        "cpp_low": 1.0,
        "cpp_mid": 1.4,
        "cpp_high": 2.5,
        "notes": "Off-peak awards to Japan/Middle East are strong.",
    },
    "delta_skymiles": {
        "name": "Delta SkyMiles",
        "issuer": "Delta Air Lines",
        "currency": "SkyMiles",
        "cpp_low": 0.9,
        "cpp_mid": 1.2,
        "cpp_high": 1.8,
        "notes": "Dynamic pricing, no award chart. Flash sales can be 2cpp+.",
    },
    "southwest_rr": {
        "name": "Southwest Rapid Rewards",
        "issuer": "Southwest Airlines",
        "currency": "Rapid Rewards points",
        "cpp_low": 1.1,
        "cpp_mid": 1.4,
        "cpp_high": 1.7,
        "notes": "Fixed value ~1.4cpp. Companion Pass doubles value.",
    },
    "alaska_mp": {
        "name": "Alaska Mileage Plan",
        "issuer": "Alaska Airlines",
        "currency": "Mileage Plan miles",
        "cpp_low": 1.2,
        "cpp_mid": 1.8,
        "cpp_high": 3.0,
        "notes": "Partner awards (CX, JAL, Emirates) can be exceptional value.",
    },
    "jetblue_tp": {
        "name": "JetBlue TrueBlue",
        "issuer": "JetBlue",
        "currency": "TrueBlue points",
        "cpp_low": 1.1,
        "cpp_mid": 1.3,
        "cpp_high": 1.6,
        "notes": "Revenue-based. Transfers from Citi/Chase.",
    },
    "virgin_atlantic": {
        "name": "Virgin Atlantic Flying Club",
        "issuer": "Virgin Atlantic",
        "currency": "Flying Club miles",
        "cpp_low": 1.2,
        "cpp_mid": 1.8,
        "cpp_high": 5.0,
        "notes": "ANA first class via VA miles is one of the best sweet spots in the game.",
    },
    "british_airways": {
        "name": "British Airways Avios",
        "issuer": "British Airways",
        "currency": "Avios",
        "cpp_low": 1.0,
        "cpp_mid": 1.5,
        "cpp_high": 2.5,
        "notes": "Short-haul Avios redemptions are very strong. High fuel surcharges on BA metal.",
    },
    "turkish_miles": {
        "name": "Turkish Miles&Smiles",
        "issuer": "Turkish Airlines",
        "currency": "Miles&Smiles miles",
        "cpp_low": 1.5,
        "cpp_mid": 2.5,
        "cpp_high": 5.0,
        "notes": "Star Alliance business class at bargain rates. One of the best programs.",
    },
    "singapore_kf": {
        "name": "Singapore KrisFlyer",
        "issuer": "Singapore Airlines",
        "currency": "KrisFlyer miles",
        "cpp_low": 1.2,
        "cpp_mid": 1.8,
        "cpp_high": 4.0,
        "notes": "SQ Suites is the holy grail. Waitlist awards via Star Alliance.",
    },
    "ana_mileage": {
        "name": "ANA Mileage Club",
        "issuer": "ANA",
        "currency": "ANA miles",
        "cpp_low": 1.2,
        "cpp_mid": 2.0,
        "cpp_high": 6.0,
        "notes": "Round-the-world awards. First class at bargain rates.",
    },
    # Hotel points
    "hyatt_woh": {
        "name": "World of Hyatt",
        "issuer": "Hyatt",
        "currency": "World of Hyatt points",
        "cpp_low": 1.5,
        "cpp_mid": 2.0,
        "cpp_high": 3.5,
        "notes": "Best hotel loyalty value. All-inclusive resorts at 25k/night are insane.",
    },
    "marriott_bonvoy": {
        "name": "Marriott Bonvoy",
        "issuer": "Marriott",
        "currency": "Bonvoy points",
        "cpp_low": 0.6,
        "cpp_mid": 0.8,
        "cpp_high": 1.2,
        "notes": "High point requirements. 5th night free helps. Transfer 3:1 to airlines.",
    },
    "hilton_honors": {
        "name": "Hilton Honors",
        "issuer": "Hilton",
        "currency": "Honors points",
        "cpp_low": 0.4,
        "cpp_mid": 0.6,
        "cpp_high": 1.0,
        "notes": "Low cpp but easy to earn (3x-14x on Amex). 5th night free on 5+ night stays.",
    },
    "ihg_rewards": {
        "name": "IHG One Rewards",
        "issuer": "IHG",
        "currency": "IHG points",
        "cpp_low": 0.5,
        "cpp_mid": 0.7,
        "cpp_high": 1.0,
        "notes": "4th night free. Points + Cash can be decent value.",
    },
}

# ── Transfer partners ──────────────────────────────────────────────

TRANSFER_PARTNERS: dict[str, list[dict]] = {
    "chase_ur": [
        {"partner": "united_mp", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "hyatt_woh", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "british_airways", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "southwest_rr", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "virgin_atlantic", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "singapore_kf", "ratio": "1:1", "transfer_time": "12-24h"},
        {"partner": "air_france_klm", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "aer_lingus", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "iberia_avios", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "marriott_bonvoy", "ratio": "1:1", "transfer_time": "1-2 days"},
        {"partner": "ihg_rewards", "ratio": "1:1", "transfer_time": "1-2 days"},
    ],
    "amex_mr": [
        {"partner": "delta_skymiles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "british_airways", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "virgin_atlantic", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "ana_mileage", "ratio": "1:1", "transfer_time": "2-5 days"},
        {"partner": "singapore_kf", "ratio": "1:1", "transfer_time": "12-24h"},
        {"partner": "air_france_klm", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "jetblue_tp", "ratio": "1:1.25", "transfer_time": "instant"},
        {"partner": "hilton_honors", "ratio": "1:2", "transfer_time": "instant"},
        {"partner": "marriott_bonvoy", "ratio": "1:1", "transfer_time": "1-2 days"},
        {"partner": "hawaiian_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "cathay_asia_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "emirates_skywards", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "turkish_miles", "ratio": "1:1", "transfer_time": "instant"},
    ],
    "citi_typ": [
        {"partner": "turkish_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "singapore_kf", "ratio": "1:1", "transfer_time": "12-24h"},
        {"partner": "virgin_atlantic", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "jetblue_tp", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "qatar_privilege", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "air_france_klm", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "cathay_asia_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "etihad_guest", "ratio": "1:1", "transfer_time": "instant"},
    ],
    "capital_one": [
        {"partner": "turkish_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "british_airways", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "air_france_klm", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "virgin_atlantic", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "singapore_kf", "ratio": "1:1", "transfer_time": "12-24h"},
        {"partner": "cathay_asia_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "emirates_skywards", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "finnair_plus", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "wyndham_rewards", "ratio": "1:1", "transfer_time": "instant"},
    ],
    "bilt": [
        {"partner": "hyatt_woh", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "aa_aadvantage", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "united_mp", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "turkish_miles", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "air_france_klm", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "alaska_mp", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "virgin_atlantic", "ratio": "1:1", "transfer_time": "instant"},
        {"partner": "ihg_rewards", "ratio": "1:1", "transfer_time": "instant"},
    ],
}

# ── Popular cards + bonus categories ───────────────────────────────

CARDS: dict[str, dict] = {
    "chase_sapphire_preferred": {
        "name": "Chase Sapphire Preferred",
        "program": "chase_ur",
        "annual_fee": 95,
        "base_earn": 1,
        "bonus_categories": {
            "travel": 5,
            "dining": 3,
            "online_grocery": 3,
            "streaming": 3,
        },
        "sign_up_bonus": 60000,
        "portal_multiplier": 1.25,
    },
    "chase_sapphire_reserve": {
        "name": "Chase Sapphire Reserve",
        "program": "chase_ur",
        "annual_fee": 550,
        "base_earn": 1,
        "bonus_categories": {
            "travel": 10,
            "dining": 3,
            "flights": 5,
        },
        "sign_up_bonus": 60000,
        "portal_multiplier": 1.5,
    },
    "chase_freedom_flex": {
        "name": "Chase Freedom Flex",
        "program": "chase_ur",
        "annual_fee": 0,
        "base_earn": 1,
        "bonus_categories": {
            "dining": 3,
            "drugstores": 3,
            "rotating_quarterly": 5,
        },
        "sign_up_bonus": 20000,
    },
    "amex_gold": {
        "name": "Amex Gold Card",
        "program": "amex_mr",
        "annual_fee": 325,
        "base_earn": 1,
        "bonus_categories": {
            "restaurants": 4,
            "us_supermarkets": 4,
            "flights_direct": 3,
        },
        "sign_up_bonus": 60000,
    },
    "amex_platinum": {
        "name": "Amex Platinum",
        "program": "amex_mr",
        "annual_fee": 695,
        "base_earn": 1,
        "bonus_categories": {
            "flights_direct": 5,
            "prepaid_hotels_amex_travel": 5,
        },
        "sign_up_bonus": 80000,
    },
    "amex_blue_business_plus": {
        "name": "Amex Blue Business Plus",
        "program": "amex_mr",
        "annual_fee": 0,
        "base_earn": 2,
        "bonus_categories": {},
        "sign_up_bonus": 15000,
        "notes": "2x on everything up to $50k/yr. Best flat-rate MR earner.",
    },
    "capital_one_venture_x": {
        "name": "Capital One Venture X",
        "program": "capital_one",
        "annual_fee": 395,
        "base_earn": 2,
        "bonus_categories": {
            "flights": 5,
            "hotels": 10,
        },
        "sign_up_bonus": 75000,
        "portal_multiplier": 1.0,
    },
    "citi_strata_premier": {
        "name": "Citi Strata Premier",
        "program": "citi_typ",
        "annual_fee": 95,
        "base_earn": 1,
        "bonus_categories": {
            "flights": 3,
            "hotels": 3,
            "restaurants": 3,
            "supermarkets": 3,
            "gas": 3,
            "ev_charging": 3,
        },
        "sign_up_bonus": 75000,
    },
    "bilt_mastercard": {
        "name": "Bilt Mastercard",
        "program": "bilt",
        "annual_fee": 0,
        "base_earn": 1,
        "bonus_categories": {
            "rent": 1,
            "dining": 3,
            "travel": 2,
        },
        "sign_up_bonus": 0,
        "notes": "No AF. Only card that earns points on rent with no fees.",
    },
}

# ── Sweet spot awards ──────────────────────────────────────────────

SWEET_SPOTS: list[dict] = [
    {
        "name": "ANA First Class via Virgin Atlantic",
        "programs": ["amex_mr", "chase_ur", "citi_typ", "bilt", "capital_one"],
        "transfer_to": "virgin_atlantic",
        "points_required": 120000,
        "cabin": "first",
        "route": "US ↔ Japan",
        "retail_value_usd": 20000,
        "cpp": 16.7,
        "availability": "hard — 2 seats/flight, 355 days out",
        "tip": "Search on United.com for *A availability, then call VA to book.",
    },
    {
        "name": "Hyatt All-Inclusive via Chase UR",
        "programs": ["chase_ur", "bilt"],
        "transfer_to": "hyatt_woh",
        "points_required": 25000,
        "cabin": "hotel",
        "route": "Mexico/Caribbean all-inclusive (Ziva/Zilara)",
        "retail_value_usd": 600,
        "cpp": 2.4,
        "availability": "good — book 6+ months out for peak",
        "tip": "Category 4-5 all-inclusives. Includes food, drinks, activities.",
    },
    {
        "name": "Turkish Airlines Business Class to Europe/Asia",
        "programs": ["citi_typ", "capital_one", "amex_mr", "bilt"],
        "transfer_to": "turkish_miles",
        "points_required": 45000,
        "cabin": "business",
        "route": "US → Europe/Asia via IST",
        "retail_value_usd": 4000,
        "cpp": 8.9,
        "availability": "moderate — IST connecting flights open up more seats",
        "tip": "One of the cheapest business class award charts. No fuel surcharges on TK metal.",
    },
    {
        "name": "British Airways Avios Short-Haul",
        "programs": ["chase_ur", "amex_mr", "capital_one"],
        "transfer_to": "british_airways",
        "points_required": 7500,
        "cabin": "economy",
        "route": "US domestic short-haul (AA metal, <1151mi)",
        "retail_value_usd": 200,
        "cpp": 2.7,
        "availability": "excellent — AA saver space is plentiful",
        "tip": "Off-peak is 6k Avios one-way. Book AA flights on BA.com.",
    },
    {
        "name": "Singapore Suites via KrisFlyer",
        "programs": ["amex_mr", "chase_ur", "citi_typ", "capital_one"],
        "transfer_to": "singapore_kf",
        "points_required": 92000,
        "cabin": "suites",
        "route": "SIN ↔ JFK/FRA/SYD (A380)",
        "retail_value_usd": 15000,
        "cpp": 16.3,
        "availability": "very hard — 1-2 seats, released ~4 days before departure",
        "tip": "The holy grail. Private suite with bed + sit-down restaurant at 35,000ft.",
    },
    {
        "name": "Air France/KLM Promo Rewards",
        "programs": ["amex_mr", "chase_ur", "citi_typ", "capital_one", "bilt"],
        "transfer_to": "air_france_klm",
        "points_required": 36000,
        "cabin": "business",
        "route": "US → Europe",
        "retail_value_usd": 3500,
        "cpp": 9.7,
        "availability": "seasonal — monthly promo awards at 25-50% off",
        "tip": "Check Flying Blue monthly promo rewards page. J to Europe from 62.5k normal, 36k on promo.",
    },
    {
        "name": "Alaska Miles on Cathay Pacific First",
        "programs": ["bilt"],
        "transfer_to": "alaska_mp",
        "points_required": 70000,
        "cabin": "first",
        "route": "US → Hong Kong (CX first class)",
        "retail_value_usd": 12000,
        "cpp": 17.1,
        "availability": "hard — 1-2 seats, check 14+ days out",
        "tip": "Alaska still has a distance-based chart. CX first is legendary.",
    },
    {
        "name": "AAdvantage Off-Peak to Japan",
        "programs": ["bilt"],
        "transfer_to": "aa_aadvantage",
        "points_required": 37500,
        "cabin": "economy",
        "route": "US → Japan (off-peak)",
        "retail_value_usd": 800,
        "cpp": 2.1,
        "availability": "good — off-peak Jan-Mar, excl spring break",
        "tip": "AA Web Specials can drop to 25-30k economy. Business 60k off-peak.",
    },
    {
        "name": "Emirates First via Emirates Skywards",
        "programs": ["amex_mr", "capital_one"],
        "transfer_to": "emirates_skywards",
        "points_required": 136000,
        "cabin": "first",
        "route": "US → Dubai/Asia/Australia",
        "retail_value_usd": 15000,
        "cpp": 11.0,
        "availability": "moderate — book 6+ months out, check connecting flights",
        "tip": "The shower-in-the-sky experience. A380 only. High fuel surcharges but still worth it.",
    },
    {
        "name": "Hilton 5th Night Free",
        "programs": ["amex_mr"],
        "transfer_to": "hilton_honors",
        "points_required": 200000,
        "cabin": "hotel",
        "route": "Any Hilton property (5-night stay, pay 4)",
        "retail_value_usd": 1000,
        "cpp": 0.5,
        "availability": "excellent",
        "tip": "Transfer Amex MR 1:2 to Hilton. On 5-night stays, effective cpp improves 20%.",
    },
]


def get_program(key: str) -> dict | None:
    return PROGRAM_VALUATIONS.get(key.lower().replace(" ", "_").replace("-", "_"))


def get_card(key: str) -> dict | None:
    return CARDS.get(key.lower().replace(" ", "_").replace("-", "_"))


def find_programs_for_partner(partner_key: str) -> list[str]:
    """Which bank programs transfer to this partner?"""
    out = []
    for prog, partners in TRANSFER_PARTNERS.items():
        for p in partners:
            if p["partner"] == partner_key:
                out.append(prog)
                break
    return out


def find_sweet_spots_for_programs(program_keys: list[str]) -> list[dict]:
    """Filter sweet spots reachable from any of the given programs."""
    keys = {k.lower() for k in program_keys}
    return [s for s in SWEET_SPOTS if keys & {p.lower() for p in s["programs"]}]
