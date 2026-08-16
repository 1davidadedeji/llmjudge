#!/usr/bin/env python3
"""
templates.py --- prompt templates for synthetic eval data generation

Contains:
    QA_TEMPLATE: template for question-answer case generation
    TOPICS: seed topics the generator draws from
"""

QA_TEMPLATE = (
    "Generate one factual question about {topic}, its correct answer, and a context "
    "passage that supports the answer. Return JSON with keys question, answer, context."
)

TOPICS = [
    "geography",
    "basic science",
    "world history",
    "programming fundamentals",
    "mathematics",
    "biology",
    "physics",
    "economics",
    "astronomy",
    "linguistics",
]

RAG_TEMPLATE = (
    "Generate a question about {topic}, a ground-truth answer, and three ranked "
    "context passages where only the first is relevant. Return JSON."
)

ADVERSARIAL_TEMPLATE = (
    "Generate a question about {topic} whose common-but-wrong answer is tempting, "
    "the correct answer, and a context passage. Return JSON."
)

SELF_CHECK_TEMPLATE = (
    "Review this QA pair about {topic} for factual errors. "
    "Return the same JSON with a corrected answer if needed."
)

HARD_SUFFIX = " Make the question require multi-hop reasoning over the context."
