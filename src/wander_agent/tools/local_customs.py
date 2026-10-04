"""Local customs: tipping guide, cultural etiquette, outlet/voltage info."""
from __future__ import annotations

_TIPPING: dict[str, dict] = {
    "US": {"expected": True, "restaurants": "18-22%", "taxis": "15-20%", "hotels": "$2-5/night", "bars": "$1-2/drink", "note": "Tipping is mandatory culture. Sub-15% is rude."},
    "GB": {"expected": True, "restaurants": "10-15%", "taxis": "round up", "hotels": "£1-2/bag", "bars": "not expected", "note": "Service charge often included — check before adding more."},
    "FR": {"expected": False, "restaurants": "5-10% if pleased", "taxis": "round up", "hotels": "€1-2/bag", "bars": "round up", "note": "Service compris included in price. Extra tip = genuine gratitude."},
    "DE": {"expected": False, "restaurants": "5-10%", "taxis": "round up", "hotels": "€1-2/bag", "bars": "round up", "note": "Say desired total when paying cash, e.g. 'macht 22' for €22 on a €19.50 bill."},
    "JP": {"expected": False, "restaurants": "0%", "taxis": "0%", "hotels": "0%", "bars": "0%", "note": "Tipping is considered rude in Japan. It can imply the person needs charity."},
    "TH": {"expected": False, "restaurants": "20-50 THB", "taxis": "round up", "hotels": "20-50 THB/bag", "bars": "20-50 THB/round", "note": "Not mandatory but appreciated. Leave coins on table."},
    "ID": {"expected": False, "restaurants": "10% if no service charge", "taxis": "round up", "hotels": "IDR 10,000-20,000/bag", "bars": "10%", "note": "Service charge often added. Check bill."},
    "AU": {"expected": False, "restaurants": "0-10% for great service", "taxis": "round up", "hotels": "not expected", "bars": "not expected", "note": "Tipping not culturally expected. Wages are high."},
    "ES": {"expected": False, "restaurants": "5-10% if pleased", "taxis": "round up", "hotels": "€1/bag", "bars": "coins", "note": "Leave loose change. 10% is generous."},
    "IT": {"expected": False, "restaurants": "5-10%", "taxis": "round up", "hotels": "€1-2/bag", "bars": "€0.10-0.20 coin", "note": "Coperto (cover charge) on bill is not a tip."},
    "MX": {"expected": True, "restaurants": "10-15%", "taxis": "10%", "hotels": "$20-50 MXN/bag", "bars": "10-15%", "note": "Economy depends on tips. 10% minimum, 15-20% appreciated."},
    "IN": {"expected": True, "restaurants": "10%", "taxis": "10-15%", "hotels": "₹50-100/bag", "bars": "10%", "note": "Service charge often added to bill. Additional cash tip goes directly to staff."},
    "AE": {"expected": False, "restaurants": "10-15% if no service charge", "taxis": "round up + 5 AED", "hotels": "10-20 AED/bag", "bars": "15% if alcohol served", "note": "Service charge common in Dubai hotels. Cash tips appreciated."},
    "SG": {"expected": False, "restaurants": "10% service charge included", "taxis": "not expected", "hotels": "not expected", "bars": "service charge included", "note": "GST + service charge (10%+7%) always added. No extra needed."},
    "CN": {"expected": False, "restaurants": "0%", "taxis": "0%", "hotels": "0%", "bars": "0%", "note": "Tipping not customary. May be refused. Tour guides: small tip OK."},
    "BR": {"expected": True, "restaurants": "10% (taxa de serviço)", "taxis": "round up", "hotels": "R$2-5/bag", "bars": "10%", "note": "10% service charge legally required. Paying it is mandatory."},
    "ZA": {"expected": True, "restaurants": "10-15%", "taxis": "10%", "hotels": "R10-20/bag", "bars": "10%", "note": "Economy relies on tips. Petrol attendants: R5-10."},
    "TR": {"expected": True, "restaurants": "10-15%", "taxis": "round up", "hotels": "20-50 TRY/bag", "bars": "10%", "note": "Tip directly in hand to waiter, not on table."},
    "GR": {"expected": True, "restaurants": "10-15%", "taxis": "round up", "hotels": "€1-2/bag", "bars": "€1/round", "note": "Leave cash on table. Service charge rarely included."},
    "PT": {"expected": False, "restaurants": "5-10%", "taxis": "round up", "hotels": "€1/bag", "bars": "round up", "note": "Appreciated but not mandatory. Leave coins."},
}
_TIPPING_DEFAULT = {
    "expected": False, "restaurants": "5-10% for good service", "taxis": "round up",
    "hotels": "small tip appreciated", "bars": "round up",
    "note": "Tipping customs vary — 10% for good service is universally appreciated.",
}

