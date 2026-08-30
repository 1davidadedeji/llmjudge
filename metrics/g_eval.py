#!/usr/bin/env python3
"""
g_eval.py --- G-Eval style custom-rubric judge, 3-judge ensemble

Contains:
    GEvalMetric: scores a test case against a custom rubric with a judge ensemble
    GEvalMetric.measure(): computes the mean ensemble score
    GEvalMetric.measure_with_details(): per-judge scores plus disagreement flag
"""

import re
from typing import Any

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric
from metrics.judge import JudgeClient

G_EVAL_PROMPT = (
    "Rubric:\n{rubric}\n\nQuestion: {question}\nAnswer: {answer}\n"
    "Score the answer against the rubric on a 1-5 scale. Reply with the number only."
)
DEFAULT_RUBRIC = "1: wrong or off-topic, 3: partially correct, 5: fully correct and complete"
G_EVAL_PROMPT_VERSION = 2
DISAGREEMENT_SPREAD = 0.25  # max-min spread that flags judge disagreement


class GEvalMetric(BaseMetric):
    """Scores a test case against a custom rubric with a 3-judge ensemble.

    A single judge inflates scores for answers from its own model family
    (measured +0.15 average self-preference bias), so judges come from three
    different families and disagreement is flagged rather than averaged away.

    Attributes:
        judges: Three judge clients, each from a different model family.
        rubric: Rubric text the judges score against.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "g_eval"

    def __init__(
        self, judges: list[JudgeClient], rubric: str = DEFAULT_RUBRIC, threshold: float = 0.7
    ) -> None:
        """Stores the judge ensemble, rubric, and pass threshold."""
        if len(judges) != 3:
            raise ValueError("ensemble requires exactly 3 judges from different families")
        self.judges = list(judges)
        self.rubric = rubric
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the mean ensemble score for one test case.

        Args:
            test_case: Eval case with the question and generated answer.

        Returns:
            score: Mean of the three judges' normalized scores.
        """
        details = self.measure_with_details(test_case)
        return float(details["mean"])

    def measure_with_details(self, test_case: LLMTestCase) -> dict[str, Any]:
        """Computes per-judge scores and the disagreement flag.

        Args:
            test_case: Eval case with the question and generated answer.

        Returns:
            details: Per-judge scores, their mean, and whether judges disagree.
        """
        prompt = G_EVAL_PROMPT.format(
            rubric=self.rubric, question=test_case.input, answer=test_case.actual_output
        )
        scores = [self.parse_score(judge.complete(prompt)) for judge in self.judges]
        mean = sum(scores) / len(scores)
        return {
            "scores": scores,
            "mean": mean,
            "disagreement": self.judges_disagree(scores),
        }

    def judges_disagree(self, scores: list[float]) -> bool:
        """Flags when the judge spread exceeds the disagreement threshold.

        Args:
            scores: Normalized per-judge scores.

        Returns:
            disagreement: True when max-min spread exceeds DISAGREEMENT_SPREAD.
        """
        return max(scores) - min(scores) > DISAGREEMENT_SPREAD

    def parse_score(self, verdict: str) -> float:
        """Parses a 1-5 judge verdict into a normalized score.

        Args:
            verdict: Raw judge output, expected to contain a 1-5 digit.

        Returns:
            score: Normalized score in [0, 1]; 0.0 when unparseable.
        """
        match = re.search(r"[1-5]", verdict)
        if not match:
            return 0.0
        return (int(match.group()) - 1) / 4


def per_judge_breakdown(scores: list[float]) -> dict[str, float]:
    """Labels ensemble scores by judge position for reporting.

    Args:
        scores: Normalized per-judge scores in ensemble order.

    Returns:
        breakdown: Mapping of judge_a/b/c labels to scores.
    """
    labels = ["judge_a", "judge_b", "judge_c"]
    return dict(zip(labels, scores, strict=True))


def should_escalate(disagreement: bool) -> bool:
    """Reports whether a run should be escalated for human review.

    Args:
        disagreement: Disagreement flag from measure_with_details().

    Returns:
        escalate: True when judges disagreed and a human should look.
    """
    return disagreement


def ensemble_confidence(scores: list[float]) -> float:
    """Converts judge agreement into a confidence figure.

    Args:
        scores: Normalized per-judge scores.

    Returns:
        confidence: 1.0 for perfect agreement, lower as spread grows.
    """
    return 1.0 - (max(scores) - min(scores))


def spread(scores: list[float]) -> float:
    """Computes the max-min spread of ensemble scores.

    Args:
        scores: Normalized per-judge scores.

    Returns:
        spread: Difference between the highest and lowest score.
    """
    return max(scores) - min(scores)
