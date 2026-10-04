"""Safety tools: emergency contacts, nearby hospitals, solo travel safety."""
from __future__ import annotations
import math

_EMERGENCY: dict[str, dict] = {
    "US": {"police": "911", "ambulance": "911", "fire": "911", "tourist_police": "N/A", "coast_guard": "911", "note": "Single number 911 covers all emergencies."},
    "GB": {"police": "999 / 101 (non-emergency)", "ambulance": "999", "fire": "999", "tourist_police": "N/A", "coast_guard": "999", "note": "112 also works. 101 for non-emergency police."},
    "AU": {"police": "000", "ambulance": "000", "fire": "000", "tourist_police": "131 444", "coast_guard": "000", "note": "106 for hearing/speech impaired. 112 also works on mobile."},
    "JP": {"police": "110", "ambulance": "119", "fire": "119", "tourist_police": "03-3501-0110 (Tokyo)", "coast_guard": "118", "note": "Japan Coast Guard: 118. Tourist helpline: #9110."},
    "TH": {"police": "191", "ambulance": "1669", "fire": "199", "tourist_police": "1155", "coast_guard": "1155", "note": "Tourist Police (1155) have English speakers. Very helpful for tourists."},
    "FR": {"police": "17", "ambulance": "15", "fire": "18", "tourist_police": "N/A", "coast_guard": "196", "note": "112 works for all. SAMU (15) is medical emergency."},
    "DE": {"police": "110", "ambulance": "112", "fire": "112", "tourist_police": "N/A", "coast_guard": "124 124", "note": "112 for fire/ambulance, 110 for police."},
    "ES": {"police": "091 / 112", "ambulance": "112", "fire": "080", "tourist_police": "902 102 112", "coast_guard": "900 202 202", "note": "112 covers all. 091 national police, 092 local police."},
    "IT": {"police": "112 / 113", "ambulance": "118", "fire": "115", "tourist_police": "N/A", "coast_guard": "1530", "note": "112 unified emergency. 113 state police."},
    "IN": {"police": "100", "ambulance": "108", "fire": "101", "tourist_police": "1363", "coast_guard": "1554", "note": "112 also works (unified national). Tourist helpline: 1800-11-1363 (toll-free)."},
    "ID": {"police": "110", "ambulance": "118", "fire": "113", "tourist_police": "N/A", "coast_guard": "N/A", "note": "112 works on most networks."},
    "AE": {"police": "999", "ambulance": "998", "fire": "997", "tourist_police": "800 POLICE (800 765423)", "coast_guard": "996", "note": "Dubai police tourist helpline: +971-4-608-0000."},
    "SG": {"police": "999", "ambulance": "995", "fire": "995", "tourist_police": "1800-255-0000", "coast_guard": "995", "note": "Crime stoppers: 1800-255-0000."},
    "CN": {"police": "110", "ambulance": "120", "fire": "119", "tourist_police": "N/A", "coast_guard": "12395", "note": "Download offline maps before arrival — Google blocked."},
    "MX": {"police": "911", "ambulance": "911", "fire": "911", "tourist_police": "078", "coast_guard": "911", "note": "078 tourist assistance. SETETUR: 800-987-8224."},
    "BR": {"police": "190", "ambulance": "192", "fire": "193", "tourist_police": "N/A", "coast_guard": "185", "note": "Carry photocopies of passport; original in hotel safe."},
    "ZA": {"police": "10111", "ambulance": "10177", "fire": "10177", "tourist_police": "0860-SAFE-SA (0860-723-372)", "coast_guard": "021-938-3300", "note": "Tourist safety: 0860-723-372."},
    "TR": {"police": "155", "ambulance": "112", "fire": "110", "tourist_police": "N/A", "coast_guard": "158", "note": "Jandarma (rural areas): 156."},
    "GR": {"police": "100", "ambulance": "166", "fire": "199", "tourist_police": "171", "coast_guard": "108", "note": "Tourist police (171) have English speakers."},
    "PT": {"police": "112", "ambulance": "112", "fire": "112", "tourist_police": "N/A", "coast_guard": "112", "note": "112 covers all emergencies. Very safe country."},
    "NL": {"police": "112", "ambulance": "112", "fire": "112", "tourist_police": "0900-8844", "coast_guard": "0900-0111", "note": "Non-emergency police: 0900-8844."},
    "CA": {"police": "911", "ambulance": "911", "fire": "911", "tourist_police": "N/A", "coast_guard": "1-800-267-6687", "note": "Same as USA. 911 for all emergencies."},
    "KE": {"police": "999 / 112", "ambulance": "999", "fire": "999", "tourist_police": "+254-20-604-767", "coast_guard": "N/A", "note": "Tourist helpline: +254-20-604-767."},
    "MA": {"police": "19", "ambulance": "150", "fire": "15", "tourist_police": "N/A", "coast_guard": "N/A", "note": "Brigade Touristique in major tourist cities."},
    "NZ": {"police": "111", "ambulance": "111", "fire": "111", "tourist_police": "N/A", "coast_guard": "111", "note": "111 covers all. Non-emergency: 105."},
}
_EMERGENCY_DEFAULT = {
    "police": "112 (EU) / 999 (Commonwealth) / 911 (Americas)",
    "ambulance": "112 / 999 / 911",
    "fire": "112 / 999 / 911",
    "tourist_police": "Check local embassy website",
    "note": "112 works in most countries as universal emergency number from mobile phones.",
}

