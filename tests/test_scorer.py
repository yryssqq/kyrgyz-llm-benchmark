import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kyrgyz_eval.models import Category, Difficulty, Item, Response
from kyrgyz_eval.scorer import parse_answer, score

ITEM = Item(
    item_id="vh_001",
    category=Category.VOWEL_HARMONY,
    difficulty=Difficulty.EASY,
    question="«китеп» сөзүнүн көптүк түрү кайсы?",
    options=["китептер", "китеплер", "китептар", "китеплар"],
    answer_index=0,
)


def test_parses_bare_digit():
    assert parse_answer("1", ITEM) == 0
    assert parse_answer("4", ITEM) == 3


def test_parses_digit_in_sentence():
    assert parse_answer("Жооп: 2", ITEM) == 1


def test_parses_full_option_text():
    assert parse_answer("китептер", ITEM) == 0


def test_option_text_match_is_whitespace_insensitive():
    assert parse_answer("  КИТЕПТЕР  ", ITEM) == 0


def test_returns_none_for_empty_response():
    assert parse_answer("", ITEM) is None
    assert parse_answer("   ", ITEM) is None


def test_returns_none_for_unparseable_response():
    assert parse_answer("билбейм", ITEM) is None


def test_digit_outside_range_is_not_matched():
    assert parse_answer("7", ITEM) is None


def test_score_marks_correct():
    response = Response(item_id="vh_001", model="m", raw_response="1", predicted_index=0)
    result = score(ITEM, response)
    assert result.correct is True
    assert result.unparseable is False


def test_score_marks_wrong():
    response = Response(item_id="vh_001", model="m", raw_response="2", predicted_index=1)
    result = score(ITEM, response)
    assert result.correct is False
    assert result.unparseable is False


def test_score_marks_unparseable():
    response = Response(item_id="vh_001", model="m", raw_response="???", predicted_index=None)
    result = score(ITEM, response)
    assert result.correct is False
    assert result.unparseable is True
