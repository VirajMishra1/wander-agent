"""Travel health advisor — vaccines, health risks, water safety per destination."""
from __future__ import annotations

# Curated from CDC Yellow Book + WHO recommendations (2024-2025 snapshot)
HEALTH_DATA: dict[str, dict] = {
    "TH": {"country": "Thailand",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Japanese Encephalitis (rural)", "Rabies (if outdoor activities)", "Hepatitis B"],
        "routine_vaccines": ["MMR", "Tdap", "COVID-19", "Flu", "Varicella"],
        "health_risks": ["Dengue fever (year-round)", "Malaria (rural border areas)", "Zika virus", "Food/waterborne illness"],
        "water_safety": "avoid_tap", "water_note": "Drink bottled or purified only. Ice at reputable restaurants usually safe.",
        "mosquito_risk": "high", "mosquito_note": "Use DEET 30%+ repellent, long sleeves at dawn/dusk. Dengue has no vaccine.",
        "altitude_sickness": False,
        "food_safety": "Cook it, boil it, peel it, or forget it. Street food from busy stalls generally safe.",
        "emergency_number": "1669 (ambulance), 191 (police)",
        "nearest_hospital_quality": "Bangkok and Chiang Mai have world-class hospitals (Bumrungrad, Bangkok Hospital). Rural areas limited.",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/thailand",
    },
    "ID": {"country": "Indonesia / Bali",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (if outdoor activities)", "Japanese Encephalitis (rural)"],
        "health_risks": ["Dengue fever", "Malaria (Papua, Kalimantan, remote islands)", "Rabies (Bali — avoid dogs/monkeys)", "Bali belly (food/water)"],
        "water_safety": "avoid_tap", "water_note": "Never drink tap. Sealed bottled water only.",
        "mosquito_risk": "high", "mosquito_note": "Dengue risk year-round. Malaria risk in Bali is low but exists.",
        "altitude_sickness": False,
        "food_safety": "Warung food generally safe from busy places. Avoid raw vegetables at unknown restaurants.",
        "emergency_number": "118 (ambulance), 110 (police)",
        "nearest_hospital_quality": "BIMC Nusa Dua (Bali) is good for tourists. Serious cases may need medevac to Singapore.",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/indonesia",
    },
    "JP": {"country": "Japan",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Japanese Encephalitis (rural travel)"],
        "health_risks": ["Air pollution (urban, mild)", "Earthquakes + tsunami (coastal)"],
        "water_safety": "tap_safe", "water_note": "Tap water is safe everywhere in Japan.",
        "mosquito_risk": "low",
        "altitude_sickness": False,
        "food_safety": "Exceptionally safe. Raw fish (sushi/sashimi) from reputable restaurants is safe.",
        "emergency_number": "119 (ambulance/fire), 110 (police)",
        "nearest_hospital_quality": "World-class. Major language barrier — carry translation app.",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/japan",
    },
    "IN": {"country": "India",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Cholera", "Rabies", "Japanese Encephalitis (rural/monsoon)", "Malaria prophylaxis"],
        "health_risks": ["Traveller's diarrhoea (very common)", "Malaria", "Dengue", "Typhoid", "Rabies", "Air pollution (Delhi/major cities)", "Heat stroke"],
        "water_safety": "avoid_tap", "water_note": "NEVER drink tap water. Sealed bottles only. Avoid ice at street stalls.",
        "mosquito_risk": "very_high", "mosquito_note": "Malaria and dengue risk significant. Take prophylaxis if in rural areas.",
        "altitude_sickness": True, "altitude_note": "Risk if visiting Ladakh, Himachal Pradesh above 3000m.",
        "food_safety": "Stick to freshly cooked hot food. Avoid salads, unpeeled fruit, street ice. Delhi belly is almost universal.",
        "emergency_number": "108 (ambulance), 100 (police)",
        "nearest_hospital_quality": "Apollo, Fortis, Max hospitals are excellent (major cities). Rural facilities extremely limited.",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/india",
    },
    "VN": {"country": "Vietnam",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (if outdoor activities)", "Japanese Encephalitis"],
        "health_risks": ["Dengue", "Malaria (remote highland/border areas)", "Food/waterborne illness", "Air pollution (Hanoi/HCMC)"],
        "water_safety": "avoid_tap",
        "mosquito_risk": "high",
        "altitude_sickness": False,
        "food_safety": "Pho and bun bo from busy street stalls are generally safe. Avoid raw shellfish.",
        "emergency_number": "115 (ambulance), 113 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/vietnam",
    },
    "KE": {"country": "Kenya",
        "required_vaccines": ["Yellow Fever (if arriving from endemic country)"],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Meningococcal", "Rabies", "Malaria prophylaxis (essential)"],
        "health_risks": ["Malaria (year-round, high risk)", "Typhoid", "Yellow fever", "Rift Valley Fever", "HIV/STIs"],
        "water_safety": "avoid_tap", "water_note": "Bottled water only. Boil/treat all water outside main hotels.",
        "mosquito_risk": "very_high", "mosquito_note": "Malaria prophylaxis (Malarone/Doxycycline) ESSENTIAL. Use bed nets.",
        "altitude_sickness": True, "altitude_note": "Nairobi at 1600m — minimal risk. Mt Kenya above 3000m — serious risk.",
        "food_safety": "Only eat fully cooked food. Avoid salads at non-tourist restaurants.",
        "emergency_number": "999 or 112 (ambulance), 999 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/kenya",
    },
    "ZA": {"country": "South Africa",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (if wildlife areas)", "Malaria prophylaxis (Kruger/KZN coast)"],
        "health_risks": ["Malaria (Kruger, KwaZulu-Natal coast)", "HIV/STIs (high prevalence)", "Crime/safety in cities", "Sun exposure"],
        "water_safety": "tap_safe", "water_note": "Tap water safe in Cape Town, Johannesburg, Durban. Check in rural areas.",
        "mosquito_risk": "moderate", "mosquito_note": "Risk only in malaria zones (Kruger, north KZN, Limpopo). Cape Town is malaria-free.",
        "altitude_sickness": False,
        "food_safety": "Generally safe in urban restaurants. Excellent seafood. Braai culture.",
        "emergency_number": "10177 (ambulance), 10111 (police), 112 (mobile)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/south-africa",
    },
    "MX": {"country": "Mexico",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid"],
        "health_risks": ["Montezuma's Revenge (traveller's diarrhoea)", "Dengue", "Zika (some areas)", "Crime/safety"],
        "water_safety": "avoid_tap", "water_note": "Never drink tap water. Bottled or purified only — even for brushing teeth.",
        "mosquito_risk": "moderate",
        "altitude_sickness": True, "altitude_note": "Mexico City at 2200m — acclimatise first day. Avoid heavy exercise day 1.",
        "food_safety": "Street tacos from busy stalls generally fine. Avoid uncooked salsas at unknown spots.",
        "emergency_number": "911",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/mexico",
    },
    "PE": {"country": "Peru",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (if trekking)", "Yellow Fever (Amazon)", "Malaria prophylaxis (Amazon basin)"],
        "health_risks": ["Altitude sickness (Cusco, Machu Picchu)", "Malaria (Amazon)", "Yellow Fever (Amazon)", "Food/water illness"],
        "water_safety": "avoid_tap",
        "mosquito_risk": "high",
        "altitude_sickness": True, "altitude_note": "Cusco 3400m, Machu Picchu 2430m. REST day 1 in Cusco. Acetazolamide helps. Coca tea available locally.",
        "food_safety": "Ceviche from reputable restaurants safe. World-class cuisine. Avoid tap water in all preparations.",
        "emergency_number": "117 (ambulance), 105 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/peru",
    },
    "FR": {"country": "France",
        "required_vaccines": [],
        "recommended_vaccines": [],
        "health_risks": ["Heatwaves (summer)", "Pickpockets (Paris tourist areas)"],
        "water_safety": "tap_safe",
        "mosquito_risk": "low",
        "altitude_sickness": False,
        "food_safety": "Excellent. French food safety standards are high.",
        "emergency_number": "15 (SAMU ambulance), 17 (police), 18 (fire), 112 (EU emergency)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/france",
    },
    "IT": {"country": "Italy", "required_vaccines": [], "recommended_vaccines": [],
        "health_risks": ["Heatwaves (summer, especially south)"],
        "water_safety": "tap_safe", "mosquito_risk": "low", "altitude_sickness": False,
        "food_safety": "Excellent. Tap water drinkable everywhere.",
        "emergency_number": "118 (ambulance), 113 (police), 112 (EU)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/italy",
    },
    "ES": {"country": "Spain", "required_vaccines": [], "recommended_vaccines": [],
        "health_risks": ["Heatwaves (summer)"],
        "water_safety": "tap_safe", "mosquito_risk": "low", "altitude_sickness": False,
        "food_safety": "Excellent. Tap water safe except Canary Islands (bottled recommended).",
        "emergency_number": "112",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/spain",
    },
    "GB": {"country": "United Kingdom", "required_vaccines": [], "recommended_vaccines": [],
        "health_risks": [],
        "water_safety": "tap_safe", "mosquito_risk": "none", "altitude_sickness": False,
        "food_safety": "Excellent food safety standards.",
        "emergency_number": "999 or 112",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/united-kingdom",
    },
    "AU": {"country": "Australia", "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A (remote areas)"],
        "health_risks": ["UV/sun exposure (extreme)", "Dangerous wildlife", "Dengue (north Queensland)"],
        "water_safety": "tap_safe", "mosquito_risk": "low",
        "altitude_sickness": False,
        "food_safety": "Excellent. Highest food safety standards.",
        "emergency_number": "000",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/australia",
    },
    "NP": {"country": "Nepal",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (trekking)", "Japanese Encephalitis (Terai/lowlands)"],
        "health_risks": ["Altitude sickness (HAPE/HACE above 3500m)", "Traveller's diarrhoea", "Malaria (Terai lowlands)", "Giardia (water)"],
        "water_safety": "avoid_tap", "water_note": "Never drink tap. Treat all water when trekking. Giardia is common.",
        "mosquito_risk": "moderate",
        "altitude_sickness": True, "altitude_note": "Kathmandu 1400m — fine. EBC trek peaks 5000m+. Acclimatise strictly. Descend immediately if HACE/HAPE symptoms.",
        "food_safety": "Dhal bhat from reputable places is safe and nutritious. Avoid salads and uncooked food.",
        "emergency_number": "102 (ambulance), 100 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/nepal",
    },
    "SG": {"country": "Singapore", "required_vaccines": [], "recommended_vaccines": ["Hepatitis A"],
        "health_risks": ["Dengue (local outbreaks)"],
        "water_safety": "tap_safe", "mosquito_risk": "low",
        "altitude_sickness": False,
        "food_safety": "Excellent. Hawker centres are government-graded — safe.",
        "emergency_number": "995 (ambulance), 999 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/singapore",
    },
    "MA": {"country": "Morocco",
        "required_vaccines": [],
        "recommended_vaccines": ["Hepatitis A", "Typhoid", "Rabies (if rural)"],
        "health_risks": ["Traveller's diarrhoea", "Heat exhaustion (Sahara)", "Altitude (Atlas Mountains)"],
        "water_safety": "avoid_tap", "water_note": "Bottled only. Mint tea is boiled and safe.",
        "mosquito_risk": "low", "altitude_sickness": False,
        "food_safety": "Tagines and couscous from restaurants are generally safe. Avoid raw salads at budget spots.",
        "emergency_number": "15 (ambulance), 19 (police)",
        "official_cdc": "https://wwwnc.cdc.gov/travel/destinations/traveler/none/morocco",
    },
}

