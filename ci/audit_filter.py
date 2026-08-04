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

def main() -> int:
    """CLI entrypoint: fails when unoverridden findings remain.

    Returns:
        exit_code: 0 when no live findings remain, 1 otherwise.
    """
    import argparse
    import datetime
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True)
    args = parser.parse_args()
    with open(args.check) as fh:
        report = json.load(fh)
    findings = [dep["name"] for dep in report.get("dependencies", []) if dep.get("vulns")]
    today = datetime.date.today().isoformat()
    remaining = filter_findings(findings, load_overrides(), today)
    if remaining:
        print(f"unaccepted vulnerabilities: {', '.join(remaining)}")
        return 1
    print("vulnerability scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

def expiring_soon(overrides: list[Override], today: str, window_days: int = 14) -> list[Override]:
    """Lists overrides expiring within the warning window.

    Args:
        overrides: Accepted-risk entries from load_overrides().
        today: Current date as an ISO string.
        window_days: Days ahead to warn about.

    Returns:
        expiring: Overrides whose expiry falls inside the window.
    """
    import datetime

    today_date = datetime.date.fromisoformat(today)
    horizon = (today_date + datetime.timedelta(days=window_days)).isoformat()
    return [o for o in overrides if today <= o.expires <= horizon]
