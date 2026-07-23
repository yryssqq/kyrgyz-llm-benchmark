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

QUESTION_TEMPLATES = {
    "plural": "«{stem}» сөзүнүн көптүк түрү кайсы?",
    "genitive": "«{stem}» сөзүнүн илик жөндөмөдөгү түрү кайсы?",
    "dative": "«{stem}» сөзүнүн барыш жөндөмөдөгү түрү кайсы?",
    "accusative": "«{stem}» сөзүнүн табыш жөндөмөдөгү түрү кайсы?",
    "locative": "«{stem}» сөзүнүн жатыш жөндөмөдөгү түрү кайсы?",
    "ablative": "«{stem}» сөзүнүн чыгыш жөндөмөдөгү түрү кайсы?",
    "poss_1sg": "«{stem}» сөзүнө «менин» таандык мүчөсүн кошсоң, кайсы туура?",
    "poss_2sg": "«{stem}» сөзүнө «сенин» таандык мүчөсүн кошсоң, кайсы туура?",
    "poss_3sg": "«{stem}» сөзүнө «анын» таандык мүчөсүн кошсоң, кайсы туура?",
}

CATEGORY = {"plural": "vowel_harmony"}
for _feature in m.CASES + m.POSSESSIVES:
    CATEGORY[_feature] = "morphology"


def build_training_pairs(stems, features):
    pairs = []
    for stem, irregular in stems:
        for feature in features:
            form = m.inflect(stem, feature, irregular=irregular)
            pairs.append({
                "stem": stem,
                "feature": feature,
                "instruction": f"«{stem}» сөзүнүн {m.FEATURE_LABELS_KY[feature]} түрүн жазыңыз.",
                "output": form,
            })
    return pairs


def build_items(stems, features, rng):
    items = []
    for stem, irregular in stems:
        for feature in features:
            correct = m.inflect(stem, feature, irregular=irregular)
            ds = m.distractors(stem, feature)
            if len(ds) < 3:
                continue
            options = ds[:3] + [correct]
            rng.shuffle(options)
            items.append({
                "item_id": f"gen_{feature}_{stem}",
                "category": CATEGORY[feature],
                "difficulty": "medium",
                "question": QUESTION_TEMPLATES[feature].format(stem=stem),
                "options": options,
                "answer_index": options.index(correct),
                "explanation": f"{feature} of {stem} is {correct}.",
            })
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems", default="data/stems.example.txt")
    parser.add_argument("--holdout", default=None)
    parser.add_argument("--features", nargs="+", default=list(FEATURES), choices=FEATURES)
    parser.add_argument("--train-out", default="data/morphology_train.jsonl")
    parser.add_argument("--items-out", default="data/morphology_items.json")
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    stems = read_stems(args.stems)

    if args.holdout:
        held = {s.strip() for s in Path(args.holdout).read_text(encoding="utf-8").split()}
        stems = [(s, irr) for s, irr in stems if s not in held]

    if args.sample:
        print("verification sample (check these forms):\n")
        flat = [(s, f, m.inflect(s, f, irregular=irr)) for s, irr in stems for f in args.features]
        for s, f, form in rng.sample(flat, min(args.sample, len(flat))):
            print(f"  {s:<10} {f:<12} -> {form}")
        return

    pairs = build_training_pairs(stems, args.features)
    items = build_items(stems, args.features, rng)

    train_path = Path(args.train_out)
    train_path.parent.mkdir(parents=True, exist_ok=True)
    with train_path.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    items_path = Path(args.items_out)
    items_path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(stems)} stems x {len(args.features)} features")
    print(f"wrote {len(pairs)} training pairs -> {train_path}")
    print(f"wrote {len(items)} MCQ items -> {items_path}")


if __name__ == "__main__":
    main()
