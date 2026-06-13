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
