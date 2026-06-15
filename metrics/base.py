#!/usr/bin/env python3
"""
base.py --- shared interface every metric implements

Contains:
    BaseMetric: abstract interface for all metrics
    BaseMetric.is_passing(): threshold check shared by all metrics
    clamp_score(): bounds a raw score into [0, 1]
"""

from abc import ABC, abstractmethod

from harness.test_case import LLMTestCase


def clamp_score(score: float) -> float:
    """Bounds a raw score into the [0, 1] range.

    Args:
        score: Raw metric score, possibly out of range.

    Returns:
        clamped: Score bounded to [0, 1].
    """
    return max(0.0, min(1.0, score))


class BaseMetric(ABC):
    """Defines the contract every llmjudge metric implements.

    Attributes:
        threshold: Minimum score for the metric to count as passing.
    """

    name: str = "base"
    threshold: float

    @abstractmethod
    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the metric score for one test case.

        Args:
            test_case: Eval case to score.

        Returns:
            score: Metric score in [0, 1].
        """

    def is_passing(self, score: float) -> bool:
        """Reports whether a score passes this metric's threshold.

        Args:
            score: Score returned by measure().

        Returns:
            passing: True when the score meets the threshold.
        """
        return score >= self.threshold
