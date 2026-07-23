#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import morphology as m
from kyrgyz_eval.stems import read_stems

FEATURES = ("plural",) + m.CASES + m.POSSESSIVES

QUESTIONS = {
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
for _f in m.CASES + m.POSSESSIVES:
    CATEGORY[_f] = "morphology"

DIFFICULTY = {"plural": "easy", "genitive": "medium", "dative": "medium",
              "accusative": "medium", "locative": "medium", "ablative": "medium",
              "poss_1sg": "hard", "poss_2sg": "hard", "poss_3sg": "hard"}


def build(stems, features, rng, target_positions):
    items = []
    position_counts: Counter = Counter()
    for stem, irregular in stems:
        for feature in features:
            correct = m.inflect(stem, feature, irregular=irregular)
            distractors = m.distractors(stem, feature)
            if len(distractors) < 3:
                continue

            want = min(range(4), key=lambda p: position_counts[p] / target_positions[p])
            options = distractors[:3]
            options.insert(want, correct)
            position_counts[want] += 1

            items.append({
                "item_id": f"gen_{feature}_{stem}",
                "category": CATEGORY[feature],
                "difficulty": DIFFICULTY[feature],
                "question": QUESTIONS[feature].format(stem=stem),
                "options": options,
                "answer_index": want,
                "explanation": f"The {feature.replace('_', ' ')} of {stem} is {correct}.",
            })
    rng.shuffle(items)
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems", default="data/stems_multi.txt")
    parser.add_argument("--out", default="data/items_generated.json")
    parser.add_argument("--limit", type=int, default=0, help="cap the number of items (0 = all)")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    stems = read_stems(args.stems)
    rng.shuffle(stems)

    target = {p: 1 for p in range(4)}
    items = build(stems, FEATURES, rng, target)
    if args.limit and len(items) > args.limit:
        items = items[:args.limit]

    Path(args.out).write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    positions = Counter(it["answer_index"] for it in items)
    categories = Counter(it["category"] for it in items)
    print(f"wrote {len(items)} items -> {args.out}")
    print(f"categories: {dict(categories)}")
    print(f"answer positions: {[positions[p] for p in range(4)]}")


if __name__ == "__main__":
    main()
