#!/usr/bin/env python3
"""
test_answer_relevancy.py --- unit tests for the answer relevancy metric

Contains:
    test_relevant_answer_scores_high: direct answer scores well
    test_tokenize_strips_stopwords: tokenizer drops stopwords
"""

from harness.test_case import LLMTestCase
from metrics.answer_relevancy import AnswerRelevancyMetric, tokenize
from metrics.judge import StubJudge


def make_case(question: str, answer: str) -> LLMTestCase:
    """Builds a minimal QA test case.

    Args:
        question: Input question text.
        answer: Generated answer text.

    Returns:
        test_case: LLMTestCase wrapping the pair.
    """
    return LLMTestCase(input=question, actual_output=answer)


def test_relevant_answer_scores_high() -> None:
    """Direct, overlapping answer scores above 0.9."""
    metric = AnswerRelevancyMetric(StubJudge(["yes"]))
    case = make_case("sky color", "sky color blue")
    assert metric.measure(case) > 0.9


def test_tokenize_strips_stopwords() -> None:
    """Tokenizer removes stopwords and lowercases."""
    assert tokenize("The Sky is Blue") == ["sky", "blue"]


def test_irrelevant_answer_scores_low() -> None:
    """Off-topic answer scores poorly."""
    metric = AnswerRelevancyMetric(StubJudge(["no"]))
    case = make_case("capital of france", "i like pizza toppings")
    assert metric.measure(case) < 0.25


def test_full_overlap_no_judge() -> None:
    """Full overlap with a no verdict still scores a half."""
    metric = AnswerRelevancyMetric(StubJudge(["no"]))
    assert metric.measure(make_case("sky color", "sky color")) == 0.5


def test_overlap_empty_question() -> None:
    """Empty question yields full overlap by convention."""
    metric = AnswerRelevancyMetric(StubJudge([]))
    assert metric.overlap("", "anything") == 1.0


def test_overlap_partial() -> None:
    """Partial token overlap yields a fraction."""
    metric = AnswerRelevancyMetric(StubJudge([]))
    assert metric.overlap("red green blue", "red") == 1 / 3


def test_judge_score_weight_half() -> None:
    """Judge verdict contributes half the score."""
    metric = AnswerRelevancyMetric(StubJudge(["yes"]))
    case = make_case("capital france", "unrelated words here")
    assert metric.measure(case) == 0.5


def test_overlap_full_when_identical() -> None:
    """Identical question and answer give full overlap."""
    metric = AnswerRelevancyMetric(StubJudge([]))
    assert metric.overlap("same words here", "same words here") == 1.0


def test_tokenize_handles_punctuation() -> None:
    """Tokenizer ignores punctuation."""
    assert tokenize("sky, blue!") == ["sky", "blue"]


def test_metric_name_stable() -> None:
    """Metric name is the stable registry key."""
    assert AnswerRelevancyMetric.name == "answer_relevancy"


def test_threshold_default() -> None:
    """Default threshold is 0.75."""
    assert AnswerRelevancyMetric(StubJudge([])).threshold == 0.75


def test_stopwords_frozen() -> None:
    """Stopword set is immutable."""
    import pytest

    from metrics.answer_relevancy import STOPWORDS

    with pytest.raises(AttributeError):
        STOPWORDS.add("x")


def test_verdict_case_insensitive() -> None:
    """Judge verdict parsing ignores casing."""
    metric = AnswerRelevancyMetric(StubJudge(["YES"]))
    assert metric.measure(make_case("", "")) >= 0.5


def test_overlap_symmetric_inputs_none_shared() -> None:
    """No shared tokens scores zero overlap."""
    metric = AnswerRelevancyMetric(StubJudge([]))
    assert metric.overlap("alpha beta", "gamma delta") == 0.0


def test_measure_returns_float() -> None:
    """Score is always a plain float."""
    metric = AnswerRelevancyMetric(StubJudge(["yes"]))
    assert isinstance(metric.measure(make_case("q words", "q words")), float)


def test_judge_weight_constant() -> None:
    """Judge verdict weight is pinned at one half."""
    from metrics.answer_relevancy import JUDGE_WEIGHT

    assert JUDGE_WEIGHT == 0.5


def test_is_on_topic_boundary() -> None:
    """On-topic boundary is inclusive of the threshold."""
    from metrics.answer_relevancy import is_on_topic

    assert is_on_topic(0.75) and not is_on_topic(0.74)


def test_tokenize_keeps_digits() -> None:
    """Tokenizer keeps numeric tokens."""
    assert tokenize("version 2 rocks") == ["version", "2", "rocks"]


def test_overlap_case_insensitive() -> None:
    """Overlap ignores casing."""
    metric = AnswerRelevancyMetric(StubJudge([]))
    assert metric.overlap("Sky", "sky") == 1.0


def test_measure_bounded() -> None:
    """Score stays within [0, 1]."""
    metric = AnswerRelevancyMetric(StubJudge(["yes"]))
    score = metric.measure(make_case("q", "a"))
    assert 0.0 <= score <= 1.0


def test_tokenize_empty_string() -> None:
    """Tokenizing an empty string yields no tokens."""
    assert tokenize("") == []
