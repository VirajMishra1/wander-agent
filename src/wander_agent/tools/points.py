"""Credit card points/miles tools.

Six tools for points travelers: valuation, transfer partners, points-vs-cash,
earning estimates, sweet spot awards, and cross-program comparison.
"""

from __future__ import annotations

import json
from typing import Any

from ..data.points_data import (
    CARDS,
    PROGRAM_VALUATIONS,
    SWEET_SPOTS,
    TRANSFER_PARTNERS,
    find_programs_for_partner,
    find_sweet_spots_for_programs,
)
from ..utils.profile_store import load_profile


def _resolve_program(key: str) -> str:
    k = key.lower().replace(" ", "_").replace("-", "_")
    if k in PROGRAM_VALUATIONS:
        return k
    for pk, pv in PROGRAM_VALUATIONS.items():
        if k in pv["name"].lower() or k == pv.get("issuer", "").lower():
            return pk
    return k


def _profile_programs() -> list[str]:
    """Extract program keys from user's stored card portfolio."""
    profile = load_profile()
    cards = profile.get("cards") or []
    programs = set()
    for c in cards:
        card_key = c.get("card_key", "")
        card_info = CARDS.get(card_key)
        if card_info:
            programs.add(card_info["program"])
        elif c.get("program"):
            programs.add(c["program"])
    return list(programs)


async def estimate_points_value(
    points_cost: int,
    cash_price: float,
    program: str,
    currency: str = "USD",
    taxes_fees: float = 0.0,
) -> dict:
    prog_key = _resolve_program(program)
    prog = PROGRAM_VALUATIONS.get(prog_key)
    if not prog:
        known = sorted(PROGRAM_VALUATIONS.keys())
        return {"error": f"Unknown program '{program}'.", "known_programs": known}

    net_cash = cash_price - taxes_fees
    if points_cost <= 0:
        return {"error": "points_cost must be positive."}

    cpp = round(net_cash * 100 / points_cost, 2)

    if cpp >= prog["cpp_high"]:
        verdict = "excellent"
        detail = f"Above {prog['cpp_high']}cpp ceiling — outstanding redemption."
    elif cpp >= prog["cpp_mid"]:
        verdict = "good"
        detail = f"Above {prog['cpp_mid']}cpp average — solid use of points."
    elif cpp >= prog["cpp_low"]:
        verdict = "fair"
        detail = f"At or above {prog['cpp_low']}cpp floor — acceptable but not special."
    else:
        verdict = "poor"
        portal_note = ""
        if prog.get("cpp_portal"):
            portal_note = f" You'd get {prog['cpp_portal']}cpp just using the travel portal."
        detail = f"Below {prog['cpp_low']}cpp floor — bad deal.{portal_note}"

    return {
        "program": prog["name"],
        "currency_name": prog["currency"],
        "points_cost": points_cost,
        "cash_price": cash_price,
        "taxes_fees_paid_cash": taxes_fees,
        "net_value_redeemed": round(net_cash, 2),
        "cents_per_point": cpp,
        "verdict": verdict,
        "detail": detail,
        "baseline_cpp": {
            "low": prog["cpp_low"],
            "mid": prog["cpp_mid"],
            "high": prog["cpp_high"],
        },
        "program_notes": prog.get("notes", ""),
    }


async def find_transfer_partners(
    program: str,
) -> dict:
    prog_key = _resolve_program(program)
    prog = PROGRAM_VALUATIONS.get(prog_key)
    if not prog:
        return {"error": f"Unknown program '{program}'.", "known_programs": sorted(PROGRAM_VALUATIONS.keys())}

    partners = TRANSFER_PARTNERS.get(prog_key, [])
    if not partners:
        return {
            "program": prog["name"],
            "note": "This is a direct loyalty program, not a transferable bank currency. Points are used within the program only.",
            "partners": [],
        }

    enriched = []
    for p in partners:
        partner_prog = PROGRAM_VALUATIONS.get(p["partner"])
        enriched.append({
            "partner": partner_prog["name"] if partner_prog else p["partner"],
            "partner_key": p["partner"],
            "transfer_ratio": p["ratio"],
            "transfer_time": p["transfer_time"],
            "partner_cpp_mid": partner_prog["cpp_mid"] if partner_prog else None,
            "partner_notes": partner_prog.get("notes", "") if partner_prog else "",
        })

    enriched.sort(key=lambda x: x.get("partner_cpp_mid") or 0, reverse=True)

    return {
        "program": prog["name"],
        "program_key": prog_key,
        "total_partners": len(enriched),
        "partners": enriched,
        "tip": "Transfer to the partner with highest cpp for your specific booking. Check availability BEFORE transferring — transfers are irreversible.",
    }


