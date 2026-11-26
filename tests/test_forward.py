from datetime import datetime, timezone

import forward


def test_settlement_uses_cash_baseline_and_cost(monkeypatch):
    rows = {
        "SPY": [(100, 100.0), (100 + 4 * 3600, 101.0)],
        "SGOV": [(100, 100.0), (100 + 4 * 3600, 100.1)],
    }
    monkeypatch.setattr(forward, "_prices", lambda symbol, start, end, interval: rows[symbol])
    record = {"fingerprint": "x", "cells": [{
        "asset": "SPY", "horizon": "4S", "as_of": "1970-01-01T00:01:40+00:00",
        "evidence": {"methods": [{"method_id": "flow_percentile", "signal": "LONG_CANDIDATE"}]},
    }]}
    result = forward._settled(record, datetime.fromtimestamp(100 + 4 * 3600 + 1, timezone.utc))
    assert len(result) == 1
    assert round(result[0]["net_excess_return"], 6) == round(0.01 - 0.001 - 0.001, 6)
