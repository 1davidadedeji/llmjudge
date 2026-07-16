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

def test_metric_names_helper() -> None:
    """metric_names lists enabled metrics in order."""
    config = load_config("llmjudge.example.yaml")
    assert config.repos[0].metric_names()[0] == "faithfulness"

def test_threshold_for_unset() -> None:
    """threshold_for returns None when no override is set."""
    config = load_config("llmjudge.example.yaml")
    assert config.repos[0].threshold_for("faithfulness") is None

def test_repo_names() -> None:
    """repo_names lists every configured repo."""
    config = load_config("llmjudge.example.yaml")
    assert "retrieval-core" in config.repo_names()

def test_find_repo() -> None:
    """find_repo locates a configured repo and misses unknown ones."""
    from config.loader import find_repo

    config = load_config("llmjudge.example.yaml")
    assert find_repo(config, "agentflow") is not None
    assert find_repo(config, "nope") is None

def test_example_has_all_five_repos() -> None:
    """Example config covers all five repos."""
    config = load_config("llmjudge.example.yaml")
    assert len(config.repo_names()) == 5

def test_default_dataset_applies() -> None:
    """default_dataset parses from the example."""
    config = load_config("llmjudge.example.yaml")
    assert config.default_dataset
