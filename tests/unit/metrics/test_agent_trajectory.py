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

def test_efficiency_exact() -> None:
    """Exact step count gives full efficiency."""
    metric = AgentTrajectoryMetric()
    assert metric.efficiency_score(["a", "b"], ["a", "b"]) == 1.0

def test_efficiency_extra_steps() -> None:
    """Extra steps reduce efficiency proportionally."""
    metric = AgentTrajectoryMetric()
    assert metric.efficiency_score(["a", "b", "c", "d"], ["a", "b"]) == 0.5

def test_efficiency_no_calls() -> None:
    """No calls yields zero efficiency."""
    assert AgentTrajectoryMetric().efficiency_score([], ["a"]) == 0.0

def test_coverage_none_expected_called() -> None:
    """Coverage of zero expected tools is vacuously handled by measure."""
    metric = AgentTrajectoryMetric()
    assert metric.measure(make_case([], [])) == 1.0

def test_partial_order_credit_none() -> None:
    """Out-of-order calls lose all order credit."""
    metric = AgentTrajectoryMetric()
    score = metric.measure(make_case(["b", "a"], ["a", "b"]))
    assert score < 1.0

def test_duplicate_calls_use_first_position() -> None:
    """Order check uses the first occurrence."""
    metric = AgentTrajectoryMetric()
    assert metric.order_score(["a", "b", "a"], ["a", "b"]) == 1.0

def test_metric_name_stable() -> None:
    """Metric name is the stable registry key."""
    assert AgentTrajectoryMetric.name == "agent_trajectory"

def test_score_bounded() -> None:
    """Score stays within [0, 1]."""
    metric = AgentTrajectoryMetric()
    score = metric.measure(make_case(["x", "y", "z"], ["a"]))
    assert 0.0 <= score <= 1.0

def test_order_weight_configurable() -> None:
    """Order weight is a constructor knob."""
    assert AgentTrajectoryMetric(order_weight=0.5).order_weight == 0.5

def test_redundant_calls_detected() -> None:
    """Repeated tools are reported once each."""
    from metrics.agent_trajectory import redundant_calls

    assert redundant_calls(["a", "b", "a", "a"]) == ["a"]

def test_step_count_delta() -> None:
    """Delta counts extra steps over the expectation."""
    from metrics.agent_trajectory import step_count_delta

    assert step_count_delta(["a", "b", "c"], ["a"]) == 2

def test_coverage_full() -> None:
    """Full coverage when all expected tools are called."""
    metric = AgentTrajectoryMetric()
    assert metric.tool_coverage(["a", "b", "c"], ["b", "a"]) == 1.0

def test_coverage_zero() -> None:
    """Zero coverage when no expected tool is called."""
    metric = AgentTrajectoryMetric()
    assert metric.tool_coverage(["x"], ["a"]) == 0.0

def test_efficiency_capped_at_one() -> None:
    """Efficiency never exceeds one even for short runs."""
    metric = AgentTrajectoryMetric()
    assert metric.efficiency_score(["a"], ["a", "b"]) == 1.0

def test_measure_missing_all_expected() -> None:
    """Calling nothing expected scores low."""
    metric = AgentTrajectoryMetric()
    assert metric.measure(make_case(["x"], ["a"])) < 0.5

def test_order_extra_tools_ignored() -> None:
    """Extra tools do not break order credit."""
    metric = AgentTrajectoryMetric()
    assert metric.order_score(["a", "x", "b"], ["a", "b"]) == 1.0

def test_threshold_stored() -> None:
    """Threshold is stored on the metric."""
    assert AgentTrajectoryMetric(threshold=0.9).threshold == 0.9

def test_trajectory_summary_mentions_counts() -> None:
    """Summary mentions called and expected counts."""
    from metrics.agent_trajectory import trajectory_summary

    assert "called 2" in trajectory_summary(["a", "b"], ["a"])

def test_summary_mentions_expected_count() -> None:
    """Summary mentions the expected count."""
    from metrics.agent_trajectory import trajectory_summary

    assert "expected 3" in trajectory_summary(["a"], ["a", "b", "c"])

def test_efficiency_shorter_run_capped() -> None:
    """Shorter-than-expected runs cap at one."""
    metric = AgentTrajectoryMetric()
    assert metric.efficiency_score(["a"], ["a", "b"]) == 1.0

def test_order_weight_bounds() -> None:
    """Order weight blends coverage and order within [0, 1]."""
    metric = AgentTrajectoryMetric(order_weight=1.0)
    score = metric.measure(make_case(["a", "b"], ["a", "b"]))
    assert score == 1.0

def test_has_loop_detection() -> None:
    """Loop detection catches three identical calls in a row."""
    from metrics.agent_trajectory import has_loop

    assert has_loop(["a", "a", "a"])
    assert not has_loop(["a", "b", "a"])

def test_metric_default_threshold() -> None:
    """Default threshold is 0.7."""
    assert AgentTrajectoryMetric().threshold == 0.7
