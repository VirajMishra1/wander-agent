# Contributing to Wander Agent

Thanks for helping make AI travel planning better. Contributions of every size are welcome — adding a single city or language is a real, useful PR.

## Quick start

```bash
git clone https://github.com/VirajMishra1/wander-agent.git
cd wander-agent
pip install -e ".[dev]"
pytest            # all tests should pass before you start
```

## Ways to contribute

- **Add data** — a city to the cost-of-living table, a language to the phrasebook, a hub airport to the stopover guide, a credit card to the points engine. These are the best first PRs.
- **Fix a bug** — see open issues labeled `bug`.
- **Improve a tool** — better fallbacks, more sources, clearer output.
- **Docs** — recipes, examples, typo fixes.

Look for issues labeled [`good first issue`](https://github.com/VirajMishra1/wander-agent/labels/good%20first%20issue) to get started.

## Pull request checklist

1. Branch from `main`.
2. Keep the change focused — one logical change per PR.
3. `pytest` passes locally (CI runs Python 3.10–3.12 + a 66-tool gate).
4. Match the existing code style — no new dependencies unless discussed.
5. Every tool must still work **without API keys** (fallbacks required).
6. Describe what changed and why in the PR body.

## Data-quality rules

- Cite a source for any factual data (visa rules, costs, advisories).
- Mark freshness honestly — static snapshots are fine, just label them.
- Don't over-claim. Hidden-city / split-ticket info is about transparency, not guaranteed bookings.

## Questions

Open a [discussion](https://github.com/VirajMishra1/wander-agent/discussions) or an issue. We respond fast.
