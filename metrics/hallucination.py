#!/usr/bin/env python3
"""
hallucination.py --- detects answer claims that contradict the provided context

Contains:
    HallucinationMetric: scores the absence of contradicted claims
    HallucinationMetric.measure(): computes the hallucination score for one test case
"""

import re

from harness.test_case import LLMTestCase
from metrics.judge import JudgeClient

CONTRADICTION_PROMPT = (
    "Context:\n{context}\n\nClaim: {claim}\n"
    "Does the context contradict this claim? Answer yes or no."
)


class HallucinationMetric:
    """Scores answers by the absence of context-contradicted claims.

    Attributes:
        judge: LLM client used for contradiction verdicts.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "hallucination"

    def __init__(self, judge: JudgeClient, threshold: float = 0.9) -> None:
        """Stores the judge client and pass threshold."""
        self.judge = judge
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the hallucination score for one test case.

        Args:
            test_case: Eval case with the answer and reference context.

        Returns:
            score: Fraction of claims not contradicted by the context.
        """
        claims = self.extract_claims(test_case.actual_output)
        if not claims:
            return 1.0
        context = "\n".join(test_case.context or test_case.retrieval_context)
        contradicted = sum(self.is_contradicted(claim, context) for claim in claims)
        return 1.0 - contradicted / len(claims)

    def extract_claims(self, answer: str) -> list[str]:
        """Splits an answer into atomic claims.

        Args:
            answer: Generated answer text.

        Returns:
            claims: Non-empty sentence-level claims.
        """
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", answer) if part.strip()]

    def is_contradicted(self, claim: str, context: str) -> bool:
        """Asks the judge whether the context contradicts one claim.

        Args:
            claim: Single atomic claim from the answer.
            context: Joined reference context.

        Returns:
            contradicted: True when the judge answers yes.
        """
        verdict = self.judge.complete(CONTRADICTION_PROMPT.format(context=context, claim=claim))
        return verdict.strip().lower().startswith("yes")
