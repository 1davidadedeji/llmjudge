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

def test_self_preference_bias_guard() -> None:
    """Ensemble mean dampens a single judge inflating its own family's answers."""
    biased = make_metric(["5", "3", "3"]).measure(make_case())
    single_judge_view = 1.0
    assert biased < single_judge_view

def test_parse_score_still_handles_prose() -> None:
    """Ensemble judge verdict parsing still finds digits in prose."""
    assert make_metric(["4"]).parse_score("a solid 4") == 0.75

def test_each_judge_called_once() -> None:
    """Every judge in the ensemble is consulted exactly once."""
    judges = [StubJudge(["4"]), StubJudge(["4"]), StubJudge(["4"])]
    GEvalMetric(judges).measure(make_case())
    assert all(len(judge.calls) == 1 for judge in judges)

def test_per_judge_breakdown_labels() -> None:
    """Breakdown labels judges by position."""
    from metrics.g_eval import per_judge_breakdown

    assert per_judge_breakdown([0.1, 0.2, 0.3])["judge_b"] == 0.2

def test_ensemble_details_keys() -> None:
    """measure_with_details exposes scores, mean, and disagreement."""
    details = make_metric(["4", "4", "4"]).measure_with_details(make_case())
    assert set(details) == {"scores", "mean", "disagreement"}

def test_should_escalate_follows_flag() -> None:
    """Escalation follows the disagreement flag."""
    from metrics.g_eval import should_escalate

    assert should_escalate(True) and not should_escalate(False)

def test_verdict_with_text_around() -> None:
    """Prose around the digit still parses."""
    assert GEvalMetric(StubJudge(["score: 5"])).measure(make_case()) == 1.0

def test_mean_of_all_ones_is_zero() -> None:
    """Three 1 verdicts average to 0.0."""
    assert make_metric(["1", "1", "1"]).measure(make_case()) == 0.0
