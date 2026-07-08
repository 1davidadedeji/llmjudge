#!/usr/bin/env python3
"""
loader.py --- loads and validates llmjudge YAML configuration

Contains:
    load_config(): parses a YAML config file into a LlmjudgeConfig
"""

import yaml

from config.schema import LlmjudgeConfig, RepoEvalConfig

DEFAULT_CONFIG_PATH = "llmjudge.yaml"


def load_config(path: str = DEFAULT_CONFIG_PATH) -> LlmjudgeConfig:
    """Parses a YAML config file into a LlmjudgeConfig.

    Args:
        path: Filesystem path to the YAML config.

    Returns:
        config: Validated LlmjudgeConfig.
    """
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    return LlmjudgeConfig(**raw)

def find_repo(config: LlmjudgeConfig, repo: str) -> "RepoEvalConfig | None":
    """Finds one repo's config by name.

    Args:
        config: Loaded top-level config.
        repo: Repo name to find.

    Returns:
        repo_config: The repo's config, or None when unconfigured.
    """
    for repo_config in config.repos:
        if repo_config.repo == repo:
            return repo_config
    return None
