#!/usr/bin/env python3
"""
calibrate.py --- calibrates judge rubrics against a human-labeled gold set

Contains:
    GoldExample: one human-labeled example
    load_gold_set(): parses the gold set JSONL
    agreement(): fraction of judge verdicts matching human labels
    suggest_threshold(): picks the threshold best separating gold labels
"""

import json
from dataclasses import dataclass
from pathlib import Path

GOLD_SET_PATH = Path(__file__).parent / "gold_set.jsonl"


@dataclass(frozen=True)
class GoldExample:
    """One human-labeled example.

    Attributes:
        example_id: Stable identifier.
        question: Input question.
        answer: Candidate answer.
        label: Human score in [0, 1].
    """

    example_id: str
    question: str
    answer: str
    label: float


def load_gold_set(path: Path = GOLD_SET_PATH) -> list[GoldExample]:
    """Parses the gold set JSONL.

    Args:
        path: Filesystem path to the gold set file.

    Returns:
        examples: Parsed GoldExample entries.
    """
    with open(path) as fh:
        return [GoldExample(**json.loads(line)) for line in fh if line.strip()]


def agreement(judge_scores: list[float], labels: list[float], tolerance: float = 0.2) -> float:
    """Computes the fraction of judge scores matching human labels.

    Args:
        judge_scores: Scores produced by the judge.
        labels: Human labels aligned with the judge scores.
        tolerance: Absolute gap counted as agreement.

    Returns:
        rate: Fraction of pairs within tolerance.
    """
    if not labels:
        return 1.0
    matches = sum(abs(score - label) <= tolerance for score, label in zip(judge_scores, labels))
    return matches / len(labels)


def suggest_threshold(labels: list[float], steps: int = 20) -> float:
    """Picks the threshold best separating pass/fail gold labels.

    Args:
        labels: Human labels in [0, 1].
        steps: Number of candidate thresholds to try.

    Returns:
        threshold: Candidate maximizing label separation accuracy.
    """
    if not labels:
        return 0.5
    best_threshold = 0.5
    best_accuracy = -1.0
    for step in range(1, steps):
        candidate = step / steps
        predicted = [label >= candidate for label in labels]
        accuracy = sum(pred == (label >= 0.5) for pred, label in zip(predicted, labels))
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = candidate
    return best_threshold

def cohens_kappa(judge_pass: list[bool], human_pass: list[bool]) -> float:
    """Computes Cohen's kappa between judge and human pass decisions.

    Args:
        judge_pass: Judge pass/fail decisions.
        human_pass: Human pass/fail decisions, aligned with the judge's.

    Returns:
        kappa: Agreement corrected for chance; 1.0 is perfect agreement.
    """
    if not human_pass:
        return 1.0
    total = len(human_pass)
    observed = sum(j == h for j, h in zip(judge_pass, human_pass)) / total
    judge_rate = sum(judge_pass) / total
    human_rate = sum(human_pass) / total
    expected = judge_rate * human_rate + (1 - judge_rate) * (1 - human_rate)
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)
