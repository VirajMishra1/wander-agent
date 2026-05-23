# wander-agent

MCP server for travel planning. 33 tools covering flights, hotels, visas, weather, itineraries, cost of living, and trip scoring. Requires no API keys.

---

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) or pip

---

## Install

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
uv pip install -e .
```

Verify:

```bash
python -c "import wander_agent; print('ok')"
```

---

## Claude Desktop

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

If `wander-agent` is not on your PATH, use the absolute path to the binary:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "/path/to/venv/bin/wander-agent"
    }
  }
}
```

Restart Claude Desktop after saving.

---

## Claude Code (CLI)

```bash
claude mcp add wander-agent wander-agent
```

Verify it registered:

```bash
claude mcp list
```

---

## Claude.ai (web)

Claude.ai only connects to remote HTTP servers. You need to deploy wander-agent to a public URL first.

### Deploy to Railway

1. Fork this repo to your GitHub account.
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo.
3. Select your fork. Railway detects the `Dockerfile` automatically.
4. Set one environment variable in Railway's dashboard:
   ```
   WANDER_TRANSPORT=streamable-http
   ```
5. Deploy. You get a URL like `https://wander-agent-production.up.railway.app`.

### Add to Claude.ai

1. claude.ai → Settings → Integrations → Add integration.
2. URL: `https://your-app.up.railway.app/mcp`
3. Name: `wander-agent`

---

## OpenAI Codex / Agents API

OpenAI's Agents API does not natively support MCP. Two options:

**Option 1 — Use the Python functions directly:**
```python
from wander_agent.tools.flights import search_flights
from wander_agent.tools.visa import check_visa_requirement
import asyncio

result = asyncio.run(search_flights("JFK", "LHR", "2026-08-15", adults=2))
```

**Option 2 — Bridge via mcp-agent:**
Use [lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent) to proxy MCP tools into OpenAI function-call format.

---

## Tools

### Flights

| Tool | What it does |
|------|-------------|
| `search_flights` | Live flight search. Pulls from Kiwi.com (real prices) and Google Flights scraper in parallel. Returns prices, duration, stops, and booking links for Skyscanner, Expedia, Turkish Airlines, lastminute.com. |
| `find_skiplagged_fares` | Hidden-city ticketing — finds connecting flights cheaper than the direct route by exiting at the layover. Carry-on only. |
| `find_mistake_fares` | Scans Secret Flying and The Flight Deal RSS for error fares and deals. |
| `cheap_anywhere_from` | Ranks cheapest destinations from an origin across 114 airports. |
| `find_destinations_by_budget` | Finds destinations reachable within a total trip budget. |
| `multi_origin_meetup` | Finds the cheapest meeting city for multiple travelers flying from different origins. |
| `verify_flight_route` | Confirms a route exists between two airports. |

### Hotels

| Tool | What it does |
|------|-------------|
| `search_hotels` | Returns hotel names scraped from Google Hotels. Prices are not available without a hotel API key — returns booking links to Booking.com, Expedia, Tripadvisor, Trivago, Airbnb, Wyndham, DirectBooker, lastminute.com, and Google Hotels. |

### Visas & Entry

| Tool | What it does |
|------|-------------|
| `check_visa_requirement` | Visa category (visa-free / ETA / e-visa / visa on arrival / visa required) for a passport + destination pair, with official apply links. Covers 22 passports. |
| `visa_free_destinations` | All destinations accessible without a full visa for a given passport. |

### Weather

| Tool | What it does |
|------|-------------|
| `get_weather` | 16-day forecast (Open-Meteo). Falls back to 5-year historical average for dates beyond the forecast window. |
| `best_month_to_visit` | Ranks all 12 months by weather suitability for a destination, based on historical climate data. |

### Advisory

| Tool | What it does |
|------|-------------|
| `get_travel_advisory` | US State Dept advisory level (1–4) and summary for a country, from the live RSS feed. |
| `list_advisories_by_level` | All countries at or above a given advisory level. |

### Costs & Currency

| Tool | What it does |
|------|-------------|
| `get_cost_of_living` | Daily budget estimates (budget / mid / luxury) for 220 cities. |
| `convert_currency` | Live currency conversion via Frankfurter (European Central Bank rates). |
| `get_exchange_rates` | Rates for multiple currencies from a base. |

### Activities & Events

