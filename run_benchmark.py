#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kyrgyz_eval import dataset, llm_client, scorer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("run_benchmark")

FIELDS = [
    "item_id", "model", "category", "difficulty",
    "answer_index", "predicted_index", "correct", "unparseable", "raw_response",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["huggingface", "openai"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--items", default="data/items.json")
    parser.add_argument("--output", default=None)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--delay", type=float, default=0.0)
    args = parser.parse_args()

    default_env = "HF_TOKEN" if args.provider == "huggingface" else "OPENAI_API_KEY"
    api_key = os.environ.get(args.api_key_env or default_env)

    items = dataset.load_items(args.items)
    logger.info("Loaded %d items from %s", len(items), args.items)

    backend = llm_client.build_backend(args.provider, args.model, api_key=api_key)

    output_path = Path(args.output or f"results/{args.model.replace('/', '__')}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_correct = 0
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for i, item in enumerate(items, start=1):
            response = backend.answer(item)
            result = scorer.score(item, response)
            n_correct += result.correct

            writer.writerow({
                "item_id": result.item_id,
                "model": result.model,
                "category": result.category.value,
                "difficulty": result.difficulty.value,
                "answer_index": result.answer_index,
                "predicted_index": result.predicted_index,
                "correct": result.correct,
                "unparseable": result.unparseable,
                "raw_response": result.raw_response.replace("\n", " ").strip(),
            })
            f.flush()

            status = "correct" if result.correct else ("unparseable" if result.unparseable else "wrong")
            logger.info("[%d/%d] %s (%s): %s", i, len(items), item.item_id, item.category.value, status)

            if args.delay and i < len(items):
                time.sleep(args.delay)

    logger.info("Accuracy: %d/%d = %.1f%%", n_correct, len(items), 100 * n_correct / len(items))
    logger.info("Wrote %s", output_path)


if __name__ == "__main__":
    main()
