"""Lightweight RAG evaluation metrics for A/B analysis.

These heuristics are intentionally dependency-free so TV4 can run analysis before
the team finalizes DeepEval/RAGAS credentials. They are not a replacement for
LLM-as-judge metrics, but they are useful for smoke testing and worst-case triage.
"""

from __future__ import annotations

import re
from statistics import mean
from typing import Iterable


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", (text or "").lower(), flags=re.UNICODE)


def token_overlap(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def context_text(retrieved: Iterable[dict]) -> str:
    return "\n".join(item.get("content", "") for item in retrieved or [])


def context_precision(question: str, retrieved: list[dict]) -> float:
    if not retrieved:
        return 0.0
    useful = 0
    for item in retrieved:
        if token_overlap(question, item.get("content", "")) >= 0.20:
            useful += 1
    return useful / len(retrieved)


def context_recall(expected_context: str, retrieved: list[dict]) -> float:
    if not expected_context:
        return 0.0
    return token_overlap(expected_context, context_text(retrieved))


def answer_relevance(question: str, answer: str) -> float:
    return token_overlap(question, answer)


def faithfulness(answer: str, retrieved: list[dict]) -> float:
    return token_overlap(answer, context_text(retrieved))


def score_case(item: dict, retrieved: list[dict], answer: str) -> dict:
    scores = {
        "faithfulness": faithfulness(answer, retrieved),
        "answer_relevance": answer_relevance(item.get("question", ""), answer),
        "context_recall": context_recall(item.get("expected_context", ""), retrieved),
        "context_precision": context_precision(item.get("question", ""), retrieved),
    }
    scores["average"] = mean(scores.values()) if scores else 0.0
    return scores


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {
            "faithfulness": 0.0,
            "answer_relevance": 0.0,
            "context_recall": 0.0,
            "context_precision": 0.0,
            "average": 0.0,
        }

    metric_names = [
        "faithfulness",
        "answer_relevance",
        "context_recall",
        "context_precision",
        "average",
    ]
    return {
        metric: mean(row["scores"][metric] for row in rows)
        for metric in metric_names
    }

