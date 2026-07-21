from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import binomtest

from .models import Result

CHANCE_LEVEL = 0.25

sns.set_theme(style="whitegrid")


def results_to_dataframe(results: list[Result]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "item_id": r.item_id,
                "model": r.model,
                "category": r.category.value,
                "difficulty": r.difficulty.value,
                "answer_index": r.answer_index,
                "predicted_index": r.predicted_index,
                "correct": r.correct,
                "unparseable": r.unparseable,
            }
            for r in results
        ]
    )


def accuracy(df: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame | float:
    if group_by:
        return df.groupby(group_by)["correct"].mean().rename("accuracy").reset_index()
    return float(df["correct"].mean())


def unparseable_rate(df: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame | float:
    if group_by:
        return df.groupby(group_by)["unparseable"].mean().rename("unparseable_rate").reset_index()
    return float(df["unparseable"].mean())


def significance_vs_chance(df: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame:
    rows = []
    groups = df.groupby(group_by) if group_by else [((), df)]

    for key, group in groups:
        n_correct = int(group["correct"].sum())
        n_total = len(group)
        test = binomtest(n_correct, n_total, CHANCE_LEVEL, alternative="greater")
        row = {
            "n_correct": n_correct,
            "n_total": n_total,
            "accuracy": n_correct / n_total if n_total else 0.0,
            "p_value": test.pvalue,
            "above_chance_p05": test.pvalue < 0.05,
        }
        if group_by:
            key_values = key if isinstance(key, tuple) else (key,)
            row = dict(zip(group_by, key_values)) | row
        rows.append(row)

    return pd.DataFrame(rows)


def plot_accuracy_by_category(df: pd.DataFrame, output_path: str | Path) -> Path:
    rates = accuracy(df, ["category", "model"])

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=rates, x="accuracy", y="category", hue="model", palette="viridis", ax=ax)
    ax.axvline(CHANCE_LEVEL, color="crimson", linestyle="--", linewidth=1.5, label="chance (25%)")
    ax.set_xlim(0, 1)
    ax.set_title("Accuracy by Category")
    ax.set_xlabel("accuracy")
    ax.set_ylabel("")
    ax.legend(loc="lower right")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_model_category_heatmap(df: pd.DataFrame, output_path: str | Path) -> Path:
    pivot = df.pivot_table(index="model", columns="category", values="correct", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(11, 3 + len(pivot)))
    sns.heatmap(
        pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1, ax=ax,
        cbar_kws={"label": "accuracy"}, linewidths=0.5,
    )
    ax.set_title("Accuracy: Model x Category")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def plot_accuracy_by_difficulty(df: pd.DataFrame, output_path: str | Path) -> Path:
    order = [d for d in ["easy", "medium", "hard"] if d in df["difficulty"].unique()]
    rates = accuracy(df, ["difficulty", "model"])

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=rates, x="difficulty", y="accuracy", hue="model", order=order, palette="viridis", ax=ax)
    ax.axhline(CHANCE_LEVEL, color="crimson", linestyle="--", linewidth=1.5, label="chance (25%)")
    ax.set_ylim(0, 1)
    ax.set_title("Accuracy by Difficulty")
    ax.set_xlabel("")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
