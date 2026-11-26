from __future__ import annotations

import json
from pathlib import Path


def check_state(path: str = "state/latest.json") -> tuple[bool, list[str]]:
    errors: list[str] = []
    target = Path(path)
    if not target.exists():
        return False, ["state/latest.json yok"]
    try:
        payload = json.loads(target.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"state okunamadı: {exc}"]
    cells = payload.get("cells") or []
    if len(cells) != 72:
        errors.append(f"beklenen 72 hücre yerine {len(cells)} hücre var")
    if len({(c.get("asset"), c.get("horizon")) for c in cells}) != len(cells):
        errors.append("mükerrer varlık-vade hücresi var")
    if not isinstance(payload.get("methods"), list) or not payload["methods"]:
        errors.append("yöntem karşılaştırması yok")
    return not errors, errors


if __name__ == "__main__":
    ok, errors = check_state()
    print("PASS" if ok else "FAIL")
    for error in errors:
        print(error)
    raise SystemExit(0 if ok else 1)
