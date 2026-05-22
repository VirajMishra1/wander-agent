"""Local events during trip dates — booking deeplinks, no API key required."""

from __future__ import annotations

from urllib.parse import quote_plus


async def get_local_events(
    city: str,
    start_date: str,
    end_date: str,
    classification: str | None = None,
    keyword: str | None = None,
    max_results: int = 20,
) -> dict:
    """Find events happening at a destination during your trip dates.

    Returns deeplinks to Eventbrite, Meetup, Songkick, Bandsintown,
    and Google Events for the city and date range. No API key required.

    Args:
        city: City name (e.g., "Paris", "New York")
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        classification: music, sports, arts, family (used in search queries)
        keyword: Artist, team, or show name
        max_results: Ignored — kept for API compatibility
    """
    q = keyword or classification or "events"
    city_enc = quote_plus(city)
    kw_enc = quote_plus(q)
    month = start_date[:7]

    booking_links = [
        {
            "service": "Eventbrite",
            "url": f"https://www.eventbrite.com/d/{city_enc}/{kw_enc}/?start_date={start_date}&end_date={end_date}",
            "coverage": "Global ticketed events",
        },
        {
            "service": "Meetup",
            "url": f"https://www.meetup.com/find/?location={city_enc}&keywords={kw_enc}&dateRange=customDate&customStartDate={start_date}&customEndDate={end_date}",
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
            "url": f"https://www.google.com/search?q={kw_enc}+events+in+{city_enc}+{quote_plus(month)}",
            "coverage": "Aggregated local events",
        },
        {
            "service": "Facebook Events",
            "url": f"https://www.facebook.com/events/search/?q={kw_enc}&location={city_enc}",
            "coverage": "Local community events",
        },
        {
            "service": "Resident Advisor",
            "url": f"https://ra.co/events?location={city_enc.lower()}",
            "coverage": "Electronic music and club events",
        },
    ]

    suggest_web_search = [
        f"events in {city} {month}",
        f"{q} {city} {start_date[:7]}",
        f"things to do {city} {start_date} to {end_date}",
    ]
    if keyword:
        suggest_web_search.insert(0, f"{keyword} {city} concert tour date {month}")

    return {
        "city": city,
        "start_date": start_date,
        "end_date": end_date,
        "classification": classification,
        "keyword": keyword,
        "results_count": 0,
        "events": [],
        "booking_links": booking_links,
        "data_confidence": "deeplinks_only",
        "note": "Click any link to browse live events. Eventbrite and Google Events have the widest coverage.",
        "suggest_web_search": suggest_web_search,
    }
