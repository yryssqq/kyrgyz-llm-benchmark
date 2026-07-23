#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import morphology as m

ENTRY = re.compile(
    r'^([а-яёөүңа-я]+):([^ \t]+)\s+N-INFL\s*;(?:\s*!\s*"?([^"!]*)"?)?',
    re.IGNORECASE,
)
CYRILLIC = re.compile(r"^[а-яёөүң]+$")
RUSSIAN_ONLY = set("вфцщьъё")

ENDINGS = ["vowel", "sonorant", "voiced", "voiceless"]
HARMONIES = [("back", "unrounded"), ("back", "rounded"), ("front", "unrounded"), ("front", "rounded")]


def harmony_of(stem: str) -> tuple[str, str]:
    vowel = m._last_vowel(stem)
    return ("back" if vowel in "аоуы" else "front",
            "rounded" if vowel in "оуөү" else "unrounded")


def ending_of(stem: str) -> str:
    last = stem[-1]
    if last in m.VOWELS:
        return "vowel"
    if last in "рй":
        return "sonorant"
    if last in m.VOICELESS:
        return "voiceless"
    return "voiced"


def parse_lexc(path: Path, min_len: int, max_len: int, native_only: bool = True) -> list[tuple[str, str]]:
    entries = []
    seen = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        match = ENTRY.match(line)
        if not match:
            continue

        lemma, stem, gloss = match.group(1), match.group(2), (match.group(3) or "").strip()
        if lemma != stem or "%" in stem:
            continue
        if "FIXME" in gloss.upper() or "CHECK" in gloss.upper() or "?" in gloss:
            continue
        if not CYRILLIC.match(lemma):
            continue
        if native_only and RUSSIAN_ONLY & set(lemma):
            continue
        if not min_len <= len(lemma) <= max_len:
            continue
        if lemma in seen:
            continue
        try:
            m._last_vowel(lemma)
        except ValueError:
            continue

        seen.add(lemma)
        entries.append((lemma, gloss))
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lexc", help="path to apertium-kir.kir.lexc")
    parser.add_argument("--out", default="data/stems_apertium.txt")
    parser.add_argument("--per-cell", type=int, default=20)
    parser.add_argument("--min-len", type=int, default=3)
    parser.add_argument("--max-len", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--allow-loanwords", action="store_true")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    entries = parse_lexc(Path(args.lexc), args.min_len, args.max_len, not args.allow_loanwords)
    print(f"parsed {len(entries)} candidate nouns")

    buckets: dict[tuple, list[tuple[str, str]]] = defaultdict(list)
    for lemma, gloss in entries:
        buckets[(harmony_of(lemma), ending_of(lemma))].append((lemma, gloss))

    selected: list[tuple[str, str]] = []
    print(f"\n{'harmony':<24}" + "".join(f"{e:>12}" for e in ENDINGS))
    for harmony in HARMONIES:
        label = f"{harmony[0]} {harmony[1]}"
        row = f"{label:<24}"
        for ending in ENDINGS:
            pool = sorted(buckets[(harmony, ending)])
            take = pool if len(pool) <= args.per_cell else rng.sample(pool, args.per_cell)
            selected.extend(take)
            row += f"{len(take):>12}"
        print(row)

    selected.sort()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("# Candidate noun stems extracted from the Apertium Kyrgyz dictionary\n")
        f.write("# (apertium-kir, https://github.com/apertium/apertium-kir, GPL).\n")
        f.write("# Balanced across vowel-harmony and final-consonant classes.\n")
        f.write("# A native speaker should review and prune this list.\n#\n")
        for lemma, gloss in selected:
            f.write(f"{lemma}{('  # ' + gloss) if gloss else ''}\n")

    print(f"\nselected {len(selected)} stems -> {out}")


if __name__ == "__main__":
    main()
