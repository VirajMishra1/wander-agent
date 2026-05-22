"""Configuration and API key management."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")
load_dotenv(Path.home() / ".wander-agent" / ".env")


def get_key(name: str) -> str | None:
    return os.environ.get(name)


def require_key(name: str) -> str:
    val = get_key(name)
    if not val:
        raise ValueError(
            f"Missing API key: {name}. Set it in .env or as an env var. See .env.example."
        )
    return val


# Hotels: Travelpayouts Hotellook. Free, no approval.
TRAVELPAYOUTS_TOKEN = get_key("TRAVELPAYOUTS_TOKEN")
TRAVELPAYOUTS_MARKER = get_key("TRAVELPAYOUTS_MARKER")  # optional affiliate id

# Activities + verification
OPENTRIPMAP_KEY = get_key("OPENTRIPMAP_API_KEY")
FOURSQUARE_KEY = get_key("FOURSQUARE_API_KEY")
LOCATIONIQ_KEY = get_key("LOCATIONIQ_API_KEY")

# Local events
TICKETMASTER_KEY = get_key("TICKETMASTER_API_KEY")
