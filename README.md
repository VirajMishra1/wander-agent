# Wander Agent

An MCP server that turns Claude into a travel agent that does things Expedia and Skyscanner can't legally do.

**27 tools. Zero API keys required.** Install once, point Claude Desktop or Claude Code at it, and ask the questions OTAs refuse to answer.

---

## What this kills

| Question | Skyscanner / Kayak / Expedia | Wander Agent |
|---|---|---|
| "Cheapest hidden-city ticket NYC→LAX" | Contractually forbidden. They can't show these. | `find_skiplagged_fares` — pulls from Skiplagged, returns hidden-city itineraries with carry-on warnings |
| "3 of us in NYC, London, Tokyo — cheapest place we can all meet next month" | No multi-origin search. Search one traveler at a time. | `multi_origin_meetup` — sums round-trip costs across all travelers for ~40 destinations |
| "Where can I see the northern lights cheapest in next 60 days?" | Static calendar. No KP-index awareness. | `find_aurora_destinations` — NOAA aurora forecast + flight prices to aurora-zone airports |
| "Find me a mistake fare from Houston anywhere this month" | Doesn't track these. | `find_mistake_fares` — RSS scraping of Secret Flying and The Flight Deal |
| "I'm Indian passport — what countries can I visit visa-free or with e-visa?" | No visa filter. | `visa_free_destinations` + `check_visa_requirement` — curated visa data, counters the viral Mery Caldass ESTA fail |
| "Is the restaurant Claude suggested actually real?" | Doesn't verify. | `verify_place` — cross-checks Wikidata + Open-Meteo + Foursquare with strict name matching |
| "Compare cost of living of Lisbon vs Tokyo vs Reykjavik in EUR" | Doesn't surface this. | `get_cost_of_living` — three tiers (budget/mid/luxury), currency-converted |
| "What countries are at travel advisory level 4 right now?" | Doesn't track. | `list_advisories_by_level` — live US State Dept RSS |

---

## The 10 viral demo prompts

Try these inside Claude Desktop or Claude Code after install. Screenshot-ready.

1. **"I'm in NYC, my partner's in London, my friend is in Tokyo. Cheapest weekend the three of us can meet next month."**  
   → `multi_origin_meetup` loops 40 destinations, sums per-traveler round-trip costs.

2. **"Find me a flight to LAX from JFK but cheaper using hidden-city ticketing."**  
   → `find_skiplagged_fares` returns hidden-city itineraries with carry-on warnings.

3. **"Where can I see northern lights for under $1500 from NYC in the next 60 days?"**  
   → `find_aurora_destinations` combines NOAA KP forecast with flight prices to Tromso, Reykjavik, Fairbanks.

4. **"I have an Indian passport. List every country I can visit with e-visa or visa-on-arrival under $400 from Bangalore."**  
   → `visa_free_destinations` filtered + `cheap_anywhere_from`. Nothing else does passport-aware filtering.

5. **"Plan a 5-day Tokyo trip in May. Use real attractions. Tell me what events are happening."**  
   → `plan_itinerary` orchestrates weather + activities + country info. `get_local_events` adds concerts.

6. **"Paris vs Rome vs Barcelona for next month. Real flight and hotel costs, ranked."**  
   → `compare_destinations` — side-by-side total cost comparison.

7. **"I have $1500 for August. Surprise me with the best destinations from JFK."**  
   → `find_destinations_by_budget` calculates flight + hotel for 40 destinations under budget.

8. **"Recent mistake fares from Los Angeles."**  
   → `find_mistake_fares` pulls live RSS from Secret Flying.

9. **"Is Egypt safe to travel right now? What vaccinations?"**  
   → `get_travel_advisory` — live US State Department RSS, levels 1-4 with summaries.

10. **"You said to eat at 'Le Cinq' in Paris. Is that real?"**  
    → `verify_place` cross-checks four sources, returns confidence.

---

## All 27 tools

