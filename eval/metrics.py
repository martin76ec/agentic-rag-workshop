"""
Retrieval-quality metrics over a gold set.

The gold set lives in eval/gold_set.json. Each item is:
    {"query": "...", "expected_services": ["svc1", "svc2", ...]}

A retriever returns a ranked list of service names. We score that list
against the expected set with three standard IR metrics.
"""
from __future__ import annotations

from collections.abc import Sequence


def recall_at_k(retrieved: Sequence[str], expected: Sequence[str], k: int) -> float:
    """Fraction of expected services that appear in the top-k retrieved.

    1.0 means every expected service was found; 0.0 means none were.
    """
    if not expected:
        return 0.0
    top_k = set(retrieved[:k])
    found = sum(1 for s in expected if s in top_k)
    return found / len(expected)


def precision_at_k(retrieved: Sequence[str], expected: Sequence[str], k: int) -> float:
    """Fraction of the top-k retrieved that were expected.

    Punishes returning irrelevant services even if recall is high.
    """
    top_k = list(retrieved[:k])
    if not top_k:
        return 0.0
    expected_set = set(expected)
    return sum(1 for s in top_k if s in expected_set) / len(top_k)


def reciprocal_rank(retrieved: Sequence[str], expected: Sequence[str]) -> float:
    """1 / rank of the first expected service in the retrieved list.

    Returns 0.0 if no expected service was retrieved at all.
    """
    expected_set = set(expected)
    for rank, svc in enumerate(retrieved, start=1):
        if svc in expected_set:
            return 1.0 / rank
    return 0.0


def aggregate(scores: list[float]) -> float:
    """Mean of a list of per-query scores. Used for MRR and macro-averaged P/R."""
    return sum(scores) / len(scores) if scores else 0.0
