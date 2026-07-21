from __future__ import annotations

import re

from .models import Item, Response, Result

DIGIT_RE = re.compile(r"\b([1-4])\b")


def parse_answer(raw_response: str, item: Item) -> int | None:
    if not raw_response or not raw_response.strip():
        return None

    text = raw_response.strip()

    match = DIGIT_RE.search(text)
    if match:
        return int(match.group(1)) - 1

    normalized = " ".join(text.lower().split())
    for index, option in enumerate(item.options):
        if normalized == " ".join(str(option).lower().split()):
            return index

    return None


def score(item: Item, response: Response) -> Result:
    predicted = response.predicted_index
    return Result(
        item_id=item.item_id,
        model=response.model,
        category=item.category,
        difficulty=item.difficulty,
        answer_index=item.answer_index,
        predicted_index=predicted,
        correct=predicted == item.answer_index,
        unparseable=predicted is None,
        raw_response=response.raw_response,
    )
