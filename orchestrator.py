from data_quality import inspect_sources
from portfolio import risk_weights
from promotion import promotion_gate
from corroboration import corroborate, superlab_package

def build_research_controls(radar, tier, cells, methods):
    cell_dicts = [c.to_dict() for c in cells]
    return {"data_quality": inspect_sources(radar, tier), "corroboration": corroborate(radar, tier),
            "risk_weights": {h: risk_weights(cell_dicts, h) for h in ("4S", "1G", "1H", "1A", "3A", "1Y")},
            "promotion": promotion_gate(methods), "superlab_package": superlab_package(cell_dicts, methods, {"source": "temel_eaverse"})}
