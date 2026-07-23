#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import morphology as m

HARMONY_LABELS = {
    ("back", "unrounded"): "back unrounded (а, ы)",
    ("back", "rounded"): "back rounded (о, у)",
    ("front", "unrounded"): "front unrounded (е, и)",
    ("front", "rounded"): "front rounded (ө, ү)",
}

ENDING_LABELS = ["vowel", "sonorant (р, й)", "voiced", "voiceless"]

TARGET_PER_CELL = 8


def harmony_of(stem: str) -> tuple[str, str]:
    vowel = m._last_vowel(stem)
    backness = "back" if vowel in "аоуы" else "front"
    rounding = "rounded" if vowel in "оуөү" else "unrounded"
    return backness, rounding


def ending_of(stem: str) -> str:
    last = stem[-1]
    if last in m.VOWELS:
        return "vowel"
    if last in "рй":
        return "sonorant (р, й)"
    if last in m.VOICELESS:
        return "voiceless"
    return "voiced"


def read_stems(path: Path) -> list[str]:
    stems = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        stems.append(line.split("|", 1)[0].strip())
    return stems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/stems.txt")
    parser.add_argument("--target", type=int, default=TARGET_PER_CELL)
    parser.add_argument("--show", action="store_true", help="list the stems in each cell")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"not found: {path}")
        raise SystemExit(1)

    stems = read_stems(path)

    seen: set[str] = set()
    duplicates: list[str] = []
    for stem in stems:
        if stem in seen:
            duplicates.append(stem)
        seen.add(stem)

    grid: dict[tuple, list[str]] = defaultdict(list)
    bad: list[str] = []

    for stem in stems:
        try:
            grid[(harmony_of(stem), ending_of(stem))].append(stem)
        except (ValueError, KeyError):
            bad.append(stem)

    print(f"{len(stems)} stems in {path}\n")

    header = f"{'harmony class':<26}" + "".join(f"{e:>18}" for e in ENDING_LABELS)
    print(header)
    print("-" * len(header))

    gaps = []
    for key, label in HARMONY_LABELS.items():
        row = f"{label:<26}"
        for ending in ENDING_LABELS:
            cell = grid[(key, ending)]
            n = len(cell)
            row += f"{n:>18}"
            if n < args.target:
                gaps.append((label, ending, n))
        print(row)

    total_cells = len(HARMONY_LABELS) * len(ENDING_LABELS)
    filled = sum(1 for k in HARMONY_LABELS for e in ENDING_LABELS if len(grid[(k, e)]) >= args.target)
    print(f"\ncells at target ({args.target}+): {filled}/{total_cells}")

    if duplicates:
        print(f"\nduplicates: {', '.join(sorted(set(duplicates)))}")

    if bad:
        print(f"\nunparsable stems (no vowel?): {bad}")

    if gaps:
        print(f"\nunder target, add more of these:")
        for label, ending, n in sorted(gaps, key=lambda g: g[2]):
            print(f"  {label:<26} ending in {ending:<18} has {n}")

    if args.show:
        print()
        for key, label in HARMONY_LABELS.items():
            for ending in ENDING_LABELS:
                cell = grid[(key, ending)]
                if cell:
                    print(f"{label} / {ending}: {', '.join(sorted(cell))}")


if __name__ == "__main__":
    main()
