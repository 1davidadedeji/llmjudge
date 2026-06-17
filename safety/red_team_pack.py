#!/usr/bin/env python3
"""
red_team_pack.py --- safety metric pack: toxicity and prompt-injection resistance

Contains:
    SafetyCase: one adversarial probe from a safety pack
    load_pack(): parses a YAML safety pack into SafetyCase entries
    RedTeamPack: scores a model's resistance to a loaded pack
"""

from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class SafetyCase:
    """One adversarial probe from a safety pack.

    Attributes:
        case_id: Stable identifier for the probe.
        category: Attack family the probe belongs to.
        prompt: Adversarial input shown to the model under test.
        expect_refusal: True when a safe model must refuse the request.
    """

    case_id: str
    category: str
    prompt: str
    expect_refusal: bool


def load_pack(path: str) -> list[SafetyCase]:
    """Parses a YAML safety pack into SafetyCase entries.

    Args:
        path: Filesystem path to the pack YAML file.

    Returns:
        cases: SafetyCase entries in file order.
    """
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    return [SafetyCase(**entry) for entry in raw["cases"]]


class RedTeamPack:
    """Scores a model's resistance to a loaded safety pack.

    Attributes:
        cases: SafetyCase entries the pack will run.
    """

    def __init__(self, cases: list[SafetyCase]) -> None:
        """Stores the case list for scoring runs."""
        self.cases = cases

    def score(self, responses: dict[str, str], refused: dict[str, bool]) -> float:
        """Computes pack resistance from per-case refusal outcomes.

        Args:
            responses: Model responses keyed by case id.
            refused: Refusal flags keyed by case id.

        Returns:
            resistance: Fraction of cases the model handled safely.
        """
        if not self.cases:
            return 1.0
        safe = sum(1 for case in self.cases if refused.get(case.case_id, False) == case.expect_refusal)
        return safe / len(self.cases)

def by_category(cases: list[SafetyCase], category: str) -> list[SafetyCase]:
    """Filters pack cases down to one attack category.

    Args:
        cases: Full case list from a loaded pack.
        category: Attack family to keep.

    Returns:
        filtered: Cases whose category matches, in input order.
    """
    return [case for case in cases if case.category == category]
