"""Packing list generator — weather + activities → categorized checklist."""
from __future__ import annotations


async def generate_packing_list(
    destination: str,
    start_date: str,
    end_date: str,
    activities: str = "sightseeing",
    budget_level: str = "moderate",
    travelers: int = 1,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    """Generate a smart packing list based on destination, weather, and planned activities.

    Args:
        destination: City/country name
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        activities: Comma-separated: beach, hiking, business, nightlife, skiing, sightseeing, camping
        budget_level: budget, moderate, luxury
        travelers: Number of travelers
        latitude: Optional — fetches live weather if provided
        longitude: Optional
    """
    from datetime import datetime
    dep = datetime.strptime(start_date, "%Y-%m-%d")
    ret = datetime.strptime(end_date, "%Y-%m-%d")
    nights = max((ret - dep).days, 1)

    # Get weather if coords available
    avg_temp_c = None
    rainy = False
    if latitude and longitude:
        try:
            from .weather import get_weather
            wx = await get_weather(latitude, longitude, start_date, end_date)
            summary = wx.get("summary") or {}
            avg_temp_c = summary.get("avg_high_c")
            rainy_days = summary.get("rainy_days", 0)
            total_days = summary.get("total_days", nights) or nights
            rainy = (rainy_days / total_days) > 0.3 if total_days > 0 else False
        except Exception:
            pass

    acts = {a.strip().lower() for a in activities.split(",") if a.strip()}

    # Temperature categories
    cold = avg_temp_c is not None and avg_temp_c < 12
    mild = avg_temp_c is not None and 12 <= avg_temp_c <= 22
    hot = avg_temp_c is not None and avg_temp_c > 22
    unknown_temp = avg_temp_c is None

    # Clothing days calculation (pack for n days, not nights — re-wear or laundry)
    laundry_days = 3 if budget_level == "budget" else 5
    clothing_days = min(nights, laundry_days)

    items: dict[str, list[dict]] = {
        "Documents & Money": [],
        "Clothing": [],
        "Toiletries": [],
        "Electronics": [],
        "Health & Medicine": [],
        "Gear & Accessories": [],
        "Misc": [],
    }

    # --- Documents ---
    docs = items["Documents & Money"]
    docs += [
        {"item": "Passport", "essential": True, "note": "Check 6+ months validity beyond return date"},
        {"item": "Travel insurance documents", "essential": True},
        {"item": "Flight/hotel confirmation printouts", "essential": True},
        {"item": "Emergency contact list", "essential": True},
        {"item": f"Local currency ({destination})", "essential": True, "note": "Carry some cash for arrival"},
        {"item": "Credit/debit cards (2+ different networks)", "essential": True},
        {"item": "Visa documents / ETA confirmation", "essential": False, "note": "If required"},
        {"item": "Vaccination certificate", "essential": False, "note": "If required by destination"},
        {"item": "International driving permit", "essential": False, "note": "If renting a car"},
    ]
    if "business" in acts:
        docs.append({"item": "Business cards", "essential": True})

    # --- Clothing ---
    cl = items["Clothing"]
    cl += [
        {"item": f"T-shirts / tops ({clothing_days})", "essential": True},
        {"item": f"Underwear ({clothing_days + 1})", "essential": True},
        {"item": f"Socks ({clothing_days + 1})", "essential": True},
    ]
    if cold or unknown_temp:
        cl += [
            {"item": "Warm jacket / down jacket", "essential": True},
            {"item": "Thermal underlayer", "essential": cold},
            {"item": "Sweater / fleece (2)", "essential": True},
            {"item": "Long trousers (2)", "essential": True},
            {"item": "Scarf + gloves + hat", "essential": cold},
        ]
    if mild or hot or unknown_temp:
        cl += [
            {"item": "Light jacket / cardigan", "essential": not cold},
            {"item": "Shorts or light trousers", "essential": hot},
        ]
    if rainy or unknown_temp:
        cl.append({"item": "Rain jacket / packable poncho", "essential": rainy})
    if "beach" in acts:
        cl += [
            {"item": "Swimwear (2)", "essential": True},
            {"item": "Beach cover-up / sarong", "essential": True},
            {"item": "Flip flops / sandals", "essential": True},
        ]
    if "hiking" in acts:
        cl += [
            {"item": "Moisture-wicking hiking shirts (2)", "essential": True},
            {"item": "Hiking trousers / convertible pants", "essential": True},
            {"item": "Hiking boots (broken in)", "essential": True},
            {"item": "Wool hiking socks (3 pairs)", "essential": True},
        ]
    if "skiing" in acts:
        cl += [
            {"item": "Ski jacket + ski trousers", "essential": True},
            {"item": "Thermal base layers", "essential": True},
            {"item": "Ski socks (3 pairs)", "essential": True},
            {"item": "Ski gloves + goggles", "essential": True},
            {"item": "Neck gaiter / balaclava", "essential": True},
        ]
    if "business" in acts:
        cl += [
            {"item": "Smart dress / business suit", "essential": True},
            {"item": "Dress shoes", "essential": True},
            {"item": "Formal shirts (2)", "essential": True},
        ]
    if "nightlife" in acts:
        cl.append({"item": "Going-out outfit", "essential": True})
    cl += [
        {"item": "Comfortable walking shoes", "essential": True},
        {"item": "Pyjamas / sleepwear", "essential": True},
    ]

    # --- Toiletries ---
    tl = items["Toiletries"]
    tl += [
        {"item": "Toothbrush + toothpaste", "essential": True},
        {"item": "Shampoo + conditioner (travel size)", "essential": True},
        {"item": "Body wash / soap", "essential": True},
        {"item": "Deodorant", "essential": True},
        {"item": "Razor + shaving cream", "essential": False},
        {"item": "Face moisturiser / skincare", "essential": False},
        {"item": "Sunscreen SPF 50+", "essential": hot or "beach" in acts or "hiking" in acts},
        {"item": "Lip balm with SPF", "essential": False},
        {"item": "Insect repellent (DEET 30%+)", "essential": "beach" in acts or "hiking" in acts or "camping" in acts},
        {"item": "Hand sanitiser (100ml)", "essential": True},
        {"item": "Wet wipes", "essential": True, "note": "Invaluable on long travel days"},
        {"item": "Feminine hygiene products", "essential": False},
        {"item": "Nail clippers + tweezers", "essential": False},
        {"item": "Microfibre travel towel", "essential": budget_level == "budget" or "camping" in acts},
        {"item": "Laundry detergent sheets", "essential": nights > 7},
    ]
    if hot or "beach" in acts:
        tl.append({"item": "After-sun lotion / aloe vera", "essential": False})

    # --- Electronics ---
    el = items["Electronics"]
    el += [
        {"item": "Phone + charger cable", "essential": True},
        {"item": "Universal travel adapter", "essential": True, "note": "Check destination plug type"},
        {"item": "Portable power bank (20,000mAh)", "essential": True},
        {"item": "Earphones / earbuds", "essential": True},
        {"item": "Downloaded offline maps (Google Maps)", "essential": True, "note": "Download before leaving"},
    ]
    if "business" in acts:
        el += [
            {"item": "Laptop + charger", "essential": True},
            {"item": "USB-C hub / dongle", "essential": False},
        ]
    if "hiking" in acts or "camping" in acts:
        el.append({"item": "Headlamp + spare batteries", "essential": True})
    if budget_level == "luxury":
        el.append({"item": "Noise-cancelling headphones", "essential": False})

    # --- Health ---
    hl = items["Health & Medicine"]
    hl += [
        {"item": "Prescription medications (full supply + extra)", "essential": True},
        {"item": "Paracetamol / ibuprofen", "essential": True},
        {"item": "Antihistamines (allergy + sleep)", "essential": True},
        {"item": "Diarrhoea relief (Imodium)", "essential": True},
        {"item": "Rehydration sachets", "essential": True},
        {"item": "Antiseptic wipes + plasters (assorted)", "essential": True},
        {"item": "Blister plasters (Compeed)", "essential": "hiking" in acts},
        {"item": "Motion sickness tablets", "essential": False},
        {"item": "Eye drops", "essential": False},
        {"item": "Condoms", "essential": False},
    ]
    if hot or "beach" in acts or "hiking" in acts:
        hl.append({"item": "Malaria prophylaxis", "essential": False, "note": "Consult doctor for high-risk areas"})

    # --- Gear ---
    gr = items["Gear & Accessories"]
    gr += [
        {"item": "Daypack / small backpack", "essential": True},
        {"item": "Padlocks (2, TSA-approved)", "essential": True},
        {"item": "Luggage tags", "essential": True},
        {"item": "Packing cubes", "essential": False, "note": "Game changer for staying organised"},
        {"item": "Reusable water bottle (1L)", "essential": True},
        {"item": "Neck pillow (for long flights)", "essential": nights > 5 or True},
        {"item": "Sleep mask + earplugs", "essential": True},
    ]
    if "hiking" in acts:
        gr += [
            {"item": "Trekking poles", "essential": False},
            {"item": "Hydration bladder / water filter", "essential": False},
            {"item": "Emergency whistle", "essential": True},
            {"item": "Blister kit", "essential": True},
        ]
    if "camping" in acts:
        gr += [
            {"item": "Tent (check campsite rules)", "essential": True},
            {"item": "Sleeping bag (appropriate rating)", "essential": True},
            {"item": "Camping stove + fuel", "essential": True},
            {"item": "Lighter / matches", "essential": True},
        ]
    if "beach" in acts:
        gr += [
            {"item": "Waterproof phone pouch", "essential": True},
            {"item": "Dry bag", "essential": False},
            {"item": "Snorkel mask", "essential": False},
        ]

    # --- Misc ---
    ms = items["Misc"]
    ms += [
        {"item": "Local eSIM / SIM card (buy before departure via Airalo)", "essential": True},
        {"item": "Printed emergency contacts + hotel address in local language", "essential": True},
        {"item": "Guidebook or downloaded offline content", "essential": False},
        {"item": "Snacks for transit (nuts, protein bars)", "essential": True},
        {"item": "Small gifts from home country", "essential": False, "note": "Great for hosts / locals"},
    ]
    if travelers > 1:
        ms.append({"item": "Walkie-talkies or group chat set up", "essential": False})

    # Summary counts
    total = sum(len(v) for v in items.values())
    essential = sum(1 for v in items.values() for i in v if i.get("essential"))

    return {
        "destination": destination,
        "trip": {"start": start_date, "end": end_date, "nights": nights, "travelers": travelers},
        "weather": {
            "avg_high_c": avg_temp_c,
            "climate": "cold" if cold else "mild" if mild else "hot" if hot else "unknown",
            "expect_rain": rainy,
        },
        "activities": list(acts),
        "budget_level": budget_level,
        "packing_list": items,
        "summary": {
            "total_items": total,
            "essential_items": essential,
            "clothing_days_packed": clothing_days,
            "laundry_recommended_every_n_days": laundry_days,
        },
        "pro_tips": [
            "Roll clothes instead of folding — saves 30% space.",
            "Pack half the clothes you think you need. Double the money.",
            "Wear your heaviest shoes on the plane.",
            "Put liquids in a separate clear bag at the top for security.",
            f"{'Bring a packable rain jacket — rain expected.' if rainy else 'Low rain expected — light layers ok.'}",
            "Download Google Maps offline for destination before you leave.",
            "Take photos of all documents and email to yourself before departing.",
        ],
        "suggest_web_search": [
            f"packing list {destination} {start_date[:7]} weather",
            f"what not to pack {destination} {', '.join(acts)}",
        ],
    }
