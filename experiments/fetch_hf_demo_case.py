"""Fetch one public RCAEval telemetry case for local IncidentIQ demonstration.

This downloads telemetry only. Evaluator labels are not loaded into the IncidentIQ
pipeline by run_real_rcaeval_case.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


DEFAULT_CASE = "re2ob_checkoutservice_cpu_2"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=DEFAULT_CASE)
    parser.add_argument("--out", default="demo_data")
    args = parser.parse_args()

    out = Path(args.out)
    snapshot_download(
        repo_id="phamquiluan/RCAEval",
        repo_type="dataset",
        allow_patterns=[f"{args.case}/*"],
        local_dir=out,
    )

    case_dir = out / args.case
    required = ["metrics.parquet", "inject_time.txt"]
    missing = [name for name in required if not (case_dir / name).exists()]
    if missing:
        raise SystemExit(f"Downloaded case is incomplete; missing: {missing}")

    print(f"Downloaded public RCAEval telemetry for {args.case} to {case_dir}")
    print("Ground-truth labels are not passed to the IncidentIQ inference pipeline.")


if __name__ == "__main__":
    main()
