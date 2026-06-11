#!/usr/bin/env python3
"""
test_g_eval.py --- unit tests for the G-Eval custom rubric judge

Contains:
    test_top_score_normalizes_to_one: a 5 verdict scores 1.0
    test_parse_score_extracts_digit: verdict parsing finds the digit
"""

from harness.test_case import LLMTestCase
from metrics.g_eval import GEvalMetric
from metrics.judge import StubJudge


def make_case() -> LLMTestCase:
    """Builds a minimal G-Eval test case.

    Returns:
        test_case: LLMTestCase with a fixed question and answer.
    """
    return LLMTestCase(input="q", actual_output="a")


def test_top_score_normalizes_to_one() -> None:
    """A 5 verdict from the judge normalizes to 1.0."""
    assert GEvalMetric(StubJudge(["5"])).measure(make_case()) == 1.0


def test_parse_score_extracts_digit() -> None:
    """Verdict parsing finds the score digit in prose."""
    metric = GEvalMetric(StubJudge([]))
    assert metric.parse_score("I would rate this a 3 overall") == 0.5
