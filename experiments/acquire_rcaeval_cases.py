"""Acquire only the RCAEval cases required for the IncidentIQ gray-area harness.

Raw telemetry stays outside Git. This script downloads exact case folders from the
official RCAEval Hugging Face dataset and verifies the expected local layout.
Existing verified case folders are reused so reruns do not download duplicate data.
"""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    from huggingface_hub import snapshot_download
except ImportError as exc:  # pragma: no cover - exercised in setup environments
    raise SystemExit(
        "huggingface_hub is required for RCAEval acquisition. "
        "Install the existing research dependency before running this script."
    ) from exc


CASES = (
    "re2ob_checkoutservice_cpu_2",
    "re2ob_checkoutservice_mem_2",
    "re2ss_user_loss_1",
    "re2ob_checkoutservice_loss_1",
    "re2ob_checkoutservice_loss_2",
)


def _case_root(root: Path, case_id: str) -> Path:
    base = root / case_id
    if (base / "metrics.parquet").exists() and (base / "inject_time.txt").exists():
        return base
    nested = base / case_id
    if (nested / "metrics.parquet").exists() and (nested / "inject_time.txt").exists():
        return nested
    return base


def _verify_case(root: Path, case_id: str) -> None:
    case_root = _case_root(root, case_id)
    required = [case_root / "metrics.parquet", case_root / "inject_time.txt"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(
            f"{case_id}: expected files are missing after acquisition: {missing}. "
            "Check the dataset case layout and retry only this acquisition step."
        )
    print(
        f"{case_id}: verified metrics.parquet + inject_time.txt; "
        f"logs={'yes' if (case_root / 'logs.parquet').exists() else 'no'}; "
        f"traces={'yes' if (case_root / 'traces.parquet').exists() else 'no'}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/rcaeval")
    parser.add_argument("--repo-id", default="phamquiluan/RCAEval")
    args = parser.parse_args()

    root = Path(args.data_root)
    root.mkdir(parents=True, exist_ok=True)

    for case_id in CASES:
        case_root = _case_root(root, case_id)
        if (case_root / "metrics.parquet").exists() and (case_root / "inject_time.txt").exists():
            print(f"{case_id}: existing verified case reused; no download needed")
            continue

        try:
            snapshot_download(
                repo_id=args.repo_id,
                repo_type="dataset",
                allow_patterns=[f"{case_id}/*", "cases.parquet"],
                local_dir=str(root),
            )
        except Exception as exc:
            raise RuntimeError(
                f"{case_id}: RCAEval acquisition failed: {exc}. "
                "No new copy should be created; inspect the existing data directory "
                "before retrying."
            ) from exc

        _verify_case(root, case_id)

    # Keep only metadata for the selected cases; this is researcher-side only.
    import pandas as pd

    index_path = root / "cases.parquet"
    if not index_path.exists():
        raise RuntimeError(
            f"RCAEval metadata index not found at {index_path}. "
            "The selected telemetry folders may exist, but the acquisition is not "
            "considered complete without cases.parquet."
        )

    selected = pd.read_parquet(index_path)
    if "case" not in selected.columns:
        raise RuntimeError(
            f"RCAEval metadata at {index_path} has no 'case' column; "
            "cannot safely build the selected-case metadata."
        )
    selected = selected[selected["case"].isin(CASES)]
    (root / "cases_metadata.json").write_text(
        selected.to_json(orient="records", indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
