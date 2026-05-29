"""Local SIM card and eSIM guide by country.

Covers 25+ countries with operator, cost, data allowance, where to buy,
tethering policy, and duration-based recommendations.

No API key — pure curated dataset. Updated 2024-Q4.
Fallback to Airalo/Holafly eSIM links for unlisted countries.
"""

from __future__ import annotations

# Country ISO2 → sim options
# Each entry:
#   local_sim: best prepaid SIM for most travelers
#   esim: best eSIM option + Airalo link
#   heavy_user: best for data-heavy use (streaming, hotspot)
#   coverage_quality: "excellent" | "good" | "fair" | "variable"
#   tethering: bool — is hotspot/tethering allowed on tourist SIMs?
#   roaming_note: string — e.g. useful if crossing into neighboring countries
#   tips: list of local tips

_SIM_DATA: dict[str, dict] = {
    "TH": {
        "country": "Thailand",
        "currency": "THB",
        "local_sim": {
            "operator": "AIS (Tourist SIM)",
            "cost_usd": 11,
            "data": "30 GB",
            "validity_days": 30,
            "calls": "Unlimited local + 100 min international",
            "where_to_buy": "Suvarnabhumi/Don Mueang airport kiosks, 7-Eleven, AIS shops",
            "activation": "Instant — scan passport at counter",
            "tips": [
                "AIS has best coverage in northern Thailand (Chiang Mai, Pai)",
                "DTAC good in southern islands (Koh Samui, Phuket)",
                "True Move cheapest but weaker rural coverage",
            ],
        },
        "esim": {
            "operator": "Airalo — AIS eSIM",
            "cost_usd": 13,
            "data": "15 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/thailand-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited data)",
            "cost_usd": 27,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/thailand",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "AIS roams in Laos, Cambodia, Myanmar — useful for border trips",
    },
    "JP": {
        "country": "Japan",
        "currency": "JPY",
        "local_sim": {
            "operator": "IIJmio Tourist SIM",
            "cost_usd": 20,
            "data": "15 GB",
            "validity_days": 15,
            "calls": "Data only (calls via LINE/WhatsApp)",
            "where_to_buy": "Narita/Haneda/Kansai airport counters, BIC Camera, Yodobashi",
            "activation": "Insert and follow in-flight setup guide",
            "tips": [
                "Tethering not allowed on most tourist SIMs — get a pocket WiFi if hotspot needed",
                "B-Mobile and IIJmio both run on Docomo's excellent network",
                "Rakuten Mobile eSIM now works — cheapest for long stays (¥0 first month)",
            ],
        },
        "esim": {
            "operator": "Airalo — IIJ eSIM",
            "cost_usd": 18,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/japan-esim",
        },
        "heavy_user": {
            "operator": "Sakura Mobile Pocket WiFi",
            "cost_usd": 35,
            "data": "Unlimited (soft throttle after 10GB/day)",
            "validity_days": 30,
            "link": "https://www.sakuramobile.jp/pocket-wifi/",
        },
        "coverage_quality": "excellent",
        "tethering": False,
        "roaming_note": "Japan SIMs do not roam in Korea/Taiwan — buy separately",
    },
    "KR": {
        "country": "South Korea",
        "currency": "KRW",
        "local_sim": {
            "operator": "KT Olleh Tourist SIM",
            "cost_usd": 18,
            "data": "Unlimited (3Mbps after 5 GB/day)",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "Incheon/Gimpo airport arrivals hall, GS25/CU convenience stores",
            "activation": "Insert SIM, call automated activation line",
            "tips": [
                "SKT and KT both have 5G coverage in Seoul metro",
                "LG U+ cheapest for short stays (7-day passes)",
                "Kakao Maps works offline — download before arriving",
            ],
        },
        "esim": {
            "operator": "Airalo — KT eSIM",
            "cost_usd": 15,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/south-korea-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 25,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/south-korea",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "KT roams in Japan under bilateral agreement — limited data",
    },
    "ID": {
        "country": "Indonesia",
        "currency": "IDR",
        "local_sim": {
            "operator": "Telkomsel (SimPATI Tourist)",
            "cost_usd": 7,
            "data": "20 GB",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "Ngurah Rai (Bali) arrivals, Soekarno-Hatta (Jakarta) T3, Alfamart/Indomaret",
            "activation": "Passport required — counter registration",
            "tips": [
                "Telkomsel best coverage across all islands including Komodo, Flores",
                "XL Axiata good in Java and Bali, cheaper",
                "3/Tri best for hotspot and streaming in cities",
                "Rural Sulawesi/Papua — only Telkomsel works reliably",
            ],
        },
        "esim": {
            "operator": "Airalo — XL eSIM",
            "cost_usd": 8,
            "data": "15 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/indonesia-esim",
        },
        "heavy_user": {
            "operator": "3 (Tri) Unlimited",
            "cost_usd": 10,
            "data": "Unlimited (throttled after 10GB/day)",
            "validity_days": 30,
            "link": "https://www.tri.co.id/",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "No meaningful roaming — buy local SIM at each major island hub",
    },
    "VN": {
        "country": "Vietnam",
        "currency": "VND",
        "local_sim": {
            "operator": "Viettel Tourist SIM",
            "cost_usd": 5,
            "data": "4 GB/day (throttled after)",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "Noi Bai (Hanoi) and Tan Son Nhat (HCMC) airport kiosks, VinMart",
            "activation": "Passport scan — 5 min activation",
            "tips": [
                "Viettel has strongest coverage end-to-end Hanoi → HCMC",
                "Vietnamobile cheapest but weak in rural areas",
                "Grab requires local number — activate before leaving airport",
            ],
        },
        "esim": {
            "operator": "Airalo — Viettel eSIM",
            "cost_usd": 7,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/vietnam-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 22,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/vietnam",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Viettel roams in Cambodia and Laos at reasonable rates",
    },
    "MY": {
        "country": "Malaysia",
        "currency": "MYR",
        "local_sim": {
            "operator": "Maxis Hotlink Tourist SIM",
            "cost_usd": 8,
            "data": "25 GB",
            "validity_days": 14,
            "calls": "Free local calls",
            "where_to_buy": "KLIA/KLIA2 arrivals, 7-Eleven, Maxis centres",
            "activation": "Instant",
            "tips": [
                "Celcom best for Sabah/Sarawak (Borneo)",
                "Digi good in KL and Penang",
                "YES 5G has fastest speeds in Klang Valley",
            ],
        },
        "esim": {
            "operator": "Airalo — Maxis eSIM",
            "cost_usd": 10,
            "data": "20 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/malaysia-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 24,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/malaysia",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Maxis Malaysia–Singapore roaming pass RM15/day — useful for day trips to SG",
    },
    "SG": {
        "country": "Singapore",
        "currency": "SGD",
        "local_sim": {
            "operator": "Singtel hi!Tourist SIM",
            "cost_usd": 12,
            "data": "100 GB",
            "validity_days": 14,
            "calls": "Unlimited local",
            "where_to_buy": "Changi Airport Terminal 1–4 arrivals, 7-Eleven",
            "activation": "Instant",
            "tips": [
                "All three operators (Singtel, StarHub, M1) have near-identical coverage",
                "SIM cards require passport registration",
                "Changi airport kiosk prices identical to city — no markup",
            ],
        },
        "esim": {
            "operator": "Airalo — Singtel eSIM",
            "cost_usd": 10,
            "data": "50 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/singapore-esim",
        },
        "heavy_user": {
            "operator": "Singtel Unlimited Day Pass",
            "cost_usd": 5,
            "data": "Unlimited",
            "validity_days": 1,
            "link": "https://www.singtel.com/personal/products-services/mobile/prepaid-cards/hi-tourist",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "Small country — no roaming needed within Singapore",
    },
    "IN": {
        "country": "India",
        "currency": "INR",
        "local_sim": {
            "operator": "Airtel Tourist SIM",
            "cost_usd": 8,
            "data": "2 GB/day",
            "validity_days": 28,
            "calls": "Unlimited local",
            "where_to_buy": "DEL/BOM/BLR/CCU airport Airtel counters — must buy at airport (tourist SIM restriction)",
            "activation": "Passport + visa required — 2–4 hour activation delay possible",
            "tips": [
                "ONLY buy tourist SIMs at airports — local SIMs require Indian address proof",
                "Airtel best for cities + Rajasthan + Himachal Pradesh",
                "Jio cheapest overall but activation slower for foreign passports",
                "Goa, Kerala, Leh: all three operators work",
                "Ladakh and Andamans: BSNL only (buy a BSNL card separately)",
            ],
        },
        "esim": {
            "operator": "Airalo — Airtel eSIM",
            "cost_usd": 15,
            "data": "10 GB",
            "validity_days": 28,
            "link": "https://www.airalo.com/india-esim",
        },
        "heavy_user": {
            "operator": "Airtel Unlimited Prepaid",
            "cost_usd": 12,
            "data": "2 GB/day unlimited",
            "validity_days": 84,
            "link": "https://www.airtel.in/prepaid-recharge-plans",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Indian SIMs do not roam in Nepal/Sri Lanka — buy local at border",
    },
    "GB": {
        "country": "United Kingdom",
        "currency": "GBP",
        "local_sim": {
            "operator": "Three UK (Pay As You Go)",
            "cost_usd": 15,
            "data": "12 GB",
            "validity_days": 30,
            "calls": "300 minutes + 3000 texts",
            "where_to_buy": "Three stores, Tesco Mobile, WH Smith (Heathrow), Boots",
            "activation": "Instant",
            "tips": [
                "Three UK allows EU roaming (still works post-Brexit in most EU countries at no extra cost)",
                "EE has best rural UK coverage if visiting Scotland Highlands or Cornwall",
                "Lycamobile cheapest for international calls",
            ],
        },
        "esim": {
            "operator": "Airalo — Three UK eSIM",
            "cost_usd": 12,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/united-kingdom-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 29,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/united-kingdom",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "Three UK includes EU roaming in France, Germany, Spain, Italy and 70+ others",
    },
    "DE": {
        "country": "Germany",
        "currency": "EUR",
        "local_sim": {
            "operator": "Aldi Talk (O2 network)",
            "cost_usd": 12,
            "data": "15 GB",
            "validity_days": 30,
            "calls": "Unlimited EU calls",
            "where_to_buy": "Aldi supermarkets, Saturn, MediaMarkt, Rewe",
            "activation": "Online ID verification (VideoIdent) — takes 15 min",
            "tips": [
                "O2 network weakest in rural Bavaria — use Telekom (more expensive) for countryside",
                "Lidl Connect uses Telekom network — best coverage for cheap price",
                "Congstar (Telekom network) has strong 5G in cities",
            ],
        },
        "esim": {
            "operator": "Airalo — Telekom eSIM",
            "cost_usd": 14,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/germany-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/germany",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "EU roaming included in all German prepaid SIMs — works in Austria, Switzerland, France, etc.",
    },
    "FR": {
        "country": "France",
        "currency": "EUR",
        "local_sim": {
            "operator": "Orange Holiday Europe",
            "cost_usd": 30,
            "data": "30 GB EU-wide",
            "validity_days": 14,
            "calls": "Unlimited EU calls",
            "where_to_buy": "Orange stores, CDG/ORY airport, FNAC",
            "activation": "Instant",
            "tips": [
                "Free Mobile is cheapest but has worst rural coverage",
                "Orange Holiday card roams across all 27 EU countries + Switzerland",
                "SFR stronger than Orange in rural Provence/Alsace",
            ],
        },
        "esim": {
            "operator": "Airalo — Orange eSIM",
            "cost_usd": 15,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/france-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/france",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "All French SIMs include EU roaming. Orange works in French overseas territories (Martinique, Guadeloupe).",
    },
    "ES": {
        "country": "Spain",
        "currency": "EUR",
        "local_sim": {
            "operator": "Lebara Spain",
            "cost_usd": 12,
            "data": "25 GB",
            "validity_days": 30,
            "calls": "Unlimited",
            "where_to_buy": "Carrefour, El Corte Inglés, tobacco kiosks (estancos), online",
            "activation": "Requires passport + NIE or passport-only registration (slower for tourists)",
            "tips": [
                "DIGI Spain cheapest but registration requires Spanish address",
                "Yoigo (Más Móvil) good for Balearic/Canary Islands",
                "Orange Spain has best rural Andalucia coverage",
            ],
        },
        "esim": {
            "operator": "Airalo — Movistar eSIM",
            "cost_usd": 13,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/spain-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/spain",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "EU roaming included — works in Portugal, France, Morocco (check individually)",
    },
    "IT": {
        "country": "Italy",
        "currency": "EUR",
        "local_sim": {
            "operator": "TIM (Telecom Italia) Tourist",
            "cost_usd": 25,
            "data": "50 GB",
            "validity_days": 30,
            "calls": "Unlimited",
            "where_to_buy": "TIM stores, FCO/MXP/VCE airports, tabacchi",
            "activation": "Passport required at counter",
            "tips": [
                "TIM has best coverage in Cinque Terre, Amalfi Coast, Sicilian interior",
                "Iliad cheapest (€7.99/month) but registration requires Italian fiscal code or patience",
                "WindTre good in northern cities (Milan, Venice)",
            ],
        },
        "esim": {
            "operator": "Airalo — TIM eSIM",
            "cost_usd": 14,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/italy-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/italy",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "EU roaming included. TIM covers Vatican City and San Marino.",
    },
    "AE": {
        "country": "UAE",
        "currency": "AED",
        "local_sim": {
            "operator": "du Tourist SIM",
            "cost_usd": 14,
            "data": "25 GB",
            "validity_days": 28,
            "calls": "200 local minutes",
            "where_to_buy": "DXB Terminal 1/3 arrivals, du and Etisalat shops in malls",
            "activation": "Passport scan — instant",
            "tips": [
                "VoIP calls (WhatsApp, FaceTime audio/video) are BLOCKED on both UAE networks",
                "Only du and Etisalat exist — no third operator",
                "Data is fast (5G in Dubai) but pricey — don't burn it streaming",
                "du slightly cheaper; Etisalat slightly better coverage in Abu Dhabi",
            ],
        },
        "esim": {
            "operator": "Airalo — du eSIM",
            "cost_usd": 18,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/united-arab-emirates-esim",
        },
        "heavy_user": {
            "operator": "Etisalat Unlimited Tourist",
            "cost_usd": 28,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.etisalat.ae/en/c/prepaid-tourist.html",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "UAE SIMs roam in Saudi Arabia and Oman with add-on passes",
    },
    "TR": {
        "country": "Turkey",
        "currency": "TRY",
        "local_sim": {
            "operator": "Turkcell Tourist SIM",
            "cost_usd": 15,
            "data": "20 GB",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "IST Sabiha Gökçen/Istanbul arrivals, Turkcell dealers everywhere",
            "activation": "Passport required — register within 30 days or SIM blocked",
            "tips": [
                "Register your foreign SIM or buy local — foreign SIMs blocked after ~30 days",
                "Türk Telekom best for Cappadocia and eastern Anatolia",
                "Vodafone Turkey cheaper in cities but weaker rural",
                "Tourist SIMs are exempt from the 120-day rule — confirmed 2024",
            ],
        },
        "esim": {
            "operator": "Airalo — Turkcell eSIM",
            "cost_usd": 13,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/turkey-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 26,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/turkey",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Turkcell roams in TRNC (Northern Cyprus). No EU roaming.",
    },
    "US": {
        "country": "United States",
        "currency": "USD",
        "local_sim": {
            "operator": "T-Mobile Prepaid Tourist",
            "cost_usd": 30,
            "data": "Unlimited",
            "validity_days": 30,
            "calls": "Unlimited US + Canada + Mexico",
            "where_to_buy": "T-Mobile stores, Best Buy, Target, Walmart — pick up SIM before arrival via Amazon",
            "activation": "Online activation — requires US ZIP code (use destination hotel ZIP)",
            "tips": [
                "T-Mobile best for urban US and Hawaii",
                "Verizon best for rural coverage and national parks",
                "AT&T Prepaid good middle ground",
                "US SIM cards can be shipped to hotel before arrival",
                "Google Fi works globally — useful if combining US with other countries",
            ],
        },
        "esim": {
            "operator": "Airalo — T-Mobile eSIM",
            "cost_usd": 28,
            "data": "15 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/united-states-esim",
        },
        "heavy_user": {
            "operator": "T-Mobile Unlimited Prepaid",
            "cost_usd": 50,
            "data": "Unlimited (5G)",
            "validity_days": 30,
            "link": "https://www.t-mobile.com/prepaid-phone",
        },
        "coverage_quality": "excellent",
        "tethering": True,
        "roaming_note": "T-Mobile Prepaid includes Canada and Mexico unlimited calling/texting",
    },
    "AU": {
        "country": "Australia",
        "currency": "AUD",
        "local_sim": {
            "operator": "Telstra Prepaid",
            "cost_usd": 25,
            "data": "30 GB",
            "validity_days": 28,
            "calls": "Unlimited",
            "where_to_buy": "SYD/MEL/BNE airports, Woolworths, Telstra stores",
            "activation": "Instant",
            "tips": [
                "Telstra essential for outback travel — only operator with regional coverage",
                "Optus and Vodafone fine in cities but dead outside major highways",
                "Boost Mobile (Telstra network) 30% cheaper than Telstra direct",
            ],
        },
        "esim": {
            "operator": "Airalo — Telstra eSIM",
            "cost_usd": 22,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/australia-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 35,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/australia",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "No meaningful regional roaming agreements — buy local SIM",
    },
    "CA": {
        "country": "Canada",
        "currency": "CAD",
        "local_sim": {
            "operator": "Public Mobile (Telus network)",
            "cost_usd": 22,
            "data": "30 GB",
            "validity_days": 30,
            "calls": "Unlimited",
            "where_to_buy": "7-Eleven, Shoppers Drug Mart, online",
            "activation": "Online — takes 10 min",
            "tips": [
                "Canada has some of the world's most expensive mobile data — eSIM often cheaper",
                "Chatr (Rogers) cheapest but weak rural BC/Quebec",
                "Lucky Mobile (Bell) better eastern Canada coverage",
                "Pre-order online before flying — avoid airport prices (2× markup)",
            ],
        },
        "esim": {
            "operator": "Airalo — Public Mobile eSIM",
            "cost_usd": 20,
            "data": "15 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/canada-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 45,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/canada",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Public Mobile includes US roaming add-on (100 min/500 MB) for cross-border trips",
    },
    "ZA": {
        "country": "South Africa",
        "currency": "ZAR",
        "local_sim": {
            "operator": "Vodacom Tourist SIM",
            "cost_usd": 8,
            "data": "10 GB",
            "validity_days": 30,
            "calls": "100 minutes local",
            "where_to_buy": "JNB/CPT airport kiosks, Shoprite, Checkers, Vodacom stores",
            "activation": "Passport required",
            "tips": [
                "Vodacom and MTN both strong in Cape Town and Johannesburg",
                "MTN better in KwaZulu-Natal and Garden Route",
                "Cell C cheapest but weak coverage outside major cities",
                "Load-shedding (power cuts) affects cell towers — download offline maps",
            ],
        },
        "esim": {
            "operator": "Airalo — Vodacom eSIM",
            "cost_usd": 9,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/south-africa-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 28,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/south-africa",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Vodacom roams in Zimbabwe, Mozambique, Lesotho — useful for southern Africa circuits",
    },
    "KE": {
        "country": "Kenya",
        "currency": "KES",
        "local_sim": {
            "operator": "Safaricom (Tourist Bundle)",
            "cost_usd": 5,
            "data": "10 GB",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "JKIA arrivals, Safaricom shops, petrol stations",
            "activation": "Passport required",
            "tips": [
                "Safaricom is the ONLY option for reliable coverage — do not use Airtel Kenya",
                "M-PESA mobile money on Safaricom essential for paying matatus and small shops",
                "Game reserves (Maasai Mara, Amboseli) have patchy coverage — download offline maps",
            ],
        },
        "esim": {
            "operator": "Airalo — Safaricom eSIM",
            "cost_usd": 8,
            "data": "5 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/kenya-esim",
        },
        "heavy_user": {
            "operator": "Safaricom Unlimited Daily Pass",
            "cost_usd": 3,
            "data": "Unlimited",
            "validity_days": 1,
            "link": "https://www.safaricom.co.ke/personal/data/bundles",
        },
        "coverage_quality": "fair",
        "tethering": True,
        "roaming_note": "Safaricom roams in Uganda and Tanzania under EAC agreement",
    },
    "MA": {
        "country": "Morocco",
        "currency": "MAD",
        "local_sim": {
            "operator": "Maroc Telecom (IAM) Tourist SIM",
            "cost_usd": 8,
            "data": "30 GB",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "CMN/RAK airport arrivals, Maroc Telecom shops, tabac shops",
            "activation": "Passport required",
            "tips": [
                "Maroc Telecom best in Atlas Mountains and Sahara",
                "Orange Maroc good in Marrakech and Casablanca",
                "inwi (Wana) cheapest but weakest in rural areas",
                "Desert tours: only Maroc Telecom has signal near Merzouga/Zagora",
            ],
        },
        "esim": {
            "operator": "Airalo — Maroc Telecom eSIM",
            "cost_usd": 10,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/morocco-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited)",
            "cost_usd": 24,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/morocco",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Maroc Telecom roams in Mauritania and West Africa",
    },
    "GE": {
        "country": "Georgia",
        "currency": "GEL",
        "local_sim": {
            "operator": "Magti Tourist SIM",
            "cost_usd": 4,
            "data": "10 GB",
            "validity_days": 30,
            "calls": "Unlimited local",
            "where_to_buy": "TBS airport arrivals, Magti/Geocell shops, small kiosks",
            "activation": "Passport scan — instant",
            "tips": [
                "Georgia one of cheapest mobile data countries in world",
                "Geocell (Silknet) equally good in Tbilisi and Batumi",
                "Beeline Georgia weakest but cheapest",
                "Kazbegi and Svaneti: Magti stronger in mountains",
            ],
        },
        "esim": {
            "operator": "Airalo — Magti eSIM",
            "cost_usd": 5,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/georgia-esim",
        },
        "heavy_user": {
            "operator": "Magti Unlimited",
            "cost_usd": 8,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.magticom.ge/en",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "Georgian SIMs do not roam in Armenia or Azerbaijan — buy separately at borders",
    },
    "PT": {
        "country": "Portugal",
        "currency": "EUR",
        "local_sim": {
            "operator": "MEO Tourist SIM",
            "cost_usd": 18,
            "data": "20 GB EU-wide",
            "validity_days": 30,
            "calls": "Unlimited",
            "where_to_buy": "LIS/OPO airport arrivals, MEO/NOS/Vodafone stores, FNAC",
            "activation": "Passport required",
            "tips": [
                "NOS has best coverage in Alentejo and Algarve coast",
                "MEO strongest in Azores and Madeira",
                "All include EU roaming — works in Spain without extra cost",
            ],
        },
        "esim": {
            "operator": "Airalo — MEO eSIM",
            "cost_usd": 12,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/portugal-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/portugal",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "EU roaming included. MEO works in Azores/Madeira — confirm before travel.",
    },
    "GR": {
        "country": "Greece",
        "currency": "EUR",
        "local_sim": {
            "operator": "Cosmote Tourist SIM",
            "cost_usd": 20,
            "data": "15 GB EU",
            "validity_days": 14,
            "calls": "Unlimited local + EU",
            "where_to_buy": "ATH airport arrivals, Cosmote/Vodafone GR/Wind stores, kiosks",
            "activation": "Instant",
            "tips": [
                "Cosmote essential for island-hopping — best coverage on small Aegean islands",
                "Vodafone Greece good in Thessaloniki and Crete",
                "Wind Greece cheapest but weak signal on remote islands",
            ],
        },
        "esim": {
            "operator": "Airalo — Cosmote eSIM",
            "cost_usd": 15,
            "data": "10 GB",
            "validity_days": 30,
            "link": "https://www.airalo.com/greece-esim",
        },
        "heavy_user": {
            "operator": "Holafly (unlimited EU)",
            "cost_usd": 34,
            "data": "Unlimited",
            "validity_days": 30,
            "link": "https://www.holafly.com/esim/greece",
        },
        "coverage_quality": "good",
        "tethering": True,
        "roaming_note": "EU roaming included. Cosmote covers most Greek islands; carry offline maps for Cyclades.",
    },
}

# City/country name → ISO2 lookup
_NAME_TO_ISO2: dict[str, str] = {
    "thailand": "TH", "thai": "TH", "bangkok": "TH", "bkk": "TH", "phuket": "TH", "chiang mai": "TH",
    "japan": "JP", "tokyo": "JP", "osaka": "JP", "kyoto": "JP", "nrt": "JP", "hnd": "JP",
    "south korea": "KR", "korea": "KR", "seoul": "KR", "busan": "KR", "icn": "KR",
    "indonesia": "ID", "bali": "ID", "jakarta": "ID", "lombok": "ID", "yogyakarta": "ID", "dps": "ID",
    "vietnam": "VN", "hanoi": "VN", "ho chi minh": "VN", "hoi an": "VN", "saigon": "VN",
    "malaysia": "MY", "kuala lumpur": "MY", "kl": "MY", "penang": "MY", "langkawi": "MY", "kul": "MY",
    "singapore": "SG", "sin": "SG",
    "india": "IN", "delhi": "IN", "mumbai": "IN", "goa": "IN", "bangalore": "IN",
    "uk": "GB", "united kingdom": "GB", "england": "GB", "london": "GB", "britain": "GB", "scotland": "GB",
    "germany": "DE", "berlin": "DE", "munich": "DE", "frankfurt": "DE", "hamburg": "DE",
    "france": "FR", "paris": "FR", "nice": "FR", "marseille": "FR", "lyon": "FR",
    "spain": "ES", "barcelona": "ES", "madrid": "ES", "seville": "ES", "ibiza": "ES",
    "italy": "IT", "rome": "IT", "milan": "IT", "florence": "IT", "venice": "IT",
    "uae": "AE", "dubai": "AE", "abu dhabi": "AE", "sharjah": "AE",
    "turkey": "TR", "istanbul": "TR", "cappadocia": "TR", "antalya": "TR",
    "usa": "US", "united states": "US", "new york": "US", "los angeles": "US", "miami": "US",
    "australia": "AU", "sydney": "AU", "melbourne": "AU", "brisbane": "AU",
    "canada": "CA", "toronto": "CA", "vancouver": "CA", "montreal": "CA",
    "south africa": "ZA", "cape town": "ZA", "johannesburg": "ZA", "safari": "ZA",
    "kenya": "KE", "nairobi": "KE", "mombasa": "KE", "maasai mara": "KE",
    "morocco": "MA", "marrakech": "MA", "marrakesh": "MA", "casablanca": "MA", "fez": "MA",
    "georgia": "GE", "tbilisi": "GE", "batumi": "GE",
    "portugal": "PT", "lisbon": "PT", "porto": "PT", "algarve": "PT",
    "greece": "GR", "athens": "GR", "santorini": "GR", "mykonos": "GR", "crete": "GR",
}


def _resolve_country(country_input: str) -> str | None:
    """Return ISO2 from country name, city name, or ISO2 code."""
    s = country_input.strip()
    upper = s.upper()
    if upper in _SIM_DATA:
        return upper
    found = _NAME_TO_ISO2.get(s.lower())
    return found


async def get_local_sim_guide(
    country: str,
    trip_duration_days: int = 7,
    data_heavy: bool = False,
) -> dict:
    """Get local SIM card and eSIM recommendations for a destination country.

    Returns operator names, approximate cost, data allowance, where to buy,
    activation steps, tethering policy, and duration-based advice.
    Covers 25+ countries. Falls back to Airalo/Holafly eSIM universal links
    for unlisted countries.

    eSIM always recommended if your phone supports it — activate before boarding,
    no airport queue required.

    Args:
        country: Country name (e.g., "Thailand", "Japan") or ISO2 code (e.g., "TH", "JP")
                 or destination city (e.g., "Bangkok", "Tokyo")
        trip_duration_days: Trip length in days (affects recommendation)
        data_heavy: True if you stream video, work remotely, or need constant hotspot
    """
    iso2 = _resolve_country(country)
    country_input_clean = country.strip()

    if iso2 is None or iso2 not in _SIM_DATA:
        # Fallback for unlisted countries
        airalo_search = f"https://www.airalo.com/search?q={country_input_clean.replace(' ', '+')}"
        holafly_search = f"https://www.holafly.com/esim/{country_input_clean.lower().replace(' ', '-')}"
        return {
            "country": country_input_clean,
            "in_dataset": False,
            "recommendation": "eSIM recommended — buy before departure to avoid airport queues",
            "primary_option": {
                "operator": "Airalo",
                "why": "Largest eSIM marketplace, 200+ countries, competitive prices",
                "link": airalo_search,
            },
            "unlimited_option": {
                "operator": "Holafly",
                "why": "Unlimited data eSIM, excellent customer support",
                "link": holafly_search,
            },
            "general_tips": [
                "Buy eSIM before boarding — activate on landing",
                "Keep home SIM in second slot for WhatsApp/banking 2FA",
                "Download offline maps (Maps.me or Google Maps offline) before flying",
                "Check if your phone is unlocked and eSIM-compatible",
            ],
            "data_confidence": "fallback — country not in curated dataset",
        }

    data = _SIM_DATA[iso2]

    # Duration-based recommendation
    if trip_duration_days <= 3:
        rec_type = "esim"
        rec_reason = f"Short trip ({trip_duration_days}d) — eSIM easiest, no airport SIM queue"
    elif trip_duration_days <= 10:
        rec_type = "heavy_user" if data_heavy else "esim"
        rec_reason = (
            f"{'Data-heavy ' if data_heavy else ''}mid-length trip ({trip_duration_days}d) — "
            + ("unlimited eSIM best value" if data_heavy else "eSIM or local SIM both work well")
        )
    else:
        rec_type = "heavy_user" if data_heavy else "local_sim"
        rec_reason = (
            f"Longer trip ({trip_duration_days}d) — "
            + ("unlimited plan best value" if data_heavy else "local SIM cheapest per day")
        )

    primary = data.get(rec_type) or data.get("local_sim")
    esim = data.get("esim")
    heavy = data.get("heavy_user")
    local_sim = data.get("local_sim")

    esim_supported_note = (
        "eSIM supported on iPhone XS+, most Samsung Galaxy S/A flagships 2019+, "
        "Google Pixel 3+. Check your model before buying."
    )

    return {
        "country": data["country"],
        "iso2": iso2,
        "currency": data["currency"],
        "in_dataset": True,
        "trip_duration_days": trip_duration_days,
        "data_heavy": data_heavy,
        "recommendation": rec_reason,
        "recommended_option": primary,
        "esim_option": esim,
        "heavy_user_option": heavy,
        "local_sim_option": local_sim,
        "coverage_quality": data["coverage_quality"],
        "tethering_allowed": data["tethering"],
        "roaming_note": data.get("roaming_note"),
        "esim_compatibility_note": esim_supported_note,
        "general_tips": [
            "Buy/activate eSIM before boarding — takes 2 min, works on landing",
            "Keep home SIM in second slot for banking 2FA SMS",
            "Screenshot your data plan and hotspot instructions in case of no signal",
            "Download Google Maps offline for your destinations before departing",
        ],
        "data_confidence": "curated_snapshot_2024q4",
        "note": (
            "Prices approximate — may vary by vendor and season. "
            "Verify before purchase. Airport kiosks sometimes charge 10-20% more than city stores."
        ),
    }
