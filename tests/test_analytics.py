import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kyrgyz_eval import analytics
from kyrgyz_eval.models import Category, Difficulty, Result


def _result(model, category, correct, difficulty=Difficulty.EASY, unparseable=False):
    return Result(
        item_id=f"{category.value}_{model}_{correct}",
        model=model,
        category=category,
        difficulty=difficulty,
        answer_index=0,
        predicted_index=0 if correct else 1,
        correct=correct,
        unparseable=unparseable,
        raw_response="1",
    )


def _results():
    return [
        _result("model-a", Category.VOWEL_HARMONY, True),
        _result("model-a", Category.MORPHOLOGY, False),
        _result("model-a", Category.CULTURE, True, difficulty=Difficulty.HARD),
        _result("model-b", Category.VOWEL_HARMONY, False),
        _result("model-b", Category.MORPHOLOGY, False),
        _result("model-b", Category.CULTURE, False, difficulty=Difficulty.HARD, unparseable=True),
    ]


def test_accuracy_overall():
    df = analytics.results_to_dataframe(_results())
    assert analytics.accuracy(df) == 2 / 6


def test_accuracy_by_model():
    df = analytics.results_to_dataframe(_results())
    rates = analytics.accuracy(df, ["model"]).set_index("model")["accuracy"]
    assert rates["model-a"] == 2 / 3
    assert rates["model-b"] == 0.0


def test_unparseable_rate():
    df = analytics.results_to_dataframe(_results())
    rates = analytics.unparseable_rate(df, ["model"]).set_index("model")["unparseable_rate"]
    assert rates["model-b"] == 1 / 3


def test_significance_flags_perfect_score_above_chance():
    results = [_result("m", Category.MORPHOLOGY, True) for _ in range(20)]
    df = analytics.results_to_dataframe(results)
    df["item_id"] = [f"i{i}" for i in range(20)]
    row = analytics.significance_vs_chance(df, ["model"]).iloc[0]
    assert row["accuracy"] == 1.0
    assert row["above_chance_p05"]


def test_significance_does_not_flag_chance_level_score():
    results = [_result("m", Category.MORPHOLOGY, i < 5) for i in range(20)]
    df = analytics.results_to_dataframe(results)
    df["item_id"] = [f"i{i}" for i in range(20)]
    row = analytics.significance_vs_chance(df, ["model"]).iloc[0]
    assert row["accuracy"] == 0.25
    assert not row["above_chance_p05"]


def test_charts_are_written(tmp_path):
    df = analytics.results_to_dataframe(_results())
    assert analytics.plot_accuracy_by_category(df, tmp_path / "cat.png").exists()
    assert analytics.plot_model_category_heatmap(df, tmp_path / "heat.png").exists()
    assert analytics.plot_accuracy_by_difficulty(df, tmp_path / "diff.png").exists()
