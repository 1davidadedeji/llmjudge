#!/usr/bin/env python3
"""
test_loader.py --- unit tests for eval config loading

Contains:
    test_load_example_config: shipped example parses and validates
"""

from config.loader import load_config


def test_load_example_config() -> None:
    """Shipped example config parses and validates."""
    config = load_config("llmjudge.example.yaml")
    assert config.repos[0].repo == "retrieval-core"
    assert config.default_dataset == "gold-v1"
