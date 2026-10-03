"""Local RCAEval case loader for IncidentIQ.

This module intentionally does not download or commit raw telemetry.
It reads the local RCAEval metadata index and locates case folders on disk.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_metadata(metadata_path: str | Path) -> list[dict[str, Any]]:
    """Load RCAEval_ALL_735.json and return normalized row metadata."""
    path = Path(metadata_path)
    with path.open("r", encoding="utf-8-sig") as f:
        payload = json.load(f)

    return [item["row"] for item in payload["rows"]]


def filter_cases(
    rows: list[dict[str, Any]],
    suite: str = "RE2",
) -> list[dict[str, Any]]:
    """Filter metadata rows by RCAEval suite."""
    return [row for row in rows if row.get("suite") == suite]


def case_paths(data_root: str | Path, case_id: str) -> dict[str, Path | None]:
    """Return expected local telemetry paths for a downloaded case."""
    folder = Path(data_root) / case_id / case_id
    return {
        "root": folder,
        "metrics": folder / "metrics.parquet",
        "logs": folder / "logs.parquet",
        "traces": folder / "traces.parquet",
        "inject_time": folder / "inject_time.txt",
    }


def case_available(data_root: str | Path, case_id: str) -> bool:
    """Return True when a local case contains its metric file and injection time."""
    paths = case_paths(data_root, case_id)
    return bool(paths["metrics"].exists() and paths["inject_time"].exists())


def build_local_manifest(
    metadata_path: str | Path,
    data_root: str | Path,
    suite: str = "RE2",
) -> list[dict[str, Any]]:
    """Create a lightweight manifest without reading large telemetry files."""
    rows = filter_cases(load_metadata(metadata_path), suite=suite)
    manifest = []

    for row in rows:
        case_id = row["case"]
        paths = case_paths(data_root, case_id)
        manifest.append(
            {
                "case": case_id,
                "dataset": row.get("dataset"),
                "system": row.get("system_name"),
                                            "has_logs": paths["logs"].exists(),
                "has_traces": paths["traces"].exists(),
                "available": case_available(data_root, case_id),
            }
        )

    return manifest


def read_injection_time(data_root: str | Path, case_id: str) -> float:
    """Read the injection timestamp for a local case without loading labels."""
    path = case_paths(data_root, case_id)["inject_time"]
    if not path.exists():
        raise FileNotFoundError(f"Missing injection time: {path}")
    text = path.read_text(encoding="utf-8").strip()
    return float(text.splitlines()[0].strip())


def load_case_paths(data_root: str | Path, case_id: str) -> dict[str, Path | None]:
    """Return only participant-safe telemetry paths for a case."""
    paths = case_paths(data_root, case_id)
    return {
        "root": paths["root"],
        "metrics": paths["metrics"] if paths["metrics"].exists() else None,
        "logs": paths["logs"] if paths["logs"].exists() else None,
        "traces": paths["traces"] if paths["traces"].exists() else None,
    }
