#!/usr/bin/env python3
"""
test_check_thresholds.py --- unit tests for merge-gate threshold resolution

Contains:
    test_resolve_uses_repo_override: repo-specific threshold wins over default
    test_resolve_falls_back_to_default: unknown repo gets the default floor
"""

from ci.check_thresholds import resolve_threshold, validate_config

CONFIG = {
    "default_threshold": 0.75,
    "repos": {"agentflow": {"threshold": 0.8}},
}


def test_resolve_uses_repo_override() -> None:
    """Repo-specific threshold wins over the global default."""
    assert resolve_threshold(CONFIG, "agentflow").threshold == 0.8


def test_resolve_falls_back_to_default() -> None:
    """Unknown repos fall back to the global default threshold."""
    assert resolve_threshold(CONFIG, "other-repo").threshold == 0.75


def test_validate_config_accepts_valid() -> None:
    """A well-formed config produces no validation problems."""
    assert validate_config(CONFIG) == []
