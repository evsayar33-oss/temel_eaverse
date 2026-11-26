from data_quality import inspect_sources
from portfolio import risk_weights
from promotion import promotion_gate

def build_research_controls(radar, tier, cells, methods):
    return {"data_quality": inspect_sources(radar, tier), "risk_weights": {h: risk_weights([c.to_dict() for c in cells], h) for h in ("4S", "1G", "1H", "1A", "3A", "1Y")}, "promotion": promotion_gate(methods)}
