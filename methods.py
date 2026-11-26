"""Deterministic model catalogue and fail-closed comparison rules.

The current source payload is a cross-sectional snapshot. It cannot prove a
backtest result. The catalogue therefore records candidates as PENDING until
the forward ledger contains enough independent, costed observations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable


MIN_OBSERVATIONS = 30
MIN_COVERAGE = 0.80
MIN_TEST_OBSERVATIONS = 20


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    name: str
    family: str
    description: str


METHODS = (
    MethodSpec("flow_percentile", "Akış yüzdeliği", "flow", "Mutlak akışı geçmiş eş uzunluklu dönemlerle karşılaştırır."),
    MethodSpec("directional_pressure", "Yön baskısı", "flow", "Net akışı mutlak akış toplamına oranlar."),
    MethodSpec("flow_percentile_pressure", "Akış + yön baskısı", "flow", "Yüzdeliği yön baskısıyla birleştirir."),
    MethodSpec("robust_z", "Robust z-score", "normalization", "Medyan ve MAD ile geçmiş uç değerleri ölçekler."),
    MethodSpec("tier1_gate", "Tier-1 teyit kapısı", "timing", "Kısa vadeli bağımsız denetim yeterli değilse bekler."),
    MethodSpec("flow_then_tier1", "Akış + Tier-1", "combined", "Temel akış yönünü zamanlama teyidiyle birleştirir."),
)


def _num(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def current_signal(method_id: str, flow_percentile: Any, pressure: Any, tier_hit: Any, tier_n: int) -> str:
    pct, press, hit = _num(flow_percentile), _num(pressure), _num(tier_hit)
    if method_id == "flow_percentile":
        return "LONG_CANDIDATE" if pct is not None and pct >= 75 else "WAIT"
    if method_id == "directional_pressure":
        return "LONG_CANDIDATE" if press is not None and press >= 20 else "WAIT"
    if method_id == "flow_percentile_pressure":
        return "LONG_CANDIDATE" if pct is not None and pct >= 75 and press is not None and press > 0 else "WAIT"
    if method_id == "robust_z":
        return "REQUIRES_HISTORY"
    if method_id == "tier1_gate":
        return "LONG_CANDIDATE" if tier_n >= MIN_TEST_OBSERVATIONS and hit is not None and hit >= 0.55 else "WAIT"
    if method_id == "flow_then_tier1":
        return "LONG_CANDIDATE" if pct is not None and pct >= 75 and tier_n >= MIN_TEST_OBSERVATIONS and hit is not None and hit >= 0.55 else "WAIT"
    raise KeyError(method_id)


def compare_methods(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank only methods with a locked, sufficient forward sample.

    Records must contain method_id, net_excess_return, observation_id and
    coverage. No record is silently discarded for missing values.
    """
    results = []
    for spec in METHODS:
        rows = [r for r in records if r.get("method_id") == spec.method_id]
        valid = [r for r in rows if isinstance(r.get("net_excess_return"), (int, float))]
        coverage = min((float(r.get("coverage", 0)) for r in rows), default=0.0)
        if len(valid) < MIN_OBSERVATIONS or coverage < MIN_COVERAGE:
            status = "PENDING · ileri örnek yetersiz"
            mean_bps = None
        else:
            mean_bps = 10_000 * sum(float(r["net_excess_return"]) for r in valid) / len(valid)
            status = "ELENEN · maliyet sonrası avantaj yok" if mean_bps <= 0 else "ADAY · ileri doğrulama bekleniyor"
        results.append({
            **asdict(spec), "observations": len(valid), "coverage": coverage,
            "mean_excess_bps": round(mean_bps, 4) if mean_bps is not None else None,
            "status": status, "selected": False,
        })
    eligible = [r for r in results if r["status"].startswith("ADAY")]
    if eligible:
        best = max(eligible, key=lambda r: r["mean_excess_bps"])
        best["selected"] = True
    return results


def method_snapshot(cell: Any) -> list[dict[str, Any]]:
    return [{
        **asdict(spec),
        "signal": current_signal(spec.method_id, cell.flow_percentile, cell.flow_pressure_pct, cell.tier1_hit, cell.tier1_n),
        "status": "PENDING · ileri test günlüğü bekleniyor",
        "observations": 0,
        "coverage": 0.0,
        "mean_excess_bps": None,
        "selected": False,
    } for spec in METHODS]