### Killer differentiators (no other OTA / agent has these)
- `find_skiplagged_fares` — hidden-city ticketing
- `multi_origin_meetup` — N-traveler convergence optimization
- `find_aurora_destinations` — NOAA forecast + flight prices, reverse natural-phenomenon search
- `find_mistake_fares` — Secret Flying + Flight Deal RSS
- `check_visa_requirement` — passport-aware visa lookup (curated dataset)
- `visa_free_destinations` — list all destinations a passport can enter
- `score_destinations` — multi-objective ranker (cost + weather + safety + events + value)
- `verify_place` — anti-hallucination cross-check (Wikidata + Open-Meteo + Foursquare + OpenTripMap)
- `verify_flight_route` — confirm route exists via probe search
- `best_month_to_visit` — 5-year climate analysis
- `get_cost_of_living` — curated 100-city dataset, three budget tiers
- `get_travel_advisory` + `list_advisories_by_level` — live US State Dept RSS

### Core search
- `search_flights` — Google Flights via `fast_flights` library
- `search_hotels` — Google Hotels names + Booking/Google/Airbnb deeplinks
- `plan_itinerary` — multi-day plan with real activities and weather
- `optimize_budget` — flexible-date search for cheapest flight + hotel combo

### Inspiration (don't know where yet)
- `find_destinations_by_budget` — "I have $X, where can I go?"
- `cheap_anywhere_from` — cheapest from origin, regional filter
- `compare_destinations` — side-by-side cost comparison

### Enrichment
- `get_weather` — live forecast or climatology for far-future dates
- `convert_currency` + `get_exchange_rates` — Frankfurter, ECB data
- `search_activities` — OpenTripMap (requires free key)
- `get_local_events` — Ticketmaster Discovery (requires free key)
- `get_destination_info` — country metadata
- `geocode` — city/place → coordinates

---

## Setup

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
uv sync --no-editable
```

Add to Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "wander-agent": {
      "command": "uv",
      "args": ["run", "--no-editable", "--directory", "/absolute/path/to/wander-agent", "wander-agent"]
    }
  }
}
```

Restart Claude. The 27 tools appear.

For Claude Code: `uv run --no-editable mcp install src/wander_agent/server.py`.

**No `.env` required for the minimum-functional agent.** Optional keys upgrade specific features:

| Key | Unlocks | Free? |
|---|---|---|
| `OPENTRIPMAP_API_KEY` | Richer attraction descriptions | Yes, no approval |
| `TICKETMASTER_API_KEY` | Live concert/event search | Yes, 5k/day |
| `FOURSQUARE_API_KEY` | Third place-verification source | Yes, 200k/month |
| `TRAVELPAYOUTS_TOKEN` | In-tool live hotel prices (otherwise click-through) | Yes, but UI is hard |

---

## Data sources (free, mostly no auth)

| Source | Used for | Auth |
|---|---|---|
| Google Flights (via `fast_flights`) | Flight search, route probe | none |
| Google Hotels (via `fast_hotels`) | Hotel names | none |
| Booking.com / Airbnb / Google Hotels deeplinks | Live hotel prices via click-through | none |
| Skiplagged | Hidden-city ticketing | none |
| Open-Meteo | Weather forecast + 5-year historical | none |
| Open-Meteo Geocoding | City → coordinates with population | none |
| Frankfurter | Currency rates from ECB | none |
| REST Countries | Country metadata | none |
| Wikidata SPARQL | Place verification | none |
| US State Department RSS | Travel advisories | none |
| Secret Flying / Flight Deal RSS | Mistake fares | none |
| NOAA SWPC | Aurora KP-index forecast | none |
| OpenTripMap | Attractions / POIs | free key |
| Foursquare | Place verification (optional) | free key |
| Ticketmaster Discovery | Events | free key |
| Travelpayouts Hotellook | Live hotel prices (optional) | free token |
| Curated cost-of-living dataset | 100-city traveler budgets | none (embedded) |
| Curated visa dataset | Visa requirements per passport | none (embedded) |
| Curated airport list | Inspiration loop targets | none (embedded) |

