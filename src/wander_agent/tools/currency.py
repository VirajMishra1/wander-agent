"""Currency conversion using Frankfurter API (free, no auth)."""

from __future__ import annotations


async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:
    """Convert between currencies using live exchange rates.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR", "JPY")

    No API key required. Powered by European Central Bank data.
    """
    from ..utils.http import get_client

    client = await get_client()
    resp = await client.get(
        "https://api.frankfurter.dev/v1/latest",
        params={
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
        },
    )
    resp.raise_for_status()
    data = resp.json()

    converted = data.get("rates", {}).get(to_currency.upper(), 0)
    rate = converted / amount if amount else 0

    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "converted_amount": round(converted, 2),
        "exchange_rate": round(rate, 6),
        "date": data.get("date", ""),
        "source": "European Central Bank via Frankfurter",
    }


async def get_exchange_rates(
    base_currency: str,
    target_currencies: str | None = None,
) -> dict:
    """Get current exchange rates for a base currency.

    Args:
        base_currency: Base currency code (e.g., "USD")
        target_currencies: Comma-separated target currencies (e.g., "EUR,GBP,JPY"). Omit for all.

    No API key required.
    """
    from ..utils.http import get_client

    client = await get_client()
    params: dict = {"from": base_currency.upper()}
    if target_currencies:
        params["to"] = target_currencies.upper()

    resp = await client.get("https://api.frankfurter.dev/v1/latest", params=params)
    resp.raise_for_status()
    data = resp.json()

    return {
        "base": base_currency.upper(),
        "date": data.get("date", ""),
        "rates": data.get("rates", {}),
        "source": "European Central Bank via Frankfurter",
    }
