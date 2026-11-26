from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from config import RADAR_URL, TIER_URL


class SourceError(RuntimeError):
    pass


def fetch_json(url: str, timeout: int = 25) -> dict[str, Any]:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "temel-eaverse/0.1"})
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise SourceError(f"JSON object expected from {url}")
    return data


def load_sources(fixtures: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if fixtures:
        return (
            json.loads((fixtures / "radar.json").read_text()),
            json.loads((fixtures / "tier.json").read_text()),
        )
    return fetch_json(RADAR_URL), fetch_json(TIER_URL)

