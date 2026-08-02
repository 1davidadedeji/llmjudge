#!/usr/bin/env python3
"""
test_contextual_precision_recall.py --- unit tests for retrieval quality metrics

Contains:
    test_precision_perfect_ranking: all-relevant ranking scores one
    test_recall_full_coverage: fully supported expectation scores one
"""

from harness.test_case import LLMTestCase
from metrics.contextual_precision_recall import ContextualPrecisionMetric, ContextualRecallMetric
from metrics.judge import StubJudge


def make_case(passages: list[str], expected: str | None = None) -> LLMTestCase:
    """Builds a retrieval test case.

    Args:
        passages: Ranked retrieved passages.
        expected: Expected answer text, if any.

    Returns:
        test_case: LLMTestCase wrapping the retrieval data.
    """
    return LLMTestCase(
        input="q", actual_output="a", expected_output=expected, retrieval_context=passages
    )


def test_precision_perfect_ranking() -> None:
    """All-relevant ranking scores a perfect precision."""
    metric = ContextualPrecisionMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case(["p1", "p2"])) == 1.0


def test_recall_full_coverage() -> None:
    """Fully supported expectation scores a perfect recall."""
    metric = ContextualRecallMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case(["p1", "p2"], expected="exp")) == 1.0

def test_precision_empty_context() -> None:
    """Empty retrieval scores precision one by convention."""
    assert ContextualPrecisionMetric(StubJudge([])).measure(make_case([])) == 1.0

def test_recall_empty_context() -> None:
    """Empty retrieval scores recall one by convention."""
    assert ContextualRecallMetric(StubJudge([])).measure(make_case([], expected="e")) == 1.0

def test_recall_single_passage_support() -> None:
    """One supporting passage out of one scores recall one."""
    metric = ContextualRecallMetric(StubJudge(["yes"]))
    assert metric.measure(make_case(["p"], expected="e")) == 1.0

def test_recall_no_expected_output() -> None:
    """Missing expected output scores recall one."""
    assert ContextualRecallMetric(StubJudge([])).measure(make_case(["p"])) == 1.0

def test_precision_none_relevant() -> None:
    """No relevant passages scores zero."""
    metric = ContextualPrecisionMetric(StubJudge(["no", "no"]))
    assert metric.measure(make_case(["p1", "p2"])) == 0.0

def test_precision_two_of_two_late() -> None:
    """Both relevant but ordered still scores one."""
    metric = ContextualPrecisionMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case(["p1", "p2"])) == 1.0

def test_precision_relevant_late_scores_lower() -> None:
    """Relevant-late ranking beats none but loses to early."""
    early = ContextualPrecisionMetric(StubJudge(["yes", "no"]))
    late = ContextualPrecisionMetric(StubJudge(["no", "yes"]))
    assert early.measure(make_case(["p1", "p2"])) > late.measure(make_case(["p1", "p2"]))

def test_recall_partial_coverage() -> None:
    """Partial support yields fractional recall."""
    metric = ContextualRecallMetric(StubJudge(["yes", "no"]))
    assert metric.measure(make_case(["p1", "p2"], expected="e")) == 0.5

def test_precision_metric_name() -> None:
    """Precision metric name is stable."""
    assert ContextualPrecisionMetric.name == "contextual_precision"

def test_recall_metric_name() -> None:
    """Recall metric name is stable."""
    assert ContextualRecallMetric.name == "contextual_recall"

def test_precision_single_relevant_first() -> None:
    """Single relevant passage at rank one scores one."""
    metric = ContextualPrecisionMetric(StubJudge(["yes", "no", "no"]))
    assert metric.measure(make_case(["p1", "p2", "p3"])) == 1.0

def test_verdict_parsing_no() -> None:
    """A no verdict counts as not relevant."""
    metric = ContextualPrecisionMetric(StubJudge(["no"]))
    assert not metric.is_relevant("p", "q")

def test_average_precision_empty() -> None:
    """Average precision of an empty ranking is zero."""
    from metrics.contextual_precision_recall import average_precision

    assert average_precision([]) == 0.0

def test_average_precision_matches_metric() -> None:
    """Standalone average precision matches the metric's ranking math."""
    from metrics.contextual_precision_recall import average_precision

    assert average_precision([True, False, True]) > average_precision([False, True, True])

def test_precision_delegates_to_average_precision() -> None:
    """Metric precision matches the standalone average-precision helper."""
    metric = ContextualPrecisionMetric(StubJudge(["yes", "no", "yes"]))
    score = metric.measure(make_case(["p1", "p2", "p3"]))
    assert 0.0 < score < 1.0

def test_precision_threshold_stored() -> None:
    """Threshold is stored on the metric."""
    assert ContextualPrecisionMetric(StubJudge([]), threshold=0.6).threshold == 0.6

def test_recall_threshold_stored() -> None:
    """Recall threshold is stored."""
    assert ContextualRecallMetric(StubJudge([]), threshold=0.65).threshold == 0.65

def test_recall_at_k_window() -> None:
    """Recall@k ignores passages past the cutoff."""
    from metrics.contextual_precision_recall import recall_at_k

    assert recall_at_k([True, False, False], 1) == 1.0

def test_precision_verdict_prompt_fields() -> None:
    """Relevance prompt embeds passage and question."""
    judge = StubJudge(["yes"])
    ContextualPrecisionMetric(judge).is_relevant("some-passage", "some-question")
    assert "some-passage" in judge.calls[0] and "some-question" in judge.calls[0]

def test_recall_supports_prompt_fields() -> None:
    """Coverage prompt embeds passage and expectation."""
    judge = StubJudge(["yes"])
    ContextualRecallMetric(judge).supports("some-passage", "some-expected")
    assert "some-passage" in judge.calls[0] and "some-expected" in judge.calls[0]

def test_mrr_first_relevant_rank() -> None:
    """MRR uses the rank of the first relevant passage."""
    from metrics.contextual_precision_recall import mrr

    assert mrr([False, True]) == 0.5