# ISO2 aliases
for code, alias in [("TH", "BKK"), ("JP", "NRT"), ("JP", "TYO"), ("ID", "DPS"),
                     ("IN", "DEL"), ("VN", "HAN"), ("SG", "SIN"), ("MA", "RAK")]:
    HEALTH_DATA[alias] = HEALTH_DATA[code]


async def check_travel_health(
    destination_iso2: str,
    trip_duration_days: int = 7,
) -> dict:
    """Get health and vaccination advice for a travel destination.

    Covers required vaccines, recommended vaccines, health risks,
    water safety, mosquito precautions, and altitude sickness.
    Data from CDC Yellow Book + WHO (2024-2025 snapshot).

    Args:
        destination_iso2: Country ISO-2 code (e.g. "TH", "IN", "KE", "JP")
        trip_duration_days: Trip length — affects which precautions are relevant
    """
    code = destination_iso2.upper()
    data = HEALTH_DATA.get(code)
    if not data:
        return {
            "destination": code,
            "error": "No health data for this destination.",
            "supported_destinations": {k: v["country"] for k, v in HEALTH_DATA.items() if len(k) == 2},
            "official_cdc": f"https://wwwnc.cdc.gov/travel/destinations/",
            "suggest_web_search": [f"CDC travel health {code} vaccines required 2026"],
        }

    urgency_items: list[str] = []
    if data.get("required_vaccines"):
        urgency_items.append(f"Get required vaccines: {', '.join(data['required_vaccines'])}")
    if data.get("mosquito_risk") in ("high", "very_high"):
        urgency_items.append("Start anti-malarial medication (if needed) 1-2 weeks before departure")
    if data.get("altitude_sickness"):
        urgency_items.append("Consult doctor about Acetazolamide (altitude sickness prevention)")

    prep_timeline = []
    if data.get("recommended_vaccines"):
        prep_timeline.append({"weeks_before": 6, "action": f"Book travel health clinic. Get: {', '.join(data['recommended_vaccines'][:3])}"})
    if data.get("mosquito_risk") in ("high", "very_high"):
        prep_timeline.append({"weeks_before": 2, "action": "Fill malaria prophylaxis prescription. Buy DEET repellent."})
    prep_timeline.append({"weeks_before": 2, "action": "Get travel insurance with medical evacuation cover."})
    prep_timeline.append({"weeks_before": 1, "action": "Pack first aid kit: Imodium, rehydration salts, antibiotics (if prescribed), antihistamines."})

    return {
        "destination": data["country"],
        "iso2": code,
        "trip_duration_days": trip_duration_days,
        "vaccines": {
            "required": data.get("required_vaccines", []),
            "recommended": data.get("recommended_vaccines", []),
            "routine": data.get("routine_vaccines", ["MMR", "Tdap", "COVID-19", "Flu"]),
            "note": "Required = cannot enter without proof. Recommended = strongly advised by CDC/WHO.",
        },
        "health_risks": data.get("health_risks", []),
        "water_safety": {
            "status": data.get("water_safety", "unknown"),
            "safe_to_drink_tap": data.get("water_safety") == "tap_safe",
            "note": data.get("water_note", ""),
        },
        "mosquito_precautions": {
            "risk_level": data.get("mosquito_risk", "low"),
            "note": data.get("mosquito_note", ""),
            "actions": ["DEET 30%+ repellent", "Long sleeves at dawn/dusk", "Sleep under bed net"] if data.get("mosquito_risk") in ("high", "very_high") else [],
        },
        "altitude_sickness": {
            "risk": data.get("altitude_sickness", False),
            "note": data.get("altitude_note", ""),
        },
        "food_safety": data.get("food_safety", ""),
        "emergency_number": data.get("emergency_number", "112"),
        "hospital_quality": data.get("nearest_hospital_quality", ""),
        "urgency_actions": urgency_items,
        "preparation_timeline": sorted(prep_timeline, key=lambda x: -x["weeks_before"]),
        "official_sources": {
            "cdc": data.get("official_cdc", "https://wwwnc.cdc.gov/travel/"),
            "who": f"https://www.who.int/countries/{code.lower()}/",
        },
        "data_confidence": "curated_snapshot_2024_2025",
        "important_note": "This is a SNAPSHOT. Consult a travel health clinic 4-6 weeks before departure for personalised advice.",
        "suggest_web_search": [
            f"travel health {data['country']} vaccines required 2026",
            f"malaria risk {data['country']} 2026" if data.get("mosquito_risk") in ("high", "very_high") else f"safe to eat {data['country']} food guide",
        ],
    }
