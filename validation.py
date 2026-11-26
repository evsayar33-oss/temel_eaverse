"""Fail-closed statistical and operational gates for model selection."""
from __future__ import annotations
import math, random
from typing import Any

def _mean(v): return sum(v) / len(v) if v else 0.0
def _drawdown(values):
    wealth = peak = 1.0; worst = 0.0
    for value in values:
        wealth *= 1 + value; peak = max(peak, wealth); worst = min(worst, wealth / peak - 1)
    return worst
def bootstrap_ci(values, seed=17, samples=2000):
    if len(values) < 2: return None
    rng = random.Random(seed)
    means = sorted(_mean([rng.choice(values) for _ in values]) for _ in range(samples))
    return means[int(.025 * samples)], means[int(.975 * samples) - 1]
def validation_metrics(records: list[dict[str, Any]], total_trials: int):
    values = [float(r["net_excess_return"]) for r in records if isinstance(r.get("net_excess_return"), (int, float))]
    if not values: return {"status": "PENDING", "reason": "maliyet sonrası ileri sonuç yok", "observations": 0}
    mean = _mean(values); sd = math.sqrt(_mean([(x - mean) ** 2 for x in values])); ci = bootstrap_ci(values)
    wins = sum(x > 0 for x in values)
    p = sum(math.comb(len(values), k) for k in range(wins, len(values) + 1)) / (2 ** len(values))
    return {"status": "MEASURED", "observations": len(values), "mean_excess_bps": mean * 10000,
            "ci95_low": ci[0] if ci else None, "ci95_high": ci[1] if ci else None,
            "win_rate": wins / len(values), "sharpe_proxy": mean / sd * math.sqrt(len(values)) if sd else None,
            "max_drawdown": _drawdown(values), "sign_test_p_bonferroni": min(1, p * max(1, total_trials)),
            "regime_count": len({r.get("regime") for r in records if r.get("regime")}), "pbo_proxy": None, "dsr_proxy": None}
def validation_gate(metrics, observations: int, coverage: float):
    failures = []
    if observations < 30: failures.append("en az 30 bağımsız ileri sonuç gerekli")
    if coverage < .80: failures.append("veri kapsamı %80 altında")
    if metrics.get("ci95_low") is None or metrics["ci95_low"] <= 0: failures.append("%95 güven aralığı pozitif değil")
    if metrics.get("sign_test_p_bonferroni", 1) > .05: failures.append("çoklu test düzeltmesi sonrası anlamlılık yok")
    if metrics.get("max_drawdown", -1) < -.20: failures.append("maksimum düşüş sınırı aşıldı")
    if metrics.get("regime_count", 0) < 3: failures.append("en az üç piyasa rejimi görülmedi")
    return ("VALIDATED", []) if not failures else ("PENDING", failures)
