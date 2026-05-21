"""Local events during trip dates via Ticketmaster Discovery API."""

from __future__ import annotations


async def get_local_events(
    city: str,
    start_date: str,
    end_date: str,
    classification: str | None = None,
    keyword: str | None = None,
    max_results: int = 20,
) -> dict:
    """Find concerts, shows, sports, and events happening during your trip.

    The "Coldplay is in Paris while you're there" feature.

    Args:
        city: City name (e.g., "Paris", "New York")
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        classification: Filter by type: music, sports, arts, family, film, miscellaneous
        keyword: Search keyword (artist, team, show name)
        max_results: Max events to return
    """
    from ..utils.config import TICKETMASTER_KEY
    from ..utils.http import get_client

    if not TICKETMASTER_KEY:
        return {"error": "TICKETMASTER_API_KEY required. Free signup at developer.ticketmaster.com (5k/day)"}

    client = await get_client()
    params: dict = {
        "apikey": TICKETMASTER_KEY,
        "city": city,
        "startDateTime": f"{start_date}T00:00:00Z",
        "endDateTime": f"{end_date}T23:59:59Z",
        "size": min(max_results, 200),
        "sort": "date,asc",
    }
    if classification:
        params["classificationName"] = classification
    if keyword:
        params["keyword"] = keyword

    try:
        resp = await client.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params=params,
        )
        if resp.status_code != 200:
            return {"error": f"Ticketmaster API returned {resp.status_code}"}

        data = resp.json()
        events_raw = data.get("_embedded", {}).get("events", [])

        events = []
        for e in events_raw[:max_results]:
            classifications = e.get("classifications", [{}])[0] if e.get("classifications") else {}
            venue = e.get("_embedded", {}).get("venues", [{}])[0] if e.get("_embedded", {}).get("venues") else {}
            prices = e.get("priceRanges", [{}])[0] if e.get("priceRanges") else {}

            events.append({
                "name": e.get("name", ""),
                "type": classifications.get("segment", {}).get("name", ""),
                "genre": classifications.get("genre", {}).get("name", ""),
                "date": e.get("dates", {}).get("start", {}).get("localDate", ""),
                "time": e.get("dates", {}).get("start", {}).get("localTime", ""),
                "venue": venue.get("name", ""),
                "venue_address": venue.get("address", {}).get("line1", ""),
                "price_min": prices.get("min"),
                "price_max": prices.get("max"),
                "currency": prices.get("currency", ""),
                "ticket_url": e.get("url", ""),
                "image": (e.get("images", [{}])[0] if e.get("images") else {}).get("url", ""),
            })

        return {
            "city": city,
            "period": {"start": start_date, "end": end_date},
            "total_found": data.get("page", {}).get("totalElements", len(events)),
            "results_count": len(events),
            "events": events,
            "source": "Ticketmaster Discovery",
        }
    except Exception as e:
        return {"error": str(e)}
