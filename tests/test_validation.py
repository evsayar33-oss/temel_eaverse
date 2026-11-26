from validation import bootstrap_ci, validation_gate, validation_metrics

def test_missing_results_fail_closed():
    metrics = validation_metrics([], 6)
    assert metrics["status"] == "PENDING"
    assert validation_gate(metrics, 0, 0.0)[0] == "PENDING"

def test_positive_short_sample_is_not_validated():
    records = [{"net_excess_return": 0.01, "regime": "risk_on"} for _ in range(10)]
    status, failures = validation_gate(validation_metrics(records, 6), 10, 1.0)
    assert status == "PENDING" and failures

def test_bootstrap_is_reproducible():
    assert bootstrap_ci([0.01, 0.02, -0.01], seed=1) == bootstrap_ci([0.01, 0.02, -0.01], seed=1)
