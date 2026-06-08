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