_SOLO_SAFETY: dict[str, dict] = {
    "TH": {"safety_level": "moderate", "female_solo": "generally safe", "male_solo": "safe", "top_risks": ["Tuk-tuk scams", "Gem scams", "Drink spiking in nightlife areas"], "safe_areas": ["Bangkok tourist zones", "Chiang Mai old city", "Koh Lanta"], "avoid": ["Don't accept unsolicited help from strangers", "Don't leave drinks unattended"], "transport_tip": "Use Bolt or Grab app — metered, safe, no scams."},
    "IN": {"safety_level": "moderate", "female_solo": "exercise caution, especially at night", "male_solo": "generally safe", "top_risks": ["Overcharging tourists", "Distraction thefts", "Harassment in some areas"], "safe_areas": ["Goa beaches", "Rajasthan tourist circuit", "Kerala backwaters"], "avoid": ["Avoid travelling alone at night in isolated areas", "Don't display expensive gear openly"], "transport_tip": "Use Uber/Ola. Agree price before rickshaws."},
    "JP": {"safety_level": "very safe", "female_solo": "one of the safest destinations for female solo travel", "male_solo": "very safe", "top_risks": ["Earthquake preparedness", "Getting lost in rural areas"], "safe_areas": ["All major cities", "Entire Japan generally"], "avoid": ["Nothing specific — very safe country"], "transport_tip": "JR Pass for shinkansen. IC card (Suica) for local transit."},
    "MX": {"safety_level": "variable — city/region dependent", "female_solo": "exercise caution, research specific areas", "male_solo": "exercise caution", "top_risks": ["Opportunistic theft", "Express kidnapping near ATMs", "Carjacking on some highways at night"], "safe_areas": ["Historic Mexico City tourist zones", "Oaxaca", "Yucatan Peninsula"], "avoid": ["Guerrero, Colima, Sinaloa, Tamaulipas states", "Driving at night", "Displaying wealth"], "transport_tip": "Use Uber or licensed taxis from stands — never hail street cabs."},
    "AE": {"safety_level": "very safe", "female_solo": "very safe — strong legal protections", "male_solo": "very safe", "top_risks": ["Legal risks from photos of people without consent", "Drug laws extremely strict"], "safe_areas": ["All Dubai/Abu Dhabi tourist areas"], "avoid": ["Photographing women, palaces, military", "Carrying any drugs"], "transport_tip": "Dubai Metro and taxis are excellent. Careem app popular."},
    "US": {"safety_level": "generally safe — varies by city/neighbourhood", "female_solo": "generally safe — research neighbourhoods", "male_solo": "generally safe", "top_risks": ["Petty theft in tourist areas", "Neighbourhood crime variance"], "safe_areas": ["Well-lit tourist districts", "Most suburban areas"], "avoid": ["Research neighbourhood safety before Airbnb bookings", "Don't display expensive items openly"], "transport_tip": "Uber/Lyft standard. Public transit good in NYC, Chicago, SF, DC."},
    "GB": {"safety_level": "very safe", "female_solo": "very safe", "male_solo": "very safe", "top_risks": ["Pickpocketing on Tube", "Phone snatching in London"], "safe_areas": ["All tourist areas"], "avoid": ["Keep phone in pocket on crowded tube platforms", "Avoid unlit areas late at night"], "transport_tip": "Oyster card or contactless for London. National Rail for intercity."},
    "ZA": {"safety_level": "exercise caution", "female_solo": "exercise significant caution", "male_solo": "exercise caution", "top_risks": ["Muggings", "Carjacking", "Smash-and-grab vehicle theft"], "safe_areas": ["Cape Town V&A Waterfront", "Sandton Johannesburg", "Kruger camps"], "avoid": ["Driving after dark outside secure areas", "Displaying valuables", "Isolated areas alone"], "transport_tip": "Hire a car from reputable company. Uber operates but check safety reviews."},
}
_SOLO_SAFETY_DEFAULT = {
    "safety_level": "research required",
    "female_solo": "research destination-specific advice before traveling",
    "male_solo": "research destination-specific advice",
    "top_risks": ["Petty theft in tourist areas", "Scams targeting tourists"],
    "safe_areas": ["Well-lit tourist districts and established accommodation areas"],
    "avoid": ["Displaying expensive gear openly", "Traveling alone late at night in unfamiliar areas"],
    "transport_tip": "Use reputable ride-hailing apps. Agree fares in advance for taxis.",
}


