from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.evaluation.metrics import evaluate_probabilities
from src.models.train_baseline import fit_baseline


def main() -> None:
    training_path = Path("data/processed/training_table.csv")
    if not training_path.exists():
        raise FileNotFoundError(
            "Missing data/processed/training_table.csv. Build the training table first."
        )

    df = pd.read_csv(training_path)

    if "season" not in df.columns:
        raise ValueError("training table must include 'season'")

    train_df = df[df["season"].isin([2021, 2022, 2023])].copy()
    test_df = df[df["season"].isin([2024])].copy()

    artifacts = fit_baseline(train_df)
    y_prob = artifacts.model_pipeline.predict_proba(test_df[artifacts.feature_columns])[:, 1]
    result = evaluate_probabilities(test_df["home_win"], y_prob)

    print("Baseline evaluation")
    print(f"log_loss={result.log_loss:.6f}")
    print(f"brier_score={result.brier_score:.6f}")
    print(f"roc_auc={result.roc_auc:.6f}")
    print(f"accuracy={result.accuracy:.6f}")


if __name__ == "__main__":
    main()
