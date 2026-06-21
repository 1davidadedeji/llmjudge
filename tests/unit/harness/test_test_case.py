#!/usr/bin/env python3
"""
test_test_case.py --- unit tests for the LLMTestCase data model

Contains:
    test_minimal_case: only input and output are required
    test_defaults_empty: optional fields default to empty
"""

from harness.test_case import LLMTestCase


def test_minimal_case() -> None:
    """Only input and actual_output are required."""
    case = LLMTestCase(input="q", actual_output="a")
    assert case.input == "q"
    assert case.actual_output == "a"


def test_defaults_empty() -> None:
    """Optional fields default to empty values."""
    case = LLMTestCase(input="q", actual_output="a")
    assert case.expected_output is None
    assert case.retrieval_context == []
    assert case.metadata == {}

def test_is_rag_case() -> None:
    """RAG flag reflects presence of retrieval context."""
    assert LLMTestCase(input="q", actual_output="a", retrieval_context=["p"]).is_rag_case
    assert not LLMTestCase(input="q", actual_output="a").is_rag_case

def test_has_expected_output() -> None:
    """Expected-output flag reflects the field."""
    assert not LLMTestCase(input="q", actual_output="a").has_expected_output
    case = LLMTestCase(input="q", actual_output="a", expected_output="e")
    assert case.has_expected_output

def test_frozen_immutable() -> None:
    """Cases are immutable once created."""
    import dataclasses

    import pytest

    case = LLMTestCase(input="q", actual_output="a")
    with pytest.raises(dataclasses.FrozenInstanceError):
        case.input = "other"

def test_metadata_independent_per_case() -> None:
    """Default metadata dicts are not shared."""
    first = LLMTestCase(input="q", actual_output="a")
    second = LLMTestCase(input="q", actual_output="a")
    assert first.metadata is not second.metadata

def test_lists_independent_per_case() -> None:
    """Default list fields are not shared."""
    first = LLMTestCase(input="q", actual_output="a")
    second = LLMTestCase(input="q", actual_output="a")
    assert first.retrieval_context is not second.retrieval_context
