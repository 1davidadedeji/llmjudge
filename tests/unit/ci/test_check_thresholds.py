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

def test_validate_config_flags_out_of_range() -> None:
    """Thresholds outside [0, 1] are rejected."""
    bad = {"default_threshold": 0.75, "repos": {"x": {"threshold": 1.5}}}
    assert validate_config(bad) == ["x: threshold 1.5 out of range [0, 1]"]

def test_validate_config_requires_default() -> None:
    """Config without a default_threshold is rejected."""
    assert validate_config({"repos": {}}) == ["missing default_threshold"]

def test_all_repos_sorted() -> None:
    """Repo listing is sorted for deterministic CI logs."""
    assert all_repos(CONFIG) == ["agentflow"]

def test_strictest_picks_highest_floor() -> None:
    """Strictest repo is the one with the highest threshold."""
    assert strictest(CONFIG).repo == "agentflow"
