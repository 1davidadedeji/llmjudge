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
]
