import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kyrgyz_eval import morphology as m


@pytest.mark.parametrize("stem,expected", [
    ("китеп", "китептер"),
    ("көз", "көздөр"),
    ("жол", "жолдор"),
    ("үй", "үйлөр"),
    ("ат", "аттар"),
    ("гүл", "гүлдөр"),
    ("тоо", "тоолор"),
    ("мугалим", "мугалимдер"),
])
def test_plural_matches_verified_benchmark(stem, expected):
    assert m.plural(stem) == expected


def test_plural_irregular_override():
    assert m.plural("бала", irregular="балдар") == "балдар"


@pytest.mark.parametrize("stem,expected", [
    ("бала", "баланын"),
    ("китеп", "китептин"),
    ("көз", "көздүн"),
])
def test_genitive(stem, expected):
    assert m.genitive(stem) == expected


@pytest.mark.parametrize("stem,expected", [
    ("үй", "үйгө"),
    ("мектеп", "мектепке"),
    ("суу", "сууга"),
])
def test_dative(stem, expected):
    assert m.dative(stem) == expected


@pytest.mark.parametrize("stem,expected", [
    ("китеп", "китепти"),
    ("бала", "баланы"),
])
def test_accusative(stem, expected):
    assert m.accusative(stem) == expected


def test_locative():
    assert m.locative("шаар") == "шаарда"
    assert m.locative("мектеп") == "мектепте"


def test_ablative():
    assert m.ablative("мектеп") == "мектептен"
    assert m.ablative("шаар") == "шаардан"
    assert m.ablative("бут") == "буттан"


def test_rounding_asymmetry_back_high_vowel():
    assert m.plural("суу") == "суулар"
    assert m.plural("бут") == "буттар"


def test_iotation_after_final_glide():
    assert m.poss_1sg("ой") == "оюм"
    assert m.poss_1sg("үй") == "үйүм"


@pytest.mark.parametrize("stem,expected", [
    ("үй", "үйүм"),
    ("бала", "балам"),
    ("китеп", "китебим"),
    ("ат", "атым"),
])
def test_possessive_1sg_with_voicing(stem, expected):
    assert m.poss_1sg(stem) == expected


@pytest.mark.parametrize("stem,expected", [
    ("бала", "баласы"),
    ("китеп", "китеби"),
    ("үй", "үйү"),
])
def test_possessive_3sg(stem, expected):
    assert m.poss_3sg(stem) == expected


def test_distractors_are_three_distinct_and_exclude_correct():
    for feature in ["plural", "genitive", "accusative", "poss_1sg"]:
        for stem in ["китеп", "көз", "үй", "тоо"]:
            correct = m.inflect(stem, feature)
            ds = m.distractors(stem, feature)
            assert len(ds) == 3
            assert len(set(ds)) == 3
            assert correct not in ds
