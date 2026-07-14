#!/usr/bin/env python3
"""
test_faithfulness.py --- unit tests for the faithfulness metric

Contains:
    test_all_claims_entailed_scores_one: grounded answer gets full marks
    test_no_claims_scores_one: empty answer is vacuously faithful
"""

from harness.test_case import LLMTestCase
from metrics.faithfulness import FaithfulnessMetric
from metrics.judge import StubJudge


def make_case(answer: str, context: list[str]) -> LLMTestCase:
    """Builds a minimal RAG test case.

    Args:
        answer: Generated answer text.
        context: Retrieved context passages.

    Returns:
        test_case: LLMTestCase wrapping the answer and context.
    """
    return LLMTestCase(input="q", actual_output=answer, retrieval_context=context)


def test_all_claims_entailed_scores_one() -> None:
    """Grounded answer gets a perfect faithfulness score."""
    metric = FaithfulnessMetric(StubJudge(["yes", "yes"]))
    case = make_case("The sky is blue. Water is wet.", ["The sky is blue and water is wet."])
    assert metric.measure(case) == 1.0


def test_no_claims_scores_one() -> None:
    """Empty answer is vacuously faithful."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert metric.measure(make_case("", ["anything"])) == 1.0

def test_threshold_out_of_range_rejected() -> None:
    """Thresholds outside [0, 1] raise a ValueError."""
    import pytest

    with pytest.raises(ValueError):
        FaithfulnessMetric(StubJudge([]), threshold=1.5)

def test_half_claims_entailed() -> None:
    """Mixed verdicts yield a fractional score."""
    metric = FaithfulnessMetric(StubJudge(["yes", "no"]))
    case = make_case("The sky is blue. The moon is made of cheese.", ["The sky is blue."])
    assert metric.measure(case) == 0.5

def test_two_thirds_entailed() -> None:
    """Two of three entailed claims score 0.667."""
    metric = FaithfulnessMetric(StubJudge(["yes", "yes", "no"]))
    case = make_case("One. Two. Three.", ["ctx"])
    assert abs(metric.measure(case) - 2 / 3) < 1e-9

def test_extract_claims_splits_sentences() -> None:
    """Claim extraction splits on sentence boundaries."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert metric.extract_claims("One. Two? Three!") == ["One.", "Two?", "Three!"]

def test_extract_claims_ignores_blank_parts() -> None:
    """Claim extraction drops whitespace-only fragments."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert metric.extract_claims("  ") == []

def test_judge_called_per_claim() -> None:
    """One judge call is made per extracted claim."""
    judge = StubJudge(["yes"] * 4)
    FaithfulnessMetric(judge).measure(make_case("A. B. C. D.", ["ctx"]))
    assert len(judge.calls) == 4

def test_verdict_parsing_accepts_yes_prefix() -> None:
    """Verdicts starting with yes count as entailment."""
    metric = FaithfulnessMetric(StubJudge(["yes, the context states this explicitly"]))
    assert metric.is_entailed("claim", "context")

def test_verdict_parsing_rejects_no() -> None:
    """A no verdict counts as not entailed."""
    metric = FaithfulnessMetric(StubJudge(["no"]))
    assert not metric.is_entailed("claim", "context")

def test_verdict_parsing_case_insensitive() -> None:
    """Verdict parsing ignores casing."""
    metric = FaithfulnessMetric(StubJudge(["YES"]))
    assert metric.is_entailed("claim", "context")

def test_measure_uses_all_context_passages() -> None:
    """Every retrieved passage is included in the prompt context."""
    judge = StubJudge(["yes"])
    metric = FaithfulnessMetric(judge)
    metric.measure(make_case("One.", ["passage-a", "passage-b"]))
    assert "passage-a" in judge.calls[0] and "passage-b" in judge.calls[0]

def test_single_claim_answer() -> None:
    """Single-sentence answers produce exactly one judge call."""
    judge = StubJudge(["no"])
    metric = FaithfulnessMetric(judge)
    assert metric.measure(make_case("Solo claim.", ["ctx"])) == 0.0
    assert len(judge.calls) == 1

def test_threshold_defaults_to_point_eight() -> None:
    """Default pass threshold is 0.8."""
    assert FaithfulnessMetric(StubJudge([])).threshold == 0.8

def test_metric_name_stable() -> None:
    """Metric name is the stable registry key."""
    assert FaithfulnessMetric.name == "faithfulness"

def test_context_joined_with_newlines() -> None:
    """Context passages join with newlines in the judge prompt."""
    judge = StubJudge(["yes"])
    FaithfulnessMetric(judge).measure(make_case("One.", ["pa", "pb"]))
    assert "pa\npb" in judge.calls[0]

def test_question_marks_split_claims() -> None:
    """Questions inside answers split into separate claims."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert len(metric.extract_claims("Really? Yes.")) == 2

def test_multiline_answer() -> None:
    """Newlines inside answers do not break claim extraction."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert metric.extract_claims("One.\nTwo.") == ["One.", "Two."]

def test_unicode_answer() -> None:
    """Non-ASCII answers are handled without errors."""
    metric = FaithfulnessMetric(StubJudge(["yes"]))
    assert metric.measure(make_case("Le ciel est bleu.", ["ctx"])) == 1.0

def test_threshold_equality_passes() -> None:
    """is_passing treats the exact threshold as passing."""
    metric = FaithfulnessMetric(StubJudge([]), threshold=0.5)
    assert metric.is_passing(0.5)

def test_score_never_exceeds_one() -> None:
    """Score stays in the [0, 1] range."""
    metric = FaithfulnessMetric(StubJudge(["yes"] * 5))
    score = metric.measure(make_case("A. B. C. D. E.", ["ctx"]))
    assert 0.0 <= score <= 1.0

def test_claims_from_bullets() -> None:
    """Bullet answers yield one claim per line."""
    from metrics.faithfulness import claims_from_bullets

    assert claims_from_bullets("- one\n* two") == ["one", "two"]