def get_emergency_contacts(country_iso2: str) -> dict:
    """Get emergency phone numbers (police, ambulance, fire, tourist police) for a country.

    Args:
        country_iso2: ISO 2-letter country code (e.g., "TH", "JP", "FR")
    """
    code = country_iso2.upper().strip()
    data = _EMERGENCY.get(code, _EMERGENCY_DEFAULT)
    return {
        "country_iso2": code,
        "police": data.get("police"),
        "ambulance": data.get("ambulance"),
        "fire": data.get("fire"),
        "tourist_police": data.get("tourist_police"),
        "coast_guard": data.get("coast_guard"),
        "universal_emergency": "112 (works in most countries from mobile)",
        "note": data.get("note"),
        "data_confidence": "curated_snapshot",
        "suggest_web_search": [f"emergency numbers {code}", f"US embassy in {code} emergency contact"],
    }


async def find_nearby_hospitals(
    latitude: float,
    longitude: float,
    radius_km: int = 10,
    max_results: int = 8,
    city: str | None = None,
) -> dict:
    """Find hospitals and medical clinics near a location using OpenStreetMap.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        radius_km: Search radius in km (1-30)
        max_results: Max results to return (1-20)
        city: City name hint for better result context
    """
    from ..utils.http import get_client

    client = await get_client()
    radius_m = max(1000, min(int(radius_km) * 1000, 30000))
    max_results = max(1, min(int(max_results), 20))
    city_hint = city or f"{latitude:.4f},{longitude:.4f}"

    query = (
        f"[out:json][timeout:20];\n(\n"
        f'  node["amenity"="hospital"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  way["amenity"="hospital"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  node["amenity"="clinic"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  way["amenity"="clinic"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  node["healthcare"="hospital"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f'  way["healthcare"="hospital"]["name"](around:{radius_m},{latitude},{longitude});\n'
        f");\nout body center {max_results * 3};\n"
    )

    from ..utils.overpass import overpass_elements

    hospitals = []
    elements, osm_error = await overpass_elements(client, query, timeout=20.0)
    try:
        if elements:
            for el in elements:
                t = el.get("tags", {})
                name = t.get("name", "").strip()
                if not name:
                    continue
                lat_p = el.get("lat") if el.get("type") == "node" else el.get("center", {}).get("lat")
                lon_p = el.get("lon") if el.get("type") == "node" else el.get("center", {}).get("lon")
                if not lat_p or not lon_p:
                    continue

                p1, p2 = math.radians(latitude), math.radians(lat_p)
                a = math.sin(math.radians(lat_p - latitude) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon_p - longitude) / 2) ** 2
                dist_m = round(6_371_000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

                hospitals.append({
                    "name": name,
                    "type": t.get("amenity") or t.get("healthcare", "hospital"),
                    "latitude": lat_p,
                    "longitude": lon_p,
                    "distance_m": dist_m,
                    "phone": t.get("phone") or t.get("contact:phone"),
                    "website": t.get("website") or t.get("contact:website"),
                    "emergency": t.get("emergency"),
                    "opening_hours": t.get("opening_hours"),
                    "links": {
                        "google_maps": f"https://www.google.com/maps?q={lat_p},{lon_p}&z=16",
                        "directions": f"https://www.google.com/maps/dir/{latitude},{longitude}/{lat_p},{lon_p}",
                    },
                    "data_source": "openstreetmap",
                })
                if len(hospitals) >= max_results:
                    break
    except Exception:
        pass

    hospitals.sort(key=lambda x: x["distance_m"])

    return {
        "location": {"latitude": latitude, "longitude": longitude, "city": city_hint},
        "radius_km": radius_km,
        "results_count": len(hospitals),
        "hospitals": hospitals,
        "nearest": hospitals[0]["name"] if hospitals else None,
        "nearest_distance_m": hospitals[0]["distance_m"] if hospitals else None,
        "tip": "For emergencies, call local ambulance first. Private hospitals often faster for tourists.",
        "data_source": "openstreetmap_overpass",
        "data_confidence": "osm_live",
        **({"warning": f"OpenStreetMap lookup failed ({osm_error}) — retry shortly or use the suggest_web_search queries."}
           if osm_error else {}),
        "suggest_web_search": [
            f"best hospital for tourists {city_hint}",
            f"international hospital {city_hint} English speaking",
        ],
    }


def get_solo_travel_safety(country_iso2: str) -> dict:
    """Get solo travel safety advice, top risks, and transport tips for a country.

    Args:
        country_iso2: ISO 2-letter country code (e.g., "TH", "IN", "ZA")
    """
    code = country_iso2.upper().strip()
    data = _SOLO_SAFETY.get(code, _SOLO_SAFETY_DEFAULT)
    return {
        "country_iso2": code,
        "safety_level": data.get("safety_level"),
        "female_solo_travel": data.get("female_solo"),
        "male_solo_travel": data.get("male_solo"),
        "top_risks": data.get("top_risks", []),
        "safe_areas": data.get("safe_areas", []),
        "what_to_avoid": data.get("avoid", []),
        "transport_tip": data.get("transport_tip"),
        "universal_tips": [
            "Share your itinerary with someone back home.",
            "Keep digital and physical copies of passport.",
            "Use a money belt or hidden pouch for passports and cards.",
            "Download offline maps before arriving.",
            "Register with your home country's embassy if staying long-term.",
        ],
        "data_confidence": "curated_snapshot",
        "suggest_web_search": [
            f"solo travel safety {code} 2026",
            f"is {code} safe for tourists 2026",
        ],
    }