_ETIQUETTE: dict[str, dict] = {
    "JP": {
        "dos": ["Remove shoes when entering homes/temples", "Bow when greeting", "Use both hands to give/receive cards or gifts", "Queue patiently", "Carry cash — many places don't take cards"],
        "donts": ["Tip anyone", "Talk loudly on public transport", "Eat or drink while walking", "Stick chopsticks upright in rice", "Point at people"],
        "dress_code": "Conservative for temples. Cover shoulders and knees. Remove shoes inside.",
        "religious_notes": "Remove shoes at temples/shrines. Don't touch sacred items.",
        "punctuality": "Being on time is critical — arriving late is disrespectful.",
        "greetings": "Bow slightly. Handshakes acceptable with foreigners. No hugging.",
        "photography": "Ask permission at temples. No photos at some shrines.",
    },
    "IN": {
        "dos": ["Remove shoes before entering temples and homes", "Use right hand for eating/giving", "Dress modestly at religious sites", "Greet with Namaste (palms together)", "Bargain at markets — it's expected"],
        "donts": ["Point feet towards people or religious icons", "Touch someone's head", "Show excessive public affection", "Eat beef (sacred animal in Hindu culture)"],
        "dress_code": "Cover head at Sikh temples. Cover shoulders/knees at all temples.",
        "religious_notes": "Remove shoes outside temples. Women may need head covering in mosques.",
        "punctuality": "Flexible — 30-60 min late is normal in social contexts.",
        "greetings": "Namaste with palms together. Handshakes with same gender usual in cities.",
        "photography": "Ask permission before photographing people. Some temples prohibit cameras.",
    },
    "TH": {
        "dos": ["Wai (palms together) as greeting", "Show respect to monks and royalty", "Dress modestly at temples", "Remove shoes before entering temples or homes", "Smile"],
        "donts": ["Touch anyone's head", "Point feet at people or Buddha images", "Raise voice or show anger", "Disrespect the royal family (serious legal offence)", "Touch monks if you are female"],
        "dress_code": "Cover shoulders and knees at temples. Sarongs often available to borrow.",
        "religious_notes": "Women must not touch or hand things directly to monks.",
        "punctuality": "Flexible. Some lateness accepted.",
        "greetings": "Wai — press palms together at chest height and bow head slightly.",
        "photography": "Ask permission before photographing monks or people praying.",
    },
    "AE": {
        "dos": ["Dress modestly outside of resorts/hotels", "Accept Arabic coffee and dates when offered", "Greet with As-salamu alaykum", "Respect Ramadan hours"],
        "donts": ["Show public affection", "Consume alcohol outside licensed venues", "Swear in public", "Photograph people or military without permission", "Eat or drink on public transport during Ramadan"],
        "dress_code": "Cover shoulders and knees in malls and souks. Bikinis only at beaches/pools.",
        "religious_notes": "Non-Muslims cannot enter mosques unless specifically open to visitors.",
        "punctuality": "Business meetings: be on time. Social: flexible.",
        "greetings": "Same-gender handshake. Men wait for women to extend hand first.",
        "photography": "Avoid photographing Emirati women, government buildings, military.",
    },
    "FR": {
        "dos": ["Greet with Bonjour before speaking", "Make effort to speak French", "Dress smartly in cities", "Wait to be seated in restaurants"],
        "donts": ["Start eating before host says bon appétit", "Ask for a doggy bag", "Speak loudly in restaurants", "Arrive exactly on time to dinner parties — 15 min late is polite"],
        "dress_code": "Smart casual. Avoid sportswear in restaurants.",
        "religious_notes": "Secular country. Religious clothing restricted in government buildings.",
        "punctuality": "Business: be on time. Social dinners: 15 min late acceptable.",
        "greetings": "Handshake for new people. La bise (cheek kiss) with acquaintances.",
        "photography": "Public spaces fine. Ask before photographing individuals.",
    },
    "CN": {
        "dos": ["Accept business cards with both hands and study them", "Bring gifts when invited to homes", "Toast with Ganbei and drink together", "Respect elders — let them enter or sit first"],
        "donts": ["Give clocks, green hats, or pears as gifts (bad symbolism)", "Discuss Taiwan, Tibet, or Tiananmen", "Write names in red ink (funerary connotation)", "Open gifts immediately when received"],
        "dress_code": "Business formal for meetings. Conservative at religious sites.",
        "religious_notes": "Modest dress at temples. Remove hats.",
        "punctuality": "Punctuality expected for business. Social gatherings more flexible.",
        "greetings": "Handshake for business. Nod or slight bow for elders.",
        "photography": "Forbidden in many temples and government areas. Ask first.",
    },
    "US": {
        "dos": ["Smile and be friendly", "Hold doors for people", "Tip service staff generously", "Queue patiently"],
        "donts": ["Ask about salary, religion, or political views with new acquaintances", "Stand too close (personal space ~1m)", "Forget to tip"],
        "dress_code": "Casual in most places. Smart casual for restaurants. Formal for upscale venues.",
        "religious_notes": "Diverse country. Respect all religions.",
        "punctuality": "Business: be on time. Social: within 15 min.",
        "greetings": "Handshake or friendly wave. Hugs with friends.",
        "photography": "Generally unrestricted in public. Private property needs permission.",
    },
}
_ETIQUETTE_DEFAULT = {
    "dos": ["Dress modestly at religious sites", "Learn a basic greeting in the local language", "Ask before photographing people", "Observe local queue customs"],
    "donts": ["Show excessive public affection", "Speak loudly or disruptively", "Ignore local dress codes"],
    "dress_code": "Conservative at religious sites. Smart casual for most situations.",
    "religious_notes": "Research local religious observances before visiting sacred sites.",
    "punctuality": "Research local norms — varies widely by country.",
    "greetings": "Handshake common in most business contexts.",
    "photography": "Ask permission before photographing individuals or sacred sites.",
}

