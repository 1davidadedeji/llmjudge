#!/usr/bin/env python3
"""
test_calibrate.py --- unit tests for rubric calibration

Contains:
    test_load_gold_set: shipped gold set parses
    test_agreement_perfect: identical scores and labels agree fully
"""

from calibration.calibrate import agreement, load_gold_set, suggest_threshold


def test_load_gold_set() -> None:
    """Shipped gold set parses into examples."""
    examples = load_gold_set()
    assert len(examples) >= 3
    assert examples[0].label == 1.0


def test_agreement_perfect() -> None:
    """Identical scores and labels agree fully."""
    assert agreement([0.9, 0.1], [1.0, 0.0]) == 1.0


def test_agreement_partial() -> None:
    """Scores outside tolerance count as disagreement."""
    assert agreement([0.9, 0.9], [1.0, 0.0]) == 0.5


def test_suggest_threshold_perfect_split() -> None:
    """A separable label set yields a threshold between the clusters."""
    threshold = suggest_threshold([1.0, 0.9, 0.1, 0.0])
    assert 0.1 < threshold < 0.9


def test_suggest_threshold_empty() -> None:
    """Empty labels fall back to 0.5."""
    assert suggest_threshold([]) == 0.5


def test_cohens_kappa_perfect() -> None:
    """Perfect agreement gives kappa 1.0."""
    from calibration.calibrate import cohens_kappa

    assert cohens_kappa([True, False], [True, False]) == 1.0


def test_cohens_kappa_empty() -> None:
    """Empty inputs give kappa 1.0 by convention."""
    from calibration.calibrate import cohens_kappa

    assert cohens_kappa([], []) == 1.0


def test_mean_absolute_error() -> None:
    """MAE averages the absolute judge-label gaps."""
    from calibration.calibrate import mean_absolute_error

    assert mean_absolute_error([1.0, 0.0], [0.5, 0.5]) == 0.5


def test_calibration_report_keys() -> None:
    """Report carries agreement, mae, kappa, and threshold."""
    from calibration.calibrate import calibration_report

    report = calibration_report([1.0, 0.0], [1.0, 0.0])
    assert set(report) == {"agreement", "mae", "kappa", "suggested_threshold"}
