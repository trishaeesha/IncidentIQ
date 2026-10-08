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


def diagnosis_is_correct(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    text = str(value).strip().lower()

    if text in {"true", "correct", "1", "yes"}:
        return True

    if text in {"false", "incorrect", "0", "no"}:
        return False

    return None


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

        for trial in participant.get("trials", []):
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

    print(f"Participant files loaded: {df['participantId'].nunique()}")
    print(f"Trial rows loaded: {len(df)}")

    unexpected = sorted(
        set(df["condition"].dropna().astype(str).str.lower())
        - EXPECTED_CONDITIONS
    )

    if unexpected:
        raise ValueError(
            f"Unexpected conditions found: {unexpected}"
        )

    df["diagnosis_correct"] = df["diagnosis"].apply(
        diagnosis_is_correct
    )

    duplicate_count = df.duplicated(
        subset=["participantId", "trialIndex"]
    ).sum()

    print(f"Duplicate participant/trial rows: {duplicate_count}")

    complete_counts = (
        df.groupby("participantId")
        .size()
        .sort_values()
    )

    print(
        f"Participants with exactly 5 trials: "
        f"{(complete_counts == 5).sum()}"
    )

    output = OUT_DIR / "participant_analysis.csv"
    df.to_csv(output, index=False)

    print(f"Output: {output}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()