async def calculate_points_or_cash(
    cash_price: float,
    points_price: int,
    program: str,
    category: str | None = None,
    card_key: str | None = None,
    currency: str = "USD",
    taxes_fees_on_award: float = 0.0,
) -> dict:
    prog_key = _resolve_program(program)
    prog = PROGRAM_VALUATIONS.get(prog_key)
    if not prog:
        return {"error": f"Unknown program '{program}'."}

    if points_price <= 0 or cash_price <= 0:
        return {"error": "Both cash_price and points_price must be positive."}

    net_cash_saved = cash_price - taxes_fees_on_award
    cpp = round(net_cash_saved * 100 / points_price, 2)

    points_earning = 0
    earning_detail = None
    if card_key:
        card = CARDS.get(card_key.lower().replace(" ", "_").replace("-", "_"))
        if card:
            multiplier = card["base_earn"]
            if category:
                cat_key = category.lower().replace(" ", "_")
                for ck, cv in card["bonus_categories"].items():
                    if cat_key in ck or ck in cat_key:
                        multiplier = cv
                        break
            points_earning = int(cash_price * multiplier)
            earning_detail = f"Paying cash earns ~{points_earning} {prog['currency']} ({multiplier}x on {category or 'base'})."

    if cpp >= prog["cpp_mid"]:
        recommendation = "use_points"
        reason = f"At {cpp}cpp, this is above the {prog['cpp_mid']}cpp average — points are the better play."
    elif cpp >= prog["cpp_low"]:
        if points_earning > points_price * 0.3:
            recommendation = "pay_cash"
            reason = f"At {cpp}cpp (fair value), paying cash and earning {points_earning} points back is better long-term."
        else:
            recommendation = "use_points"
            reason = f"At {cpp}cpp (fair value), points are a reasonable use."
    else:
        recommendation = "pay_cash"
        reason = f"At {cpp}cpp, below the {prog['cpp_low']}cpp floor — save your points for a better redemption."

    result: dict[str, Any] = {
        "recommendation": recommendation,
        "reason": reason,
        "cents_per_point": cpp,
        "cash_price": cash_price,
        "points_price": points_price,
        "taxes_fees_on_award": taxes_fees_on_award,
        "program": prog["name"],
    }
    if earning_detail:
        result["cash_earning"] = earning_detail
        result["points_earned_if_cash"] = points_earning
    return result


async def estimate_points_earning(
    amount: float,
    card_key: str,
    category: str = "general",
    currency: str = "USD",
) -> dict:
    ck = card_key.lower().replace(" ", "_").replace("-", "_")
    card = CARDS.get(ck)
    if not card:
        return {"error": f"Unknown card '{card_key}'.", "known_cards": sorted(CARDS.keys())}

    prog = PROGRAM_VALUATIONS.get(card["program"], {})
    multiplier = card["base_earn"]
    matched_category = "base"

    cat_key = category.lower().replace(" ", "_")
    for ck_name, cv in card["bonus_categories"].items():
        if cat_key in ck_name or ck_name in cat_key:
            multiplier = cv
            matched_category = ck_name
            break

    points_earned = int(amount * multiplier)
    cpp_mid = prog.get("cpp_mid", 1.5)
    cash_value = round(points_earned * cpp_mid / 100, 2)

    return {
        "card": card["name"],
        "program": prog.get("name", card["program"]),
        "amount_spent": amount,
        "category": category,
        "matched_category": matched_category,
        "multiplier": f"{multiplier}x",
        "points_earned": points_earned,
        "estimated_value": f"${cash_value}",
        "at_cpp": cpp_mid,
        "all_bonus_categories": card["bonus_categories"],
        "annual_fee": card["annual_fee"],
    }


