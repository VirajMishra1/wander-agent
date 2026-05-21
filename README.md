# 🧭 Wander Agent

> **The AI travel agent that does what no other open-source tool does.**

An MCP server with **20 tools** that turn Claude (or any MCP-compatible AI) into a world-class travel agent. Two modes: **Inspiration** (don't know where to go) and **Planning** (know where you're going). Plus differentiators nobody else ships.

**100% free APIs. No paid keys. No frontend. Just import and go.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What makes this different

Every other open-source travel agent is a Streamlit app or Next.js webapp. They're products. **Wander Agent is a capability** — add it to Claude/ChatGPT/Cursor and any AI becomes a travel agent.

### Real use cases that nothing else handles:

> 🎯 "I have $1500. Trip in March. Surprise me."
> → `find_destinations_by_budget` calculates flight+hotel for 50+ destinations under $1500, ranks them.

> 🎭 "Paris vs Rome vs Barcelona for next month — show me everything."
> → `compare_destinations` returns flight+hotel costs for all three, side-by-side, ranked.

> 🌍 "Where should I go in July for warm weather, low crime, and music festivals?"
> → `score_destinations` ranks by cost + weather + safety + events simultaneously.

> 🎤 "Plan Tokyo in May. Also tell me if any of my favorite bands are playing then."
> → `plan_itinerary` + `get_local_events` returns the trip plus concerts/shows during those exact dates.

> 💰 "How far does $100/day actually go in Lisbon vs Tokyo vs Reykjavik?"
> → `get_cost_of_living` returns budget breakdown for each city.

> 🚨 "Is Egypt safe right now? What vaccinations do I need?"
> → `get_travel_advisory` returns official government advisories + health requirements.

> 📅 "When is the best time to visit Bali?"
> → `best_month_to_visit` analyzes 5 years of historical climate data.

> 🛡️ "AI suggested 'Restaurant Le Bernardin in Lyon' — does that actually exist?"
> → `verify_place` cross-checks OpenStreetMap, Foursquare, and OpenTripMap.

---

## The 20 Tools

### 🎲 Inspiration Mode (don't know where to go)
| Tool | What it does |
|------|--------------|
| `find_destinations_by_budget` | "I have $X, where can I go?" — ranks destinations under budget with full flight+hotel calc |
| `cheap_anywhere_from` | Cheapest destinations from your origin |
| `compare_destinations` | Side-by-side cost comparison of N cities |

### 📋 Planning Mode (you know where)
| Tool | What it does |
|------|--------------|
| `search_flights` | Travelpayouts → Kiwi Tequila fallback chain |
| `search_hotels` | Hotellook → Xotelo fallback chain |
| `plan_itinerary` | Day-by-day plan with real activities and weather |
| `optimize_budget` | Cheapest flight+hotel combo, searches flexible dates |

### 🎯 Mind-Blow Differentiators
| Tool | What it does | Nobody else has this |
|------|--------------|----------------------|
| `score_destinations` | Multi-objective ranking: cost + weather + safety + events + QoL | ✅ |
| `get_travel_advisory` | Official safety + visa + health + vaccinations | ✅ |
| `get_local_events` | Concerts/shows/sports during your trip dates | ✅ |
| `get_cost_of_living` | "Your $100/day = how far?" budget guidance | ✅ |
| `best_month_to_visit` | 5-year climate analysis for any location | ✅ |
| `verify_place` | Anti-hallucination — cross-checks AI suggestions | ✅ |

### 🛠️ Enrichment (used by both modes)
`get_weather` · `convert_currency` · `get_exchange_rates` · `search_activities` · `get_destination_info` · `geocode` · `verify_flight_route`

---

## Setup (5 minutes)

### 1. Install
```bash
git clone https://github.com/YOUR_USERNAME/wander-agent.git
cd wander-agent
uv sync
```

### 2. Get free API keys
```bash
cp .env.example .env
```

**Bare minimum (works for ~80% of features):**
- [Travelpayouts](https://www.travelpayouts.com) — free signup, no approval. One token for flights + hotels.

**Full power (still all free):**
- [Kiwi Tequila](https://tequila.kiwi.com) — flight fallback
- [OpenTripMap](https://opentripmap.io) — attractions  
- [Foursquare](https://developer.foursquare.com) — place verification (200k/mo)
- [Ticketmaster](https://developer.ticketmaster.com) — local events (5k/day)

**Zero auth required:**  
weather · currency · travel advisories · cost of living · country info · geocoding · hotel fallback

### 3. Add to Claude Desktop
`~/Library/Application Support/Claude/claude_desktop_config.json`:
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

### 4. Add to Claude Code
```bash
uv run mcp install src/wander_agent/server.py
```

---

## Architecture

```
wander-agent/
├── src/wander_agent/
│   ├── server.py                  # MCP server (20 tools)
│   ├── tools/
│   │   ├── inspiration.py         # find_by_budget, anywhere_from, compare
│   │   ├── flights.py             # Travelpayouts → Kiwi fallback
│   │   ├── hotels.py              # Hotellook → Xotelo fallback
│   │   ├── itinerary.py           # Multi-day orchestrator
│   │   ├── budget.py              # Flexible-date optimizer
│   │   ├── score.py               # Multi-objective ranker
│   │   ├── advisory.py            # travelbriefing.org (no auth)
│   │   ├── events.py              # Ticketmaster Discovery
│   │   ├── cost_of_living.py      # Teleport (no auth)
│   │   ├── seasons.py             # Open-Meteo historical
│   │   ├── weather.py             # Open-Meteo forecast (no auth)
│   │   ├── currency.py            # Frankfurter (no auth)
│   │   ├── activities.py          # OpenTripMap
│   │   ├── destination.py         # REST Countries + Nominatim (no auth)
│   │   └── verify.py              # OSM + Foursquare + OTM cross-check
│   └── utils/
│       ├── http.py                # Shared async client
│       └── config.py              # API key management
├── pyproject.toml
└── .env.example
```

---

## API Sources (all free tiers)

| Source | Used For | Auth |
|--------|----------|------|
| Travelpayouts | Flights, hotels, anywhere search | Free token |
| Kiwi Tequila | Flight fallback | Free sandbox |
| Xotelo | Hotel fallback (TripAdvisor data) | **None** |
| Open-Meteo | Weather + historical climate | **None** |
| Frankfurter | Currency rates (ECB data) | **None** |
| REST Countries | Country info | **None** |
| Nominatim/OSM | Geocoding | **None** |
| travelbriefing.org | Travel advisories | **None** |
| Teleport | Cost of living, QoL scores | **None** |
| OpenTripMap | Attractions, POIs | Free key |
| Foursquare | Place verification | Free (200k/mo) |
| Ticketmaster Discovery | Local events | Free (5k/day) |

**8 of 12 sources need zero authentication.**

---

## Why this is a big deal

There are MCP servers for flights. MCP servers for hotels. But nothing unifies the full travel agent workflow with verification, inspiration mode, and differentiators like cost-of-living + events + multi-objective scoring.

This is the first **complete agentic travel toolkit** for the MCP era.

PRs welcome. License: MIT.

---

### Star the repo if Wander Agent helps you plan a trip 🌟
