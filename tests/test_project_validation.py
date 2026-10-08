from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]

PYTHON_FILES = [
    ROOT / "ml" / "src" / "participant_analysis.py",
    ROOT / "ml" / "src" / "participant_ml.py",
    ROOT / "ml" / "src" / "condition_analysis.py",
    ROOT / "ml" / "src" / "research_relationships.py",
    ROOT / "ml" / "src" / "participant_visualizations.py",
]


def test_required_python_files_exist():
    for path in PYTHON_FILES:
        assert path.exists(), f"Missing required file: {path}"


def test_python_files_compile():
    for path in PYTHON_FILES:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))


def test_required_documentation_exists():
    required = [
        ROOT / "DATA_DICTIONARY.md",
        ROOT / "REPRODUCIBILITY.md",
        ROOT / "RESEARCH_ANALYSIS_WORKFLOW.md",
        ROOT / "RESULTS_TEMPLATE.md",
        ROOT / "REPORT_STRUCTURE.md",
        ROOT / "PRESENTATION_STRUCTURE.md",
    ]

    for path in required:
        assert path.exists(), f"Missing documentation: {path}"


def test_participant_ml_does_not_use_participant_id_as_feature():
    path = ROOT / "ml" / "src" / "participant_ml.py"
    source = path.read_text(encoding="utf-8")

    assert '"participantId"' not in source.split("features =", 1)[-1].split("]", 1)[0]


def test_participant_pipeline_has_no_fake_result_generation():
    for path in PYTHON_FILES:
        source = path.read_text(encoding="utf-8").lower()

        suspicious = [
            "fake participant",
            "synthetic participant result",
            "generate_fake_results",
            "generate_synthetic_results",
        ]

        for phrase in suspicious:
            assert phrase not in source, f"Suspicious phrase in {path}: {phrase}"