_OUTLETS: dict[str, dict] = {
    "US": {"plug_types": ["A", "B"], "voltage": "120V", "frequency": "60Hz", "note": "Type A (2 flat pins) most common."},
    "CA": {"plug_types": ["A", "B"], "voltage": "120V", "frequency": "60Hz", "note": "Same as USA."},
    "MX": {"plug_types": ["A", "B"], "voltage": "127V", "frequency": "60Hz", "note": "Same plugs as USA."},
    "GB": {"plug_types": ["G"], "voltage": "230V", "frequency": "50Hz", "note": "Type G (3 rectangular pins). Unique to UK/Ireland/HK. Bring a UK adapter."},
    "IE": {"plug_types": ["G"], "voltage": "230V", "frequency": "50Hz", "note": "Same as UK."},
    "HK": {"plug_types": ["G"], "voltage": "220V", "frequency": "50Hz", "note": "Same as UK."},
    "AU": {"plug_types": ["I"], "voltage": "230V", "frequency": "50Hz", "note": "Type I (flat diagonal pins). Also used in NZ and China."},
    "NZ": {"plug_types": ["I"], "voltage": "230V", "frequency": "50Hz", "note": "Same as Australia."},
    "CN": {"plug_types": ["A", "C", "I"], "voltage": "220V", "frequency": "50Hz", "note": "Multiple types. Universal sockets common in hotels."},
    "JP": {"plug_types": ["A", "B"], "voltage": "100V", "frequency": "50/60Hz", "note": "100V is unique — lowest in the world. Most modern electronics work fine."},
    "IN": {"plug_types": ["C", "D", "M"], "voltage": "230V", "frequency": "50Hz", "note": "Type D (3 round pins) most common. Hotels often have universal sockets."},
    "TH": {"plug_types": ["A", "B", "C"], "voltage": "220V", "frequency": "50Hz", "note": "Multiple types. Most hotels have universal sockets."},
    "ID": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Type C/F (2 round pins). European standard."},
    "SG": {"plug_types": ["G"], "voltage": "230V", "frequency": "50Hz", "note": "Same as UK."},
    "MY": {"plug_types": ["G"], "voltage": "240V", "frequency": "50Hz", "note": "Same as UK."},
    "FR": {"plug_types": ["C", "E"], "voltage": "230V", "frequency": "50Hz", "note": "Type E (2 round pins + hole). Standard European."},
    "DE": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Type F (Schuko). Standard across most of Europe."},
    "ES": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Type F/C (Schuko). Standard European."},
    "IT": {"plug_types": ["C", "F", "L"], "voltage": "230V", "frequency": "50Hz", "note": "Type L (3 round pins in line) is unique to Italy. Bring a universal adapter."},
    "GR": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Standard European."},
    "PT": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Standard European."},
    "AE": {"plug_types": ["G", "C", "F"], "voltage": "220-240V", "frequency": "50Hz", "note": "Type G most common in hotels."},
    "SA": {"plug_types": ["A", "B", "G"], "voltage": "127/220V", "frequency": "60Hz", "note": "Dual voltage. Type G in newer buildings."},
    "ZA": {"plug_types": ["M", "N", "C"], "voltage": "230V", "frequency": "50Hz", "note": "Type M (large 3-pin) is South Africa's unique standard. Bring a dedicated adapter."},
    "BR": {"plug_types": ["N", "C"], "voltage": "127/220V", "frequency": "60Hz", "note": "Type N (IEC standard). Voltage varies by region."},
    "TR": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz", "note": "Standard European Schuko."},
    "EG": {"plug_types": ["C", "F"], "voltage": "220V", "frequency": "50Hz", "note": "Standard European."},
    "KE": {"plug_types": ["G"], "voltage": "240V", "frequency": "50Hz", "note": "Type G (UK). Bring a UK adapter."},
}
_OUTLETS_DEFAULT = {
    "plug_types": ["C", "F"], "voltage": "220-240V", "frequency": "50Hz",
    "note": "Most of the world uses 220-240V/50Hz. A universal adapter covers most cases.",
}

