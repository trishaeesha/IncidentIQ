import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "ml" / "data" / "participant_results"
OUT_DIR = ROOT / "ml" / "results"

OUT_DIR.mkdir(parents=True, exist_ok=True)


EXPECTED_CONDITIONS = {
    "clear",
    "ambiguous",
    "conflicting",
    "incomplete",
    "misleading",
}


# Ground truth taken from the study case definitions
# in study-site/web/index.html.
CASE_GROUND_TRUTH = {
    "CASE-01": "Checkoutservice CPU/resource saturation",
    "CASE-02": "Checkoutservice memory/resource pressure",
    "CASE-03": "Checkoutservice network packet loss",
    "CASE-04": "Checkoutservice network packet loss",
    "CASE-05": "User-service network packet loss",
}


REQUIRED_FIELDS = {
    "participantId",
    "trialIndex",
    "caseId",
    "condition",
    "diagnosis",
    "confidence",
    "workload",
    "aiFollowed",
    "aiOverridden",
    "elapsedSeconds",
}


def normalize_text(value):
    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def diagnosis_is_correct(case_id, diagnosis):
    if case_id not in CASE_GROUND_TRUTH:
        return None

    expected = normalize_text(
        CASE_GROUND_TRUTH[case_id]
    )

    actual = normalize_text(diagnosis)

    if not actual:
        return None

    return actual == expected


def load_participants():
    files = sorted(DATA_DIR.glob("P*.json"))

    if not files:
        print("No participant result files found.")
        print(f"Expected files in: {DATA_DIR}")
        return pd.DataFrame()

    rows = []

    for path in files:
        with path.open("r", encoding="utf-8") as f:
            participant = json.load(f)

        participant_id = participant.get("participantId")

        if not participant_id:
            print(
                f"WARNING: participantId missing in {path.name}"
            )

        trials = participant.get("trials", [])

        for trial in trials:
            missing = REQUIRED_FIELDS - set(trial.keys())

            if missing:
                raise ValueError(
                    f"{path.name}, trial "
                    f"{trial.get('trialIndex')}: "
                    f"missing required fields: "
                    f"{sorted(missing)}"
                )

            row = {
                "participantId": participant_id,
                "trialIndex": trial.get("trialIndex"),
                "caseId": trial.get("caseId"),
                "condition": trial.get("condition"),
                "diagnosis": trial.get("diagnosis"),
                "confidence": trial.get("confidence"),
                "workload": trial.get("workload"),
                "aiFollowed": trial.get("aiFollowed"),
                "aiOverridden": trial.get("aiOverridden"),
                "elapsedSeconds": trial.get("elapsedSeconds"),
            }

            rows.append(row)

    return pd.DataFrame(rows)


def main():
    df = load_participants()

    if df.empty:
        return

    print(
        f"Participant files loaded: "
        f"{df['participantId'].nunique()}"
    )
    print(f"Trial rows loaded: {len(df)}")

    unexpected = sorted(
        set(
            df["condition"]
            .dropna()
            .astype(str)
            .str.lower()
        )
        - EXPECTED_CONDITIONS
    )

    if unexpected:
        raise ValueError(
            f"Unexpected conditions found: {unexpected}"
        )

    unknown_cases = sorted(
        set(df["caseId"].dropna().astype(str))
        - set(CASE_GROUND_TRUTH)
    )

    if unknown_cases:
        raise ValueError(
            f"Unknown case IDs found: {unknown_cases}"
        )

    df["correct_diagnosis"] = df["caseId"].map(
        CASE_GROUND_TRUTH
    )

    df["diagnosis_correct"] = [
        diagnosis_is_correct(case_id, diagnosis)
        for case_id, diagnosis
        in zip(df["caseId"], df["diagnosis"])
    ]

    duplicate_count = df.duplicated(
        subset=["participantId", "trialIndex"]
    ).sum()

    print(
        f"Duplicate participant/trial rows: "
        f"{duplicate_count}"
    )

    if duplicate_count > 0:
        raise ValueError(
            "Duplicate participant/trial rows found."
        )

    complete_counts = (
        df.groupby("participantId")
        .size()
        .sort_values()
    )

    complete_participants = (
        complete_counts == 5
    ).sum()

    print(
        f"Participants with exactly 5 trials: "
        f"{complete_participants}"
    )

    incomplete_participants = complete_counts[
        complete_counts != 5
    ]

    if not incomplete_participants.empty:
        print(
            "Participants without exactly 5 trials:"
        )
        print(incomplete_participants)

    unresolved = df["diagnosis_correct"].isna().sum()

    print(
        f"Trials with unresolved correctness: "
        f"{unresolved}"
    )

    output = OUT_DIR / "participant_analysis.csv"

    df.to_csv(
        output,
        index=False
    )

    print(f"Output: {output}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()
