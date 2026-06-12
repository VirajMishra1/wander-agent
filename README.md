<div align="center">

# 🌍 Wander Agent

**A travel planning AI with 60 tools, zero API keys required.**

Ask your AI anything about travel — flights, hotels, visas, weather, safety, local food, packing lists — and get real data back, not hallucinations.

[![CI](https://github.com/VirajMishra1/wander-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/VirajMishra1/wander-agent/actions/workflows/ci.yml) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/) [![MCP](https://img.shields.io/badge/protocol-MCP-purple.svg)](https://modelcontextprotocol.io/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/VirajMishra1/wander-agent/blob/main/LICENSE)

[See the launch demo](https://x.com/virajm1shra/status/2059930318359109965)

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
- **Split-ticket search** — book two separate tickets via a hub; OTAs are contractually forbidden from showing you this
- **Month-level price scan** — check every month for the next year, returns cheapest month to fly
- **Fare calendar** — cheapest day within a given month, day-of-week analysis
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
- **Passport power ranking** — Henley Index 2024 rank, visa-free %, regional breakdown
- **Dual-passport comparison** — see exactly which destinations each passport unlocks that the other doesn't
- **Transit visa check** — do you need a visa just to change planes? 200+ passport × layover rules
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
- **Open-jaw trips** — fly into Rome, train to Paris, fly home from Paris. Composed automatically.

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
- **Local SIM guide** — 25+ countries: best prepaid SIM vs eSIM, cost, where to buy, tethering policy

</details>

<details>
<summary><strong>🧠 Memory & Decisions</strong></summary>

- Saves your home airports, passports, currency, and interests — never ask again
- Logs your trip history
- **Saved trips** — a persistent trip with an 8-item booking checklist that survives across sessions
- **Fare watching** — set a target price on a route, re-price on demand, get a buy signal when it drops
- **Value ranking** — scores options 0–100 on price *plus* stops, duration, refundability, baggage and hassle (flags hidden-city / split-ticket risk), so cheapest isn't blindly "best"

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

From PyPI (recommended):

```bash
pip install wander-agent
```

Or with [uv](https://docs.astral.sh/uv/) — no install at all, run directly:

```bash
uvx wander-agent
```

Or from source:

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
pip install -e .
```

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

## All 60 Tools

### ✈️ Flights

| Tool | What it does |
|------|-------------|
| `search_flights` | Live flight search across Google Flights and Kiwi.com in parallel. Returns prices, duration, stops, and booking links. |
| `find_skiplagged_fares` | Hidden-city fares — buy a connecting flight and exit at the layover city. Often 40–60% cheaper. Carry-on only. |
| `find_split_ticket` | Book two separate tickets through a hub instead of one through-ticket. OTAs are contractually forbidden from showing this. Savings of 20–60% on many routes. Includes full risk disclosure. |
| `find_cheapest_month` | Scans the next 12 months by sampling the first Tuesday of each month (statistically cheapest booking day). Returns all months ranked by price with season analysis and booking links. |
| `fare_calendar` | Full month price grid — up to 15 sampled days, day-of-week analysis, price tiers, best/worst weeks. Find the cheapest day to fly within a given month. |
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
| `get_passport_power` | Henley Index 2024 rank, visa-free access count, frictionless travel %, and regional breakdown for any passport. Pass two passports to get a head-to-head diff: exactly which destinations each one unlocks that the other doesn't. |
| `check_transit_visa` | Do you need a transit visa at your layover airport? Covers 200+ passport × layover-country combinations. Checks LHR, JFK, DXB, SIN, FRA, IST, DOH, NRT, ICN, YYZ, SYD, and 30+ others. |

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
| `find_open_jaw` | Plan a fly-in/overland/fly-out trip: land in city A, travel by train or bus, fly home from city B. Composes flight + ground transport search. Shows total cost vs a round-trip to city A only. Accepts city names or IATA codes. |
| `score_destinations` | Ranks destinations by a weighted combination of cost, weather, safety, and events. |
| `compare_destinations` | Side-by-side comparison of 2–5 destinations for the same dates. |

### 🍜 Food & Nightlife

| Tool | What it does |
|------|-------------|
| `search_restaurants_bars` | Real venues near a location from OpenStreetMap. Returns cuisine, price level, opening hours, distance, and links to Google Maps, Zomato, TripAdvisor, Yelp, OpenTable, Resy, and Untappd. |

### 🌐 Smart Trip Tools

| Tool | What it does |
|------|-------------|
| `score_nomad_cities` | Ranks cities for remote work across 6 dimensions: cost, safety, internet speed, weather, visa ease, and lifestyle. Configurable weights. |
| `calculate_flight_carbon` | CO2e footprint for any flight using ICAO/DEFRA 2024 factors with radiative forcing (RFI ×1.9). Per-passenger and total emissions, Gold Standard offset cost, and train/car comparison for short routes. |

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
| `get_local_sim_guide` | Best prepaid SIM card and eSIM for 25+ countries. Returns operator, cost, data allowance, where to buy, tethering policy, and duration-based advice (≤3 days → eSIM; longer → local SIM). Falls back to Airalo/Holafly for unlisted countries. |

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

### 🧳 Saved Trips (cross-session memory)

Persisted to `~/.wander_agent/trips.json`. A trip carries an 8-item booking checklist (flights, hotel, visa, insurance, ground transport, advisory, packing, notify bank).

| Tool | What it does |
|------|-------------|
| `save_trip` | Save a trip you're planning. Returns a `trip_id` and a fresh booking checklist. |
| `list_my_trips` | List saved trips with checklist progress. Filter by status (planning/booked/completed/cancelled). |
| `get_trip_status` | Full state + checklist progress for one trip, by id or destination. |
| `update_trip` | Change status/dates, tick checklist items, or shortlist a flight/hotel option onto the trip. |
| `delete_trip` | Remove a saved trip. |

### 🔔 Fare Watching

Persisted to `~/.wander_agent/fare_watches.json`. Records a baseline price and a price history per watched route.

| Tool | What it does |
|------|-------------|
| `watch_fare` | Start watching a route with an optional target price. Captures a baseline on creation. |
| `list_fare_watches` | List watches with baseline / last / lowest price seen and status. |
| `check_fare_watches` | Re-price watched routes now. Returns buy-signal alerts: `target_hit`, `price_drop`, `price_rise`, `no_change`. |
| `stop_fare_watch` | Pause or delete a watch. |

### ⚖️ Value Ranking

| Tool | What it does |
|------|-------------|
| `rank_trip_options` | Scores a list of flight/trip options 0–100 on price plus stops, duration, refundability, baggage and hassle. Presets: cheapest / fastest / easiest / flexible / balanced. Flags hidden-city, split-ticket and self-transfer risk so the cheapest fare isn't blindly the winner. |

---

## Tool Rankings: Usefulness × X-Factor

Ranked by a combination of practical impact and uniqueness — things no OTA, no chatbot, and no other travel tool does.

| Rank | Tool | Why it's here |
|------|------|---------------|
| 🥇 1 | `find_split_ticket` | OTAs are **contractually prevented** from showing this. Book two tickets via a hub instead of a through-ticket. 20–60% savings on many long-haul routes. The travel industry's open secret. |
| 2 | `find_skiplagged_fares` | Hidden-city ticketing. Buy a flight to city B with a layover in city A — exit in city A and never board the last leg. 40–60% off. Illegal per airline T&Cs but not against any law. Carry-on only. |
| 3 | `plan_trip_package` | One message → complete trip. Fires 8+ tools in parallel: flights, hotels, visa, weather, safety, activities, ground transport, cost estimate. The single best demo of what this agent can do. |
| 4 | `find_cheapest_month` | Scans 12 months, samples first Tuesday of each (statistically cheapest booking day). Returns months ranked by price with season labels. Shifting by 1–2 months = hundreds of dollars saved. |
| 5 | `check_transit_visa` | The one nobody thinks to check until it's too late. Do you need a visa just to change planes at Heathrow? At Frankfurt? 200+ passport × layover combinations. Catches the trip-killer before you book. |
| 6 | `multi_origin_meetup` | Three friends, three different cities. What's the cheapest city for all of them to meet? No OTA has a tool for this. |
| 7 | `find_open_jaw` | Fly into Rome, take a train to Paris, fly home from Paris. No OTA lets you compose this. Automatically prices both flights + the overland segment and compares vs a simple round-trip to Rome. |
| 8 | `get_passport_power` | Henley 2024 rank, visa-free %, regional breakdown. Dual-passport mode: exact set-diff of which destinations each passport unlocks. "Use your Indian passport for Thailand, your US passport for Brazil." |
| 9 | `score_nomad_cities` | 6-dimension scoring for digital nomad decisions: cost, safety, internet speed, weather, visa ease, lifestyle. Configurable weights. "Score Bali vs Lisbon vs Tbilisi for 3 months, weight internet 3× above cost." |
| 10 | `find_mistake_fares` | Error fares and airline pricing mistakes from dedicated deal aggregators. Passive discovery — "are there any crazy cheap fares out of JFK right now?" |
| 11 | `fare_calendar` | Full price grid for a month. Up to 15 sampled days, cheapest day highlighted, day-of-week analysis (Tuesdays 18% cheaper on average), best/worst weeks. |
| 12 | `cheap_anywhere_from` | "Where can I fly cheapest from London right now?" Scans 114 airports. Discovery tool for spontaneous travelers. |
| 13 | `find_destinations_by_budget` | "I have $1,500 total for 7 nights, leaving from NYC — where can I actually go?" Returns ranked reachable destinations. |
| 14 | `optimize_budget` | Shifts departure ±7 days to find the cheapest flight + hotel combo. Same trip, different dates, lower price. |
| 15 | `calculate_flight_carbon` | ICAO/DEFRA 2024 emission factors with radiative forcing (RFI ×1.9). Per-person and total CO2e, Gold Standard offset cost at $18/tonne, train/car comparison for routes under 1,500km. |
| 16 | `search_flights` | Core engine. Parallel Google Flights + Kiwi.com. Checks nearby airports automatically. |
| 17 | `check_visa_requirement` | Most-asked travel question. Instant answer with official government apply link. |
| 18 | `plan_itinerary` | Day-by-day schedule with weather per day and activity suggestions. |
| 19 | `score_destinations` | Weighted rank: cost + weather + safety + upcoming events. "Best place to go in September with good weather, under $150/day, safety level 1." |
| 20 | `visa_free_destinations` | Full list of countries a passport can enter without a full embassy visa. |
| 21 | `get_local_sim_guide` | 25+ countries. Best prepaid SIM vs eSIM, exact cost, where to buy, tethering, activation steps. Short trip = eSIM. Long trip = local SIM. Saves the first-hour scramble at every airport. |
| 22 | `compare_destinations` | Side-by-side: cost, weather, safety, visa requirements, flights — for 2–5 destinations, same dates. |
| 23 | `search_ground_transport` | Bus + train + ferry with real booking links. Region-aware. Often cheaper and more convenient than flying for routes under 500km. |
| 24 | `check_travel_health` | Required vaccines, recommended vaccines, water safety, food safety, mosquito risk, altitude risk, pre-trip timeline. CDC + WHO 2025 data. |
| 25 | `get_travel_advisory` | Live US State Dept level 1–4 with summary. Pulled from RSS — not cached stale data. |
| 26 | `get_weather` | 16-day live forecast. Falls back to 5-year historical climate data for further-ahead dates. |
| 27 | `find_aurora_destinations` | Best spots for northern lights with live NOAA KP-index forecast + flight prices from your origin. Viral for the "bucket list" audience. |
| 28 | `search_hotels` | Hotel search with deep links to 9 booking sites. No prices shown directly (all hotel price APIs are paid), but all the links you need. |
| 29 | `get_cost_of_living` | Daily budget for 220 cities: budget / mid-range / luxury tiers. |
| 30 | `best_month_to_visit` | Climate-based ranking of all 12 months for a location. Based on 5 years of historical data. |
| 31 | `get_stopover_guide` | What to actually do during a long layover at DXB, SIN, IST, DOH, NRT, CDG, HKG, ICN, AMS, or HND. In-airport options + city excursion feasibility. |
| 32 | `search_activities` | Wikidata attractions by category: museums, parks, architecture, food, nightlife, historic, nature. |
| 33 | `find_places` | OpenStreetMap viewpoints, beaches, hiking trails, coworking spaces, waterfalls, hot springs, markets. |
| 34 | `search_restaurants_bars` | Real venues from OSM with 7 booking site links per result. Cuisine filter, price level, distance. |
| 35 | `get_language_phrasebook` | 17 languages. Local script + romanized pronunciation + audio tips. |
| 36 | `generate_packing_list` | Tailored to destination weather, planned activities, trip length, and budget level. |
| 37 | `get_local_events` | Live Eventbrite events at destination: concerts, festivals, sports. Best for 0–60 day horizon. |
| 38 | `get_travel_news` | Google News scan for disruptions: strikes, closures, protests, entry bans. |
| 39 | `calculate_jet_lag` | Severity rating + science-based recovery: pre-trip sleep shifting, melatonin timing, light exposure schedule. |
| 40 | `get_destination_info` | Country basics: currency, language, timezone, dialling code, driving side. |
| 41 | `list_advisories_by_level` | All countries currently at Level 2, 3, or 4. Useful for insurance and risk-screening. |
| 42 | `verify_flight_route` | Confirms a route actually exists. Catches hallucinated itineraries before you book. |
| 43 | `onboard_traveler` | One-time setup: home airports, passports, currency, interests. Feeds every tool automatically. |
| 44 | `get_traveler_profile` | Load saved profile. Used automatically at session start. |
| 45 | `update_traveler_profile` | Update preferences or log a completed trip. |
| 46 | `get_trip_history` | Your logged trip history. |
| 47 | `convert_currency` | ECB live rate conversion. |
| 48 | `get_exchange_rates` | Multi-currency rates from a base currency. |
| 49 | `geocode` | Place name → latitude/longitude. Used internally by most tools. |
| 50 | `verify_place` | Confirms a place exists before building a trip around it. Anti-hallucination guardrail. |

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
| Skiplagged | Hidden-city fares | No (fragile scraper) |
| Rome2Rio / Omio | Ground transport options | No (fallback to deeplinks) |
| Eventbrite | Live local events | No |
| Foursquare Places v3 | Restaurant/bar ratings and price levels | Optional (free tier) |
| Ticketmaster Discovery | Live event listings | Optional (free tier) |
| Static datasets | Visa requirements, cost of living, airport data, transit visa rules, SIM card data, Henley rankings | N/A |

---

## How much can you trust each number?

Most results carry a `data_meta` block so the AI can tell you how reliable a figure is before you book:

```json
"data_meta": {
  "confidence": "scraped_live",
  "trust_score": 80,
  "trust_label": "Live scrape",
  "meaning": "Scraped from Google Flights just now. Real but can shift minute to minute.",
  "fetched_at": "2026-06-02T18:30:00+00:00",
  "source": "google_flights + kiwi.com"
}
```

| Label | Trust | What it means |
|-------|-------|---------------|
| `deeplink` | 95 | Opens the live provider page — always current |
| `live_api` | 90 | Official API (ECB rates, NOAA) |
| `live_rss` | 85 | Live government feed (State Dept advisories) |
| `live_forecast` | 85 | Open-Meteo live weather |
| `scraped_live` | 80 | Real-time scrape — real but volatile |
| `curated_snapshot` | 55 | Hand-curated dataset — verify before booking |
| `wikidata_fallback` | 50 | Wikidata-derived |
| `estimated` | 35 | Modeled figure — rough guide only |

---

## Honest limitations

**Flight prices:** Google Flights scraper can break if Google changes their page structure. Kiwi prices are real and bookable. Both run in parallel — if one fails the other still returns results.

**Split-ticket risk:** `find_split_ticket` surfaces real savings but carries missed-connection risk. If your first flight is delayed the second airline won't wait and won't rebook you. The tool always returns a full risk disclosure list. Buy travel insurance that covers missed connections on separate tickets.

**Hotel prices:** Every hotel price API is paid. This tool returns hotel names and links to 9 booking sites where you can see real prices. No prices are shown directly.

**Visa data:** Static snapshot (updated 2024). Policies change — always verify with the official link in the response before you book anything. Do not rely on this for immigration decisions.

**Transit visa data:** Rules encoded as a static dataset covering 200+ combinations. Edge cases (nationalities with bilateral exemptions, recent policy changes) may be missing. Always verify with the airline or destination embassy.

**Passport power data:** Henley Index 2024 snapshot. Rankings shift year to year. Confirm with official sources before making nationality-based decisions.

**SIM card data:** Curated snapshot as of 2024-Q4. Prices and plans change frequently. Treat as guidance; verify before purchase.

**Events:** Scraped from Eventbrite. Best coverage for events 0–60 days ahead. Further-future events may not be listed yet.

**Travel advisories:** US State Dept only. Updated within 24–48 hours of official changes via RSS.

**Health data:** Curated snapshot from CDC Yellow Book and WHO 2024–2025 recommendations. Not a substitute for advice from a travel medicine clinic.

**Ground transport:** Rome2Rio data for route discovery. Actual prices and schedules must be confirmed on the booking sites — times and fares change.

**Carbon calculations:** ICAO/DEFRA 2024 emission factors with standard RFI multiplier (×1.9). Actual emissions vary by aircraft type, load factor, and routing. Use as an estimate, not an accounting figure.

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

**CI:** every push and PR to `main` runs the test suite on Python 3.10/3.11/3.12 and asserts the registered tool count.

**Releases:** publishing a GitHub release triggers the PyPI publish workflow (trusted publishing — no tokens). Bump `version` in `pyproject.toml` and `server.json` first.

---

## License

MIT

mcp-name: io.github.VirajMishra1/wander-agent
