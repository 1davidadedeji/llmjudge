#!/usr/bin/env python3
"""
test_generator.py --- unit tests for the synthetic dataset generator

Contains:
    test_generate_writes_cache: generated cases land in the cache
    test_generate_uses_warm_cache: a warm cache skips the judge
"""

from data.generator import SyntheticGenerator
from metrics.judge import StubJudge

PAYLOAD = '{"question": "q", "answer": "a", "context": "c"}'


def make_generator(tmp_path, responses: list[str]) -> SyntheticGenerator:
    """Builds a generator with a scripted judge and temp cache.

    Args:
        tmp_path: Pytest temp dir for the cache.
        responses: Scripted judge responses.

    Returns:
        generator: SyntheticGenerator under test.
    """
    return SyntheticGenerator(StubJudge(responses), cache_dir=str(tmp_path))


def test_generate_writes_cache(tmp_path) -> None:
    """Generated cases land in the cache directory."""
    generator = make_generator(tmp_path, [PAYLOAD, PAYLOAD])
    cases = generator.generate("geography", count=2)
    assert len(cases) == 2
    assert list(tmp_path.glob("*.jsonl"))


def test_generate_uses_warm_cache(tmp_path) -> None:
    """A warm cache skips the judge entirely."""
    generator = make_generator(tmp_path, [PAYLOAD])
    generator.generate("geography", count=1)
    cases = generator.generate("geography", count=1)
    assert len(cases) == 1
