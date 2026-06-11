"""Local events — real data scraped from Eventbrite + deeplink fallbacks.

Eventbrite embeds JSON-LD (schema.org Event) in their public search pages.
No API key required. Falls back to deeplinks if scraping fails.
"""

from __future__ import annotations

import json
import re
from urllib.parse import quote_plus


def _eb_city_slug(city: str) -> str:
    """Convert 'New York' → 'new-york' for Eventbrite URL. Eventbrite redirects to country--city."""
    return city.lower().strip().replace(" ", "-").replace(",", "").replace(".", "").replace("'", "")


async def _scrape_eventbrite(
    city: str,
    start_date: str,
    end_date: str,
    keyword: str,
    max_results: int,
) -> list[dict]:
    """Scrape Eventbrite search page for real event data via embedded JSON-LD."""
    try:
        from ..utils.http import get_client
        client = await get_client()

        slug = _eb_city_slug(city)
        kw_slug = _eb_city_slug(keyword) if keyword and keyword not in ("events", "") else "events"
        url = f"https://www.eventbrite.com/d/{slug}/{kw_slug}/"

        resp = await client.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,*/*",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=12.0,
        )
        if resp.status_code != 200:
            return []

        html = resp.text

        # Extract JSON-LD blocks (Eventbrite embeds schema.org Event lists)
        ld_blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            html,
            re.DOTALL,
        )

        events: list[dict] = []
        for block in ld_blocks:
            try:
                data = json.loads(block)
            except Exception:
                continue

            items = data.get("itemListElement", [])
            for item in items:
                ev = item.get("item", {}) if isinstance(item, dict) else {}
                if not ev:
                    continue

                name = ev.get("name", "") or ev.get("description", "")
                name = (name or "")[:120].strip()
                url_ev = ev.get("url", "")
                start = ev.get("startDate", "")
                end_ev = ev.get("endDate", start)
                location = ev.get("location", {})
                venue = ""
                if isinstance(location, dict):
                    venue = location.get("name", "") or location.get("address", {}).get("addressLocality", "")

                if not name or not url_ev:
                    continue

                # Filter out events clearly outside the trip window
                # (loose: only drop if more than 7 days before start or after end)
                if start and end_date and start[:10] > end_date[:10]:
                    continue

                events.append({
                    "name": name[:120],
                    "start": start[:16] if start else "",
                    "end": end_ev[:16] if end_ev else "",
                    "venue": venue,
                    "url": url_ev,
                    "source": "eventbrite",
                })

                if len(events) >= max_results:
                    break

            if len(events) >= max_results:
                break

        return events

    except Exception:
        return []


async def get_local_events(
    city: str,
    start_date: str,
    end_date: str,
    classification: str | None = None,
    keyword: str | None = None,
    max_results: int = 20,
) -> dict:
    """Find events happening at a destination during your trip dates.

    Scrapes Eventbrite for real event data (name, date, venue, URL).
    Falls back to deeplinks if scraping is unavailable.

    Args:
        city: City name (e.g., "Paris", "New York")
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        classification: music, sports, arts, family
        keyword: Artist, team, or show name
        max_results: Max events to return
    """
    kw = keyword or classification or "events"
    city_enc = quote_plus(city)
    kw_enc = quote_plus(kw)
    month = start_date[:7]

    # Try real scrape first
    events = await _scrape_eventbrite(city, start_date, end_date, kw, max_results)

    confidence = "scraped_live" if events else "deeplinks_only"

    booking_links = [
        {
            "service": "Eventbrite",
            "url": f"https://www.eventbrite.com/d/{quote_plus(_eb_city_slug(city))}/{quote_plus(kw)}/",
            "coverage": "Global ticketed events",
        },
        {
            "service": "Meetup",
            "url": (
                f"https://www.meetup.com/find/?location={city_enc}"
                f"&keywords={kw_enc}"
                f"&dateRange=customDate&customStartDate={start_date}&customEndDate={end_date}"
            ),
            "coverage": "Community gatherings and social events",
        },
        {
            "service": "Songkick",
            "url": f"https://www.songkick.com/search?query={city_enc}&type=concert",
            "coverage": "Concerts and live music",
        },
        {
            "service": "Bandsintown",
            "url": f"https://www.bandsintown.com/c/{city_enc}?came_from=257",
            "coverage": "Concerts and live music",
        },
        {
            "service": "Google Events",
            "url": (
                f"https://www.google.com/search"
                f"?q={kw_enc}+events+in+{city_enc}+{quote_plus(month)}"
            ),
            "coverage": "Aggregated local events",
        },
        {
            "service": "Facebook Events",
            "url": f"https://www.facebook.com/events/search/?q={kw_enc}&location={city_enc}",
            "coverage": "Local community events",
        },
        {
            "service": "Resident Advisor",
            "url": f"https://ra.co/events?location={_eb_city_slug(city)}",
            "coverage": "Electronic music and club events",
        },
        {
            "service": "Ticketmaster",
            "url": (
                f"https://www.ticketmaster.com/search?q={kw_enc}"
                f"&city={city_enc}&startDate={start_date}&endDate={end_date}"
            ),
            "coverage": "Major concerts, sports, theatre",
        },
        {
            "service": "Viator",
            "url": (
                f"https://www.viator.com/searchResults/all"
                f"?text={kw_enc}+{city_enc}&startDate={start_date}&endDate={end_date}"
            ),
            "coverage": "Guided tours and experiences",
        },
    ]

    suggest_web_search = [
        f"events in {city} {month}",
        f"{kw} {city} {start_date[:7]}",
        f"things to do {city} {start_date} to {end_date}",
    ]
    if keyword:
        suggest_web_search.insert(0, f"{keyword} {city} {month}")

    from ..utils.freshness import stamp

    return stamp({
        "city": city,
        "start_date": start_date,
        "end_date": end_date,
        "classification": classification,
        "keyword": keyword,
        "results_count": len(events),
        "events": events,
        "booking_links": booking_links,
        "note": (
            "Live Eventbrite events shown above when available. "
            "Click booking_links for full listings on each platform."
        ),
        "suggest_web_search": suggest_web_search,
    }, confidence, source="eventbrite")
