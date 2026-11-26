from __future__ import annotations

import argparse
from pathlib import Path

from engine import build_matrix, summary
from forward import settle_forward
from sources import load_sources
from storage import persist
from orchestrator import build_research_controls
from storage import load_latest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path)
    args = parser.parse_args()
    radar, tier = load_sources(args.fixtures)
    cells = build_matrix(radar, tier)
    settled = settle_forward()
    metadata = summary(cells) | {"source_as_of": max(cell.as_of for cell in cells)}
    metadata["forward_results_added"] = settled
    persist(cells, metadata)
    latest = load_latest()
    latest["controls"] = build_research_controls(radar, tier, cells, latest.get("methods", []))
    import json
    Path("state/latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2) + "\n")
    print(metadata)


if __name__ == "__main__":
    main()

