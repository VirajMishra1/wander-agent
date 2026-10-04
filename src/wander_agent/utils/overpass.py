"""Overpass API client with retry (the public instance intermittently 504s under load)."""

from __future__ import annotations

import asyncio

_ENDPOINT = "https://overpass-api.de/api/interpreter"
_ATTEMPTS = 3
_RETRY_DELAY = 1.5  # seconds


async def overpass_elements(client, query: str, timeout: float = 12.0) -> tuple[list[dict], str | None]:
    """POST an Overpass QL query, retrying on timeouts/5xx/429.

    Returns (elements, error). error is None on success, else the last failure.
    """
    error = "no response"
    for attempt in range(_ATTEMPTS):
        if attempt:
            await asyncio.sleep(_RETRY_DELAY)
        try:
            resp = await client.post(_ENDPOINT, data={"data": query}, timeout=timeout)
        except Exception as e:
            error = type(e).__name__
            continue
        if resp.status_code != 200:
            error = f"HTTP {resp.status_code}"
            continue
        try:
            return resp.json().get("elements", []), None
        except ValueError:
            error = "invalid JSON"
    return [], f"overpass-api.de: {error}"
