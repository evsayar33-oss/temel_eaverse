from methods import METHODS, compare_methods, current_signal


def test_catalog_runs_all_methods_without_promoting_snapshot():
    assert len(METHODS) == 6
    assert current_signal("flow_percentile", 80, 10, None, 0) == "LONG_CANDIDATE"
    assert current_signal("flow_then_tier1", 80, 10, 1.0, 4) == "WAIT"


def test_comparison_fails_closed_until_sample_is_sufficient():
    result = compare_methods([{"method_id": "flow_percentile", "net_excess_return": 0.02, "coverage": 1.0}])
    item = next(x for x in result if x["method_id"] == "flow_percentile")
    assert item["status"].startswith("PENDING")
    assert not item["selected"]


def test_positive_sample_still_needs_all_validation_gates():
    records = [{"method_id": "flow_percentile", "net_excess_return": 0.01, "coverage": 1.0} for _ in range(30)]
    result = compare_methods(records)
    item = next(x for x in result if x["method_id"] == "flow_percentile")
    assert not item["selected"]
    assert item["status"].startswith("PENDING")
    assert item["mean_excess_bps"] == 100.0
