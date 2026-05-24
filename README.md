<div align="center">

# 🌍 Wander Agent

**A travel planning AI with 41 tools, zero API keys required.**

Ask your AI anything about travel — flights, hotels, visas, weather, safety, local food, packing lists — and get real data back, not hallucinations.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/) [![MCP](https://img.shields.io/badge/protocol-MCP-purple.svg)](https://modelcontextprotocol.io/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## What is this?

Wander Agent is a **tool plugin for AI assistants** (Claude, Cursor, Windsurf, etc.) that gives the AI real travel data to work with.

Without this plugin, asking an AI "cheapest flights from New York to Tokyo in August?" gets you a made-up answer. With this plugin, the AI calls real data sources — Google Flights, Open-Meteo, US State Dept advisories, OpenStreetMap — and gives you actual prices, real forecasts, and live visa requirements.

**You talk to the AI the same way you always do. The AI does the rest.**

> *"Plan me a 10-day trip to Bali for 2 people leaving from Dubai in September, budget $3,000"*
> → Real flights, real hotels, visa requirements, weather forecast, local restaurants, packing list, day-by-day itinerary — all in one response.

---

## What can it do?

<details>
<summary><strong>✈️ Flights</strong></summary>

- Search live flights (Google Flights + Kiwi.com in parallel)
- Find hidden-city fares — e.g. buy NYC→Mexico via Houston, exit in Houston at 40% discount
- Scan for mistake fares and error pricing from deal alert sites
- Find the cheapest destination you can fly to from anywhere
- Find cheapest meeting point for friends flying from different cities
- Automatically checks nearby airports (JFK also checks EWR, LGA; DXB also checks SHJ, AUH)

</details>

<details>
<summary><strong>🏨 Hotels</strong></summary>

- Search hotels with direct booking links to Booking.com, Airbnb, Expedia, Tripadvisor, and 6 more
- Optimize for cheapest flight + hotel combo across flexible dates

</details>

<details>
<summary><strong>📋 Visas & Entry</strong></summary>

- Check if you need a visa, e-visa, ETA, or nothing at all
- See every country you can enter without a full visa
- Official government apply links included

</details>

<details>
<summary><strong>🌤️ Weather</strong></summary>

- 16-day live forecast for any location
- Best month to visit anywhere based on 5 years of climate data
- Jet lag calculator with science-based recovery schedule

</details>

<details>
<summary><strong>⚠️ Safety</strong></summary>

- Live US State Dept advisory level for any country (1 = safe, 4 = do not travel)
- List every country at or above a given risk level
- Recent travel news: strikes, airport closures, entry bans, protests

</details>

<details>
<summary><strong>💰 Costs</strong></summary>

- Daily budget estimates for 220 cities (budget / mid-range / luxury)
- Live currency conversion
- Total trip cost estimate combining flights, hotels, and daily spend

</details>

<details>
<summary><strong>🗺️ Planning</strong></summary>

- Day-by-day itinerary with weather and activities for each day
- Rank and score destinations by cost + weather + safety + events
- Compare multiple destinations side-by-side
- Aurora viewing destinations with NOAA KP-index forecast

</details>

<details>
<summary><strong>🍜 Food & Nightlife</strong></summary>

- Restaurants, bars, pubs, and cafes near any location (OpenStreetMap)
- Cuisine filters, price level, opening hours, distance
- Booking links: Google Maps, Zomato, TripAdvisor, Yelp, OpenTable, Resy, Untappd

</details>

<details>
<summary><strong>🎒 On the Ground</strong></summary>

- Packing list tailored to weather, activities, and trip length
- Language phrasebook for 17 languages with pronunciation guides
- Layover guide for 10 major hub airports (DXB, SIN, IST, DOH, NRT, CDG, HKG, ICN, AMS, HND)
- Health requirements: vaccines, water safety, food safety, pre-trip timeline
- Bus, train, and ferry options with direct booking links
- Viewpoints, beaches, hiking trails, coworking spaces near any location

</details>

<details>
<summary><strong>🧠 Memory</strong></summary>

- Saves your home airports, passports, currency, and interests
- Never ask again — the AI uses your profile automatically
- Logs your trip history

</details>

---

## Setup (5 minutes)

### Step 1 — Install Python

You need Python 3.10 or newer. Check if you have it:

```bash
python3 --version
```

Don't have it? Download from [python.org](https://www.python.org/downloads/).

---

### Step 2 — Install Wander Agent

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
pip install -e .
```

> **Using uv?** Replace `pip install -e .` with `uv pip install -e .`

Verify it worked:

```bash
wander-agent --help
```

---

### Step 3 — Connect to your AI

Pick the app you use:

<details>
<summary><strong>Claude Desktop</strong></summary>

Open this file in a text editor:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent"
    }
  }
}
```

Save the file, then **quit and reopen Claude Desktop**.

If you get an error about `wander-agent` not being found, find the full path first:

```bash
which wander-agent
```

Then use that path in the config:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "/usr/local/bin/wander-agent"
    }
  }
}
```

</details>

<details>
<summary><strong>Claude Code (terminal)</strong></summary>

```bash
claude mcp add wander-agent wander-agent
```

Confirm it registered:

```bash
claude mcp list
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

