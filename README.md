# wander-agent

MCP server for travel planning. 33 tools covering flights, hotels, visas, weather, itineraries, cost-of-living, ground transport, and trip scoring. Connects to any MCP-compatible AI client.

No single API key is required. All tools degrade gracefully — live data when keys are present, Wikidata/static fallbacks otherwise.

---

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

---

## Install

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
uv pip install -e .
# or: pip install -e .
```

Verify:

```bash
python -c "import wander_agent; print('ok')"
```

---

## Environment Variables

All optional. Copy `.env.example` to `.env` and fill in what you have.

| Variable | Used by | Without it |
|---|---|---|
| `OPENTRIPMAP_API_KEY` | `search_activities` | Falls back to Wikidata SPARQL |
| `AMADEUS_CLIENT_ID` | `search_flights` | Falls back to Google Flights scraper |
| `AMADEUS_CLIENT_SECRET` | `search_flights` | Falls back to Google Flights scraper |
| `SERPAPI_KEY` | `search_hotels`, `get_local_events` | Falls back to static scraping |
| `EXCHANGERATE_API_KEY` | `convert_currency`, `get_exchange_rates` | Falls back to open.er-api.com (rate-limited) |
| `ROME2RIO_KEY` | `search_ground_transport` | Falls back to public demo key |

---

## MCP Client Setup

The server entry point is `wander-agent` (installed by pip/uv).

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent"
    }
  }
}
```

If `wander-agent` isn't in PATH, use the full path:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "/path/to/your/venv/bin/wander-agent"
    }
  }
}
```

Restart Claude Desktop after editing.

### Claude Code (CLI)

```bash
claude mcp add wander-agent wander-agent
```

Or with env vars:

```bash
claude mcp add wander-agent -e OPENTRIPMAP_API_KEY=your_key wander-agent
```

### Cursor

Add to `.cursor/mcp.json` in your project root, or `~/.cursor/mcp.json` globally:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent",
      "env": {
        "OPENTRIPMAP_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Cline (VS Code extension)

Open VS Code settings, search for `Cline: Mcp Settings`, or edit `cline_mcp_settings.json` directly:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent",
      "args": []
    }
  }
}
```

### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent"
    }
  }
}
```

### Continue.dev

Add to `.continuerc.json` in your project, or `~/.continue/config.json` globally:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "wander-agent"
        }
      }
    ]
  }
}
```

### Zed

Edit `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "wander-agent": {
      "command": {
        "path": "wander-agent",
        "args": []
      }
    }
  }
}
```

### OpenAI Codex / Agents API

