#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_test(path: Path) -> list[tuple[str, str]]:
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        msgs = json.loads(line)["messages"]
        pairs.append((msgs[0]["content"], msgs[1]["content"]))
    return pairs


def first_token(text: str) -> str:
    text = text.strip()
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line.split()[0].strip(".,!?;:«»\"'")
    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mlx-community/Qwen2.5-0.5B-Instruct-4bit")
    parser.add_argument("--adapter", default=None)
    parser.add_argument("--test", default="mlx_data/test.jsonl")
    parser.add_argument("--max-tokens", type=int, default=12)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    from mlx_lm import generate, load

    kwargs = {"adapter_path": args.adapter} if args.adapter else {}
    model, tokenizer = load(args.model, **kwargs)

    pairs = load_test(Path(args.test))
    if args.limit:
        pairs = pairs[:args.limit]

    correct = 0
    errors: Counter[str] = Counter()
    records = []

    for instruction, gold in pairs:
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": instruction}], tokenize=False, add_generation_prompt=True
        )
        raw = generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens, verbose=False)
        prediction = first_token(raw)
        hit = prediction == gold
        correct += hit
        if not hit:
            errors[f"{gold} -> {prediction}"] += 1
        records.append({"instruction": instruction, "gold": gold, "prediction": prediction, "correct": hit})

    accuracy = correct / len(pairs) if pairs else 0.0
    print(f"model: {args.model}" + (f" + adapter {args.adapter}" if args.adapter else " (base)"))
    print(f"held-out accuracy: {correct}/{len(pairs)} = {accuracy:.1%}")

    if errors:
        print("\nmost common errors (gold -> predicted):")
        for pattern, count in errors.most_common(10):
            print(f"  {count:>3}  {pattern}")

    if args.out:
        Path(args.out).write_text(
            json.dumps({"model": args.model, "adapter": args.adapter,
                        "accuracy": accuracy, "n": len(pairs), "records": records},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