| Tool | What it does |
|------|-------------|
| `search_activities` | Attractions near a location from Wikidata SPARQL. |
| `get_local_events` | Real events scraped from Eventbrite (name, date, venue, URL). Falls back to deeplinks for Meetup, Songkick, Ticketmaster, Resident Advisor if scraping unavailable. |
| `get_destination_info` | Country metadata: currency, language, timezone, dialling code, driving side. |
| `geocode` | Coordinates and country for a place name. |
| `verify_place` | Confirms a place exists and returns its canonical name and coordinates. |

### Planning & Scoring

| Tool | What it does |
|------|-------------|
| `plan_trip_package` | Orchestrates flights + hotels + visa + weather + advisory + activities + ground transport in one call. |
| `plan_itinerary` | Day-by-day itinerary with weather and activities for each day. |
| `score_destinations` | Ranks destinations by weighted combination of cost, weather, safety, and events. |
| `compare_destinations` | Side-by-side cost and weather comparison for 2–5 destinations. |
| `optimize_budget` | Finds cheapest flight and hotel combination across a flexible date window. |

### Ground Transport

| Tool | What it does |
|------|-------------|
| `search_ground_transport` | Bus, train, and ferry booking links. Region-aware — shows Amtrak/Greyhound/FlixBus in the US, Trainline/BlaBlaCar in Europe, IRCTC in India, 12Go in Southeast Asia. |
| `find_aurora_destinations` | Aurora-viewing destinations with live NOAA KP-index forecast and flight prices. |

### Traveler Profile

| Tool | What it does |
|------|-------------|
| `get_traveler_profile` | Load saved profile (home airports, passports, currency, interests, trip history). |
| `onboard_traveler` | First-time setup — saves name, home airports, passports, and preferences. |
| `update_traveler_profile` | Update any profile field. |
| `get_trip_history` | Last N completed trips. |

---

## Data Sources

| Source | Provides | Key required |
|--------|----------|-------------|
| Kiwi.com MCP (`mcp.kiwi.com`) | Live flight prices and booking links | No |
| Google Flights (fast-flights scraper) | Flight prices and airline names | No |
| Eventbrite (HTML scrape) | Live event listings with dates and venues | No |
| Open-Meteo | Weather forecast and historical climate | No |
| Frankfurter API | Currency exchange rates (ECB) | No |
| Wikidata SPARQL | Attractions and points of interest | No |
| US State Dept RSS | Travel advisories | No |
| Open-Meteo Geocoding | Coordinates for place names | No |
| RESTCountries | Country metadata | No |
| Secret Flying / The Flight Deal RSS | Mistake fares and deals | No |
| NOAA Space Weather | Aurora KP-index forecast | No |
| Skiplagged (undocumented endpoint) | Hidden-city fares | No (fragile) |
| Static dataset | Visa requirements (22 passports), cost of living (220 cities), 114 destination airports | N/A |

---

## What the data actually is

- **Flight prices**: Kiwi.com returns real bookable prices. Google Flights scraper returns typical prices that may lag by minutes. Both run in parallel; Kiwi result takes priority.
- **Hotel prices**: Not available. All hotel price APIs require a commercial key. The hotel tool returns names from Google Hotels and booking deeplinks to 9 providers.
- **Visa data**: Static snapshot from IATA Timatic and Wikipedia visa tables. Policies change — always verify with the official link in the response before booking.
- **Events**: Scraped from Eventbrite public search pages. Coverage is best for events 0–60 days out; events further ahead may not appear yet.
- **Travel advisories**: US State Dept only. Updated via RSS, typically within 24–48 hours of official changes.
- **Cost of living**: Manual dataset of 220 cities, updated periodically. Use as a rough planning guide, not a budget guarantee.

---

## Architecture

- **Framework**: FastMCP — `@mcp.tool()` registers each function as an MCP tool.
- **HTTP client**: Single `httpx.AsyncClient` singleton, shared across all tools.
- **Concurrency**: `asyncio.gather()` throughout. `plan_trip_package` fans out 8+ parallel requests.
- **Profile store**: `~/.wander_agent/profile.json`. New fields are merged with defaults on read so old profiles never break.
- **Nearby airports**: 27 metro areas mapped in `utils/airport_data.py`. `plan_trip_package` and `cheap_anywhere_from` automatically check alternates (e.g. JFK → also EWR, LGA).
- **Transport**: Defaults to `stdio` for local clients. Set `WANDER_TRANSPORT=streamable-http` and `PORT` for HTTP deployment.

---

## Development

```bash
uv pip install -e ".[dev]"
python -m pytest tests/ -v
```

Adding a tool: create the function in `src/wander_agent/tools/`, import it in `server.py`, wrap it with `@mcp.tool()`.
