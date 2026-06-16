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

def test_metric_threshold_bounds() -> None:
    """Threshold overrides must stay in [0, 1]."""
    import pytest
    from pydantic import ValidationError

    from config.schema import MetricSelection

    with pytest.raises(ValidationError):
        MetricSelection(name="faithfulness", threshold=1.5)
