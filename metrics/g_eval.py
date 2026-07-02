#!/usr/bin/env python3
"""
g_eval.py --- G-Eval style custom-rubric judge metric

Contains:
    GEvalMetric: scores a test case against a custom rubric with an LLM judge
    GEvalMetric.measure(): computes the normalized rubric score
"""

import re

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric
from metrics.judge import JudgeClient

G_EVAL_PROMPT_VERSION = 1
G_EVAL_PROMPT = (
    "Rubric:\n{rubric}\n\nQuestion: {question}\nAnswer: {answer}\n"
    "Score the answer against the rubric on a 1-5 scale. Reply with the number only."
)
DEFAULT_RUBRIC = "1: wrong or off-topic, 3: partially correct, 5: fully correct and complete"


class GEvalMetric(BaseMetric):
    """Scores a test case against a custom rubric using a single LLM judge.

    Attributes:
        judge: LLM client used as the rubric judge.
        rubric: Rubric text the judge scores against.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "g_eval"

    def __init__(self, judge: JudgeClient, rubric: str = DEFAULT_RUBRIC, threshold: float = 0.7) -> None:
        """Stores the judge, rubric, and pass threshold."""
        self.judge = judge
        self.rubric = rubric
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the normalized rubric score for one test case.

        Args:
            test_case: Eval case with the question and generated answer.

        Returns:
            score: Judge's 1-5 verdict normalized to [0, 1].
        """
        prompt = G_EVAL_PROMPT.format(
            rubric=self.rubric, question=test_case.input, answer=test_case.actual_output
        )
        verdict = self.judge.complete(prompt)
        return self.parse_score(verdict)

    def parse_score(self, verdict: str) -> float:
        """Parses a 1-5 judge verdict into a normalized score.

        Args:
            verdict: Raw judge output, expected to contain a 1-5 digit.

        Returns:
            score: Normalized score in [0, 1]; 0.0 when unparseable.
        """
        match = re.search(r"\b([1-5])\b", verdict)
        if not match:
            return 0.0
        return (int(match.group()) - 1) / 4

def rubric_score_label(score: float) -> str:
    """Maps a normalized score back to a rubric label.

    Args:
        score: Normalized G-Eval score in [0, 1].

    Returns:
        label: Human-readable band for the score.
    """
    if score >= 0.75:
        return "excellent"
    if score >= 0.5:
        return "adequate"
    return "poor"
