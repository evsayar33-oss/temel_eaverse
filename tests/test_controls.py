from data_quality import inspect_sources
from promotion import promotion_gate

def test_quality_is_explicit_when_sources_are_empty():
    result = inspect_sources({}, {})
    assert result["status"] == "DEGRADED" and result["issues"]

def test_promotion_blocks_without_one_validated_method():
    assert promotion_gate([])["status"] == "BLOCKED"
