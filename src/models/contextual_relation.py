"""Context-aware evidence relation baseline.

This is deliberately non-LLM: it tests whether preserving service/signal/time
context fixes the failure before adding a learned language model.
"""
from __future__ import annotations
import re

def relate(evidence: dict, hypothesis: str) -> str:
    text = " ".join(str(evidence.get(k,"")) for k in ("observation","signal","service")).lower()
    h = hypothesis.lower()
    if "resource saturation" in h:
        if re.search(r"\b(cpu|mem|memory|load|resource)\b", text):
            return "supporting"
    if "database or storage pressure" in h:
        if re.search(r"\b(disk|diskio|storage|io|database|db)\b", text):
            return "supporting"
    if "error or failure increase" in h:
        if re.search(r"(?<![a-z])(error|failure|exception|warning)(?![a-z])", text):
            return "supporting"
    return "neutral"
