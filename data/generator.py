#!/usr/bin/env python3
"""
generator.py --- synthetic eval dataset generator

Contains:
    SyntheticGenerator: generates QA eval cases from prompt templates
    SyntheticGenerator.generate(): produces a batch of synthetic cases
    SyntheticGenerator.load_gold_set(): loads the cached synthetic gold set
"""

import hashlib
import json
import os
from pathlib import Path

from data.templates import QA_TEMPLATE, TOPICS
from metrics.judge import JudgeClient

DEFAULT_CACHE_DIR = ".cache/llmjudge"


class SyntheticGenerator:
    """Generates QA eval cases from prompt templates.

    Attributes:
        judge: LLM client used for case generation.
        cache_dir: Directory generated cases are cached in.
    """

    def __init__(self, judge: JudgeClient, cache_dir: str = DEFAULT_CACHE_DIR) -> None:
        """Stores the judge client and cache location."""
        self.judge = judge
        self.cache_dir = Path(cache_dir)

    def cache_key(self, topic: str) -> str:
        """Builds the cache key for a topic.

        Args:
            topic: Topic the cases were generated for.

        Returns:
            key: Stable hash key for the topic.
        """
        return hashlib.sha256(topic.encode()).hexdigest()[:16]

    def generate(self, topic: str, count: int = 10) -> list[dict]:
        """Produces a batch of synthetic cases, using the cache when warm.

        Args:
            topic: Topic to generate cases for.
            count: Number of cases to generate.

        Returns:
            cases: Generated QA case dicts.
        """
        cache_path = self.cache_dir / f"{self.cache_key(topic)}.jsonl"
        if cache_path.exists():
            return [json.loads(line) for line in cache_path.read_text().splitlines() if line]
        cases = []
        for _ in range(count):
            raw = self.judge.complete(QA_TEMPLATE.format(topic=topic))
            cases.append(json.loads(raw))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("\n".join(json.dumps(case) for case in cases))
        return cases

    def load_gold_set(self) -> list[dict]:
        """Loads the cached synthetic gold set.

        Returns:
            cases: Every cached case across topics.
        """
        cases = []
        for path in sorted(self.cache_dir.glob("*.jsonl")):
            cases.extend(json.loads(line) for line in path.read_text().splitlines() if line)
        return cases

    def topics(self) -> list[str]:
        """Lists the seed topics.

        Returns:
            topics: Seed topic list.
        """
        return list(TOPICS)

    def generate_rag_cases(self, topic: str, count: int = 5) -> list[dict]:
        """Generates cases with ranked retrieval contexts.

        Args:
            topic: Topic to generate cases for.
            count: Number of cases to generate.

        Returns:
            cases: Generated RAG case dicts.
        """
        from data.templates import RAG_TEMPLATE

        return [json.loads(self.judge.complete(RAG_TEMPLATE.format(topic=topic))) for _ in range(count)]
