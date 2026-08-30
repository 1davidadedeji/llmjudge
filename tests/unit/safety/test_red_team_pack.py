#!/usr/bin/env python3
"""
test_red_team_pack.py --- unit tests for the red-team safety pack

Contains:
    test_score_all_refused: full marks when every probe is refused
    test_score_partial: partial resistance yields a fractional score
"""

from safety.red_team_pack import RedTeamPack, SafetyCase

CASES = [
    SafetyCase("c1", "hate", "p1", True),
    SafetyCase("c2", "hate", "p2", True),
]


def test_score_all_refused() -> None:
    """Full resistance when every case is refused as expected."""
    pack = RedTeamPack(CASES)
    assert pack.score({}, {"c1": True, "c2": True}) == 1.0


def test_score_partial() -> None:
    """Half resistance when one of two cases is answered unsafely."""
    pack = RedTeamPack(CASES)
    assert pack.score({}, {"c1": True, "c2": False}) == 0.5


def test_score_empty_pack() -> None:
    """An empty pack scores as fully resistant by convention."""
    assert RedTeamPack([]).score({}, {}) == 1.0


def test_by_category_filters() -> None:
    """Category filter keeps only matching cases."""
    from safety.red_team_pack import by_category

    mixed = CASES + [SafetyCase("c3", "fraud", "p3", True)]
    assert [c.case_id for c in by_category(mixed, "fraud")] == ["c3"]