_PLUG_DESC = {
    "A": "2 flat parallel pins (North America, Japan)",
    "B": "2 flat pins + round grounding pin (North America)",
    "C": "2 round pins (Europlug — widely compatible)",
    "D": "3 round pins in triangle (India, Nepal)",
    "E": "2 round pins + hole (France, Belgium)",
    "F": "2 round pins with side clips — Schuko (Germany, Europe)",
    "G": "3 rectangular pins in triangle (UK, Ireland, Singapore, HK)",
    "I": "2-3 flat diagonal pins (Australia, NZ, China)",
    "L": "3 round pins in line (Italy)",
    "M": "3 large round pins (South Africa)",
    "N": "2 round pins + oval grounding (Brazil)",
}


def get_tipping_guide(country_iso2: str) -> dict:
    """Get tipping customs and expected amounts for a country.

    Args:
        country_iso2: ISO 2-letter country code (e.g., "US", "JP", "TH")
    """
    code = country_iso2.upper().strip()
    data = _TIPPING.get(code, _TIPPING_DEFAULT)
    return {
        "country_iso2": code,
        "tipping_expected": data.get("expected", False),
        "by_category": {
            "restaurants": data.get("restaurants"),
            "taxis": data.get("taxis"),
            "hotels_per_bag": data.get("hotels"),
            "bars": data.get("bars"),
        },
        "key_note": data.get("note"),
        "data_confidence": "curated_snapshot",
        "suggest_web_search": [f"tipping guide {code} 2026"],
    }


def get_cultural_etiquette(country_iso2: str) -> dict:
    """Get cultural dos, don'ts, dress codes, and etiquette tips for a country.

    Args:
        country_iso2: ISO 2-letter country code (e.g., "JP", "IN", "TH")
    """
    code = country_iso2.upper().strip()
    data = _ETIQUETTE.get(code, _ETIQUETTE_DEFAULT)
    return {
        "country_iso2": code,
        "dos": data.get("dos", []),
        "donts": data.get("donts", []),
        "dress_code": data.get("dress_code"),
        "religious_notes": data.get("religious_notes"),
        "punctuality": data.get("punctuality"),
        "greetings": data.get("greetings"),
        "photography_rules": data.get("photography"),
        "data_confidence": "curated_snapshot",
        "suggest_web_search": [
            f"cultural etiquette {code} tourist guide 2026",
            f"what not to do in {code} as a tourist",
        ],
    }


def get_outlet_info(country_iso2: str) -> dict:
    """Get electrical outlet plug types and voltage information for a country.

    Args:
        country_iso2: ISO 2-letter country code (e.g., "US", "JP", "AU")
    """
    code = country_iso2.upper().strip()
    data = _OUTLETS.get(code, _OUTLETS_DEFAULT)
    plug_types = data.get("plug_types", [])
    voltage = data.get("voltage", "220-240V")
    us_compatible = any(p in ("A", "B") for p in plug_types) and any(v in voltage for v in ("120V", "127V", "100V"))
    eu_compatible = any(p in ("C", "E", "F") for p in plug_types)

    return {
        "country_iso2": code,
        "plug_types": plug_types,
        "plug_descriptions": {p: _PLUG_DESC.get(p, f"Type {p}") for p in plug_types},
        "voltage": voltage,
        "frequency": data.get("frequency"),
        "note": data.get("note"),
        "adapter_needed_from_us": not us_compatible,
        "adapter_needed_from_eu": not eu_compatible,
        "recommendation": "Bring a universal travel adapter — works in 150+ countries.",
        "data_confidence": "curated_snapshot",
        "suggest_web_search": [f"power outlet type {code} travel adapter"],
    }
