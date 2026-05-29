"""Mistake fare detector via Secret Flying + The Flight Deal RSS feeds.

"Going.com" (formerly Scott's Cheap Flights) charges $49/yr. We get the same
signal for free by parsing public RSS feeds. Filters by origin and date freshness.
"""

from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from urllib.parse import urlparse


async def find_mistake_fares(
    origin: str | None = None,
    days_lookback: int = 14,
    max_results: int = 20,
) -> dict:
    """Find recently posted mistake fares and deal-fare alerts.

    Pulls from Secret Flying and The Flight Deal (free RSS, no auth).
    Filters by origin city if provided.

    Args:
        origin: City name (e.g., "New York", "Los Angeles") or omit for all
        days_lookback: Only show posts from last N days
        max_results: Max deals to return
    """
    from ..utils.http import get_client

    client = await get_client()
    feeds = [
        ("Secret Flying", "https://www.secretflying.com/feed/"),
        ("The Flight Deal", "https://www.theflightdeal.com/feed/"),
    ]
    if origin:
        origin_slug = origin.lower().replace(" ", "-").replace(",", "")
        feeds.append((f"The Flight Deal ({origin})",
                      f"https://www.theflightdeal.com/category/{origin_slug}/feed/"))

    cutoff = datetime.now().timestamp() - days_lookback * 86400
    all_deals = []

    for source_name, url in feeds:
        try:
            _allowed = {"www.theflightdeal.com", "secretflying.com", "www.secretflying.com"}
            if urlparse(url).hostname not in _allowed:
                continue
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 WanderAgent travel-deals-rss-parser"},
                timeout=15.0,
            )
            if resp.status_code != 200:
                continue
            xml = resp.text

            for item_match in re.finditer(r"<item>(.*?)</item>", xml, re.DOTALL):
                block = item_match.group(1)
                title_m = re.search(r"<title>(?:<!\[CDATA\[)?([^<\]]+)", block)
                link_m = re.search(r"<link>([^<]+)</link>", block)
                pub_m = re.search(r"<pubDate>([^<]+)</pubDate>", block)
                desc_m = re.search(r"<description>(?:<!\[CDATA\[)?(.+?)(?:\]\]>)?</description>", block, re.DOTALL)
                cats = re.findall(r"<category>([^<]+)</category>", block)

                title = unescape(title_m.group(1)).strip() if title_m else ""
                link = link_m.group(1).strip() if link_m else ""

                # Filter by date freshness
                pub_ts = None
                if pub_m:
                    try:
                        from email.utils import parsedate_to_datetime
                        pub_ts = parsedate_to_datetime(pub_m.group(1)).timestamp()
                    except Exception:
                        pass
                if pub_ts and pub_ts < cutoff:
                    continue

                # Skip if origin specified and not mentioned in title/categories
                if origin:
                    haystack = (title + " " + " ".join(cats)).lower()
                    if origin.lower() not in haystack:
                        continue

                desc = ""
                if desc_m:
                    raw = desc_m.group(1)
                    clean = re.sub(r"<[^>]+>", " ", raw)
                    desc = re.sub(r"\s+", " ", unescape(clean)).strip()[:400]

                # Detect price in title (common formats: $XXX, from $X)
                price_match = re.search(r"\$([0-9]{2,4})", title)
                price = int(price_match.group(1)) if price_match else None

                # Detect mistake-fare keywords
                is_error = any(
                    kw in title.lower() or kw in desc.lower()
                    for kw in ["error fare", "mistake fare", "glitch"]
                )

                all_deals.append({
                    "source": source_name,
                    "title": title,
                    "price_usd_in_title": price,
                    "is_mistake_fare": is_error,
                    "categories": cats[:5],
                    "summary": desc,
                    "url": link,
                    "published": pub_m.group(1) if pub_m else "",
                })
        except Exception:
            continue

    # Dedupe by URL
    seen = set()
    unique = []
    for d in all_deals:
        if d["url"] in seen:
            continue
        seen.add(d["url"])
        unique.append(d)

    # Mistake fares first, then by price
    unique.sort(key=lambda x: (not x["is_mistake_fare"], x["price_usd_in_title"] or 99999))
    top = unique[:max_results]

    mistake_count = sum(1 for d in top if d["is_mistake_fare"])

    return {
        "origin_filter": origin or "all",
        "days_lookback": days_lookback,
        "results_count": len(top),
        "mistake_fare_count": mistake_count,
        "deals": top,
        "sources": [name for name, _ in feeds],
        "tip": "Mistake fares often disappear within hours. Book fast and don't add hotels.",
        "suggest_web_search": [
            "mistake fare booking tips fly with hold strategy",
            "what to do if airline cancels mistake fare 2026",
        ],
    }