Create or edit `.cursor/mcp.json` in your home directory:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent"
    }
  }
}
```

Restart Cursor.

</details>

<details>
<summary><strong>Windsurf</strong></summary>

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

Restart Windsurf.

</details>

<details>
<summary><strong>Cline (VS Code extension)</strong></summary>

Open VS Code settings, search for "Cline MCP", edit `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "wander-agent"
    }
  }
}
```

</details>

<details>
<summary><strong>Continue.dev</strong></summary>

Edit `.continuerc.json` in your project or home directory:

```json
{
  "mcpServers": [
    {
      "name": "wander-agent",
      "command": "wander-agent"
    }
  ]
}
```

</details>

<details>
<summary><strong>Zed</strong></summary>

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

</details>

---

## Optional: API keys for better data

Everything works without any API keys. These add richer data if you want:

| Variable | What it unlocks | Get it free at |
|----------|----------------|----------------|
| `FOURSQUARE_API_KEY` | Real ratings and price levels for restaurants/bars | [foursquare.com/developers](https://foursquare.com/developers/signup) |
| `TICKETMASTER_API_KEY` | Live event listings (concerts, sports, shows) | [developer.ticketmaster.com](https://developer.ticketmaster.com) |

Set them before starting your AI:

```bash
export FOURSQUARE_API_KEY=your_key_here
export TICKETMASTER_API_KEY=your_key_here
```

Or add them to your shell profile (`~/.zshrc`, `~/.bashrc`) to make them permanent.

---

## All 41 Tools

### ✈️ Flights

| Tool | What it does |
|------|-------------|
| `search_flights` | Live flight search across Google Flights and Kiwi.com. Returns prices, duration, stops, and booking links. |
| `find_skiplagged_fares` | Hidden-city fares — buy a connecting flight and exit at the layover city. Often 40–60% cheaper. Carry-on only. |
| `find_mistake_fares` | Scans Secret Flying and The Flight Deal RSS for error fares and flash deals. |
| `cheap_anywhere_from` | Cheapest destinations from an origin across 114 airports worldwide. |
| `find_destinations_by_budget` | Finds destinations reachable within a total budget (flights + hotels). |
| `multi_origin_meetup` | Cheapest city for multiple friends to meet, flying from different cities. |
| `verify_flight_route` | Confirms a direct or connecting route exists between two airports. |
| `find_aurora_destinations` | Aurora-viewing destinations with live NOAA KP-index forecast and flight prices. |

### 🏨 Hotels

| Tool | What it does |
|------|-------------|
| `search_hotels` | Hotels with booking links to Booking.com, Airbnb, Expedia, Tripadvisor, and 6 more. |
| `optimize_budget` | Finds the cheapest flight + hotel combo across a flexible date window (±7 days). |

### 📋 Visas & Entry

| Tool | What it does |
|------|-------------|
| `check_visa_requirement` | Visa category for a passport + destination pair. Returns visa-free, ETA, e-visa, visa on arrival, or visa required — with the official apply link. |
| `visa_free_destinations` | Every country a given passport can enter without a full embassy visa. |

### 🌤️ Weather

| Tool | What it does |
|------|-------------|
| `get_weather` | 16-day live weather forecast for any coordinates. Falls back to 5-year historical data for dates beyond the forecast window. |
| `best_month_to_visit` | Ranks all 12 months for a location by weather quality, based on historical climate data. |

### ⚠️ Safety & News

| Tool | What it does |
|------|-------------|
| `get_travel_advisory` | US State Dept advisory level (1–4) and summary. Pulled from the live RSS feed. |
| `list_advisories_by_level` | All countries currently at or above a given advisory level. |
| `get_travel_news` | Scans Google News for recent disruptions: strikes, airport closures, entry bans, protests. |

### 💰 Costs & Currency

| Tool | What it does |
|------|-------------|
| `get_cost_of_living` | Daily budget estimates for 220 cities across budget, mid-range, and luxury tiers. |
| `convert_currency` | Live currency conversion via European Central Bank rates. |
| `get_exchange_rates` | Exchange rates for multiple currencies from a base currency. |

### 🗺️ Planning & Scoring

| Tool | What it does |
|------|-------------|
| `plan_trip_package` | The main orchestrator. Calls 8+ tools in parallel and returns a complete trip: flights, hotels, visa, weather, safety, activities, ground transport, cost estimate, and booking checklist. |
| `plan_itinerary` | Day-by-day itinerary with weather forecast and suggested activities for each day. |
| `score_destinations` | Ranks destinations by a weighted combination of cost, weather, safety, and events. |
| `compare_destinations` | Side-by-side comparison of 2–5 destinations for the same dates. |

### 🍜 Food & Nightlife

| Tool | What it does |
|------|-------------|
| `search_restaurants_bars` | Real venues near a location from OpenStreetMap. Returns cuisine, price level, opening hours, distance, and links to Google Maps, Zomato, TripAdvisor, Yelp, OpenTable, Resy, and Untappd. |

### 🎒 On the Ground

| Tool | What it does |
|------|-------------|
| `generate_packing_list` | Packing list tailored to destination weather, activities, trip length, and budget level. |
| `find_places` | Viewpoints, beaches, hiking trails, coworking spaces, waterfalls, markets, and more from OpenStreetMap. |
| `calculate_jet_lag` | Jet lag severity with a science-based recovery schedule: pre-departure shift, melatonin timing, light exposure strategy. |
| `get_language_phrasebook` | Phrasebook for 17 languages with local script, romanized pronunciation, and audio tips. |
| `get_stopover_guide` | What to do during a layover at 10 major hubs. Includes transit visa check, in-airport activities, and city excursion options. |
| `check_travel_health` | Required and recommended vaccines, water safety, food safety, mosquito risk, altitude risk, and a pre-trip preparation timeline. Based on CDC and WHO 2024–2025 data. |
| `search_ground_transport` | Bus, train, and ferry options with booking links. Region-aware: Amtrak and Greyhound for the US, Trainline and BlaBlaCar for Europe, IRCTC for India, 12Go for Southeast Asia. |

### 🏛️ Attractions & Info

| Tool | What it does |
|------|-------------|
| `search_activities` | Attractions near a location from Wikidata. Filter by category: museums, parks, architecture, nightlife, food, historic, nature, and more. |
| `get_local_events` | Live events from Eventbrite: concerts, sports, festivals. |
| `get_destination_info` | Country basics: currency, official language, timezone, dialling code, driving side. |
| `geocode` | Converts a place name to coordinates. |
| `verify_place` | Confirms a place actually exists (catches AI hallucinations before they reach you). |

### 🧠 Traveler Profile

| Tool | What it does |
|------|-------------|
| `get_traveler_profile` | Loads your saved profile: home airports, passports, currency, interests, and trip history. |
| `onboard_traveler` | One-time setup. Saves your preferences so the AI uses them automatically in every future session. |
| `update_traveler_profile` | Update any field or log a completed trip. |
| `get_trip_history` | Your logged trip history. |

---

## Data sources

| Source | What it provides | Key needed? |
|--------|----------------|-------------|
| Google Flights (scraper) | Flight prices and airline names | No |
| Kiwi.com | Live bookable flight prices | No |
| Open-Meteo | Weather forecast and 5-year historical climate | No |
| Frankfurter (ECB) | Currency exchange rates | No |
| Wikidata SPARQL | Attractions and points of interest | No |
| OpenStreetMap Overpass | Restaurants, bars, beaches, viewpoints, hiking | No |
| US State Dept RSS | Travel advisories | No |
| Open-Meteo Geocoding | Coordinates for place names | No |
| RESTCountries | Country metadata | No |
| Secret Flying / The Flight Deal | Mistake fares and deals | No |
| NOAA Space Weather | Aurora KP-index forecast | No |
| Google News RSS | Travel disruption news | No |
| Skiplagged | Hidden-city fares | No (fragile) |
| Foursquare Places v3 | Restaurant/bar ratings and price levels | Optional (free tier) |
| Ticketmaster Discovery | Live event listings | Optional (free tier) |
| Static datasets | Visa requirements, cost of living, airport data | N/A |

---

## Honest limitations

**Flight prices:** Google Flights scraper can break if Google changes their page structure. Kiwi prices are real and bookable. Both run in parallel — the cheaper one wins.

**Hotel prices:** Every hotel price API is paid. This tool returns hotel names and links to 9 booking sites where you can see real prices. No prices are shown directly.

**Visa data:** Static snapshot. Policies change — always verify with the official link in the response before you book anything.

**Events:** Scraped from Eventbrite. Best coverage for events 0–60 days ahead. Further-future events may not be listed yet.

**Travel advisories:** US State Dept only. Updated within 24–48 hours of official changes via RSS.

**Health data:** Curated snapshot from CDC Yellow Book and WHO 2024–2025 recommendations. Not a substitute for advice from a travel medicine clinic.

---

## Cloud deployment (Docker)

The included `Dockerfile` and `railway.toml` let you host this server in the cloud so you can connect to it from any device — not just the computer where you installed it.

**You do not need this for normal local use.** Install and run locally as described in Setup above.

If you want to self-host on [Railway](https://railway.app):

```bash
# Push to GitHub, then connect repo to Railway
# Set env vars in Railway dashboard if using optional API keys
```

The server switches from stdio (local) to HTTP automatically based on the `WANDER_TRANSPORT` environment variable.

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Count registered tools
grep -c "@mcp.tool()" src/wander_agent/server.py
```

**Adding a tool:**
1. Create `src/wander_agent/tools/your_tool.py` with an async function
2. Import it in `src/wander_agent/server.py`
3. Wrap with `@mcp.tool()` and an async wrapper function
4. Restart your AI client to pick up the new tool

---

## License

MIT — see [LICENSE](LICENSE).
