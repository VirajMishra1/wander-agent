"""Kiwi.com MCP client — live flight search with real prices.

Calls the public Kiwi MCP SSE server at mcp.kiwi.com.
No API key required. Returns [] on any failure (graceful degradation).
"""

from __future__ import annotations

import json
from datetime import datetime

_KIWI_URL = "https://mcp.kiwi.com"
_TIMEOUT = 12  # seconds


def _ymd_to_dmy(date_str: str) -> str:
    """YYYY-MM-DD → dd/mm/yyyy (Kiwi's required format)."""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")


def _secs_to_hm(seconds: int) -> str:
    h, m = divmod(seconds // 60, 60)
    return f"{h}h {m}m" if m else f"{h}h"


async def search_kiwi_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    currency: str = "USD",
    max_results: int = 5,
    nonstop_only: bool = False,
) -> list[dict]:
    """Return normalized Kiwi flight results. Returns [] on any failure."""
    try:
        from mcp.client.sse import sse_client
        from mcp import ClientSession
    except ImportError:
        return []

    try:
        params: dict = {
            "flyFrom": origin,
            "flyTo": destination,
            "departureDate": _ymd_to_dmy(departure_date),
            "passengers": {"adults": adults},
            "curr": currency.upper(),
            "sort": "price",
        }
        if return_date:
            params["returnDate"] = _ymd_to_dmy(return_date)

        async with sse_client(_KIWI_URL, timeout=_TIMEOUT) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("search-flight", params)

        if not result or not result.content:
            return []

        raw_text = (
            result.content[0].text
            if hasattr(result.content[0], "text")
            else str(result.content[0])
        )
        flights_raw = json.loads(raw_text)
        if not isinstance(flights_raw, list):
            return []

        normalized: list[dict] = []
        seen: set = set()
        for f in flights_raw:
            layovers = f.get("layovers", [])
            stops = len(layovers)
            if nonstop_only and stops > 0:
                continue
            price = f.get("price", 0)
            if not price:
                continue
            dep_local = f.get("departure", {}).get("local", "")
            arr_local = f.get("arrival", {}).get("local", "")
            dedup_key = (dep_local, arr_local, price)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            stop_cities = [lv.get("city", lv.get("at", "")) for lv in layovers]
            normalized.append({
                "departure": dep_local,
                "arrival": arr_local,
                "duration": _secs_to_hm(f.get("totalDurationInSeconds", 0)),
                "stops": stops,
                "stop_cities": stop_cities,
                "price": float(price),
                "currency": f.get("currency", currency).upper(),
                "book_url": f.get("deepLink", ""),
                "data_confidence": "live",
                "source": "kiwi.com",
            })
            if len(normalized) >= max_results:
                break

        return normalized

    except Exception:
        return []
