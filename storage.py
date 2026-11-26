from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path

from models import Cell
from methods import compare_methods


STATE_DIR = Path("state")


def persist(cells: list[Cell], metadata: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    model_records = []
    history = STATE_DIR / "forward_ledger.jsonl"
    if history.exists():
        for line in history.read_text().splitlines():
            if line.strip():
                model_records.append(json.loads(line))
    payload = {"metadata": metadata, "cells": [cell.to_dict() for cell in cells],
               "methods": compare_methods(model_records)}
    target = STATE_DIR / "latest.json"
    temporary = STATE_DIR / "latest.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    os.replace(temporary, target)
    evidence = [{"asset": c.asset, "horizon": c.horizon, "as_of": c.as_of,
                 "evidence": c.evidence} for c in cells]
    fingerprint = hashlib.sha256(
        json.dumps(evidence, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()
    ledger = STATE_DIR / "observations.jsonl"
    previous = ""
    if ledger.exists():
        lines = [line for line in ledger.read_text().splitlines() if line.strip()]
        if lines:
            previous = json.loads(lines[-1]).get("fingerprint", "")
    if fingerprint != previous:
        record = {"fingerprint": fingerprint, "metadata": metadata,
                  "cells": [cell.to_dict() for cell in cells]}
        with ledger.open("a") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def load_latest() -> dict:
    path = STATE_DIR / "latest.json"
    return json.loads(path.read_text()) if path.exists() else {"metadata": {}, "cells": []}

