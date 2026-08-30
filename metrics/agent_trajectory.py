#!/usr/bin/env python3
"""
agent_trajectory.py --- scores multi-hop agent runs against expected tool usage

Contains:
    TrajectoryStep: one step in an agent run
    AgentTrajectoryMetric: scores tool usage, order, and efficiency
"""

from dataclasses import dataclass

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric


@dataclass(frozen=True)
class TrajectoryStep:
    """One step in an agent run.

    Attributes:
        tool: Name of the tool invoked.
        tool_input: Arguments passed to the tool.
        observation: Output returned by the tool.
    """

    tool: str
    tool_input: str
    observation: str


class AgentTrajectoryMetric(BaseMetric):
    """Scores agent runs on tool usage, order, and efficiency.

    Attributes:
        threshold: Minimum score for the metric to count as passing.
        order_weight: Weight given to call-order correctness.
    """

    name = "agent_trajectory"

    def __init__(self, threshold: float = 0.7, order_weight: float = 0.3) -> None:
        """Stores the pass threshold and order weight."""
        self.threshold = threshold
        self.order_weight = order_weight

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the trajectory score for one agent run.

        Args:
            test_case: Eval case with called and expected tools.

        Returns:
            score: Blend of tool coverage, order correctness, and efficiency.
        """
        called = test_case.tools_called
        expected = test_case.expected_tools
        if not expected:
            return 1.0 if not called else 0.5
        coverage = self.tool_coverage(called, expected)
        order = self.order_score(called, expected)
        efficiency = self.efficiency_score(called, expected)
        base = (1 - self.order_weight) * coverage + self.order_weight * order
        return base * efficiency

    def tool_coverage(self, called: list[str], expected: list[str]) -> float:
        """Computes what fraction of expected tools were called.

        Args:
            called: Tools the agent actually invoked, in order.
            expected: Tools the run was expected to invoke.

        Returns:
            coverage: Fraction of expected tools present in called.
        """
        return len(set(expected) & set(called)) / len(expected)

    def order_score(self, called: list[str], expected: list[str]) -> float:
        """Checks whether expected tools appear in the expected order.

        Args:
            called: Tools the agent actually invoked, in order.
            expected: Tools the run was expected to invoke, in order.

        Returns:
            score: 1.0 when expected tools appear in relative order, else 0.0.
        """
        positions = []
        for tool in expected:
            if tool not in called:
                return 0.0
            positions.append(called.index(tool))
        return 1.0 if positions == sorted(positions) else 0.0

    def efficiency_score(self, called: list[str], expected: list[str]) -> float:
        """Penalizes runs that use far more steps than expected.

        Args:
            called: Tools the agent actually invoked, in order.
            expected: Tools the run was expected to invoke.

        Returns:
            score: Ratio of expected to actual step counts, capped at 1.0.
        """
        if not called:
            return 0.0
        return min(1.0, len(expected) / len(called))


def redundant_calls(called: list[str]) -> list[str]:
    """Lists tools called more than once.

    Args:
        called: Tools the agent invoked, in order.

    Returns:
        repeated: Tools appearing more than once, deduplicated.
    """
    seen: set[str] = set()
    repeated: list[str] = []
    for tool in called:
        if tool in seen and tool not in repeated:
            repeated.append(tool)
        seen.add(tool)
    return repeated


def step_count_delta(called: list[str], expected: list[str]) -> int:
    """Computes how many extra steps the run took over the expectation.

    Args:
        called: Tools the agent invoked, in order.
        expected: Tools the run was expected to invoke.

    Returns:
        delta: Extra step count; negative when the run was shorter.
    """
    return len(called) - len(expected)


def trajectory_summary(called: list[str], expected: list[str]) -> str:
    """Builds a one-line summary of a scored trajectory.

    Args:
        called: Tools the agent invoked, in order.
        expected: Tools the run was expected to invoke.

    Returns:
        summary: Human-readable comparison of called versus expected tools.
    """
    return f"called {len(called)} tools, expected {len(expected)}: {', '.join(called)}"


def has_loop(called: list[str], window: int = 3) -> bool:
    """Detects immediate repetition loops in a trajectory.

    Args:
        called: Tools the agent invoked, in order.
        window: Minimum run length of identical calls to count as a loop.

    Returns:
        looping: True when any tool repeats window times in a row.
    """
    run = 1
    for prev, cur in zip(called, called[1:], strict=False):
        run = run + 1 if cur == prev else 1
        if run >= window:
            return True
    return False
