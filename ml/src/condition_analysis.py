from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "ml" / "results" / "participant_analysis.csv"
OUTPUT = ROOT / "ml" / "results" / "condition_analysis.csv"


def main():
    if not INPUT.exists():
        print("Participant analysis file not found.")
        print(f"Expected: {INPUT}")
        print("Waiting for real participant study data.")
        return

    df = pd.read_csv(INPUT)

    required = [
        "participantId",
        "condition",
        "diagnosis_correct",
        "confidence",
        "workload",
        "elapsedSeconds",
    ]

    missing = [
        column for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    summary = (
        df.groupby("condition")
        .agg(
            trials=("diagnosis_correct", "size"),
            accuracy=("diagnosis_correct", "mean"),
            mean_confidence=("confidence", "mean"),
            mean_workload=("workload", "mean"),
            mean_elapsed_seconds=("elapsedSeconds", "mean"),
        )
        .reset_index()
    )

    summary["accuracy_percent"] = (
        summary["accuracy"] * 100
    )

    summary.to_csv(OUTPUT, index=False)

    print(f"Output: {OUTPUT}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
