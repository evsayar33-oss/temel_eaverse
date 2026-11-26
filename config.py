from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    symbol: str
    label: str
    tier1_key: str | None
    market: str


ASSETS = (
    Asset("SPY", "S&P 500", "SPX", "US_ETF"),
    Asset("QQQ", "Nasdaq-100", "NQ", "US_ETF"),
    Asset("DIA", "Dow Jones", None, "US_ETF"),
    Asset("IWM", "Russell 2000", None, "US_ETF"),
    Asset("SGOV", "ABD 0–3 ay bono", None, "US_ETF"),
    Asset("SHY", "ABD 1–3 yıl tahvil", None, "US_ETF"),
    Asset("GLD", "Altın", "XAU", "US_ETF"),
    Asset("SLV", "Gümüş", "XAG", "US_ETF"),
    Asset("CPER", "Bakır", None, "US_ETF"),
    Asset("USO", "WTI petrol", None, "US_ETF"),
    Asset("IBIT", "Bitcoin ETF", "BTC", "US_ETF"),
    Asset("ETHA", "Ether ETF", "ETH", "US_ETF"),
)

HORIZONS = {
    "4S": {"label": "4 saat", "tier_hours": "4"},
    "1G": {"label": "1 gün", "tier_hours": "24"},
    "1H": {"label": "1 hafta", "radar": "1H"},
    "1A": {"label": "1 ay", "radar": "1A"},
    "3A": {"label": "3 ay", "radar": "3A"},
    "1Y": {"label": "1 yıl", "radar": "1Y"},
}

RADAR_URL = (
    "https://raw.githubusercontent.com/evsayar33-oss/global_capital_radar/"
    "main/history/rotation/latest.json"
)
TIER_URL = (
    "https://raw.githubusercontent.com/evsayar33-oss/tier1_quant_terminal/"
    "audit/30d-evidence/independent_audit/summary.json"
)

