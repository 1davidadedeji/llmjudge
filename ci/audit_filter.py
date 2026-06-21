#!/usr/bin/env python3
"""
audit_filter.py --- filters pip-audit findings through accepted-risk overrides

Contains:
    Override: one accepted vulnerability with an expiry date
    load_overrides(): parses ci/audit_overrides.yaml
    filter_findings(): drops findings covered by an unexpired override
"""

from dataclasses import dataclass

import yaml

OVERRIDES_PATH = "ci/audit_overrides.yaml"


@dataclass(frozen=True)
class Override:
    """One accepted vulnerability with an expiry date.

    Attributes:
        vuln_id: Advisory identifier the override covers.
        expires: ISO date after which the override no longer applies.
        reason: Why the risk is accepted.
    """

    vuln_id: str
    expires: str
    reason: str


def load_overrides(path: str = OVERRIDES_PATH) -> list[Override]:
    """Parses the overrides file.

    Args:
        path: Filesystem path to the overrides YAML.

    Returns:
        overrides: Parsed Override entries.
    """
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    return [Override(**entry) for entry in raw.get("overrides", [])]


def filter_findings(findings: list[str], overrides: list[Override], today: str) -> list[str]:
    """Drops findings covered by an unexpired override.

    Args:
        findings: Advisory identifiers reported by the scanner.
        overrides: Accepted-risk entries from load_overrides().
        today: Current date as an ISO string.

    Returns:
        remaining: Findings not covered by any live override.
    """
    active = {override.vuln_id for override in overrides if override.expires >= today}
    return [finding for finding in findings if finding not in active]
