#!/usr/bin/env python3
"""
test_agent_trajectory.py --- unit tests for the agent trajectory metric

Contains:
    test_perfect_run_scores_one: exact expected calls score perfectly
    test_missing_tool_lowers_coverage: missing expected tool reduces coverage
"""

from harness.test_case import LLMTestCase
from metrics.agent_trajectory import AgentTrajectoryMetric


def make_case(called: list[str], expected: list[str]) -> LLMTestCase:
    """Builds an agent-run test case.

    Args:
        called: Tools actually invoked, in order.
        expected: Tools expected to be invoked, in order.

    Returns:
        test_case: LLMTestCase wrapping the trajectory data.
    """
    return LLMTestCase(
        input="q", actual_output="a", tools_called=called, expected_tools=expected
    )


def test_perfect_run_scores_one() -> None:
    """Exact expected calls in order score a perfect run."""
    metric = AgentTrajectoryMetric()
    assert metric.measure(make_case(["search", "read"], ["search", "read"])) == 1.0


def test_missing_tool_lowers_coverage() -> None:
    """Missing an expected tool reduces coverage."""
    metric = AgentTrajectoryMetric()
    assert metric.tool_coverage(["search"], ["search", "read"]) == 0.5

def test_no_expected_tools_and_none_called() -> None:
    """No expectations and no calls scores one."""
    assert AgentTrajectoryMetric().measure(make_case([], [])) == 1.0

def test_no_expected_tools_but_called() -> None:
    """Unexpected calls score a middling 0.5."""
    assert AgentTrajectoryMetric().measure(make_case(["search"], [])) == 0.5

def test_order_score_in_order() -> None:
    """In-order expected calls get full order credit."""
    metric = AgentTrajectoryMetric()
    assert metric.order_score(["search", "read"], ["search", "read"]) == 1.0

def test_order_score_out_of_order() -> None:
    """Out-of-order expected calls get no order credit."""
    metric = AgentTrajectoryMetric()
    assert metric.order_score(["read", "search"], ["search", "read"]) == 0.0

def test_order_score_missing_tool() -> None:
    """A missing expected tool zeroes the order score."""
    metric = AgentTrajectoryMetric()
    assert metric.order_score(["read"], ["search", "read"]) == 0.0
