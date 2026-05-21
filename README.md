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

- `search_flights` — Travelpayouts primary, Kiwi Tequila fallback
- `search_hotels` — Hotellook (Travelpayouts)
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

Twelve APIs. Eight of them require no authentication at all. The other four have free tiers generous enough that you can use this seriously without paying anyone.

| Source | Purpose | Auth |
|---|---|---|
| Open-Meteo | Live weather + historical climate | none |
| Open-Meteo Geocoding | City → coordinates with population, timezone | none |
| Frankfurter | Currency rates from the European Central Bank | none |
| REST Countries | Country metadata | none |
| Wikidata SPARQL | Place verification | none |
| US State Department RSS | Travel advisories | none |
| Curated dataset | Cost of living | none (in-repo) |
| Travelpayouts | Flights + hotels | free token |
| Kiwi Tequila | Flight fallback | free sandbox |
| OpenTripMap | Attractions and POIs | free key |
| Foursquare | Secondary verification source | free 200k/month |
| Ticketmaster Discovery | Local events | free 5k/day |

For the bare minimum useful agent you only need the Travelpayouts token. Sign-up is two minutes with no approval process. Everything else is optional.

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
│   ├── flights.py         # Travelpayouts → Kiwi fallback chain
│   ├── hotels.py          # Hotellook
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

**Fallback chains over single sources.** Flights try Travelpayouts first, then Kiwi. The chain is in code, not in prompts, so the LLM doesn't have to retry.

**Climatology for far-future dates.** Open-Meteo's forecast horizon is 16 days. Anything beyond that, the weather tool pulls five years of historical data for the exact same calendar dates and averages it. You get a reasonable answer for "what's the weather in Tokyo in November" without lying that it's a real forecast.

**Cached advisories.** The State Department RSS feed is fetched once per process and cached for 60 minutes. Most travel sessions hit it many times — caching means the user pays one HTTP round trip, not twenty.

**Verification by composition.** `verify_place` doesn't trust any one source. A high-confidence verification means at least two of Wikidata, Open-Meteo geocoding, Foursquare, and OpenTripMap independently confirmed the place exists. A single source is medium confidence. Zero sources is "do not recommend."

**Geocoding disambiguation.** Open-Meteo returns up to ten matches for ambiguous names. The tool sorts them by capital-city status, then exact name match, then population. "Bali" returns Indonesia (4.2M), not the village in West Bengal.

**No frontend.** No React. No Streamlit. No webapp. The MCP protocol is the interface. Any AI assistant that speaks MCP can use this.

## Limitations

- Travelpayouts data is cached from search aggregators. Live availability for booking still requires going through the affiliate URLs.
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
