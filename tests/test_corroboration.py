from corroboration import corroborate

def test_secondary_source_gap_is_visible():
    result = corroborate({"secondary_flow": {"observed": 3, "same_date_comparisons": 0}}, {})
    assert result["status"] == "PARTIAL"
    assert result["issues"]
