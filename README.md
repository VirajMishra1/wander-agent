# Wander Agent

An MCP server that turns Claude (or any MCP-compatible AI) into a working travel agent. It searches flights, finds hotels, builds itineraries, ranks destinations by what actually matters to you, and verifies its own recommendations against real data so the model doesn't hallucinate restaurants that don't exist.

There is no UI. You install it once, point Claude Desktop or Claude Code at it, and then you have 21 travel tools available inside any AI conversation.

## Why this exists

Most open-source AI travel projects are standalone web apps. They're products, not capabilities. The MCP servers that do exist tend to be narrow — flights only, or hotels only — with no composition between them.

Wander Agent is the opposite. It's a single MCP server that orchestrates 12 different APIs into a coherent travel agent, designed to be imported into the AI you already use. Two modes:

- **Inspiration mode**: you have a budget but no destination. Ask "where can I go with $1500 in March?" and the agent returns ranked destinations with full flight + hotel costs.
- **Planning mode**: you know where you're going. Ask "plan five days in Tokyo, I like food and history" and the agent fetches flights, hotels, real attractions, weather for your dates, country info, and local events.

Both modes share a verification layer that cross-checks any recommendation against multiple sources before passing it to you, which is the main thing that keeps the LLM honest.

## What's in it

There are 21 tools. They fall into four groups.

### Inspiration (you don't know where yet)

- `find_destinations_by_budget` — calculates flight + hotel for many destinations and returns the ones under your total budget, with full cost breakdowns
- `cheap_anywhere_from` — cheapest destinations from your origin, optionally constrained to a month
- `compare_destinations` — side-by-side cost comparison for a list of cities on the same dates

### Planning (you do)

- `search_flights` — **Google Flights data via the `fast_flights` library**. No API key. Prices auto-converted to your requested currency. Internal retry across fetch modes if Google serves stripped HTML.
- `search_hotels` — **Hybrid strategy, no API key required.** Returns real hotel names from Google Hotels (via `fast_hotels`) plus constructed Booking.com/Google Hotels/Airbnb deeplinks for live prices plus suggested web-search queries the LLM can run for reviews. If `TRAVELPAYOUTS_TOKEN` is set as an optional bonus, also returns live Hotellook prices in-tool.
- `plan_itinerary` — orchestrates weather, activities, country info, and currency into a day-by-day plan
- `optimize_budget` — flexible-date search for cheapest flight + hotel combination

### Differentiators

These are the tools that don't exist anywhere else as MCP capabilities.

- `score_destinations` — multi-objective ranking. Weights cost, weather match, safety advisories, event density, and quality-of-life into a single composite score per city. You set the weights.
- `get_travel_advisory` — pulls live from the US State Department's RSS feed, returns levels 1–4, the full advisory text, and the official URL. Cached for 60 minutes.
- `list_advisories_by_level` — list every country currently at advisory level N or above
- `get_local_events` — concerts, sports, shows happening during your trip dates via Ticketmaster Discovery. "Coldplay is playing in Paris while you're there" is the use case.
- `get_cost_of_living` — daily traveler budget at three tiers (budget/mid/luxury) for 100+ destinations, with optional currency conversion
- `best_month_to_visit` — analyzes five years of historical climate data to recommend months matching your preference (warm-dry, cool-dry, snow, etc.)
- `verify_place` — cross-checks any place name against Wikidata, Open-Meteo geocoding, Foursquare, and OpenTripMap. Returns a confidence score so you can tell the LLM "don't recommend things that don't exist."
- `verify_flight_route` — confirms a route is actually flown between two airports

### Enrichment (used by both modes)

`get_weather` (live forecast within 16 days, climatology beyond), `convert_currency`, `get_exchange_rates`, `search_activities`, `get_destination_info`, `geocode`.

## Data sources

Thirteen APIs. Nine require no authentication. The remaining four have free tiers generous enough for serious use.

