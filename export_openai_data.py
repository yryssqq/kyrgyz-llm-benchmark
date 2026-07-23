#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import morphology as m
from kyrgyz_eval.stems import read_stems

FEATURES = ("plural",) + m.CASES + m.POSSESSIVES

SYSTEM = "Сен кыргыз тилинин морфологиясын билесиң. Берилген сөздүн суралган формасын бир сөз менен жаз."


def instruction(stem: str, feature: str) -> str:
    return f"«{stem}» сөзүнүн {m.FEATURE_LABELS_KY[feature]} түрүн жазыңыз."


def records(stem_list):
    rows = []
    for stem, irregular in stem_list:
        for feature in FEATURES:
            rows.append({"messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": instruction(stem, feature)},
                {"role": "assistant", "content": m.inflect(stem, feature, irregular=irregular)},
            ]})
    return rows


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems", default="data/stems_multi.txt")
    parser.add_argument("--out", default="openai_data")
    parser.add_argument("--test-frac", type=float, default=0.2)
    parser.add_argument("--valid-frac", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    stems = read_stems(args.stems)
    rng.shuffle(stems)

    n_test = max(1, int(len(stems) * args.test_frac))
    n_valid = max(1, int(len(stems) * args.valid_frac))
    test_stems = stems[:n_test]
    valid_stems = stems[n_test:n_test + n_valid]
    train_stems = stems[n_test + n_valid:]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "train.jsonl", records(train_stems))
    write_jsonl(out / "valid.jsonl", records(valid_stems))
    write_jsonl(out / "test.jsonl", records(test_stems))
    (out / "test_stems.json").write_text(
        json.dumps(sorted(s for s, _ in test_stems), ensure_ascii=False, indent=2), encoding="utf-8")

    n_train = len(train_stems) * len(FEATURES)
    print(f"train stems {len(train_stems)} | valid {len(valid_stems)} | test {len(test_stems)}")
    print(f"train pairs {n_train} | test pairs {len(test_stems)*len(FEATURES)}")
    print(f"wrote {out}/train.jsonl, valid.jsonl, test.jsonl")

    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        toks = sum(len(enc.encode(msg["content"]))
                   for row in records(train_stems) for msg in row["messages"])
        toks += n_train * 6
        print(f"\napprox training tokens/epoch: {toks:,}")
        for epochs in (3, 4):
            print(f"  {epochs} epochs, gpt-4o-mini @ $3/1M:  ${toks*epochs/1e6*3:.2f}")
            print(f"  {epochs} epochs, gpt-4o     @ $25/1M: ${toks*epochs/1e6*25:.2f}")
    except ImportError:
        print("\n(install tiktoken for a token/cost estimate)")


if __name__ == "__main__":
    main()
