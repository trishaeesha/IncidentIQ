"""Exploratory participant-level ML analysis for IncidentIQ.

The target is diagnosis_correct.

Participant identity is used only as the grouping variable for GroupKFold;
it is never used as a predictive feature.

Two feature sets are evaluated:
1. Pre-decision: condition, trialIndex
2. Post-decision: confidence, workload, elapsedSeconds, aiFollowed, aiOverridden

This analysis is exploratory and does not establish causality or production
predictive performance.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "ml" / "results" / "participant_analysis.csv"
OUTPUT = ROOT / "ml" / "results" / "participant_ml_metrics.csv"
CM_OUTPUT = ROOT / "ml" / "results" / "participant_confusion_matrix.csv"


REQUIRED_COLUMNS = [
    "participantId",
    "trialIndex",
    "condition",
    "diagnosis_correct",
    "confidence",
    "workload",
    "elapsedSeconds",
    "aiFollowed",
    "aiOverridden",
]


def make_pipeline(
    model,
    categorical_features: list[str],
    numeric_features: list[str],
) -> Pipeline:
    transformers = []

    if categorical_features:
        categorical_pipeline = Pipeline(
            [
                (
                    "imputer",
                    SimpleImputer(strategy="most_frequent"),
                ),
                (
                    "onehot",
                    OneHotEncoder(handle_unknown="ignore"),
                ),
            ]
        )

        transformers.append(
            (
                "categorical",
                categorical_pipeline,
                categorical_features,
            )
        )

    if numeric_features:
        numeric_pipeline = Pipeline(
            [
                (
                    "imputer",
                    SimpleImputer(strategy="median"),
                ),
            ]
        )

        transformers.append(
            (
                "numeric",
                numeric_pipeline,
                numeric_features,
            )
        )

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def main() -> None:
    if not INPUT.exists():
        print("Participant analysis file not found.")
        print(f"Expected: {INPUT}")
        return

    df = pd.read_csv(INPUT)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Participant analysis dataset is empty.")

    y = df["diagnosis_correct"].astype(int)
    groups = df["participantId"]

    unique_groups = groups.nunique()

    if unique_groups < 2:
        raise ValueError(
            "At least two participants are required for GroupKFold."
        )

    n_splits = min(5, unique_groups)

    feature_sets = {
        "pre_decision": {
            "features": [
                "condition",
                "trialIndex",
            ],
            "categorical": [
                "condition",
            ],
            "numeric": [
                "trialIndex",
            ],
        },
        "post_decision": {
            "features": [
                "confidence",
                "workload",
                "elapsedSeconds",
                "aiFollowed",
                "aiOverridden",
            ],
            "categorical": [
                "aiFollowed",
                "aiOverridden",
            ],
            "numeric": [
                "confidence",
                "workload",
                "elapsedSeconds",
            ],
        },
    }

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        ),
    }

    results = []
    confusion_rows = []

    for feature_set_name, config in feature_sets.items():
        features = config["features"]

        X = df[features].copy()

        for column in config["categorical"]:
            X[column] = X[column].astype(str)

        for model_name, model in models.items():
            fold_metrics = []
            confusion_total = None

            cv = GroupKFold(n_splits=n_splits)

            for fold, (train_idx, test_idx) in enumerate(
                cv.split(X, y, groups=groups),
                start=1,
            ):
                X_train = X.iloc[train_idx]
                X_test = X.iloc[test_idx]
                y_train = y.iloc[train_idx]
                y_test = y.iloc[test_idx]

                pipeline = make_pipeline(
                    model,
                    config["categorical"],
                    config["numeric"],
                )

                pipeline.fit(
                    X_train,
                    y_train,
                )

                predictions = pipeline.predict(X_test)
                probabilities = pipeline.predict_proba(X_test)[:, 1]

                auc = roc_auc_score(
                    y_test,
                    probabilities,
                )

                metrics = {
                    "feature_set": feature_set_name,
                    "model": model_name,
                    "fold": fold,
                    "accuracy": accuracy_score(
                        y_test,
                        predictions,
                    ),
                    "precision": precision_score(
                        y_test,
                        predictions,
                        zero_division=0,
                    ),
                    "recall": recall_score(
                        y_test,
                        predictions,
                        zero_division=0,
                    ),
                    "f1": f1_score(
                        y_test,
                        predictions,
                        zero_division=0,
                    ),
                    "roc_auc": auc,
                }

                fold_metrics.append(metrics)

                cm = confusion_matrix(
                    y_test,
                    predictions,
                    labels=[0, 1],
                )

                if confusion_total is None:
                    confusion_total = cm
                else:
                    confusion_total += cm

            results.extend(fold_metrics)

            confusion_rows.extend(
                [
                    {
                        "feature_set": feature_set_name,
                        "model": model_name,
                        "actual": "incorrect",
                        "predicted_incorrect": int(
                            confusion_total[0, 0]
                        ),
                        "predicted_correct": int(
                            confusion_total[0, 1]
                        ),
                    },
                    {
                        "feature_set": feature_set_name,
                        "model": model_name,
                        "actual": "correct",
                        "predicted_incorrect": int(
                            confusion_total[1, 0]
                        ),
                        "predicted_correct": int(
                            confusion_total[1, 1]
                        ),
                    },
                ]
            )

    metrics_df = pd.DataFrame(results)
    cm_df = pd.DataFrame(confusion_rows)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_df.to_csv(
        OUTPUT,
        index=False,
    )

    cm_df.to_csv(
        CM_OUTPUT,
        index=False,
    )

    summary = (
        metrics_df.groupby(
            ["feature_set", "model"],
            as_index=False,
        )[
            [
                "accuracy",
                "precision",
                "recall",
                "f1",
                "roc_auc",
            ]
        ]
        .mean()
    )

    print(
        f"Metrics output: {OUTPUT}"
    )
    print(
        f"Confusion matrix output: {CM_OUTPUT}"
    )
    print(
        f"Participants: {unique_groups}"
    )
    print(
        f"Trials: {len(df)}"
    )
    print(
        f"GroupKFold splits: {n_splits}"
    )
    print()

    print("Pre-decision features:")
    print(
        "  ['condition', 'trialIndex']"
    )

    print("Post-decision features:")
    print(
        "  ['confidence', 'workload', 'elapsedSeconds', "
        "'aiFollowed', 'aiOverridden']"
    )

    print()
    print("Mean cross-validation metrics:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
