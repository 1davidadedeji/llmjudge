#!/usr/bin/env python3
"""
test_merge_gate.py --- unit tests for the CI merge gate

Contains:
    test_evaluate_gate_passes_when_scores_meet_thresholds: all scores above floor
    test_evaluate_gate_blocks_on_regression: one score below floor blocks
"""

from ci.merge_gate import evaluate_gate, threshold_for

THRESHOLDS = {"faithfulness": 0.80, "hallucination": 0.90}


def test_evaluate_gate_passes_when_scores_meet_thresholds() -> None:
    """Run passes the gate when every metric clears its floor."""
    payload = {"status": "succeeded", "scores": {"faithfulness": 0.9, "hallucination": 0.95}}
    assert evaluate_gate(payload, THRESHOLDS).passed


def test_evaluate_gate_blocks_on_regression() -> None:
    """Run is blocked when any metric falls below its floor."""
    payload = {"status": "succeeded", "scores": {"faithfulness": 0.5, "hallucination": 0.95}}
    result = evaluate_gate(payload, THRESHOLDS)
    assert not result.passed
    assert result.regressions == ["faithfulness"]


def test_threshold_for_falls_back_to_default() -> None:
    """Unknown metrics use the default floor."""
    assert threshold_for(THRESHOLDS, "g_eval") == 0.75

def test_evaluate_gate_treats_missing_score_as_zero() -> None:
    """A metric absent from the payload counts as a zero score."""
    payload = {"status": "succeeded", "scores": {}}
    assert evaluate_gate(payload, THRESHOLDS).regressions == list(THRESHOLDS)

def test_format_regression_report_pass() -> None:
    """Passing gate renders a one-line pass report."""
    from ci.merge_gate import GateResult, format_regression_report

    assert format_regression_report(GateResult(True, []), "agentflow").endswith("passed")

def test_format_regression_report_blocked() -> None:
    """Blocked gate names the regressed metrics in the report."""
    from ci.merge_gate import GateResult, format_regression_report

    report = format_regression_report(GateResult(False, ["faithfulness"]), "graphmind")
    assert "BLOCKED" in report and "faithfulness" in report

def test_is_terminal() -> None:
    """Only succeeded and failed count as terminal statuses."""
    from ci.merge_gate import is_terminal

    assert is_terminal("succeeded") and is_terminal("failed")
    assert not is_terminal("running") and not is_terminal("unknown")

def test_gate_result_fields() -> None:
    """GateResult exposes passed and regressions."""
    from ci.merge_gate import GateResult

    result = GateResult(False, ["m"])
    assert not result.passed and result.regressions == ["m"]

def test_default_thresholds_cover_core_metrics() -> None:
    """Default thresholds gate the core metrics."""
    from ci.merge_gate import DEFAULT_THRESHOLDS

    assert "faithfulness" in DEFAULT_THRESHOLDS

def test_poll_interval_positive() -> None:
    """Poll interval is a positive number of seconds."""
    from ci.merge_gate import POLL_INTERVAL_S

    assert POLL_INTERVAL_S > 0

def test_timeout_generous() -> None:
    """Gate timeout leaves room for a full eval suite."""
    from ci.merge_gate import DEFAULT_TIMEOUT_S

    assert DEFAULT_TIMEOUT_S >= 600

def test_threshold_for_known_metric() -> None:
    """Known metrics resolve their configured floor."""
    assert threshold_for({"m": 0.9}, "m") == 0.9

def test_evaluate_gate_passes_exact_floor() -> None:
    """A score exactly at the floor passes."""
    payload = {"status": "succeeded", "scores": {"faithfulness": 0.8}}
    assert evaluate_gate(payload, {"faithfulness": 0.8}).passed

def test_summarize_scores_sorted() -> None:
    """Score summary lists metrics alphabetically for stable logs."""
    from ci.merge_gate import summarize_scores

    assert summarize_scores({"b": 1.0, "a": 0.5}) == "a=0.500, b=1.000"
