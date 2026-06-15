#!/usr/bin/env python3
"""
answer_relevancy.py --- measures how relevant the answer is to the input question

Contains:
    AnswerRelevancyMetric: scores answer relevance against the input
    AnswerRelevancyMetric.measure(): computes the relevancy score for one test case
"""

import re

from harness.test_case import LLMTestCase
from metrics.base import BaseMetric
from metrics.judge import JudgeClient

RELEVANCY_PROMPT = (
    "Question: {question}\nAnswer: {answer}\n"
    "Does the answer address the question directly? Answer yes or no."
)
STOPWORDS = frozenset(
    "a an the is are was were of to in on for and or with that this it as at by".split()
)


def tokenize(text: str) -> list[str]:
    """Splits text into lowercase content tokens.

    Args:
        text: Raw text to tokenize.

    Returns:
        tokens: Alphabetic tokens with stopwords removed.
    """
    return [tok for tok in re.findall(r"[a-z']+", text.lower()) if tok not in STOPWORDS]


class AnswerRelevancyMetric(BaseMetric):
    """Scores how directly the answer addresses the input question.

    Attributes:
        judge: LLM client used for the relevancy verdict.
        threshold: Minimum score for the metric to count as passing.
    """

    name = "answer_relevancy"

    def __init__(self, judge: JudgeClient, threshold: float = 0.75) -> None:
        """Stores the judge client and pass threshold."""
        self.judge = judge
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        """Computes the relevancy score for one test case.

        Args:
            test_case: Eval case with the question and generated answer.

        Returns:
            score: Blend of the judge verdict and lexical overlap.
        """
        verdict = self.judge.complete(
            RELEVANCY_PROMPT.format(question=test_case.input, answer=test_case.actual_output)
        )
        judge_score = 1.0 if verdict.strip().lower().startswith("yes") else 0.0
        return 0.5 * judge_score + 0.5 * self.overlap(test_case.input, test_case.actual_output)

    def overlap(self, question: str, answer: str) -> float:
        """Computes content-word overlap between question and answer.

        Args:
            question: Input question text.
            answer: Generated answer text.

        Returns:
            overlap: Fraction of question content tokens present in the answer.
        """
        question_tokens = set(tokenize(question))
        if not question_tokens:
            return 1.0
        answer_tokens = set(tokenize(answer))
        return len(question_tokens & answer_tokens) / len(question_tokens)
