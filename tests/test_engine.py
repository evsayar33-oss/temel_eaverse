from config import ASSETS, HORIZONS
from engine import build_matrix, summary


def fixtures():
    radar = {
        "seen_at": "2026-11-26T00:00:00+00:00",
        "continuity": {"assets": {"SPY": {"selected": {
            "daily_flow_usd": 2_000_000,
            "daily_observation": {"magnitude_percentile": 80, "reference_count": 52},
            "horizons": {"1H": {"net_usd_m": 10, "reference_count": 52, "action": "ALIM ADAYI"}},
        }}}},
    }
    tier = {
        "horizons": {"4": {"verdict": "INSUFFICIENT", "independent_by_asset_n": 4, "model_hit": 1.0}},
        "price_coverage": {"SPX": {"valid": 7, "polls": 37}},
    }
    return radar, tier


def test_builds_every_asset_horizon_cell():
    radar, tier = fixtures()
    cells = build_matrix(radar, tier)
    assert len(cells) == len(ASSETS) * len(HORIZONS) == 72
    assert summary(cells)["expected_cell_count"] == 72
    assert summary(cells)["proven_cells"] == 0


def test_does_not_promote_insufficient_tier_evidence():
    radar, tier = fixtures()
    cell = next(c for c in build_matrix(radar, tier) if c.asset == "SPY" and c.horizon == "4S")
    assert cell.tier1_n == 4
    assert "KANIT YETERSİZ" in cell.combined_status


def test_long_horizon_uses_radar_observation():
    radar, tier = fixtures()
    cell = next(c for c in build_matrix(radar, tier) if c.asset == "SPY" and c.horizon == "1H")
    assert cell.flow_usd_m == 10
    assert cell.reference_count == 52

