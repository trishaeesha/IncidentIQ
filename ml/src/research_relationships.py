from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "ml" / "results" / "participant_analysis.csv"
OUTPUT = ROOT / "ml" / "results" / "research_relationships.csv"


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
        "aiFollowed",
        "aiOverridden",
    ]

    missing = [
        column for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    for column in ["aiFollowed", "aiOverridden"]:
        df[column] = (
            df[column]
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

    rows = []

    def add_relationship(name, subset):
        if len(subset) == 0:
            return

        rows.append({
            "relationship": name,
            "trials": len(subset),
            "accuracy": subset["diagnosis_correct"].mean(),
            "mean_confidence": subset["confidence"].mean(),
            "mean_workload": subset["workload"].mean(),
            "mean_elapsed_seconds": subset["elapsedSeconds"].mean(),
        })

    add_relationship(
        "AI followed",
        df[df["aiFollowed"] == 1],
    )

    add_relationship(
        "AI not followed",
        df[df["aiFollowed"] == 0],
    )

    add_relationship(
        "AI overridden",
        df[df["aiOverridden"] == 1],
    )

    add_relationship(
        "AI not overridden",
        df[df["aiOverridden"] == 0],
    )

    add_relationship(
        "Conflicting condition",
        df[df["condition"] == "conflicting"],
    )

    add_relationship(
        "Misleading condition",
        df[df["condition"] == "misleading"],
    )

    add_relationship(
        "Incomplete condition",
        df[df["condition"] == "incomplete"],
    )

    add_relationship(
        "Ambiguous condition",
        df[df["condition"] == "ambiguous"],
    )

    add_relationship(
        "Clear condition",
        df[df["condition"] == "clear"],
    )

    output_df = pd.DataFrame(rows)

    output_df.to_csv(OUTPUT, index=False)

    print(f"Output: {OUTPUT}")
    print(output_df.to_string(index=False))


if __name__ == "__main__":
    main()
