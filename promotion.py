from __future__ import annotations
from typing import Any

def promotion_gate(methods: list[dict[str, Any]]) -> dict[str, Any]:
    validated = [m for m in methods if m.get("status", "").startswith("VALIDATED")]
    if len(validated) != 1: return {"status": "BLOCKED", "reason": "tam olarak bir doğrulanmış yöntem yok", "method_id": None}
    return {"status": "REVIEW_REQUIRED", "reason": "bağımsız inceleme ve manuel yayın onayı gerekli", "method_id": validated[0].get("method_id")}
