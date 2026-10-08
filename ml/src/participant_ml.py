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
from sklearn.preprocessing import OneHotEncoder, StandardScaler
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

    if "diagnosis_correct" not in df.columns:
        raise ValueError("diagnosis_correct column is missing.")

    df = df.dropna(subset=["diagnosis_correct", "participantId"])

    if df["diagnosis_correct"].nunique() < 2:
        print("Not enough target classes for classification.")
        print("Need both correct and incorrect diagnosis trials.")
        return

    y = df["diagnosis_correct"].astype(int)
    groups = df["participantId"]

    feature_candidates = [
        "condition",
        "confidence",
        "workload",
        "elapsedSeconds",
        "aiFollowed",
        "aiOverridden",
    ]

    features = [
        column for column in feature_candidates
        if column in df.columns
    ]

    if not features:
        raise ValueError("No usable ML features found.")

    X = df[features].copy()

    numeric_features = [
        column for column in [
            "confidence",
            "workload",
            "elapsedSeconds",
        ]
        if column in X.columns
    ]

    categorical_features = [
        column for column in ["condition"]
        if column in X.columns
    ]

    boolean_features = [
        column for column in ["aiFollowed", "aiOverridden"]
        if column in X.columns
    ]

    for column in boolean_features:
        X[column] = (
            X[column]
            .astype(str)
            .str.lower()
            .map({
                "true": 1,
                "false": 0,
                "1": 1,
                "0": 0,
                "yes": 1,
                "no": 0,
            })
        )

    numeric_features.extend(boolean_features)

    transformers = []

    if numeric_features:
        transformers.append(
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_features,
            )
        )

    if categorical_features:
        transformers.append(
            (
                "categorical",
                Pipeline([
                    (
                        "imputer",
                        SimpleImputer(strategy="most_frequent"),
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
        )

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    models = {
        "logistic_regression": LogisticRegression(
            max_iter=2000
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

    cv = GroupKFold(n_splits=n_splits)

    results = []
    confusion_total = None

    for model_name, model in models.items():

        fold_metrics = []

        for fold, (train_idx, test_idx) in enumerate(
            cv.split(X, y, groups=groups),
            start=1,
        ):
            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_train = y.iloc[train_idx]
            y_test = y.iloc[test_idx]

            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model),
            ])

            pipeline.fit(X_train, y_train)

            predictions = pipeline.predict(X_test)

            fold_metrics.append({
                "model": model_name,
                "fold": fold,
                "accuracy": accuracy_score(
                    y_test, predictions
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

        results.extend(fold_metrics)

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUTPUT, index=False)

    cm_df = pd.DataFrame(
        confusion_total,
        index=["actual_incorrect", "actual_correct"],
        columns=["predicted_incorrect", "predicted_correct"],
    )

    cm_df.to_csv(CM_OUTPUT)

    print(f"Metrics output: {OUTPUT}")
    print(f"Confusion matrix output: {CM_OUTPUT}")
    print(f"Participants: {unique_groups}")
    print(f"Trials: {len(df)}")
    print(f"GroupKFold splits: {n_splits}")
    print(metrics_df)


if __name__ == "__main__":
    main()
