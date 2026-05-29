"""Stopover / layover advisor — what to do with time at major hub airports."""
from __future__ import annotations

STOPOVERS: dict[str, dict] = {
    "IST": {
        "city": "Istanbul", "country": "Turkey",
        "airport": "Istanbul Airport (IST)",
        "city_distance_km": 35, "transport_to_city": "Metro 45min ~$3, Taxi ~$30",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA"],
        "in_airport": {
            "2h": ["Turkish Airlines lounge (business/miles)", "Duty-free (massive, best in Europe)", "Airport spa (Turkish bath experience)", "Sleep pods"],
            "3h": ["Full meal at sit-down restaurant", "Shopping — electronics/cosmetics/fashion", "Prayer room"],
        },
        "city_excursions": {
            "4h": ["Galata Tower + Karaköy neighbourhood (take metro)", "Grand Bazaar area (taxi recommended)"],
            "6h": ["Sultanahmet: Blue Mosque + Hagia Sophia exterior", "Bosphorus view from Galata Bridge"],
            "8h": ["Full Sultanahmet: Blue Mosque + Hagia Sophia + Topkapi Palace + Grand Bazaar", "Bosphorus cruise (1hr, ~$15)"],
            "12h+": ["Overnight: all of above + Kadıköy Asian side + restaurant dinner"],
        },
        "tips": ["Store luggage at airport left-luggage (24hr). Get Istanbulkart transit card ($3).", "Blue Mosque closes 5x daily for prayer (30min). Plan around it."],
        "booking_links": {"airport_transit_hotel": "https://www.yotelpad.com/properties/istanbul/", "google_maps": "https://maps.app.goo.gl/istanbul-airport"},
    },
    "DXB": {
        "city": "Dubai", "country": "UAE",
        "airport": "Dubai International (DXB)",
        "city_distance_km": 10, "transport_to_city": "Metro 30min ~$3, Taxi ~$15",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA", "IN"],
        "in_airport": {
            "2h": ["Emirates lounge (business/Platinum)", "Duty-free (gold, perfume, electronics)", "Connection Airside Hotel (day use)", "Zabeel food court"],
            "3h": ["International zone shopping", "Sleep at Connection Hotel"],
        },
        "city_excursions": {
            "4h": ["Dubai Mall + Burj Khalifa exterior (metro ride)", "Dubai Creek + gold/spice souks"],
            "6h": ["Burj Khalifa observation deck (book ahead)", "Dubai Marina walk", "Jumeirah Beach 1hr"],
            "8h": ["Burj Khalifa + Dubai Mall + Dubai Frame or Museum of the Future", "Desert dune bashing tour"],
            "12h+": ["Full day: Burj Khalifa + souks + marina + beach + sunset dhow cruise"],
        },
        "tips": ["Metro runs to city for $3. Dress conservatively outside airport.", "Alcohol only in licensed hotel restaurants/bars."],
        "booking_links": {"airport_hotel": "https://www.thelelapalace.com/en/airport-hotel", "google_maps": "https://maps.app.goo.gl/dubai-airport"},
    },
    "SIN": {
        "city": "Singapore", "country": "Singapore",
        "airport": "Changi Airport (SIN)",
        "city_distance_km": 20, "transport_to_city": "MRT 30min ~$2, Taxi ~$25",
        "visa_free_transit": ["most passports — 96hr VFTF available"],
        "in_airport": {
            "2h": ["Jewel Changi (connected — indoor rain vortex, free)", "Rooftop pool (Crowne Plaza)", "Movie theatre (free for transit passengers)", "Butterfly garden (Terminal 3, free)"],
            "3h": ["Casino (passport needed, small entry fee)", "Full nap in sleep zone", "Full meal at hawker-style food court"],
        },
        "city_excursions": {
            "4h": ["Gardens by the Bay + Marina Bay Sands exterior (MRT)", "Chinatown + hawker centre lunch"],
            "6h": ["Gardens by the Bay Supertrees + Cloud Forest dome (book ahead)", "Clarke Quay river walk + lunch"],
            "8h": ["Sentosa Island + beaches", "Orchard Road shopping + hawker dinner"],
            "12h+": ["Full day: Gardens + Zoo or Universal Studios + hawker dinner + Marina Bay night view"],
        },
        "tips": ["Changi is consistently the world's best airport. Even just Jewel is worth 2hrs.", "96hr VFTF — apply at immigration, free, no advance booking."],
        "booking_links": {"airport_hotel": "https://www.crowneplaza.com/changi", "google_maps": "https://maps.app.goo.gl/changi-airport"},
    },
    "DOH": {
        "city": "Doha", "country": "Qatar",
        "airport": "Hamad International (DOH)",
        "city_distance_km": 15, "transport_to_city": "Metro 30min ~$2, Taxi ~$20",
        "visa_free_transit": ["most nationalities — free transit visa on arrival"],
        "in_airport": {
            "2h": ["Damien Hirst sculptures (free, world class art)", "Qatar Duty Free", "Oryx Lounge (pay)", "Squash court + gym (24hr)"],
            "3h": ["Sleep at Hamad International transit hotel (4hr rooms)", "Al Mourjan Business Lounge"],
        },
        "city_excursions": {
            "4h": ["Souq Waqif (traditional market) + Corniche waterfront walk (metro)"],
            "6h": ["Museum of Islamic Art + Souq Waqif + Pearl-Qatar"],
            "8h": ["Full Doha: MIA + Souq Waqif + Pearl + Katara Cultural Village"],
            "12h+": ["Desert safari or kayaking + all above"],
        },
        "tips": ["Free transit visa for most nationalities. Qatar Airways lounges are among the world's best."],
        "booking_links": {"airport_hotel": "https://www.ihg.com/intercontinental/doha-airport", "google_maps": "https://maps.app.goo.gl/doha-hamad"},
    },
    "NRT": {
        "city": "Tokyo", "country": "Japan",
        "airport": "Narita International (NRT)",
        "city_distance_km": 60, "transport_to_city": "Narita Express 60min ~$30, Limousine Bus 90min ~$25",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA"],
        "in_airport": {
            "2h": ["Ippudo ramen + sushi restaurants", "Duty-free Japanese goods (wagyu snacks, sake, matcha)", "Currency exchange"],
            "3h": ["Onsen (Narita Yonex nearby)", "Try konbini (7-Eleven, FamilyMart) for real Japanese snacks"],
        },
        "city_excursions": {
            "5h": ["Narita town: Naritasan Shinshoji Temple (20min bus, free) + Omotesando shopping street"],
            "8h": ["Tokyo: Asakusa + Senso-ji Temple + Akihabara or Shibuya crossing (2hr train each way — tight)"],
            "12h+": ["Full Tokyo day: Shibuya + Harajuku + Shinjuku + ramen dinner"],
        },
        "tips": ["Tokyo is 60km away — only worth going if you have 8hr+. Narita town is underrated for 5hr+.", "Get IC Suica card at airport for all transit."],
        "booking_links": {"airport_hotel": "https://www.nrtairportrest.com/", "google_maps": "https://maps.app.goo.gl/narita"},
    },
    "HND": {
        "city": "Tokyo", "country": "Japan",
        "airport": "Tokyo Haneda (HND)",
        "city_distance_km": 15, "transport_to_city": "Monorail/Keikyu 30min ~$5, Taxi ~$40",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA"],
        "in_airport": {
            "2h": ["Edo Koji — replica Edo-period shopping street with restaurants", "Rooftop observation deck (free)", "Onsen (Haneda Rest, T2)"],
        },
        "city_excursions": {
            "4h": ["Shinagawa + Odaiba (30min monorail)", "Shibuya crossing (35min)"],
            "6h": ["Asakusa + Senso-ji + Ueno Park"],
            "8h": ["Full Tokyo: Shibuya + Harajuku + Shinjuku"],
        },
        "tips": ["Much closer to Tokyo than Narita. City worth it for even 4hr layovers."],
        "booking_links": {"google_maps": "https://maps.app.goo.gl/haneda"},
    },
    "CDG": {
        "city": "Paris", "country": "France",
        "airport": "Charles de Gaulle (CDG)",
        "city_distance_km": 30, "transport_to_city": "RER B 40min ~$15, Taxi ~$60",
        "visa_free_transit": ["most EU/Schengen + US, GB, AU, CA"],
        "in_airport": {
            "2h": ["Duty-free French wine/champagne/cheese", "Sit-down brasserie in terminal"],
            "3h": ["Air France lounge (Business/Flying Blue)", "Terminals 2E/2F walking exploration"],
        },
        "city_excursions": {
            "4h": ["Montmartre + Sacré-Coeur (RER B to Gare du Nord, Metro)", "Le Marais neighbourhood"],
            "6h": ["Eiffel Tower exterior + Seine bank walk + croissant café"],
            "8h": ["Louvre (book ahead) + Tuileries Garden + Champs-Élysées + Arc de Triomphe"],
            "12h+": ["Full Paris day: Louvre + Eiffel + Montmartre + dinner"],
        },
        "tips": ["RER B train is cheapest (~$15) to city centre. Validate ticket before entering. Pickpockets at Gare du Nord — watch bags."],
        "booking_links": {"airport_hotel": "https://www.hilton.com/en/hotels/cdgophi-hilton-paris-cdg/", "google_maps": "https://maps.app.goo.gl/cdg-paris"},
    },
    "HKG": {
        "city": "Hong Kong", "country": "Hong Kong SAR",
        "airport": "Hong Kong International (HKG)",
        "city_distance_km": 35, "transport_to_city": "Airport Express 24min ~$14, Taxi ~$50",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA", "IN"],
        "in_airport": {
            "2h": ["SkyPlaza mall connected to terminal", "IMAX cinema", "Golf simulator"],
            "3h": ["Sky Deck (T2, free views)", "Dim sum at one of 5 restaurants"],
        },
        "city_excursions": {
            "4h": ["Tsim Sha Tsui waterfront + Avenue of Stars + Victoria Harbour view"],
            "6h": ["The Peak tram + view + Central district"],
            "8h": ["Temple Street night market + dim sum + Victoria Peak + Star Ferry"],
            "12h+": ["Full HK: Lantau Buddha + big Buddha + city + night market"],
        },
        "tips": ["Airport Express is the most reliable. Octopus card ($15 incl deposit) works for all transit."],
        "booking_links": {"airport_hotel": "https://www.regenthotels.com/hongkong", "google_maps": "https://maps.app.goo.gl/hkg"},
    },
    "ICN": {
        "city": "Seoul", "country": "South Korea",
        "airport": "Incheon International (ICN)",
        "city_distance_km": 50, "transport_to_city": "AREX 43min ~$9, Taxi ~$70",
        "visa_free_transit": ["US", "GB", "EU", "AU", "CA"],
        "in_airport": {
            "2h": ["Korean Cultural Street (T2 — traditional crafts, pottery, free)", "Korean spa (Spa On Air, airside, $25)", "Korean BBQ restaurant"],
            "3h": ["Transit hotel (nap rooms from $30/4hr)", "Duty-free K-beauty"],
        },
        "city_excursions": {
            "4h": ["Incheon Chinatown + Jayu Park (nearby, 15min taxi)"],
            "6h": ["Seoul: Gyeongbokgung Palace + Insadong (AREX)"],
            "8h": ["Seoul: Myeongdong shopping + Bukchon Hanok Village + street food"],
            "12h+": ["Full Seoul: palaces + N Seoul Tower + Hongdae nightlife"],
        },
        "tips": ["Incheon is one of the world's best airports. Korean spa airside — genuinely worth it even for 3hr layovers."],
        "booking_links": {"airport_hotel": "https://www.transithotel-incheon.com/", "google_maps": "https://maps.app.goo.gl/incheon"},
    },
    "AMS": {
        "city": "Amsterdam", "country": "Netherlands",
        "airport": "Amsterdam Schiphol (AMS)",
        "city_distance_km": 17, "transport_to_city": "Train 17min ~$6, Taxi ~$45",
        "visa_free_transit": ["US", "GB", "AU", "CA", "most EU"],
        "in_airport": {
            "2h": ["Rijksmuseum satellite (Schiphol Museum, free, real masterpieces)", "Heineken Experience beer tasting bar", "KLM Crown Lounge"],
            "3h": ["Meditation centre (free)", "Casino"],
        },
        "city_excursions": {
            "3h": ["Amsterdam city centre — Vondelpark + Dam Square (train 17min)"],
            "5h": ["Anne Frank House (book months ahead) + canal walk + stroopwafel"],
            "7h": ["Rijksmuseum + Van Gogh Museum + Jordaan neighbourhood + canal cruise"],
            "12h+": ["Full Amsterdam: museums + markets + red light district (curious) + dinner"],
        },
        "tips": ["One of the fastest airports to city in the world (17min). OV-chipkaart or contactless on trains. Bikes everywhere — rent for $15."],
        "booking_links": {"airport_hotel": "https://www.citizenm.com/hotels/europe/amsterdam/amsterdam-airport-hotel", "google_maps": "https://maps.app.goo.gl/schiphol"},
    },
}


