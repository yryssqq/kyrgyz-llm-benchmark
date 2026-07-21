#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import dataset

TARGET_PER_CATEGORY = 8


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/items.json")
    args = parser.parse_args()

    try:
        items = dataset.load_items(args.path)
    except dataset.DatasetError as exc:
        print(f"INVALID: {exc}")
        raise SystemExit(1)

    print(f"OK: {len(items)} items loaded from {args.path}\n")

    print("items per category:")
    counts = dataset.category_counts(items)
    for category in [c.value for c in dataset.Category]:
        n = counts.get(category, 0)
        flag = "" if n >= TARGET_PER_CATEGORY else f"  <- below target of {TARGET_PER_CATEGORY}"
        print(f"  {category:<20} {n}{flag}")

    print("\nanswer position distribution:")
    bias = dataset.answer_position_bias(items)
    total = len(items)
    for position in range(4):
        n = bias.get(position, 0)
        share = n / total if total else 0
        print(f"  option {position + 1}: {n:>3}  ({share:.0%})")

    shares = [bias.get(p, 0) / total for p in range(4)] if total else []
    if shares and (max(shares) > 0.40 or min(shares) < 0.10):
        print("\nWARNING: answers are unevenly distributed across positions.")
        print("A model that always guesses one position would score above chance.")


if __name__ == "__main__":
    main()