**18 sources. 15 require zero authentication.**

---

## Architecture

```
src/wander_agent/
├── server.py                  # FastMCP entry. Registers 27 tools.
├── tools/
│   ├── flights.py             # Google Flights via fast_flights
│   ├── hotels.py              # Names + deeplinks + web-search hints
│   ├── inspiration.py         # find_by_budget, cheap_anywhere, compare
│   ├── budget.py              # Flexible-date optimizer
│   ├── itinerary.py           # Multi-day orchestrator
│   ├── score.py               # Multi-objective ranker
│   ├── skiplagged.py          # Hidden-city ticketing
│   ├── meetup.py              # N-traveler convergence
│   ├── aurora.py              # KP-forecast + flight prices
│   ├── mistake_fares.py       # Secret Flying + Flight Deal RSS
│   ├── visa.py                # Passport visa requirements
│   ├── advisory.py            # US State Dept RSS parser
│   ├── events.py              # Ticketmaster Discovery
│   ├── cost_of_living.py      # Curated dataset + currency
│   ├── seasons.py             # 5-year climate analysis
│   ├── weather.py             # Forecast or climatology
│   ├── currency.py            # Frankfurter
│   ├── activities.py          # OpenTripMap
│   ├── destination.py         # REST Countries + Open-Meteo geocoding
│   └── verify.py              # 4-source anti-hallucination check
└── utils/
    ├── http.py                # Shared async client
    ├── config.py              # API key management
    ├── cost_data.py           # Embedded cost-of-living dataset
    └── airport_data.py        # Curated destinations + IATA↔city
```

---

## Design choices worth knowing

**Composes with Claude's web search.** Most tool outputs include a `suggest_web_search` field with concrete query suggestions. The server `instructions` field tells Claude when to use Wander Agent tools vs its own web search. Structured queries → tools. Live deals / reviews / recent news → web search.

**Internal retry instead of prompt-level retry.** `fast_flights` occasionally serves stripped HTML. The flight tool retries across fetch modes (`common`, `fallback`) inside the function so the LLM never sees the failure.

**Climatology for far-future dates.** Open-Meteo forecasts cover 16 days. Beyond that, the weather tool pulls 5 years of historical data for the same calendar dates and averages it.

**Cached advisories.** US State Dept RSS is fetched once per process and cached 60 minutes.

**Strict name matching in verify_place.** Earlier versions accepted "Le Cinquin" as a match for "Le Cinq". Now requires exact match or whole-string containment with reasonable length ratio.

**IATA ↔ city translation for everything.** Tools accept either form. Internal helpers convert as needed for flight (IATA) vs hotel (city name) lookups.

**Anti-hallucination by composition.** A "high confidence" verification means at least two of Wikidata, Open-Meteo geocoding, Foursquare, and OpenTripMap independently confirmed the place exists and the name matched strictly.

---

## Honest limitations

- **`fast_flights` and `fast_hotels` scrape Google.** Google can change HTML at any time. Tools retry across fetch modes; if everything fails the LLM can fall back to web search.
- **Hotel prices are unreliable to scrape** (Google JS-renders them). Tool returns real hotel names + deeplinks. Setting `TRAVELPAYOUTS_TOKEN` adds live in-tool prices as a bonus.
- **Skiplagged fares are real but legally risky.** Tool returns explicit warnings: carry-on only, one-way only, airline policies vary. Use at your own risk.
- **Visa data is a curated snapshot.** Policies change. Tool always advises verifying with the official embassy before booking.
- **Mistake fares are time-sensitive.** Often gone within hours of posting. Tool surfaces the signal; user has to act fast.
- **State Department advisories reflect US perspective.** Other passports should also consult their own government's guidance.

---

## License

MIT. PRs welcome.
