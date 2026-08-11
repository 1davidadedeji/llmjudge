#!/usr/bin/env python3
"""
contextual_precision_recall.py --- retrieval quality metrics over ranked context

Contains:
    ContextualPrecisionMetric: rewards relevant passages ranked early
    ContextualRecallMetric: rewards coverage of the expected output
"""

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric
from metrics.base import BaseMetric
from metrics.judge import JudgeClient

VERDICT_PROMPT = (
    "Passage: {passage}\nQuestion: {question}\n"
    "Is this passage useful for answering the question? Answer yes or no."
)
COVERAGE_PROMPT = (
    "Expected answer: {expected}\nPassage: {passage}\n"
    "Does this passage support part of the expected answer? Answer yes or no."
)


class ContextualPrecisionMetric(BaseMetric):
    """Rewards relevant passages appearing early in the ranking.

    Attributes:
        judge: LLM client used for relevance verdicts.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "contextual_precision"

    def __init__(self, judge: JudgeClient, threshold: float = 0.7) -> None:
        """Stores the judge client and pass threshold."""
        self.judge = judge
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes contextual precision for one test case.

        Args:
            test_case: Eval case with ranked retrieved passages.

        Returns:
            score: Weighted precision favoring early relevant passages.
        """
        passages = test_case.retrieval_context
        if not passages:
            return 1.0
        verdicts = [self.is_relevant(p, test_case.input) for p in passages]
        return average_precision(verdicts)

    def is_relevant(self, passage: str, question: str) -> bool:
        """Asks the judge whether a passage is relevant to the question.

        Args:
            passage: One retrieved passage.
            question: Input question text.

        Returns:
            relevant: True when the judge answers yes.
        """
        verdict = self.judge.complete(VERDICT_PROMPT.format(passage=passage, question=question))
        return verdict.strip().lower().startswith("yes")


class ContextualRecallMetric(BaseMetric):
    """Rewards retrieved coverage of the expected answer.

    Attributes:
        judge: LLM client used for coverage verdicts.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "contextual_recall"

    def __init__(self, judge: JudgeClient, threshold: float = 0.7) -> None:
        """Stores the judge client and pass threshold."""
        self.judge = judge
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes contextual recall for one test case.

        Args:
            test_case: Eval case with expected output and retrieved passages.

        Returns:
            score: Fraction of passages supporting the expected answer.
        """
        passages = test_case.retrieval_context
        if not passages or test_case.expected_output is None:
            return 1.0
        hits = [self.supports(p, test_case.expected_output) for p in passages]
        return sum(hits) / len(hits)

    def supports(self, passage: str, expected: str) -> bool:
        """Asks the judge whether a passage supports the expected answer.

        Args:
            passage: One retrieved passage.
            expected: Expected answer text.

        Returns:
            supports: True when the judge answers yes.
        """
        verdict = self.judge.complete(COVERAGE_PROMPT.format(passage=passage, expected=expected))
        return verdict.strip().lower().startswith("yes")

def average_precision(verdicts: list[bool]) -> float:
    """Computes average precision from ranked relevance verdicts.

    Args:
        verdicts: Relevance flags in ranking order.

    Returns:
        score: Average precision across relevant ranks.
    """
    relevant = 0
    weighted = 0.0
    for rank, flag in enumerate(verdicts, start=1):
        if flag:
            relevant += 1
            weighted += relevant / rank
    return weighted / relevant if relevant else 0.0

def recall_at_k(verdicts: list[bool], k: int) -> float:
    """Computes recall over only the top-k ranked passages.

    Args:
        verdicts: Relevance flags in ranking order.
        k: Rank cutoff.

    Returns:
        score: Fraction of top-k passages that are relevant.
    """
    window = verdicts[:k]
    if not window:
        return 1.0
    return sum(window) / len(window)

def mrr(verdicts: list[bool]) -> float:
    """Computes mean reciprocal rank for ranked verdicts.

    Args:
        verdicts: Relevance flags in ranking order.

    Returns:
        score: Reciprocal rank of the first relevant passage.
    """
    for rank, flag in enumerate(verdicts, start=1):
        if flag:
            return 1.0 / rank
    return 0.0
