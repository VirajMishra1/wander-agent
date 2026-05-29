"""Travel news — live Google News RSS for disruptions, strikes, entry changes."""
from __future__ import annotations
import asyncio
import html
import re
from datetime import datetime, timedelta


_TRAVEL_KEYWORDS = [
    "strike", "airport closed", "flight cancelled", "travel warning",
    "entry ban", "visa suspension", "border closed", "passport control",
    "travel disruption", "airline bankrupt", "typhoon", "hurricane",
    "earthquake", "flood", "political unrest", "protest travel",
    "security alert", "terrorist", "volcano eruption", "tsunami warning",
]


def _is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in _TRAVEL_KEYWORDS)


def _parse_rss_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    fmts = ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"]
    for fmt in fmts:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pass
    return date_str


async def get_travel_news(
    destination: str | None = None,
    days_lookback: int = 7,
    max_results: int = 10,
) -> dict:
    """Get live travel news, disruptions, and alerts for a destination.

    Pulls from Google News RSS (free, no API key). Covers:
    - Airport strikes and closures
    - Flight cancellations
    - Entry requirement changes
    - Natural disasters
    - Political unrest affecting travel
    - Airline bankruptcies

    Args:
        destination: City or country to search news for (e.g. "France", "Bangkok")
        days_lookback: Only show news from last N days
        max_results: Max news items
    """
    from ..utils.http import get_client
    client = await get_client()

    queries = []
    if destination:
        queries.append(f"{destination} travel disruption OR strike OR entry ban OR visa")
        queries.append(f"{destination} airport OR airline news")
    else:
        queries.append("travel disruption OR airport strike OR entry ban OR travel warning")

    cutoff = datetime.utcnow() - timedelta(days=days_lookback)
    articles: list[dict] = []
    seen_titles: set[str] = set()

    async def _fetch_query(q: str) -> list[dict]:
        encoded = q.replace(" ", "+").replace("OR", "OR")
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        items = []
        try:
            resp = await client.get(url, timeout=10.0, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return items
            text = resp.text
            # Parse RSS items
            raw_items = re.findall(r"<item>(.*?)</item>", text, re.DOTALL)
            for raw in raw_items[:max_results * 2]:
                title_m = re.search(r"<title>(.*?)</title>", raw, re.DOTALL)
                link_m = re.search(r"<link>(.*?)</link>", raw, re.DOTALL)
                desc_m = re.search(r"<description>(.*?)</description>", raw, re.DOTALL)
                pub_m = re.search(r"<pubDate>(.*?)</pubDate>", raw, re.DOTALL)
                src_m = re.search(r"<source[^>]*>(.*?)</source>", raw, re.DOTALL)

                title = re.sub(r"<[^>]+>", "", title_m.group(1) if title_m else "").strip()
                link = (link_m.group(1) if link_m else "").strip()
                summary = html.unescape(re.sub(r"<[^>]+>", "", desc_m.group(1) if desc_m else "")).strip()[:300]
                pub_date = pub_m.group(1).strip() if pub_m else None
                source = re.sub(r"<[^>]+>", "", src_m.group(1) if src_m else "").strip()

                if not title or title in seen_titles:
                    continue

                # Date filter
                parsed_date = _parse_rss_date(pub_date)
                if parsed_date:
                    try:
                        article_dt = datetime.strptime(parsed_date[:16], "%Y-%m-%d %H:%M")
                        if article_dt < cutoff:
                            continue
                    except Exception:
                        pass

                seen_titles.add(title)
                items.append({
                    "title": title,
                    "source": source or "Google News",
                    "published": parsed_date,
                    "summary": summary,
                    "url": link,
                    "disruption_alert": _is_relevant(title, summary),
                })
        except Exception:
            pass
        return items

    all_results = await asyncio.gather(*[_fetch_query(q) for q in queries], return_exceptions=True)
    for r in all_results:
        if isinstance(r, list):
            for a in r:
                if a["title"] not in {x["title"] for x in articles}:
                    articles.append(a)

    # Sort: disruption alerts first, then by date
    articles.sort(key=lambda x: (not x.get("disruption_alert", False), x.get("published") or ""))
    articles = articles[:max_results]

    disruptions = [a for a in articles if a.get("disruption_alert")]

    return {
        "destination": destination or "global",
        "days_lookback": days_lookback,
        "results_count": len(articles),
        "disruption_alerts": len(disruptions),
        "articles": articles,
        "warning": f"⚠️ {len(disruptions)} disruption alert(s) found — check before travelling!" if disruptions else None,
        "official_sources": {
            "us_state_dept": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html",
            "uk_fco": f"https://www.gov.uk/foreign-travel-advice/{(destination or '').lower().replace(' ', '-')}",
            "australia_smartraveller": f"https://www.smartraveller.gov.au/destinations/{(destination or '').lower().replace(' ', '-')}",
            "canada_travel": "https://travel.gc.ca/travelling/advisories",
        },
        "suggest_web_search": [
            f"{destination or 'travel'} disruption news {datetime.utcnow().strftime('%B %Y')}",
            f"{destination or 'global'} airport strike {datetime.utcnow().strftime('%Y')}",
        ],
    }
