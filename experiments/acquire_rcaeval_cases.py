"""Acquire only the RCAEval cases required for the IncidentIQ gray-area harness.

Raw telemetry stays outside Git. This script downloads exact case folders from the
official RCAEval Hugging Face dataset and verifies the expected local layout.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


CASES = (
    "re2ob_checkoutservice_cpu_2",
    "re2ob_checkoutservice_mem_2",
    "re2ss_user_loss_1",
    "re2ob_checkoutservice_loss_1",
    "re2ob_checkoutservice_loss_2",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/rcaeval")
    parser.add_argument("--repo-id", default="phamquiluan/RCAEval")
    args = parser.parse_args()

    root = Path(args.data_root)
    root.mkdir(parents=True, exist_ok=True)

    for case_id in CASES:
        snapshot_download(
            repo_id=args.repo_id,
            repo_type="dataset",
            allow_patterns=[f"{case_id}/*", "cases.parquet"],
            local_dir=str(root),
        )

        case_root = root / case_id
        # Some snapshot layouts may nest the case folder once more.
        if not (case_root / "metrics.parquet").exists():
            nested = case_root / case_id
            if nested.exists():
                case_root = nested

        required = [case_root / "metrics.parquet", case_root / "inject_time.txt"]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(
                f"{case_id}: acquisition completed but expected files are missing: {missing}"
            )

        print(
            f"{case_id}: verified metrics.parquet + inject_time.txt; "
            f"logs={'yes' if (case_root / 'logs.parquet').exists() else 'no'}; "
            f"traces={'yes' if (case_root / 'traces.parquet').exists() else 'no'}"
        )

    # Keep only metadata for the selected cases; this is researcher-side only.
    import pandas as pd
    index_path = root / "cases.parquet"
    if index_path.exists():
        selected = pd.read_parquet(index_path)
        selected = selected[selected["case"].isin(CASES)]
        (root / "cases_metadata.json").write_text(
            selected.to_json(orient="records", indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
