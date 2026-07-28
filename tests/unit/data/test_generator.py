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

def test_load_gold_set_aggregates_topics(tmp_path) -> None:
    """Gold set loads every cached topic file."""
    generator = make_generator(tmp_path, [PAYLOAD, PAYLOAD])
    generator.generate("geography", count=1)
    generator.generate("basic science", count=1)
    assert len(generator.load_gold_set()) == 2

def test_cache_key_stable(tmp_path) -> None:
    """Cache keys are stable per topic."""
    generator = make_generator(tmp_path, [])
    assert generator.cache_key("geography") == generator.cache_key("geography")
    assert generator.cache_key("geography") != generator.cache_key("history")

def test_topics_returns_copy(tmp_path) -> None:
    """topics() returns a copy, not the shared list."""
    generator = make_generator(tmp_path, [])
    topics = generator.topics()
    topics.append("extra")
    assert "extra" not in generator.topics()

def test_generate_rag_cases(tmp_path) -> None:
    """RAG case generation uses the RAG template."""
    generator = make_generator(tmp_path, [PAYLOAD])
    cases = generator.generate_rag_cases("biology", count=1)
    assert cases == [{"question": "q", "answer": "a", "context": "c"}]

def test_topics_nonempty(tmp_path) -> None:
    """Seed topic list is never empty."""
    generator = make_generator(tmp_path, [])
    assert generator.topics()

def test_estimate_calls(tmp_path) -> None:
    """Cost estimate is one call per generated case."""
    generator = make_generator(tmp_path, [])
    assert generator.estimate_calls(7) == 7
    assert generator.estimate_calls(-1) == 0

def test_deduplicate(tmp_path) -> None:
    """Duplicate questions collapse to the first occurrence."""
    generator = make_generator(tmp_path, [])
    cases = [{"question": "q"}, {"question": "q"}, {"question": "r"}]
    assert len(generator.deduplicate(cases)) == 2

def test_validate_case(tmp_path) -> None:
    """Validation flags cases missing required fields."""
    generator = make_generator(tmp_path, [])
    assert generator.validate_case({"question": "q"}) == ["missing answer", "missing context"]
    assert generator.validate_case({"question": "q", "answer": "a", "context": "c"}) == []

def test_generate_skips_invalid_cases(tmp_path) -> None:
    """Invalid generations are dropped from the batch."""
    generator = make_generator(tmp_path, ["{}", PAYLOAD])
    cases = generator.generate("economics", count=2)
    assert cases == [{"question": "q", "answer": "a", "context": "c"}]

def test_gold_set_excludes_real_queries(tmp_path) -> None:
    """Real production queries never leak into the synthetic gold set."""
    import json as _json

    generator = make_generator(tmp_path, [PAYLOAD])
    generator.generate("geography", count=1)
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    leaked = {"question": "real-user-query", "provenance": "real"}
    (real_dir / "queries.jsonl").write_text(_json.dumps(leaked))
    gold = generator.load_gold_set()
    assert all(case.get("provenance") == "synthetic" for case in gold)
    assert not any(case.get("question") == "real-user-query" for case in gold)
