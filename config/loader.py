#!/usr/bin/env python3
"""
loader.py --- loads and validates llmjudge YAML configuration

Contains:
    load_config(): parses a YAML config file into a LlmjudgeConfig
"""

import yaml

from config.schema import LlmjudgeConfig

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
