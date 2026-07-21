from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    VOWEL_HARMONY = "vowel_harmony"
    MORPHOLOGY = "morphology"
    SYNTAX = "syntax"
    LEXICAL_SEMANTICS = "lexical_semantics"
    IDIOMS = "idioms"
    CULTURE = "culture"
    TRANSLATION = "translation"
    ORTHOGRAPHY = "orthography"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Item:
    item_id: str
    category: Category
    difficulty: Difficulty
    question: str
    options: list[str]
    answer_index: int
    explanation: str = ""

    @property
    def answer(self) -> str:
        return self.options[self.answer_index]


@dataclass
class Response:
    item_id: str
    model: str
    raw_response: str
    predicted_index: int | None
    error: str | None = None


@dataclass
class Result:
    item_id: str
    model: str
    category: Category
    difficulty: Difficulty
    answer_index: int
    predicted_index: int | None
    correct: bool
    unparseable: bool
    raw_response: str
