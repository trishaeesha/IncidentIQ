"""Build a local RCAEval RE2 manifest and a deterministic diverse candidate pool.

Raw telemetry stays on the user's machine. Generated CSVs are ignored by Git.
The six gray-area conditions are intentionally NOT assigned here: they must be
validated from evidence rather than inferred from metadata alone.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.rcaeval_loader import build_local_manifest, load_metadata, filter_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--candidate-count", type=int, default=90)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = filter_cases(load_metadata(args.metadata), suite="RE2")
    meta = {r["case"]: r for r in rows}
    manifest = pd.DataFrame(
        build_local_manifest(args.metadata, args.data_root, suite="RE2")
    )

    if len(manifest) != 270:
        raise RuntimeError(f"Expected 270 RE2 cases, found {len(manifest)}.")

    manifest["fault_description"] = manifest["case"].map(
        lambda c: meta[c].get("fault_description")
    )
    manifest["n_metrics"] = manifest["case"].map(lambda c: meta[c].get("n_metrics"))
    manifest["n_timesteps"] = manifest["case"].map(
        lambda c: meta[c].get("n_timesteps")
    )
    manifest["duration_minutes"] = manifest["case"].map(
        lambda c: meta[c].get("duration_minutes")
    )
    manifest["n_logs"] = manifest["case"].map(lambda c: meta[c].get("n_logs", 0))
    manifest["n_traces"] = manifest["case"].map(
        lambda c: meta[c].get("n_traces", 0)
    )
    manifest["injection_time"] = manifest["case"].map(
        lambda c: meta[c].get("injection_time")
    )

    # Research-controlled fields. Leave condition blank until telemetry-based
    # evidence analysis and human validation are complete.
    manifest["condition"] = ""
    manifest["condition_validation_status"] = "unvalidated"
    manifest["selected_for_benchmark"] = False
    manifest["selection_reason"] = ""

    # Deterministic candidate pool: spread cases across system, fault and
    # repetition without treating repetitions as independent incidents.
    # This is a DIVERSE POOL, not the final 6-condition benchmark.
    manifest = manifest.sort_values(
        ["system", "fault", "repetition", "case"], kind="stable"
    ).reset_index(drop=True)

    groups = manifest.groupby(["system", "fault"], sort=True)
    per_group = max(1, args.candidate_count // len(groups))
    selected_parts = []
    for _, group in groups:
        reps = group.sort_values(["repetition", "case"])
        selected_parts.append(reps.head(per_group))

    candidates = pd.concat(selected_parts, ignore_index=True).drop_duplicates("case")

    # Fill any shortfall deterministically from cases not yet selected.
    if len(candidates) < args.candidate_count:
        remaining = manifest[~manifest["case"].isin(candidates["case"])]
        candidates = pd.concat(
            [candidates, remaining.head(args.candidate_count - len(candidates))]
        )

    candidates = candidates.head(args.candidate_count).copy()
    manifest.loc[manifest["case"].isin(candidates["case"]), "selected_for_benchmark"] = True
    manifest.loc[
        manifest["case"].isin(candidates["case"]), "selection_reason"
    ] = "diverse candidate pool; condition not yet validated"

    manifest.to_csv(output_dir / "rcaeval_re2_manifest.csv", index=False)
    candidates.to_csv(output_dir / "rcaeval_re2_candidate_pool.csv", index=False)

    print(f"RE2 cases: {len(manifest)}")
    print(f"Locally available: {int(manifest['available'].sum())}")
    print(f"Candidate pool: {len(candidates)}")
    print(f"Systems: {manifest['system'].nunique()}")
    print(f"Fault types: {manifest['fault'].nunique()}")
    print("Gray-area conditions remain UNVALIDATED by design.")
    print(f"Manifest: {output_dir / 'rcaeval_re2_manifest.csv'}")
    print(f"Candidates: {output_dir / 'rcaeval_re2_candidate_pool.csv'}")


if __name__ == "__main__":
    main()
