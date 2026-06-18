#!/usr/bin/env python3
"""
test_judge_stub.py --- unit tests for the deterministic StubJudge

Contains:
    test_stub_returns_scripted_in_order: scripted responses come back in order
    test_stub_falls_back_to_yes: exhausted scripts return yes
"""

from metrics.judge import StubJudge


def test_stub_returns_scripted_in_order() -> None:
    """Scripted responses come back in call order."""
    judge = StubJudge(["a", "b"])
    assert judge.complete("p") == "a"
    assert judge.complete("p") == "b"


def test_stub_falls_back_to_yes() -> None:
    """An exhausted script falls back to yes."""
    judge = StubJudge([])
    assert judge.complete("p") == "yes"


def test_stub_records_calls() -> None:
    """Every prompt is recorded on the calls list."""
    judge = StubJudge([])
    judge.complete("first")
    judge.complete("second")
    assert judge.calls == ["first", "second"]
