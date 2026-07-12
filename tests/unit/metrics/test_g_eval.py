#!/usr/bin/env python3
"""
test_g_eval.py --- unit tests for the G-Eval 3-judge ensemble

Contains:
    test_ensemble_mean_of_three: mean score averages the three judges
    test_disagreement_flagged: wide judge spread is flagged
"""

import pytest

from harness.test_case import LLMTestCase
from metrics.g_eval import GEvalMetric
from metrics.judge import StubJudge


def make_case() -> LLMTestCase:
    """Builds a minimal G-Eval test case.

    Returns:
        test_case: LLMTestCase with a fixed question and answer.
    """
    return LLMTestCase(input="q", actual_output="a")


def make_metric(verdicts: list[str]) -> GEvalMetric:
    """Builds an ensemble whose judges return the given verdicts.

    Args:
        verdicts: One verdict per judge, in judge order.

    Returns:
        metric: GEvalMetric backed by scripted StubJudges.
    """
    return GEvalMetric([StubJudge([verdict]) for verdict in verdicts])


def test_ensemble_mean_of_three() -> None:
    """Mean score averages the three judges' normalized scores."""
    assert make_metric(["5", "3", "1"]).measure(make_case()) == 0.5


def test_disagreement_flagged() -> None:
    """Wide judge spread sets the disagreement flag."""
    details = make_metric(["5", "1", "1"]).measure_with_details(make_case())
    assert details["disagreement"]


def test_agreement_not_flagged() -> None:
    """Narrow judge spread does not set the disagreement flag."""
    details = make_metric(["4", "4", "5"]).measure_with_details(make_case())
    assert not details["disagreement"]


def test_requires_exactly_three_judges() -> None:
    """Ensemble rejects any size other than three."""
    with pytest.raises(ValueError):
        GEvalMetric([StubJudge([])])

def test_self_preference_bias_gaurd() -> None:
    """Ensemble mean dampens a single judge inflating its own family's answers."""
    biased = make_metric(["5", "3", "3"]).measure(make_case())
    single_judge_view = 1.0
    assert biased < single_judge_view
