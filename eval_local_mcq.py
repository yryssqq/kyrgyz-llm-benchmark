#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import dataset, scorer
from kyrgyz_eval.llm_client import build_prompt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--items", default="data/items_generated.json")
    parser.add_argument("--max-tokens", type=int, default=8)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    from mlx_lm import generate, load

    kwargs = {"adapter_path": args.adapter} if args.adapter else {}
    model, tokenizer = load(args.model, **kwargs)

    items = dataset.load_items(args.items)
    correct = 0
    records = []
    for item in items:
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": build_prompt(item)}], tokenize=False, add_generation_prompt=True
        )
        raw = generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens, verbose=False)
        predicted = scorer.parse_answer(raw, item)
        hit = predicted == item.answer_index
        correct += hit
        records.append({"item_id": item.item_id, "predicted": predicted,
                        "answer": item.answer_index, "correct": hit})

    accuracy = correct / len(items) if items else 0.0
    print(f"model: {args.model}" + (f" + adapter {args.adapter}" if args.adapter else " (base)"))
    print(f"MCQ accuracy: {correct}/{len(items)} = {accuracy:.1%}")

    if args.out:
        Path(args.out).write_text(
            json.dumps({"model": args.model, "adapter": args.adapter,
                        "accuracy": accuracy, "n": len(items), "records": records},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
