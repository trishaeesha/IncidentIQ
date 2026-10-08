from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "ml" / "results" / "participant_analysis.csv"
OUTPUT = ROOT / "ml" / "results" / "participant_ml_metrics.csv"
CM_OUTPUT = ROOT / "ml" / "results" / "participant_confusion_matrix.csv"


def main():
    if not INPUT.exists():
        print("Participant analysis file not found.")
        print(f"Expected: {INPUT}")
        print("This is normal until real participant results are available.")
        return

    df = pd.read_csv(INPUT)

    required = {
        "participantId",
        "diagnosis_correct",
        "condition",
        "caseId",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Required ML columns are missing: {sorted(missing)}"
        )

    df = df.dropna(
        subset=[
            "diagnosis_correct",
            "participantId",
            "condition",
            "caseId",
        ]
    )

    if df["diagnosis_correct"].nunique() < 2:
        print("Not enough target classes for classification.")
        print("Need both correct and incorrect diagnosis trials.")
        return

    y = df["diagnosis_correct"].astype(int)

    # Participant ID is used ONLY for grouped cross-validation.
    # It is never included in X.
    groups = df["participantId"]

    feature_candidates = [
        "condition",
        "caseId",
    ]

    features = [
        column
        for column in feature_candidates
        if column in df.columns
    ]

    if not features:
        raise ValueError("No usable ML features found.")

    X = df[features].copy()

    categorical_features = [
        column
        for column in ["condition", "caseId"]
        if column in X.columns
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline([
                    (
                        "imputer",
                        SimpleImputer(
                            strategy="most_frequent"
                        ),
                    ),
                    (
                        "onehot",
                        OneHotEncoder(
                            handle_unknown="ignore"
                        ),
                    ),
                ]),
                categorical_features,
            )
        ]
    )

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

    unique_groups = groups.nunique()

    if unique_groups < 2:
        print("Not enough participants for GroupKFold.")
        return

    n_splits = min(5, unique_groups)

    cv = GroupKFold(
        n_splits=n_splits
    )

    results = []
    confusion_by_model = {}

    for model_name, model in models.items():

        fold_metrics = []
        confusion_total = None

        for fold, (train_idx, test_idx) in enumerate(
            cv.split(
                X,
                y,
                groups=groups,
            ),
            start=1,
        ):

            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]

            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]

            pipeline = Pipeline([
                (
                    "preprocessor",
                    preprocessor,
                ),
                (
                    "model",
                    model,
                ),
            ])

            pipeline.fit(
                X_train,
                y_train,
            )

            predictions = pipeline.predict(
                X_test
            )

            fold_metrics.append({
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
            })

            cm = confusion_matrix(
                y_test,
                predictions,
                labels=[0, 1],
            )

            if confusion_total is None:
                confusion_total = cm
            else:
                confusion_total += cm

        results.extend(
            fold_metrics
        )

        confusion_by_model[
            model_name
        ] = confusion_total

    metrics_df = pd.DataFrame(
        results
    )

    metrics_df.to_csv(
        OUTPUT,
        index=False,
    )

    confusion_rows = []

    for model_name, cm in confusion_by_model.items():

        confusion_rows.extend([
            {
                "model": model_name,
                "actual": "incorrect",
                "predicted_incorrect": int(cm[0, 0]),
                "predicted_correct": int(cm[0, 1]),
            },
            {
                "model": model_name,
                "actual": "correct",
                "predicted_incorrect": int(cm[1, 0]),
                "predicted_correct": int(cm[1, 1]),
            },
        ])

    cm_df = pd.DataFrame(
        confusion_rows
    )

    cm_df.to_csv(
        CM_OUTPUT,
        index=False,
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
    print(
        f"ML features: {features}"
    )
    print()
    print(metrics_df)


if __name__ == "__main__":
    main()
