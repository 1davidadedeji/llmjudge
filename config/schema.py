#!/usr/bin/env python3
"""
schema.py --- per-repo eval configuration schema

Contains:
    MetricSelection: one metric enabled for a repo, with optional threshold override
    RepoEvalConfig: eval configuration for one repo
    LlmjudgeConfig: top-level configuration across repos
"""

from pydantic import BaseModel, Field


class MetricSelection(BaseModel):
    """One metric enabled for a repo.

    Attributes:
        name: Metric registry name.
        threshold: Optional per-repo threshold override.
    """

    name: str
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class RepoEvalConfig(BaseModel):
    """Eval configuration for one repo.

    Attributes:
        repo: Repo name as used in the results store.
        dataset: Dataset identifier the repo evaluates against.
        metrics: Metrics enabled for the repo.
    """

    repo: str
    dataset: str
    metrics: list[MetricSelection]

    def threshold_for(self, metric: str) -> float | None:
        """Resolves the per-repo threshold override for a metric.

        Args:
            metric: Metric registry name.

        Returns:
            threshold: Override value, or None when unset.
        """
        for selection in self.metrics:
            if selection.name == metric:
                return selection.threshold
        return None

    def metric_names(self) -> list[str]:
        """Lists the metric names enabled for the repo.

        Returns:
            names: Metric registry names in config order.
        """
        return [metric.name for metric in self.metrics]


class LlmjudgeConfig(BaseModel):
    """Top-level configuration across repos.

    Attributes:
        repos: Per-repo eval configurations.
        default_dataset: Dataset used when a repo omits one.
    """

    repos: list[RepoEvalConfig]
    default_dataset: str = "gold-v1"

    def repo_names(self) -> list[str]:
        """Lists configured repo names.

        Returns:
            names: Repo names in config order.
        """
        return [repo.repo for repo in self.repos]
