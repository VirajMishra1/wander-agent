"""Shared fixtures for wander-agent tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make src importable without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture()
def tmp_profile(tmp_path, monkeypatch):
    """Redirect profile store to a temporary directory."""
    import wander_agent.utils.profile_store as ps

    profile_dir = tmp_path / ".wander_agent"
    profile_dir.mkdir()
    profile_path = profile_dir / "profile.json"

    monkeypatch.setattr(ps, "_PROFILE_DIR", profile_dir)
    monkeypatch.setattr(ps, "_PROFILE_PATH", profile_path)
    return profile_path


@pytest.fixture()
def reset_http_client(monkeypatch):
    """Reset the httpx singleton between tests."""
    import wander_agent.utils.http as http_mod

    monkeypatch.setattr(http_mod, "_client", None)
    yield
    monkeypatch.setattr(http_mod, "_client", None)