async def find_sweet_spot_awards(
    programs: str | None = None,
    cabin: str | None = None,
    max_points: int | None = None,
    route_keyword: str | None = None,
) -> dict:
    prog_list: list[str] = []
    if programs:
        prog_list = [_resolve_program(p.strip()) for p in programs.split(",")]
    else:
        prog_list = _profile_programs()

    if prog_list:
        spots = find_sweet_spots_for_programs(prog_list)
    else:
        spots = list(SWEET_SPOTS)

    if cabin:
        cab = cabin.lower()
        spots = [s for s in spots if cab in s["cabin"].lower()]

    if max_points:
        spots = [s for s in spots if s["points_required"] <= max_points]

    if route_keyword:
        kw = route_keyword.lower()
        spots = [s for s in spots if kw in s["route"].lower() or kw in s["name"].lower()]

    spots.sort(key=lambda s: s["cpp"], reverse=True)

    results = []
    for s in spots:
        results.append({
            "name": s["name"],
            "points_required": s["points_required"],
            "cabin": s["cabin"],
            "route": s["route"],
            "retail_value_usd": s["retail_value_usd"],
            "cpp": s["cpp"],
            "availability": s["availability"],
            "tip": s["tip"],
            "reachable_from": [PROGRAM_VALUATIONS[p]["name"] for p in s["programs"] if p in PROGRAM_VALUATIONS],
            "transfer_to": PROGRAM_VALUATIONS.get(s["transfer_to"], {}).get("name", s["transfer_to"]),
        })

    return {
        "filtered_by_programs": [PROGRAM_VALUATIONS.get(p, {}).get("name", p) for p in prog_list] if prog_list else "all",
        "total_sweet_spots": len(results),
        "sweet_spots": results,
        "tip": "Always check award availability BEFORE transferring points. Transfers are one-way and irreversible.",
    }


async def compare_points_programs(
    cash_price: float,
    programs: str | None = None,
    cabin: str = "economy",
    route: str | None = None,
    currency: str = "USD",
) -> dict:
    prog_list: list[str] = []
    if programs:
        prog_list = [_resolve_program(p.strip()) for p in programs.split(",")]
    else:
        prog_list = _profile_programs()

    if not prog_list:
        return {
            "error": "No programs specified and no cards in profile. Pass programs='chase_ur,amex_mr' or add cards to your profile.",
            "known_programs": sorted(k for k in PROGRAM_VALUATIONS if k in TRANSFER_PARTNERS),
        }

    comparisons = []
    for pk in prog_list:
        prog = PROGRAM_VALUATIONS.get(pk)
        if not prog:
            continue

        cpp_mid = prog["cpp_mid"]
        estimated_points = int(cash_price * 100 / cpp_mid)

        portal_cpp = prog.get("cpp_portal")
        portal_points = int(cash_price * 100 / portal_cpp) if portal_cpp else None

        partners = TRANSFER_PARTNERS.get(pk, [])
        best_partner = None
        if partners:
            enriched = []
            for p in partners:
                pp = PROGRAM_VALUATIONS.get(p["partner"])
                if pp:
                    enriched.append({"name": pp["name"], "cpp_mid": pp["cpp_mid"], "ratio": p["ratio"]})
            if enriched:
                enriched.sort(key=lambda x: x["cpp_mid"], reverse=True)
                best_partner = enriched[0]

        sweet = find_sweet_spots_for_programs([pk])
        if cabin:
            sweet = [s for s in sweet if cabin.lower() in s["cabin"].lower() or s["cabin"] == "hotel"]
        if route:
            rk = route.lower()
            sweet = [s for s in sweet if rk in s["route"].lower()]

        comparisons.append({
            "program": prog["name"],
            "program_key": pk,
            "cpp_mid": cpp_mid,
            "estimated_points_at_mid": estimated_points,
            "portal_points": portal_points,
            "portal_cpp": portal_cpp,
            "best_transfer_partner": best_partner,
            "matching_sweet_spots": len(sweet),
            "top_sweet_spot": sweet[0]["name"] if sweet else None,
        })

    comparisons.sort(key=lambda c: c["cpp_mid"], reverse=True)

    best = comparisons[0] if comparisons else None
    return {
        "cash_price": cash_price,
        "currency": currency.upper(),
        "cabin": cabin,
        "programs_compared": len(comparisons),
        "comparisons": comparisons,
        "recommendation": f"Best value: {best['program']} at {best['cpp_mid']}cpp mid-range." if best else "No programs matched.",
        "tip": "Higher cpp = fewer points needed. But check actual award pricing — these are baseline estimates.",
    }
