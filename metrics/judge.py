#!/usr/bin/env python3
"""
judge.py --- LLM judge client interface used by metrics

Contains:
    JudgeClient: protocol every judge client implements
    StubJudge: deterministic judge for tests and local runs
"""

from typing import Protocol


class JudgeClient(Protocol):
    """Defines the minimal interface every LLM judge client implements."""

    def complete(self, prompt: str) -> str:
        """Returns the model completion for a prompt.

        Args:
            prompt: Fully rendered prompt to score.

        Returns:
            completion: Raw model output text.
        """
        ...


class StubJudge:
    """Deterministic judge for tests and local development.

    Attributes:
        responses: Queued completions returned in call order.
        calls: Prompts seen so far, in call order.
    """

    def __init__(self, responses: list[str]) -> None:
        """Stores the scripted completions."""
        self.responses = list(responses)
        self.calls = []

    def complete(self, prompt: str) -> str:
        """Returns the next scripted completion.

        Args:
            prompt: Fully rendered prompt to score.

        Returns:
            completion: Next scripted response, or "yes" when exhausted.
        """
        self.calls.append(prompt)
        if self.responses:
            return self.responses.pop(0)
        return "yes"