OpenAI's Agents API does not natively support MCP as of mid-2025. To use wander-agent tools, either:
- Wrap tool calls manually using the wander-agent Python functions directly
- Use a bridge like [mcp-agent](https://github.com/lastmile-ai/mcp-agent) to proxy MCP tools into OpenAI tool format

---

## Tools Reference

### Trip Planning

| Tool | Description | Key Parameters |
|---|---|---|
| `plan_trip_package` | One-call bookable trip: flights + hotels + visa + weather + advisory + ground transport + attractions + cost estimate + booking checklist | `origin`, `destination`, `departure_date`, `trip_length_days`, `travelers`, `passport_country`, `budget_level` |
| `plan_itinerary` | Day-by-day itinerary for a destination | `destination`, `days`, `interests`, `budget_level` |
| `score_destinations` | Rank destinations by cost/weather/safety/events (weighted) | `destinations` (CSV), `travel_start`, `travel_end`, `weights`, `origin` |
| `compare_destinations` | Side-by-side comparison of 2–5 destinations | `destinations` (CSV), `travel_dates`, `budget_level` |
| `optimize_budget` | Break down budget across flights/hotels/food/activities | `destination`, `total_budget`, `trip_days`, `travelers` |

### Flights

| Tool | Description | Key Parameters |
|---|---|---|
| `search_flights` | Search round-trip or one-way flights. Price always per-person. | `origin`, `destination`, `departure_date`, `return_date`, `adults` |
| `find_destinations_by_budget` | Find destinations reachable within a flight budget from an origin | `origin`, `max_budget`, `departure_date`, `currency` |
| `cheap_anywhere_from` | Cheapest flights from an origin across all destinations | `origin`, `departure_date`, `round_trip_days`, `max_results` |
| `find_skiplagged_fares` | Hidden-city ticketing fare search | `origin`, `destination`, `date` |
| `find_mistake_fares` | Scan for anomalously cheap fares (error fares) | `origin`, `max_price`, `departure_date` |
| `multi_origin_meetup` | Find cheapest meeting point for travelers flying from multiple origins | `origins` (CSV), `travel_start`, `travel_end` |
| `verify_flight_route` | Verify a flight route exists and return sample pricing | `origin`, `destination` |

### Hotels

| Tool | Description | Key Parameters |
|---|---|---|
| `search_hotels` | Search hotels with pricing. Returns booking deep-links. | `city`, `check_in`, `check_out`, `adults`, `max_results` |

### Visa & Entry

| Tool | Description | Key Parameters |
|---|---|---|
| `check_visa_requirement` | Visa category + guidance + official apply links for a passport/destination pair | `passport_country` (ISO-2), `destination_country` (ISO-2) |
| `visa_free_destinations` | List all destinations accessible without a full visa for a passport | `passport_country`, `include_categories` |

### Weather & Advisory

| Tool | Description | Key Parameters |
|---|---|---|
| `get_weather` | Forecast or historical weather for a location and date range | `latitude`, `longitude`, `start_date`, `end_date` |
| `best_month_to_visit` | Best and worst months to visit a destination by weather | `destination` |
| `get_travel_advisory` | US State Dept advisory level + summary for a country | `country` |
| `list_advisories_by_level` | All countries at or above a given advisory level | `min_level` (1–4) |

### Costs & Currency

| Tool | Description | Key Parameters |
|---|---|---|
| `get_cost_of_living` | Daily budget estimates (budget/mid/luxury) for a city | `city`, `home_currency` |
| `convert_currency` | Convert an amount between currencies | `amount`, `from_currency`, `to_currency` |
| `get_exchange_rates` | Live exchange rates for a base currency | `base_currency`, `target_currencies` |

### Activities & Destination Info

| Tool | Description | Key Parameters |
|---|---|---|
| `search_activities` | Attractions near a location. Uses OpenTripMap if keyed, Wikidata otherwise. | `latitude`, `longitude`, `radius_km`, `category` |
| `get_local_events` | Events at a destination during travel dates | `city`, `start_date`, `end_date` |
| `get_destination_info` | Country info: currency, language, timezone, calling code | `country_name` |
| `geocode` | Lat/lon + country for a place name | `place_name` |
| `verify_place` | Confirm a place exists and return canonical name | `place_name`, `country` |

### Niche / Inspiration

| Tool | Description | Key Parameters |
|---|---|---|
| `find_aurora_destinations` | Destinations with aurora viewing conditions for a date | `travel_start`, `travel_end` |
| `search_ground_transport` | Bus/train/ferry options between cities. Region-aware (US/Europe/India/SEA). | `origin_city`, `destination_city`, `date`, `travelers` |

### Traveler Profile

| Tool | Description | Key Parameters |
|---|---|---|
| `get_traveler_profile` | Load saved traveler preferences. Returns onboarding prompts if first use. | — |
| `onboard_traveler` | Save home airports, passports, travel style, dietary, interests | `name`, `home_airports`, `passports`, `home_currency`, `travel_style` |
| `update_traveler_profile` | Update any profile field. Supports append operations for visas and trips. | any profile field |
| `get_trip_history` | Last N completed trips | `limit` |

---

## Data Sources

| Source | Provides | API Key | Fallback |
|---|---|---|---|
| Google Flights (scraper) | Flight prices and routes | None | — |
| fast-flights (PyPI) | Flight price parsing | None | — |
| Open-Meteo | Weather forecasts + historical | None (free) | — |
| Wikidata SPARQL | Attractions near coordinates | None (free) | — |
| OpenTripMap | Rated attractions database | `OPENTRIPMAP_API_KEY` | Wikidata |
| US State Dept RSS | Travel advisories | None (public RSS) | — |
| Nominatim / OSM | Geocoding | None (free) | — |
| Rome2Rio API | Multi-modal ground transport | `ROME2RIO_KEY` | Public demo key |
| open.er-api.com | Exchange rates | None (rate-limited) | — |
| ExchangeRate-API | Exchange rates (higher limits) | `EXCHANGERATE_API_KEY` | open.er-api |
| Teleport / Numbeo (static) | Cost-of-living estimates | None | Static data |
| Curated static data | Visa requirements, nearby airports | None | — |

---

## Architecture

**Framework:** [FastMCP](https://github.com/jlowin/fastmcp) — Python MCP server with `@mcp.tool()` decorator registration.

**HTTP:** Single `httpx.AsyncClient` singleton (`utils/http.py`). Lazy-initialized, shared across all tools, closed on server shutdown.

**Concurrency:** All multi-source tools use `asyncio.gather(..., return_exceptions=True)`. `plan_trip_package` fans out 8+ parallel HTTP calls.

**Profile persistence:** `~/.wander_agent/profile.json`. JSON, schema versioned. Loaded/merged with defaults on every read so new fields never break existing profiles.

**Nearby airports:** Static dict in `utils/airport_data.py` — 40+ airport pairs (JFK↔EWR↔LGA, LHR↔LGW↔STN, DXB↔SHJ↔AUH, etc.). Used by `plan_trip_package` and `cheap_anywhere_from` to automatically check alternate origin airports.

**Fallback chain per tool:**
- Flights: Amadeus API → Google Flights scraper
- Hotels: Serpapi → fast-hotels scraper → booking.com deep-links
- Activities: OpenTripMap → Wikidata SPARQL
- Ground transport: Rome2Rio API → regional service deep-links (Amtrak, Greyhound, Megabus, FlixBus, BlaBlaBus, Trainline, IRCTC, 12Go, etc.)
- Exchange rates: ExchangeRate-API → open.er-api.com

**Confidence labels:** Every tool response includes `data_confidence`:
- `scraped_live` — scraped in real time, may be stale within minutes
- `live_forecast` — live from Open-Meteo API
- `live_rss` — live from RSS feed
- `curated_snapshot` — hand-curated static data, updated periodically
- `estimated` — calculated from available data, not a direct quote
- `wikidata_fallback` — from Wikidata SPARQL, variable quality
- `deeplinks_only` — no live data, booking links only

---

## Limitations

- **Flight prices**: Scraped from Google Flights. Fragile — if the scraper breaks, prices will be unavailable. Prices are always per-person; `cheapest_price_total` field gives the full group cost.
- **Hotel prices**: Estimated from available data, not live quotes. Use booking deep-links for actual availability and pricing.
- **Visa data**: Curated static snapshot. Policies change — always verify with the official embassy link returned in the response before booking.
- **Travel advisories**: From US State Dept RSS. Typically accurate but may lag 24–48h behind official updates.
- **Activities**: Without `OPENTRIPMAP_API_KEY`, falls back to Wikidata SPARQL which has inconsistent coverage outside major cities.
- **Ground transport**: Deep-links to booking services. Route availability and pricing require clicking through to the provider.
- **Score destinations**: Composite score is a heuristic — change `weights` to match your actual priorities.

---

## Development

```bash
# Install with dev deps
uv pip install -e ".[dev]"
# or: pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Check syntax
python -m py_compile src/wander_agent/server.py

# Run the server directly
python -m wander_agent
# or
wander-agent
```

### Adding a tool

1. Create or add to an appropriate file in `src/wander_agent/tools/`
2. Import the function in `src/wander_agent/server.py`
3. Add an `@mcp.tool()` decorated wrapper function in `server.py`
4. Add tests in `tests/`

The MCP server instructions (at the top of `server.py`) tell the agent how to compose tools. Update these when adding tools that should be called as part of multi-tool workflows.
