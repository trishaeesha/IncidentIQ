"""Contextual evidence-to-hypothesis relation using pretrained NLI.

This is an experimental component. It does not determine root cause by itself;
it only estimates whether an observation entails, contradicts, or is neutral
toward a candidate hypothesis.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


LABELS = ("contradiction", "entailment", "neutral")
DEFAULT_MODEL = "cross-encoder/nli-deberta-v3-xsmall"


@dataclass(frozen=True)
class NLIResult:
    evidence: str
    hypothesis: str
    relation: str
    score: float


class NLIEvidenceInterpreter:
    """Lazy-loaded NLI model so the core deterministic baseline stays lightweight."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as exc:
                raise RuntimeError(
                    "Optional NLI dependencies are not installed. "
                    "Install requirements-nlp.txt to enable this experiment."
                ) from exc
            self._model = CrossEncoder(self.model_name)
        return self._model

    def classify(self, evidence: str, hypothesis: str) -> NLIResult:
        if not evidence.strip() or not hypothesis.strip():
            raise ValueError("evidence and hypothesis must be non-empty")
        scores = self._load().predict([(evidence, hypothesis)])[0]
        # SentenceTransformers NLI models expose scores in the documented
        # contradiction / entailment / neutral order.
        index = int(scores.argmax())
        return NLIResult(
            evidence=evidence,
            hypothesis=hypothesis,
            relation=LABELS[index],
            score=float(scores[index]),
        )

    def classify_many(
        self, pairs: Iterable[tuple[str, str]]
    ) -> list[NLIResult]:
        pairs = list(pairs)
        if not pairs:
            return []
        model = self._load()
        scores = model.predict(pairs)
        results = []
        for (evidence, hypothesis), row in zip(pairs, scores):
            index = int(row.argmax())
            results.append(
                NLIResult(
                    evidence=evidence,
                    hypothesis=hypothesis,
                    relation=LABELS[index],
                    score=float(row[index]),
                )
            )
        return results
