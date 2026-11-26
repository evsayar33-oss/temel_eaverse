from __future__ import annotations
from typing import Any

def risk_weights(cells: list[dict[str, Any]], horizon: str) -> list[dict[str, Any]]:
    eligible = [c for c in cells if c.get("horizon") == horizon and c.get("asset") != "SGOV" and c.get("radar_status") == "VAR" and "ÖLÇÜLEMEDİ" not in c.get("combined_status", "")]
    if not eligible: return []
    weight = 1.0 / len(eligible)
    return [{"asset": c["asset"], "horizon": horizon, "weight": weight, "reason": "eşit başlangıç payı"} for c in eligible]