| Source | Purpose | Auth |
|---|---|---|
| **Google Flights** (via `fast_flights`) | **Flight search (primary)** | **none — scraper library** |
| Open-Meteo | Live weather + historical climate | none |
| Open-Meteo Geocoding | City → coordinates with population, timezone | none |
| Frankfurter | Currency rates from the European Central Bank | none |
| REST Countries | Country metadata | none |
| Wikidata SPARQL | Place verification | none |
| US State Department RSS | Travel advisories | none |
| Curated dataset | Cost of living | none (in-repo) |
| Curated airport list | Inspiration tools (looped fast_flights) | none (in-repo) |
| **Google Hotels** (via `fast_hotels`) | **Hotel names (primary)** | **none — scraper library** |
| Booking.com / Airbnb / Google Hotels deeplinks | Live price click-through | none (URL construction) |
| Hotellook (Travelpayouts) | Optional in-tool live prices | optional free token |
| OpenTripMap | Attractions and POIs | free key |
| Foursquare | Secondary verification source | free 200k/month |
| Ticketmaster Discovery | Local events | free 5k/day |

**On Google Flights specifically.** Google killed the official QPX Express API in 2018 and never released a replacement. There is no public, free, official Google Flights API. The `fast_flights` Python library scrapes Google Flights' protobuf-encoded responses — it returns the actual flight inventory you'd see in the Google UI, including airlines, times, and prices. The trade-off: scrapers can break when Google changes their HTML. The tool retries across multiple fetch modes to handle most flakiness.

**On the inspiration tools specifically.** "Find me anywhere cheap from JFK" is hard without an aggregator API. We don't have one (Kiwi Tequila closed public sandbox in 2024, partner-only now). Instead, the inspiration tools loop `fast_flights` over a curated list of ~40 popular global destinations in parallel. Each call takes ~1-3s, and with batching of 5 concurrent the full sweep finishes in 10-30 seconds. You can scope it by region (`europe`, `asia`, etc.) to make it faster.

**On hotels specifically.** Free hotel pricing APIs are dying for indie developers. Travelpayouts/Hotellook still works but their token UI is hard to navigate. Booking.com partner API is approval-only. Xotelo's endpoints changed. We went hybrid: the tool scrapes Google Hotels for real hotel names (the only part that scrapes reliably), constructs deeplinks to Booking.com / Google Hotels / Airbnb for live prices via click-through, and emits `suggest_web_search` queries so Claude can fetch reviews and rates via its own web search. If a user does set `TRAVELPAYOUTS_TOKEN`, Hotellook prices appear in-tool as a bonus.

**For the bare minimum useful agent, you need zero API keys.** Flights, hotels, weather, advisories, currency, cost-of-living, scoring, and verification all work without any signup. Optional keys upgrade certain features (events, in-tool hotel prices, richer attractions, third verification source).

## How Wander Agent composes with Claude's web search

Wander Agent provides structured data. Claude has web search built in. They cover different domains and work better together than either alone.

The server's instructions tell Claude when to use which. Many tool outputs also include a `suggest_web_search` field with concrete query suggestions Claude should run for the latest unstructured information.

- **Use the tools for:** prices, weather, advisories, scoring, verification, cost-of-living. Anything where you want a deterministic, cached, machine-readable answer.
- **Use web search for:** mistake fares, deal blogs, recent destination news, restaurant reviews, visa policy changes since the last data refresh, festivals not in Ticketmaster, trip reports.

Example: `search_flights` returns JFK→LAX prices but also suggests Claude search for `"JFK to LAX mistake fares 2026-06"` and `"airline strikes affecting JFK LAX"`. The agent does the structured math; Claude fills in the live context.

## Setup

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
uv sync
cp .env.example .env
# Edit .env. The only key you really need is TRAVELPAYOUTS_TOKEN.
```

### Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS (or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/wander-agent", "wander-agent"]
    }
  }
}
```

Restart Claude Desktop. The tools should appear in the tool list.

### Add to Claude Code

From inside the repo:

```bash
uv run mcp install src/wander_agent/server.py
```

Or add to your project's `.claude/settings.json`:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/wander-agent", "wander-agent"]
    }
  }
}
```

## How to actually use it

Once installed, you just talk to Claude. The agent picks the right tools.

```
You: I have $1500. I want to go somewhere warm in March. Surprise me.

Claude: [calls find_destinations_by_budget with origin=JFK, budget=1500,
         departure_month=2026-03, then score_destinations on top results
         with weather_pref=warm_dry]
```

```
You: Paris vs Rome vs Barcelona for next month — show me real numbers.

Claude: [calls compare_destinations]
```

```
You: Plan five days in Tokyo in May. I like food and architecture.
     Also tell me if any interesting concerts happen those days.

