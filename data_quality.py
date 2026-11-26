from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

def inspect_sources(radar: dict[str, Any], tier: dict[str, Any]) -> dict[str, Any]:
    issues = []
    for name, value in (("radar", radar.get("seen_at")), ("tier1", tier.get("as_of_utc"))):
        if not value: issues.append(f"{name}: zaman damgası yok")
        else:
            try: datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            except ValueError: issues.append(f"{name}: zaman damgası geçersiz")
    assets = ((radar.get("continuity") or {}).get("assets") or {})
    if not assets: issues.append("radar: varlık akışı yok")
    unavailable = [key for key, row in (tier.get("price_coverage") or {}).items() if not row.get("valid")]
    return {"status": "PASS" if not issues else "DEGRADED", "issues": issues,
            "tier1_unavailable_assets": unavailable, "checked_at": datetime.now(timezone.utc).isoformat()}
