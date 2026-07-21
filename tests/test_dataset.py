import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kyrgyz_eval import dataset
from kyrgyz_eval.models import Category

EXAMPLE_PATH = Path(__file__).parent.parent / "data" / "items.example.json"


def _write(tmp_path, items):
    path = tmp_path / "items.json"
    path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    return path


def _valid_item(**overrides):
    item = {
        "item_id": "vh_001",
        "category": "vowel_harmony",
        "difficulty": "easy",
        "question": "суроо?",
        "options": ["a", "b", "c", "d"],
        "answer_index": 0,
    }
    item.update(overrides)
    return item


def test_loads_example_file():
    items = dataset.load_items(EXAMPLE_PATH)
    assert len(items) == 3
    assert all(isinstance(i.category, Category) for i in items)


def test_answer_property_matches_index(tmp_path):
    path = _write(tmp_path, [_valid_item(answer_index=2)])
    assert dataset.load_items(path)[0].answer == "c"


def test_rejects_duplicate_ids(tmp_path):
    path = _write(tmp_path, [_valid_item(), _valid_item()])
    with pytest.raises(dataset.DatasetError, match="Duplicate"):
        dataset.load_items(path)


def test_rejects_wrong_option_count(tmp_path):
    path = _write(tmp_path, [_valid_item(options=["a", "b", "c"])])
    with pytest.raises(dataset.DatasetError, match="expected 4 options"):
        dataset.load_items(path)


def test_rejects_duplicate_options(tmp_path):
    path = _write(tmp_path, [_valid_item(options=["a", "a", "c", "d"])])
    with pytest.raises(dataset.DatasetError, match="distinct"):
        dataset.load_items(path)


def test_rejects_out_of_range_answer_index(tmp_path):
    path = _write(tmp_path, [_valid_item(answer_index=4)])
    with pytest.raises(dataset.DatasetError, match="answer_index"):
        dataset.load_items(path)


def test_rejects_unknown_category(tmp_path):
    path = _write(tmp_path, [_valid_item(category="poetry")])
    with pytest.raises(dataset.DatasetError, match="unknown category"):
        dataset.load_items(path)


def test_rejects_missing_field(tmp_path):
    item = _valid_item()
    del item["question"]
    path = _write(tmp_path, [item])
    with pytest.raises(dataset.DatasetError, match="missing fields"):
        dataset.load_items(path)


def test_answer_position_bias(tmp_path):
    items = [
        _valid_item(item_id="a", answer_index=0),
        _valid_item(item_id="b", answer_index=0),
        _valid_item(item_id="c", answer_index=3),
    ]
    loaded = dataset.load_items(_write(tmp_path, items))
    assert dataset.answer_position_bias(loaded) == {0: 2, 3: 1}
