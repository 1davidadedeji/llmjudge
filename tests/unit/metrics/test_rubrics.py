#!/usr/bin/env python3
"""
test_rubrics.py --- unit tests for rubric template loading

Contains:
    test_load_g_eval_rubric: g_eval template parses with its criteria
    test_rubric_path_resolves: path resolution follows the metric name
"""

from metrics.rubrics import load_rubric, rubric_path


def test_load_g_eval_rubric() -> None:
    """G-Eval template parses with its three criteria."""
    template = load_rubric("g_eval")
    assert template.metric == "g_eval"
    assert len(template.criteria) == 3
    assert template.scale_max == 5


def test_rubric_path_resolves() -> None:
    """Path resolution appends the metric name to the template dir."""
    assert rubric_path("faithfulness").name == "faithfulness.yaml"

def test_scale_bounds_ordered() -> None:
    """Every shipped template has an ordered scale."""
    for name in ("g_eval", "faithfulness", "hallucination"):
        template = load_rubric(name)
        assert template.scale_min < template.scale_max

def test_list_rubrics_covers_core_metrics() -> None:
    """Template listing includes the core metrics."""
    from metrics.rubrics import list_rubrics

    rubrics = list_rubrics()
    assert "faithfulness" in rubrics and "g_eval" in rubrics
