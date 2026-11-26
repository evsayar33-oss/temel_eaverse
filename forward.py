"""Mature observations into costed forward results.

Yahoo's public chart endpoint is used only as a price reference. Missing or
stale prices remain pending. The ledger never fabricates an outcome.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from config import HORIZONS

STATE_DIR = Path("state")
COST_BPS = 10.0
HOURS = {"4S": 4, "1G": 24, "1H": 24 * 7, "1A": 24 * 30, "3A": 24 * 91, "1Y": 24 * 365}


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _prices(symbol: str, start: int, end: int, interval: str) -> list[tuple[int, float]]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = requests.get(url, params={"period1": start, "period2": end, "interval": interval, "events": "div,splits"}, timeout=20,
                            headers={"User-Agent": "temel-eaverse/0.1"})
    response.raise_for_status()
    result = response.json().get("chart", {}).get("result") or []
    if not result:
        return []
    timestamps = result[0].get("timestamp") or []
    closes = ((result[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    return [(int(ts), float(close)) for ts, close in zip(timestamps, closes) if close is not None and close > 0]


def _at_or_after(rows: list[tuple[int, float]], target: int) -> tuple[int, float] | None:
    return next((row for row in rows if row[0] >= target), None)


def _settled(record: dict[str, Any], now: datetime) -> list[dict[str, Any]]:
    results = []
    for cell in record.get("cells", []):
        horizon = cell.get("horizon")
        if horizon not in HOURS:
            continue
        asof = cell.get("as_of")
        try:
            start = _epoch(asof)
        except (TypeError, ValueError):
            continue
        end = start + HOURS[horizon] * 3600
        if end > int(now.timestamp()):
            continue
        interval = "1h" if horizon in ("4S", "1G") else "1d"
        window_end = end + 3 * 86400
        try:
            asset_rows = _prices(cell["asset"], start - 86400, window_end, interval)
            cash_rows = _prices("SGOV", start - 86400, window_end, interval)
        except (requests.RequestException, ValueError, KeyError):
            continue
        entry = _at_or_after(asset_rows, start)
        exit_ = _at_or_after(asset_rows, end)
        cash_entry = _at_or_after(cash_rows, start)
        cash_exit = _at_or_after(cash_rows, end)
        if not all((entry, exit_, cash_entry, cash_exit)):
            continue
        asset_return = exit_[1] / entry[1] - 1
        cash_return = cash_exit[1] / cash_entry[1] - 1
        for method in (cell.get("evidence") or {}).get("methods", []):
            method_id = method.get("method_id")
            signal = method.get("signal")
            if not method_id or signal in ("REQUIRES_HISTORY", None):
                continue
            active = signal == "LONG_CANDIDATE"
            gross = asset_return - cash_return if active else 0.0
            net = gross - COST_BPS / 10000 if active else gross
            results.append({
                "observation_id": f"{record.get('fingerprint')}:{cell['asset']}:{horizon}:{method_id}",
                "method_id": method_id, "asset": cell["asset"], "horizon": horizon,
                "signal": signal, "as_of": asof, "settled_at": now.isoformat(),
                "entry_price": entry[1], "exit_price": exit_[1], "cash_entry": cash_entry[1],
                "cash_exit": cash_exit[1], "gross_excess_return": gross,
                "cost_bps": COST_BPS if active else 0.0, "net_excess_return": net,
                "coverage": 1.0, "price_source": "YAHOO_CHART_REFERENCE",
            })
    return results


def settle_forward() -> int:
    observations = STATE_DIR / "observations.jsonl"
    ledger = STATE_DIR / "forward_ledger.jsonl"
    if not observations.exists():
        return 0
    existing = set()
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            if line.strip():
                existing.add(json.loads(line).get("observation_id"))
    added = 0
    now = datetime.now(timezone.utc)
    for line in observations.read_text().splitlines():
        if not line.strip():
            continue
        for result in _settled(json.loads(line), now):
            if result["observation_id"] in existing:
                continue
            with ledger.open("a") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            existing.add(result["observation_id"])
            added += 1
    return added
