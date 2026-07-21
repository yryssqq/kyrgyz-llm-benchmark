#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

from kyrgyz_eval import analytics


def load_results(paths: list[str]) -> pd.DataFrame:
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    df["correct"] = df["correct"].astype(bool)
    df["unparseable"] = df["unparseable"].astype(bool)
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_files", nargs="+")
    parser.add_argument("--output-dir", default="results/report")
    args = parser.parse_args()

    df = load_results(args.csv_files)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "n_evaluations": int(len(df)),
        "chance_level": analytics.CHANCE_LEVEL,
        "overall_accuracy": analytics.accuracy(df),
        "accuracy_by_model": analytics.accuracy(df, ["model"]).to_dict(orient="records"),
        "accuracy_by_category": analytics.accuracy(df, ["category"]).to_dict(orient="records"),
        "accuracy_by_difficulty": analytics.accuracy(df, ["difficulty"]).to_dict(orient="records"),
        "unparseable_rate_by_model": analytics.unparseable_rate(df, ["model"]).to_dict(orient="records"),
        "significance_by_model": analytics.significance_vs_chance(df, ["model"]).to_dict(orient="records"),
        "significance_by_model_category": analytics.significance_vs_chance(
            df, ["model", "category"]
        ).to_dict(orient="records"),
    }

    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    analytics.plot_accuracy_by_category(df, output_dir / "accuracy_by_category.png")
    analytics.plot_model_category_heatmap(df, output_dir / "model_category_heatmap.png")
    analytics.plot_accuracy_by_difficulty(df, output_dir / "accuracy_by_difficulty.png")

    print(f"\nWrote summary and charts to {output_dir}")


if __name__ == "__main__":
    main()