async def get_stopover_guide(
    airport: str,
    layover_hours: float,
    passport_country: str = "US",
) -> dict:
    """Get a layover guide for a major hub airport.

    Tells you exactly what you can do with your transit time — in-airport
    activities and city excursions ranked by time available.

    Args:
        airport: Airport IATA code (e.g. "IST", "DXB", "SIN", "DOH", "NRT")
        layover_hours: Hours of layover time
        passport_country: ISO-2 passport for transit visa check (e.g. "US", "IN")
    """
    code = airport.upper()
    data = STOPOVERS.get(code)
    if not data:
        return {
            "airport": code,
            "error": f"No detailed guide for {code} yet.",
            "supported_airports": list(STOPOVERS.keys()),
            "suggest_web_search": [
                f"{code} airport layover guide things to do",
                f"how to spend {int(layover_hours)} hours in {code} airport",
            ],
        }

    # Determine usable time (subtract 90min for re-check-in buffer)
    usable_hours = max(layover_hours - 1.5, 0)

    # In-airport activities
    in_airport_activities = []
    for duration_str, acts in data["in_airport"].items():
        h = float(duration_str.replace("h", ""))
        if usable_hours >= h:
            in_airport_activities.extend(acts)

    # City excursions
    city_excursions = []
    recommended_excursion = None
    if data.get("city_excursions"):
        for duration_str, acts in sorted(data["city_excursions"].items(), key=lambda x: float(x[0].replace("h+", "").replace("h", ""))):
            min_h = float(duration_str.replace("h+", "").replace("h", ""))
            if usable_hours >= min_h:
                city_excursions = acts
                recommended_excursion = duration_str

    # Visa check
    visa_ok = passport_country.upper() in [p.upper() for p in data.get("visa_free_transit", [])]
    visa_note = (
        "✅ Transit without visa likely — verify with airline." if visa_ok
        else f"⚠️ Check transit visa requirements for {passport_country} passport at {code}."
    )

    go_to_city = usable_hours >= 4 and bool(city_excursions)

    return {
        "airport": code,
        "city": data["city"],
        "country": data["country"],
        "layover_hours": layover_hours,
        "usable_hours": round(usable_hours, 1),
        "transport_to_city": data["transport_to_city"],
        "transit_visa": {
            "likely_ok": visa_ok,
            "note": visa_note,
            "verify_url": f"https://www.iatatravelcentre.com/",
        },
        "recommendation": {
            "go_to_city": go_to_city,
            "verdict": (
                f"✅ Go to {data['city']}! {usable_hours:.0f}hrs is enough." if go_to_city
                else f"Stay in airport — {usable_hours:.0f}hrs usable isn't enough for city safely."
            ),
        },
        "in_airport": in_airport_activities,
        "city_excursions": city_excursions if go_to_city else [],
        "tips": data.get("tips", []),
        "booking_links": {
            **data.get("booking_links", {}),
            "google_maps_airport": f"https://www.google.com/maps/search/{data['airport'].replace(' ', '+')}",
            "google_flights_transit": f"https://www.google.com/search?q={code}+airport+layover+guide",
        },
        "suggest_web_search": [
            f"{code} airport layover {int(layover_hours)} hours guide 2026",
            f"things to do {data['city']} in {int(usable_hours)} hours",
        ],
    }
