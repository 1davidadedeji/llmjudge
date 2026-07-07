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

def test_bottom_score_normalizes_to_zero() -> None:
    """A 1 verdict normalizes to 0.0."""
    assert GEvalMetric(StubJudge(["1"])).measure(make_case()) == 0.0

def test_mid_score_normalizes_to_half() -> None:
    """A 3 verdict normalizes to 0.5."""
    assert GEvalMetric(StubJudge(["3"])).measure(make_case()) == 0.5

def test_unparseable_verdict_scores_zero() -> None:
    """No digit in the verdict scores 0.0."""
    metric = GEvalMetric(StubJudge([]))
    assert metric.parse_score("no idea") == 0.0

def test_custom_rubric_used_in_prompt() -> None:
    """The configured rubric is sent to the judge."""
    judge = StubJudge(["5"])
    GEvalMetric(judge, rubric="custom-rubric-text").measure(make_case())
    assert "custom-rubric-text" in judge.calls[0]

def test_default_rubric_when_unset() -> None:
    """Default rubric is used when none is given."""
    assert GEvalMetric(StubJudge([])).rubric.startswith("1: wrong")

def test_threshold_default() -> None:
    """Default threshold is 0.7."""
    assert GEvalMetric(StubJudge([])).threshold == 0.7

def test_metric_name_stable() -> None:
    """Metric name is the stable registry key."""
    assert GEvalMetric.name == "g_eval"

def test_score_includes_question() -> None:
    """The question is included in the judge prompt."""
    judge = StubJudge(["5"])
    GEvalMetric(judge).measure(LLMTestCase(input="unique-question", actual_output="a"))
    assert "unique-question" in judge.calls[0]

def test_score_includes_answer() -> None:
    """The answer is included in the judge prompt."""
    judge = StubJudge(["5"])
    GEvalMetric(judge).measure(LLMTestCase(input="q", actual_output="unique-answer"))
    assert "unique-answer" in judge.calls[0]

def test_parse_first_digit_wins() -> None:
    """Parsing uses the first 1-5 digit in the verdict."""
    metric = GEvalMetric(StubJudge([]))
    assert metric.parse_score("2 then 4") == 0.25

def test_prompt_version_pinned() -> None:
    """Prompt version is pinned for attributable score changes."""
    from metrics.g_eval import G_EVAL_PROMPT_VERSION

    assert G_EVAL_PROMPT_VERSION == 1

def test_rubric_score_label_bands() -> None:
    """Score labels follow the three-band mapping."""
    from metrics.g_eval import rubric_score_label

    assert rubric_score_label(0.9) == "excellent"
    assert rubric_score_label(0.5) == "adequate"
    assert rubric_score_label(0.1) == "poor"

def test_parse_ignores_embedded_digits() -> None:
    """Digits inside longer numbers are not treated as scores."""
    metric = GEvalMetric(StubJudge([]))
    assert metric.parse_score("rated 45 out of 50") == 0.0

def test_score_two_normalizes_quarter() -> None:
    """A 2 verdict normalizes to 0.25."""
    assert GEvalMetric(StubJudge(["2"])).measure(make_case()) == 0.25

def test_score_four_normalizes_three_quarter() -> None:
    """A 4 verdict normalizes to 0.75."""
    assert GEvalMetric(StubJudge(["4"])).measure(make_case()) == 0.75

def test_threshold_custom() -> None:
    """Custom threshold is stored."""
    assert GEvalMetric(StubJudge([]), threshold=0.9).threshold == 0.9
