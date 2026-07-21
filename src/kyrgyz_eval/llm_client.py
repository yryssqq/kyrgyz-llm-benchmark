from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod

from .models import Item, Response
from .scorer import parse_answer

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """Төмөнкү суроого жооп бериңиз. Жообуңузду бир гана сан менен жазыңыз (1, 2, 3 же 4). Башка эч нерсе жазбаңыз.

Суроо: {question}
1) {option_1}
2) {option_2}
3) {option_3}
4) {option_4}

Жооп:"""


def build_prompt(item: Item) -> str:
    return PROMPT_TEMPLATE.format(
        question=item.question,
        option_1=item.options[0],
        option_2=item.options[1],
        option_3=item.options[2],
        option_4=item.options[3],
    )


class BaseBackend(ABC):
    name: str

    @abstractmethod
    def _call(self, prompt: str) -> str: ...

    def answer(self, item: Item, max_retries: int = 3, backoff_seconds: float = 2.0) -> Response:
        prompt = build_prompt(item)
        last_error: str | None = None

        for attempt in range(1, max_retries + 1):
            try:
                raw = self._call(prompt)
                return Response(
                    item_id=item.item_id,
                    model=self.name,
                    raw_response=raw,
                    predicted_index=parse_answer(raw, item),
                )
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "call failed (item=%s, model=%s, attempt=%d/%d): %s",
                    item.item_id, self.name, attempt, max_retries, last_error,
                )
                if attempt < max_retries:
                    time.sleep(backoff_seconds * attempt)

        return Response(
            item_id=item.item_id,
            model=self.name,
            raw_response="",
            predicted_index=None,
            error=last_error,
        )


class HuggingFaceBackend(BaseBackend):
    def __init__(self, model_id: str, token: str | None = None, max_tokens: int = 16):
        from huggingface_hub import InferenceClient

        self.name = model_id
        self.max_tokens = max_tokens
        self._client = InferenceClient(model=model_id, token=token)

    def _call(self, prompt: str) -> str:
        response = self._client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""


class OpenAIBackend(BaseBackend):
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None, max_tokens: int = 16):
        from openai import OpenAI

        self.name = model
        self.max_tokens = max_tokens
        self._client = OpenAI(api_key=api_key)

    def _call(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""


def build_backend(provider: str, model: str, api_key: str | None = None) -> BaseBackend:
    if provider == "huggingface":
        return HuggingFaceBackend(model_id=model, token=api_key)
    if provider == "openai":
        return OpenAIBackend(model=model, api_key=api_key)
    raise ValueError(f"Unknown provider '{provider}'. Use 'huggingface' or 'openai'.")
