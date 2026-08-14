#!/usr/bin/env python3
"""
test_faithfulness_golden.py --- golden-set tests pinning faithfulness behavior

Contains:
    test_golden_cases: every golden case scores inside its expected band
    load_golden_cases(): parses the golden dataset
"""

import json
from pathlib import Path

import pytest

from harness.test_case import LLMTestCase
from metrics.faithfulness import FaithfulnessMetric
from metrics.judge import StubJudge

GOLDEN_PATH = Path(__file__).parent / "data" / "faithfulness_gold.jsonl"


def load_golden_cases() -> list[dict]:
    """Parses the golden dataset.

    Returns:
        cases: Golden case dicts with answer, context, verdicts, and score band.
    """
    with open(GOLDEN_PATH) as fh:
        return [json.loads(line) for line in fh if line.strip()]


@pytest.mark.parametrize("case", load_golden_cases(), ids=lambda c: c["id"])
def test_golden_cases(case: dict) -> None:
    """Every golden case scores inside its expected band."""
    metric = FaithfulnessMetric(StubJudge(case["verdicts"]))
    test_case = LLMTestCase(
        input=case["question"], actual_output=case["answer"], retrieval_context=case["context"]
    )
    score = metric.measure(test_case)
    assert case["min_score"] <= score <= case["max_score"], case["id"]

def test_golden_ids_unique() -> None:
    """Golden case ids never collide."""
    ids = [case["id"] for case in load_golden_cases()]
    assert len(ids) == len(set(ids))
