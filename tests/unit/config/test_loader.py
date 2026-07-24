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

def test_metrics_nonempty_per_repo() -> None:
    """Every configured repo enables at least one metric."""
    config = load_config("llmjudge.example.yaml")
    for repo in config.repos:
        assert repo.metrics

def test_repo_config_preserves_order() -> None:
    """Repo order in the file is preserved."""
    config = load_config("llmjudge.example.yaml")
    names = config.repo_names()
    assert names[0] == "retrieval-core"

def test_uses_metric() -> None:
    """uses_metric reflects the repo's selections."""
    config = load_config("llmjudge.example.yaml")
    assert config.repos[0].uses_metric("faithfulness")
    assert not config.repos[0].uses_metric("agent_trajectory")

def test_metric_selection_name_required() -> None:
    """MetricSelection requires a name."""
    import pytest
    from pydantic import ValidationError

    from config.schema import MetricSelection

    with pytest.raises(ValidationError):
        MetricSelection()
