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
        str(value).strip().lower().split()
    )


def diagnosis_is_correct(case_id, diagnosis):
    if case_id not in CASE_GROUND_TRUTH:
        return None

    expected = normalize_text(CASE_GROUND_TRUTH[case_id])
    actual = normalize_text(diagnosis)

    if not actual:
        return None

    return actual == expected


def load_participants():
    csv_files = sorted(
        DATA_DIR.glob("*.csv")
    )

    if not csv_files:
        print("No participant CSV files found.")
        print(f"Expected files in: {DATA_DIR}")
        return pd.DataFrame()

    # Prefer the validated 27-participant / 135-trial dataset.
    preferred = DATA_DIR / (
        "IncidentIQ_clean_analysis_27_complete_participants.csv"
    )

    if preferred.exists():
        input_file = preferred
    else:
        input_file = csv_files[0]

    print(f"Loading participant data: {input_file.name}")

    df = pd.read_csv(input_file)

    missing = REQUIRED_FIELDS - set(df.columns)

    if missing:
        print("Missing required fields:")
        for field in sorted(missing):
            print(f"  - {field}")
        return pd.DataFrame()

    return df


def validate_data(df):
    if df.empty:
        return df

    print(f"Loaded trials: {len(df)}")

    participants = df["participantId"].nunique()
    print(f"Unique participants: {participants}")

    trial_counts = (
        df.groupby("participantId")["trialIndex"]
        .nunique()
    )

    complete = int((trial_counts == 5).sum())

    print(f"Participants with exactly 5 trials: {complete}")

    duplicate_count = int(
        df.duplicated(
            subset=["participantId", "trialIndex"],
            keep=False,
        ).sum()
    )

    print(f"Duplicate participant/trial rows: {duplicate_count}")

    invalid_conditions = sorted(
        set(df["condition"].dropna().astype(str).str.lower())
        - EXPECTED_CONDITIONS
    )

    if invalid_conditions:
        print(
            "Unexpected conditions:",
            invalid_conditions,
        )

    unresolved = 0
    correctness = []

    for _, row in df.iterrows():
        calculated = diagnosis_is_correct(
            row["caseId"],
            row["diagnosis"],
        )

        supplied = row.get("diagnosis_correct")

        if pd.isna(supplied):
            final_value = calculated
        else:
            supplied_text = str(supplied).strip().lower()

            if supplied_text in {"true", "1", "yes"}:
                final_value = True
            elif supplied_text in {"false", "0", "no"}:
                final_value = False
            else:
                final_value = calculated

        if final_value is None:
            unresolved += 1

        correctness.append(final_value)

    df["correct_diagnosis"] = correctness
    df["diagnosis_correct"] = df["correct_diagnosis"]

    print(f"Unresolved correctness: {unresolved}")

    return df


def main():
    df = load_participants()

    if df.empty:
        return

    df = validate_data(df)

    if df.empty:
        return

    output = OUT_DIR / "participant_analysis.csv"
    df.to_csv(output, index=False)

    print(f"Participant analysis written to: {output}")
    print(f"Output rows: {len(df)}")


if __name__ == "__main__":
    main()
