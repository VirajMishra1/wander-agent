"""Configuration — no API keys required."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")
load_dotenv(Path.home() / ".wander-agent" / ".env")
