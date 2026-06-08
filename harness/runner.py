#!/usr/bin/env python3
"""
runner.py --- pytest-style eval runner

Contains:
    EvalRunner: runs metrics over test cases and collects per-case results
    EvalRunner.run(): scores every case with every configured metric
"""

from harness.test_case import LLMTestCase


class EvalRunner:
    """Runs metrics over test cases and collects per-case results.

    Attributes:
        metrics: Metric instances to apply to every case.
    """

    def __init__(self, metrics: list) -> None:
        """Stores the metric list."""
        self.metrics = list(metrics)

    def run(self, cases: list[LLMTestCase]) -> dict[str, dict[str, float]]:
        """Scores every case with every configured metric.

        Args:
            cases: Test cases to evaluate.

        Returns:
            results: Mapping of metric name to per-case scores.
        """
        results: dict[str, dict[str, float]] = {}
        for metric in self.metrics:
            results[metric.name] = {
                str(index): metric.measure(case) for index, case in enumerate(cases)
            }
        return results
