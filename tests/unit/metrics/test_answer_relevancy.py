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
    case = make_case("what color is the sky", "the sky is blue")
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
