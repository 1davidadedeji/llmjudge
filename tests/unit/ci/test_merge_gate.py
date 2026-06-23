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
