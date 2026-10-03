import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from src.nlp.nli_evidence import NLIEvidenceInterpreter


def test_nli_rejects_empty_text_without_loading_model():
    model = NLIEvidenceInterpreter()
    with pytest.raises(ValueError):
        model.classify("", "resource saturation")


def test_nli_module_is_lazy_loaded():
    model = NLIEvidenceInterpreter()
    assert model._model is None
