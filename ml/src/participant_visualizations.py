from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "ml" / "results" / "participant_analysis.csv"
FIGURES = ROOT / "ml" / "figures"

FIGURES.mkdir(parents=True, exist_ok=True)


def main():
    if not INPUT.exists():
        print("Participant analysis file not found.")
        print(f"Expected: {INPUT}")
        print("Waiting for real participant study data.")
        return

    df = pd.read_csv(INPUT)

    required = [
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
        raise ValueError(f"Missing columns: {missing}")

    # 1. Condition vs correctness
    condition_accuracy = (
        df.groupby("condition")["diagnosis_correct"]
        .mean()
        .sort_index()
    )

    condition_accuracy.plot(kind="bar")
    plt.ylabel("Diagnosis correctness")
    plt.xlabel("Condition")
    plt.title("Diagnosis Correctness by Incident Condition")
    plt.tight_layout()
    plt.savefig(
        FIGURES / "condition_vs_correctness.png",
        dpi=200,
    )
    plt.close()

    # 2. Confidence by condition
    confidence = (
        df.groupby("condition")["confidence"]
        .mean()
        .sort_index()
    )

    confidence.plot(kind="bar")
    plt.ylabel("Mean confidence")
    plt.xlabel("Condition")
    plt.title("Confidence by Incident Condition")
    plt.tight_layout()
    plt.savefig(
        FIGURES / "confidence_by_condition.png",
        dpi=200,
    )
    plt.close()

    # 3. Workload by condition
    workload = (
        df.groupby("condition")["workload"]
        .mean()
        .sort_index()
    )

    workload.plot(kind="bar")
    plt.ylabel("Mean workload")
    plt.xlabel("Condition")
    plt.title("Workload by Incident Condition")
    plt.tight_layout()
    plt.savefig(
        FIGURES / "workload_by_condition.png",
        dpi=200,
    )
    plt.close()

    # 4. Elapsed time by condition
    elapsed = (
        df.groupby("condition")["elapsedSeconds"]
        .mean()
        .sort_index()
    )

    elapsed.plot(kind="bar")
    plt.ylabel("Mean elapsed seconds")
    plt.xlabel("Condition")
    plt.title("Diagnostic Time by Incident Condition")
    plt.tight_layout()
    plt.savefig(
        FIGURES / "time_by_condition.png",
        dpi=200,
    )
    plt.close()

    print(f"Figures created in: {FIGURES}")
    print("1. condition_vs_correctness.png")
    print("2. confidence_by_condition.png")
    print("3. workload_by_condition.png")
    print("4. time_by_condition.png")


if __name__ == "__main__":
    main()
