"""Regression test for the researcher report field contract."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_build_research_report_uses_scored_records(tmp_path: Path) -> None:
    telemetry = tmp_path / "telemetry.json"
    analysis = tmp_path / "analysis.json"
    output = tmp_path / "report.json"

    telemetry.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "case_id": "case-1",
                        "condition": "clear",
                        "status": "VALIDATED",
                        "telemetry_verified": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    analysis.write_text(
        json.dumps({"participant_records": 1, "scored_records": 1}),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            "experiments/build_research_report.py",
            "--telemetry",
            str(telemetry),
            "--analysis",
            str(analysis),
            "--out",
            str(output),
        ],
        check=True,
    )

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["engineering_validation"]["human_results_available"] is True
    assert report["conclusion_status"] == "READY_FOR_EVIDENCE_REVIEW"
