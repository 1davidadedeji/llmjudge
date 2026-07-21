#!/usr/bin/env python3
"""
check_thresholds.py --- validates and resolves per-repo merge-gate thresholds

Contains:
    RepoThreshold: resolved threshold entry for one repo
    load_threshold_config(): parses ci/thresholds.yaml
    resolve_threshold(): resolves the effective threshold for a repo
"""

from dataclasses import dataclass

import yaml

CONFIG_PATH = "ci/thresholds.yaml"
MIN_THRESHOLD = 0.0
MAX_THRESHOLD = 1.0


@dataclass(frozen=True)
class RepoThreshold:
    """Resolved threshold entry for one repo.

    Attributes:
        repo: Repo name the threshold applies to.
        threshold: Blended score floor the repo must meet to merge.
    """

    repo: str
    threshold: float


def load_threshold_config(path: str = CONFIG_PATH) -> dict:
    """Parses the thresholds config file.

    Args:
        path: Filesystem path to the thresholds YAML file.

    Returns:
        config: Parsed mapping with default_threshold and per-repo entries.
    """
    with open(path) as fh:
        return yaml.safe_load(fh)


def resolve_threshold(config: dict, repo: str) -> RepoThreshold:
    """Resolves the effective threshold for a repo.

    Args:
        config: Parsed thresholds config from load_threshold_config().
        repo: Repo name to resolve.

    Returns:
        entry: RepoThreshold using the repo override or the global default.
    """
    repos = config.get("repos", {})
    if repo in repos:
        return RepoThreshold(repo=repo, threshold=float(repos[repo]["threshold"]))
    return RepoThreshold(repo=repo, threshold=float(config["default_threshold"]))

def validate_config(config: dict) -> list[str]:
    """Validates a parsed thresholds config.

    Args:
        config: Parsed thresholds config from load_threshold_config().

    Returns:
        problems: Validation error messages; empty when the config is valid.
    """
    problems = []
    if "default_threshold" not in config:
        problems.append("missing default_threshold")
    for repo, entry in config.get("repos", {}).items():
        value = float(entry.get("threshold", -1))
        if not MIN_THRESHOLD <= value <= MAX_THRESHOLD:
            problems.append(f"{repo}: threshold {value} out of range [0, 1]")
    return problems

def all_repos(config: dict) -> list[str]:
    """Lists every repo with an explicit threshold entry.

    Args:
        config: Parsed thresholds config from load_threshold_config().

    Returns:
        repos: Sorted repo names from the config.
    """
    return sorted(config.get("repos", {}))

def strictest(config: dict) -> RepoThreshold:
    """Finds the repo with the strictest threshold.

    Args:
        config: Parsed thresholds config from load_threshold_config().

    Returns:
        entry: RepoThreshold with the highest configured floor.
    """
    repos = config.get("repos", {})
    name = max(repos, key=lambda repo: float(repos[repo]["threshold"]))
    return RepoThreshold(repo=name, threshold=float(repos[name]["threshold"]))

def blended_score(scores: dict[str, float]) -> float:
    """Computes the blended gate score from per-metric scores.

    Args:
        scores: Mapping of metric names to scores.

    Returns:
        blended: Mean score across metrics; 0.0 for an empty mapping.
    """
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)

def gate_decision(config: dict, repo: str, scores: dict[str, float]) -> bool:
    """Decides whether a repo's scores pass its merge-gate threshold.

    Args:
        config: Parsed thresholds config from load_threshold_config().
        repo: Repo name to decide for.
        scores: Per-metric scores from the eval run.

    Returns:
        passed: True when the blended score meets the repo threshold.
    """
    return blended_score(scores) >= resolve_threshold(config, repo).threshold
