from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .models import Category, Difficulty, Item

REQUIRED_FIELDS = {"item_id", "category", "difficulty", "question", "options", "answer_index"}
OPTIONS_PER_ITEM = 4


class DatasetError(ValueError):
    pass


def load_items(path: str | Path) -> list[Item]:
    path = Path(path)
    if not path.exists():
        raise DatasetError(f"Item file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise DatasetError("Item file must contain a JSON list")

    items: list[Item] = []
    seen: set[str] = set()
    for i, entry in enumerate(raw):
        missing = REQUIRED_FIELDS - entry.keys()
        if missing:
            raise DatasetError(f"Item at index {i} is missing fields: {sorted(missing)}")

        item_id = entry["item_id"]
        if item_id in seen:
            raise DatasetError(f"Duplicate item_id: {item_id}")
        seen.add(item_id)

        try:
            category = Category(entry["category"])
        except ValueError as exc:
            raise DatasetError(f"{item_id}: unknown category '{entry['category']}'") from exc

        try:
            difficulty = Difficulty(entry["difficulty"])
        except ValueError as exc:
            raise DatasetError(f"{item_id}: unknown difficulty '{entry['difficulty']}'") from exc

        options = entry["options"]
        if len(options) != OPTIONS_PER_ITEM:
            raise DatasetError(f"{item_id}: expected {OPTIONS_PER_ITEM} options, got {len(options)}")
        if len(set(options)) != len(options):
            raise DatasetError(f"{item_id}: options must be distinct")
        if any(not str(o).strip() for o in options):
            raise DatasetError(f"{item_id}: options must not be blank")
        if not str(entry["question"]).strip():
            raise DatasetError(f"{item_id}: question must not be blank")

        answer_index = entry["answer_index"]
        if not isinstance(answer_index, int) or not 0 <= answer_index < OPTIONS_PER_ITEM:
            raise DatasetError(f"{item_id}: answer_index must be an int in 0..{OPTIONS_PER_ITEM - 1}")

        items.append(
            Item(
                item_id=item_id,
                category=category,
                difficulty=difficulty,
                question=entry["question"],
                options=options,
                answer_index=answer_index,
                explanation=entry.get("explanation", ""),
            )
        )
    return items


def answer_position_bias(items: list[Item]) -> dict[int, int]:
    return dict(sorted(Counter(item.answer_index for item in items).items()))


def category_counts(items: list[Item]) -> dict[str, int]:
    return dict(sorted(Counter(item.category.value for item in items).items()))
