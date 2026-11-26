from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

SOURCE_REGISTRY = {
    "radar_primary": {"role": "primary_flow", "provider": "Global Capital Radar/FRED", "status": "CONNECTED"},
    "radar_secondary": {"role": "shadow_flow", "provider": "ETFIQ", "status": "CONNECTED"},
    "tier1_price": {"role": "independent_price_audit", "provider": "Tier-1 audit", "status": "CONNECTED"},
    "forward_price": {"role": "reference_price", "provider": "Yahoo Chart", "status": "REFERENCE_ONLY"},
    "superlab": {"role": "independent_research_review", "provider": "Quant Superlab", "status": "EXPORT_READY"},
}

def corroborate(radar: dict[str, Any], tier: dict[str, Any]) -> dict[str, Any]:
    secondary = radar.get("secondary_flow") or {}
    comparisons = int(secondary.get("same_date_comparisons") or 0)
    observations = int(secondary.get("observed") or 0)
    issues = []
    if observations and comparisons == 0:
        issues.append("ikincil akış kaynağı bağlı, aynı tarihli karşılaştırma henüz yok")
    coverage = tier.get("price_coverage") or {}
    if coverage and not any(int(v.get("valid") or 0) > 0 for v in coverage.values()):
        issues.append("Tier-1 bağımsız fiyat kapsamı yok")
    return {"status": "PARTIAL" if issues else "CORROBORATED", "issues": issues,
            "secondary_observations": observations, "same_date_comparisons": comparisons,
            "checked_at": datetime.now(timezone.utc).isoformat(), "sources": SOURCE_REGISTRY}

def superlab_package(cells: list[dict[str, Any]], methods: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": 1, "purpose": "independent_read_only_review", "metadata": metadata,
            "methods": methods, "observations": [{"asset": c["asset"], "horizon": c["horizon"],
            "as_of": c["as_of"], "evidence": c["evidence"]} for c in cells]}
