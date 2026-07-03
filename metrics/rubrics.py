#!/usr/bin/env python3
"""
rubrics.py --- per-metric rubric templates loaded from YAML

Contains:
    RubricTemplate: one metric's rubric template
    load_rubric(): parses a rubric template YAML file
    rubric_path(): resolves the template path for a metric name
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

TEMPLATE_DIR = Path(__file__).parent / "rubric_templates"


@dataclass(frozen=True)
class RubricTemplate:
    """One metric's rubric template.

    Attributes:
        metric: Metric name the template belongs to.
        version: Template version, bumped on any criteria change.
        criteria: Ordered scoring criteria shown to the judge.
        scale_min: Lowest score on the rubric scale.
        scale_max: Highest score on the rubric scale.
    """

    metric: str
    version: int
    criteria: list[str]
    scale_min: int
    scale_max: int


def rubric_path(metric: str) -> Path:
    """Resolves the template path for a metric name.

    Args:
        metric: Metric name to resolve.

    Returns:
        path: Filesystem path of the metric's rubric template.
    """
    return TEMPLATE_DIR / f"{metric}.yaml"


def load_rubric(metric: str) -> RubricTemplate:
    """Parses the rubric template for a metric.

    Args:
        metric: Metric name whose template should be loaded.

    Returns:
        template: Parsed RubricTemplate.
    """
    with open(rubric_path(metric)) as fh:
        raw = yaml.safe_load(fh)
    return RubricTemplate(**raw)

def list_rubrics() -> list[str]:
    """Lists every metric with a rubric template on disk.

    Returns:
        metrics: Sorted metric names with available templates.
    """
    return sorted(path.stem for path in TEMPLATE_DIR.glob("*.yaml"))

def template_version(metric: str) -> int:
    """Reads just the version of a metric's rubric template.

    Args:
        metric: Metric name whose template version is wanted.

    Returns:
        version: Template version number.
    """
    return load_rubric(metric).version
