from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from config import ASSETS, HORIZONS
from models import Cell
from methods import method_snapshot


def _selected(radar: dict[str, Any], symbol: str) -> dict[str, Any] | None:
    assets = ((radar.get("continuity") or {}).get("assets") or {})
    item = assets.get(symbol) or {}
    selected = item.get("selected")
    return selected if isinstance(selected, dict) else None


def _radar_data(selected: dict[str, Any] | None, horizon: str) -> dict[str, Any]:
    if selected is None:
        return {}
    if horizon == "1G":
        observation = dict(selected.get("daily_observation") or {})
        value = selected.get("daily_flow_usd")
        observation["net_usd_m"] = value / 1_000_000 if isinstance(value, (int, float)) else None
        observation.setdefault("action", selected.get("action", "BEKLE"))
        return observation
    key = HORIZONS[horizon].get("radar")
    return dict(((selected.get("horizons") or {}).get(key) or {})) if key else {}


def _tier_data(tier: dict[str, Any], tier_key: str | None, horizon: str) -> dict[str, Any]:
    hours = HORIZONS[horizon].get("tier_hours")
    if tier_key is None or hours is None:
        return {}
    aggregate = dict(((tier.get("horizons") or {}).get(hours) or {}))
    coverage = dict(((tier.get("price_coverage") or {}).get(tier_key) or {}))
    if not aggregate or not coverage:
        return {}
    valid, polls = int(coverage.get("valid", 0)), int(coverage.get("polls", 0))
    aggregate["asset_valid"] = valid
    aggregate["asset_polls"] = polls
    aggregate["coverage"] = valid / polls if polls else 0.0
    return aggregate


def _combined(radar_h: dict[str, Any], tier_h: dict[str, Any], horizon: str) -> str:
    if horizon in ("4S", "1G"):
        if not tier_h:
            return "ÖLÇÜLEMEDİ · Tier-1 eşleşmesi yok"
        if tier_h.get("verdict") != "SUFFICIENT":
            return "KANIT YETERSİZ · kısa vade gözlemi sürüyor"
        return "TIER-1 KISA VADE KANITI VAR"
    if not radar_h:
        return "ÖLÇÜLEMEDİ · temel akış yok"
    if int(radar_h.get("reference_count") or 0) < 5:
        return "KANIT YETERSİZ · tarihsel dönem az"
    return "TEMEL GÖZLEM VAR · sonuç vadesi bekleniyor"


def build_matrix(radar: dict[str, Any], tier: dict[str, Any]) -> list[Cell]:
    as_of = str(radar.get("seen_at") or tier.get("as_of_utc") or datetime.now(timezone.utc).isoformat())
    cells: list[Cell] = []
    for asset in ASSETS:
        selected = _selected(radar, asset.symbol)
        for horizon, spec in HORIZONS.items():
            rh = _radar_data(selected, horizon)
            th = _tier_data(tier, asset.tier1_key, horizon)
            flow = rh.get("net_usd_m")
            cells.append(Cell(
                asset=asset.symbol,
                label=asset.label,
                horizon=horizon,
                horizon_label=spec["label"],
                radar_status="VAR" if rh else "YOK",
                radar_action=str(rh.get("action") or "BEKLE · veri yok"),
                flow_usd_m=float(flow) if isinstance(flow, (int, float)) else None,
                flow_percentile=rh.get("magnitude_percentile"),
                flow_pressure_pct=rh.get("directional_pressure_pct"),
                reference_count=int(rh.get("reference_count") or 0),
                tier1_status=str(th.get("verdict") or ("EŞLEŞME YOK" if asset.tier1_key is None else "VADE YOK")),
                tier1_n=int(th.get("independent_by_asset_n") or 0),
                tier1_hit=th.get("model_hit"),
                combined_status=_combined(rh, th, horizon),
                as_of=as_of,
                evidence={"radar": rh, "tier1": th, "tier1_key": asset.tier1_key,
                          "methods": method_snapshot(type("Signal", (), {
                              "flow_percentile": rh.get("magnitude_percentile"),
                              "flow_pressure_pct": rh.get("directional_pressure_pct"),
                              "tier1_hit": th.get("model_hit"), "tier1_n": int(th.get("independent_by_asset_n") or 0),
                          })())},
            ))
    return cells


def summary(cells: list[Cell]) -> dict[str, Any]:
    expected = len(ASSETS) * len(HORIZONS)
    return {
        "cell_count": len(cells),
        "expected_cell_count": expected,
        "radar_observed": sum(c.radar_status == "VAR" for c in cells),
        "tier1_observed": sum(c.tier1_n > 0 for c in cells),
        "observable_cells": sum("ÖLÇÜLEMEDİ" not in c.combined_status for c in cells),
        "proven_cells": 0,
    }

