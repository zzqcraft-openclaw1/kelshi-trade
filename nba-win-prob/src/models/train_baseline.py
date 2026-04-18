from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features.schema import ALL_FEATURE_COLUMNS


@dataclass
class BaselineArtifacts:
    model_pipeline: Pipeline
    feature_columns: list[str]


def build_baseline_pipeline() -> Pipeline:
    numeric_features = list(ALL_FEATURE_COLUMNS)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            )
        ]
    )

    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        class_weight="balanced",
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def fit_baseline(training_df: pd.DataFrame) -> BaselineArtifacts:
    if "home_win" not in training_df.columns:
        raise ValueError("training_df must include 'home_win'")

    X = training_df[ALL_FEATURE_COLUMNS]
    y = training_df["home_win"]

    pipeline = build_baseline_pipeline()
    pipeline.fit(X, y)

    return BaselineArtifacts(
        model_pipeline=pipeline,
        feature_columns=list(ALL_FEATURE_COLUMNS),
    )