Claude: [calls plan_itinerary, then get_local_events]
```

```
You: Is Egypt safe right now? Do I need shots?

Claude: [calls get_travel_advisory]
```

```
You: You said to eat at "Le Brilliant Bistro" in Lyon. Is that real?

Claude: [calls verify_place, confirms across Wikidata + Foursquare + OSM]
```

## Architecture

```
src/wander_agent/
├── server.py              # FastMCP entry point. Registers 21 tools.
├── tools/
│   ├── inspiration.py     # find_destinations_by_budget, cheap_anywhere_from, compare_destinations
│   ├── flights.py         # fast_flights (Google Flights scraper)
│   ├── hotels.py          # fast_hotels names + deeplinks + web-search hints + optional Hotellook
│   ├── itinerary.py       # Orchestrator: weather + activities + country info in parallel
│   ├── budget.py          # Flexible-date optimizer (asyncio.gather over date combos)
│   ├── score.py           # Multi-objective ranker
│   ├── advisory.py        # US State Dept RSS parser, 60-min cache
│   ├── events.py          # Ticketmaster Discovery
│   ├── cost_of_living.py  # Curated dataset + currency conversion
│   ├── seasons.py         # 5-year climate analysis
│   ├── weather.py         # Forecast OR climatology depending on horizon
│   ├── currency.py        # Frankfurter
│   ├── activities.py      # OpenTripMap with category filtering
│   ├── destination.py     # Geocoding + country info
│   └── verify.py          # Wikidata + Open-Meteo + Foursquare cross-check
└── utils/
    ├── http.py            # Shared httpx.AsyncClient with connection pooling
    ├── config.py          # .env loading, key management
    └── cost_data.py       # Embedded cost-of-living dataset
```

Every tool is a `@mcp.tool()`-decorated async function. They share a single connection-pooled HTTP client. The MCP lifespan handler closes the client on shutdown.

## Design choices worth knowing

**Internal retry instead of prompt-level retry.** `fast_flights` occasionally returns stripped HTML. The flight tool retries across fetch modes (`common`, `fallback`) inside the function so the LLM never sees the failure.

**Climatology for far-future dates.** Open-Meteo's forecast horizon is 16 days. Anything beyond that, the weather tool pulls five years of historical data for the exact same calendar dates and averages it. You get a reasonable answer for "what's the weather in Tokyo in November" without lying that it's a real forecast.

**Cached advisories.** The State Department RSS feed is fetched once per process and cached for 60 minutes. Most travel sessions hit it many times — caching means the user pays one HTTP round trip, not twenty.

**Verification by composition.** `verify_place` doesn't trust any one source. A high-confidence verification means at least two of Wikidata, Open-Meteo geocoding, Foursquare, and OpenTripMap independently confirmed the place exists. A single source is medium confidence. Zero sources is "do not recommend."

**Geocoding disambiguation.** Open-Meteo returns up to ten matches for ambiguous names. The tool sorts them by capital-city status, then exact name match, then population. "Bali" returns Indonesia (4.2M), not the village in West Bengal.

**No frontend.** No React. No Streamlit. No webapp. The MCP protocol is the interface. Any AI assistant that speaks MCP can use this.

## Limitations

- Hotel prices are unreliable to scrape (Google JS-renders them). The tool gives you real hotel names plus deeplinks for click-through pricing. Setting `TRAVELPAYOUTS_TOKEN` upgrades this with live prices in-tool.
- `fast_flights` and `fast_hotels` are scraper libraries. They can break when Google changes HTML. The tools retry across fetch modes; if everything fails the LLM can fall back to web search.
- The cost-of-living dataset is a snapshot. It covers ~100 cities directly and falls back to country-level medians for unlisted places.
- The Ticketmaster events tool covers North America and most of Europe well. Coverage in Asia and Latin America is patchier.
- The State Department advisories reflect US perspective. Travelers from other countries should also check their own government's guidance.

## Contributing

Pull requests welcome. The repo conventions:

- One tool, one job. If a tool needs more than ~150 lines, it should probably be split.
- Free APIs only. If an API requires payment or partnership approval, it doesn't go in this repo.
- Every tool needs to handle the missing-API-key case gracefully and return an error dict with a hint instead of crashing.
- The shared HTTP client in `utils/http.py` should be used by all tools — no per-tool client instantiation.

## License

MIT.
