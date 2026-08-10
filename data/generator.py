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
        cache_path = self.cache_dir / "synthetic" / f"{self.cache_key(topic)}.jsonl"
        if cache_path.exists():
            return [json.loads(line) for line in cache_path.read_text().splitlines() if line]
        cases = []
        for _ in range(count):
            raw = self.judge.complete(QA_TEMPLATE.format(topic=topic))
            case = json.loads(raw)
            case["provenance"] = "synthetic"
            if not self.validate_case(case):
                cases.append(case)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("\n".join(json.dumps(case) for case in cases))
        return cases

    def load_gold_set(self) -> list[dict]:
        """Loads the cached synthetic gold set.

        Returns:
            cases: Every cached case across topics.
        """
        cases = []
        for path in sorted((self.cache_dir / "synthetic").glob("*.jsonl")):
            for line in path.read_text().splitlines():
                if line:
                    case = json.loads(line)
                    if case.get("provenance") == "synthetic":
                        cases.append(case)
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

    def cache_size(self) -> int:
        """Counts cached case files.

        Returns:
            count: Number of cached JSONL files.
        """
        return len(list(self.cache_dir.glob("*.jsonl")))

    def estimate_calls(self, count: int) -> int:
        """Estimates judge calls needed for a generation batch.

        Args:
            count: Cases planned for the batch.

        Returns:
            calls: Judge calls the batch will make.
        """
        return max(0, count)

    def deduplicate(self, cases: list[dict]) -> list[dict]:
        """Drops cases whose question already appears in the batch.

        Args:
            cases: Generated case dicts.

        Returns:
            deduplicated: Cases with duplicate questions removed.
        """
        seen: set[str] = set()
        unique = []
        for case in cases:
            question = case.get("question", "")
            if question not in seen:
                seen.add(question)
                unique.append(case)
        return unique

    def validate_case(self, case: dict) -> list[str]:
        """Validates one generated case.

        Args:
            case: Generated case dict.

        Returns:
            problems: Missing-field messages; empty when valid.
        """
        return [f"missing {field}" for field in ("question", "answer", "context") if field not in case]

    def generate_topics_batch(self, count_per_topic: int = 5) -> dict[str, list[dict]]:
        """Generates a batch across every seed topic.

        Args:
            count_per_topic: Cases to generate per topic.

        Returns:
            batches: Mapping of topic to generated cases.
        """
        return {topic: self.generate(topic, count_per_topic) for topic in self.topics()}

    def difficulty_mix(self, count: int) -> dict[str, int]:
        """Plans the easy/medium/hard split for a batch.

        Args:
            count: Total cases planned.

        Returns:
            mix: Mapping of difficulty label to case count.
        """
        hard = max(1, count // 5)
        medium = max(1, count // 3)
        return {"easy": count - hard - medium, "medium": medium, "hard": hard}
