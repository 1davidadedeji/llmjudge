#!/usr/bin/env python3
"""
faithfulness.py --- measures whether the answer is grounded in the retrieved context

Contains:
    FaithfulnessMetric: scores claim-level entailment against the context
    FaithfulnessMetric.measure(): computes the faithfulness score for one test case
    FaithfulnessMetric.extract_claims(): splits an answer into atomic claims
    FaithfulnessMetric.is_entailed(): asks the judge for one entailment verdict
"""

import re

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric
from metrics.judge import JudgeClient

CLAIM_PROMPT = (
    "Context:\n{context}\n\nClaim: {claim}\n"
    "Is the claim fully supported by the context? Answer yes or no."
)


class FaithfulnessMetric(BaseMetric):
    """Scores claim-level entailment of the answer against the context.

    Attributes:
        judge: LLM client used for entailment verdicts.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "faithfulness"

    def __init__(self, judge: JudgeClient, threshold: float = 0.8) -> None:
        """Stores the judge client and pass threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1]")
        self.judge = judge
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the faithfulness score for one test case.

        Args:
            test_case: Eval case with the answer and retrieved context.

        Returns:
            score: Fraction of answer claims entailed by the context.
        """
        claims = self.extract_claims(test_case.actual_output)
        if not claims:
            return 1.0
        context = "\n".join(test_case.retrieval_context)
        verdicts = [self.is_entailed(claim, context) for claim in claims]
        return sum(verdicts) / len(verdicts)

    def extract_claims(self, answer: str) -> list[str]:
        """Splits an answer into atomic claims.

        Args:
            answer: Generated answer text.

        Returns:
            claims: Non-empty sentence-level claims.
        """
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", answer) if part.strip()]

    def is_entailed(self, claim: str, context: str) -> bool:
        """Asks the judge whether the context entails one claim.

        Args:
            claim: Single atomic claim from the answer.
            context: Joined retrieved context.

        Returns:
            entailed: True when the judge answers yes.
        """
        verdict = self.judge.complete(CLAIM_PROMPT.format(context=context, claim=claim))
        return verdict.strip().lower().startswith("yes")
