"""Cost of living and quality of life via Teleport API (no auth)."""

from __future__ import annotations


async def get_cost_of_living(
    city: str,
    home_currency: str = "USD",
) -> dict:
    """Get cost-of-living index, quality scores, and budget guidance for a city.

    "Your $100/day = lavish in Lisbon, broke in London."
    Uses Teleport.org API (free, no auth). 270+ cities supported.

    Args:
        city: City name (e.g., "Lisbon", "Tokyo", "San Francisco")
        home_currency: Your home currency for comparison (USD, EUR, etc.)
    """
    from ..utils.http import get_client

    client = await get_client()

    try:
        # Step 1: find city slug
        search_resp = await client.get(
            "https://api.teleport.org/api/cities/",
            params={"search": city, "limit": 1},
        )
        if search_resp.status_code != 200:
            return {"error": f"Could not search city '{city}'"}

        cities = search_resp.json().get("_embedded", {}).get("city:search-results", [])
        if not cities:
            return {"error": f"City '{city}' not found. Teleport covers ~270 cities."}

        city_link = cities[0].get("_links", {}).get("city:item", {}).get("href", "")
        if not city_link:
            return {"error": "No city link returned"}

        city_resp = await client.get(city_link)
        city_data = city_resp.json()
        urban_area_link = city_data.get("_links", {}).get("city:urban_area", {}).get("href", "")
        if not urban_area_link:
            return {
                "error": f"No urban area data for '{city}'. Try a larger metro nearby.",
                "city_full_name": city_data.get("full_name", city),
            }

        # Step 2: get urban area details + scores
        ua_resp = await client.get(urban_area_link)
        ua_data = ua_resp.json()
        ua_slug = ua_data.get("ua_id", "").replace(":", "")

        # Scores
        scores_resp = await client.get(f"{urban_area_link}scores/")
        scores_data = scores_resp.json() if scores_resp.status_code == 200 else {}

        category_scores = []
        for cat in scores_data.get("categories", []):
            category_scores.append({
                "name": cat.get("name", ""),
                "score_out_of_10": round(cat.get("score_out_of_10", 0), 2),
            })

        # Salaries (cost of living proxy)
        salaries_resp = await client.get(f"{urban_area_link}salaries/")
        salaries = []
        if salaries_resp.status_code == 200:
            for s in salaries_resp.json().get("salaries", [])[:5]:
                job = s.get("job", {}).get("title", "")
                salary = s.get("salary_percentiles", {}).get("percentile_50", 0)
                salaries.append({"job": job, "median_usd_annual": round(salary, 0)})

        # Details (cost of living indexes)
        details_resp = await client.get(f"{urban_area_link}details/")
        budget_data = {}
        if details_resp.status_code == 200:
            for category in details_resp.json().get("categories", []):
                if category.get("id") == "COST-OF-LIVING":
                    for d in category.get("data", []):
                        budget_data[d.get("id", "")] = {
                            "label": d.get("label", ""),
                            "value": d.get("currency_dollar_value"),
                            "currency": "USD",
                        }

        return {
            "city": ua_data.get("full_name", city),
            "urban_area_slug": ua_slug,
            "category_scores": sorted(category_scores, key=lambda x: -x["score_out_of_10"]),
            "summary": scores_data.get("summary", "")[:500],
            "median_salaries_sample": salaries,
            "cost_of_living_items_usd": budget_data,
            "tip": "Higher category scores = better. Compare cities by score profile.",
            "source": "Teleport",
        }
    except Exception as e:
        return {"error": str(e)}
