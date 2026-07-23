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


def instruction(stem: str, feature: str) -> str:
    return f"«{stem}» сөзүнүн {m.FEATURE_LABELS_KY[feature]} түрүн жазыңыз."


def make_records(stem_list) -> list[dict]:
    records = []
    for stem, irregular in stem_list:
        for feature in FEATURES:
            records.append({
                "messages": [
                    {"role": "user", "content": instruction(stem, feature)},
                    {"role": "assistant", "content": m.inflect(stem, feature, irregular=irregular)},
                ]
            })
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems", default="data/stems.example.txt")
    parser.add_argument("--out", default="mlx_data")
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
    write_jsonl(out / "train.jsonl", make_records(train_stems))
    write_jsonl(out / "valid.jsonl", make_records(valid_stems))
    write_jsonl(out / "test.jsonl", make_records(test_stems))

    held_out = sorted(s for s, _ in test_stems)
    (out / "test_stems.json").write_text(json.dumps(held_out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"train stems {len(train_stems)} | valid {len(valid_stems)} | test {len(test_stems)}")
    print(f"train pairs {len(train_stems)*len(FEATURES)} | test pairs {len(test_stems)*len(FEATURES)}")
    print(f"held-out stems: {', '.join(held_out)}")
    print(f"wrote {out}/train.jsonl, valid.jsonl, test.jsonl")


if __name__ == "__main__":
    main()
