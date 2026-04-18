import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score

from src.nba_win_prob.config import ARTIFACTS_DIR
from src.nba_win_prob.models.baseline import build_model

ID_COLS = {
    "game_id",
    "game_date",
    "season_id",
    "home_team_id",
    "away_team_id",
    "home_team",
    "away_team",
    "home_win",
}


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path).sort_values("game_date").reset_index(drop=True)


def split_timewise(df: pd.DataFrame, train_frac: float = 0.7, val_frac: float = 0.15):
    n = len(df)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in ID_COLS]


def evaluate(y_true, y_prob) -> dict[str, float]:
    y_pred = (y_prob >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "log_loss": float(log_loss(y_true, y_prob)),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    args = parser.parse_args()

    dataset_path = Path("data/processed") / f"pregame_dataset_{args.season}.parquet"
    df = load_dataset(dataset_path)
    train_df, val_df, test_df = split_timewise(df)
    features = feature_columns(df)

    model = build_model()
    model.fit(train_df[features], train_df["home_win"])

    metrics = {
        "train": evaluate(train_df["home_win"], model.predict_proba(train_df[features])[:, 1]),
        "val": evaluate(val_df["home_win"], model.predict_proba(val_df[features])[:, 1]),
        "test": evaluate(test_df["home_win"], model.predict_proba(test_df[features])[:, 1]),
        "num_rows": len(df),
        "num_features": len(features),
        "features": features,
    }

    out_dir = ARTIFACTS_DIR / args.season
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "baseline.joblib")
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
