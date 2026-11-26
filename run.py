from __future__ import annotations

import argparse
from pathlib import Path

from engine import build_matrix, summary
from forward import settle_forward
from sources import load_sources
from storage import persist


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
    print(metadata)


if __name__ == "__main__":
    main()

