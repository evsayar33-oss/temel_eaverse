from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Cell:
    asset: str
    label: str
    horizon: str
    horizon_label: str
    radar_status: str
    radar_action: str
    flow_usd_m: float | None
    flow_percentile: float | None
    flow_pressure_pct: float | None
    reference_count: int
    tier1_status: str
    tier1_n: int
    tier1_hit: float | None
    combined_status: str
    as_of: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

