#!/usr/bin/env python3
"""
test_audit_filter.py --- unit tests for vulnerability-override filtering

Contains:
    test_filter_drops_covered_finding: live override hides its finding
    test_filter_keeps_expired_override: expired override stops applying
"""

from ci.audit_filter import Override, filter_findings


def test_filter_drops_covered_finding() -> None:
    """A finding covered by a live override is filtered out."""
    overrides = [Override("CVE-0000-1", "2999-01-01", "false positive in dev-only path")]
    assert filter_findings(["CVE-0000-1"], overrides, "2026-06-21") == []


def test_filter_keeps_expired_override() -> None:
    """An expired override no longer hides its finding."""
    overrides = [Override("CVE-0000-1", "2026-01-01", "stale")]
    assert filter_findings(["CVE-0000-1"], overrides, "2026-06-21") == ["CVE-0000-1"]


def test_filter_passes_through_unrelated() -> None:
    """Findings with no matching override always survive."""
    assert filter_findings(["CVE-1111-2"], [], "2026-06-21") == ["CVE-1111-2"]

def test_override_requires_reason() -> None:
    """Overrides without a justification are rejected at construction time."""
    import pytest

    with pytest.raises(TypeError):
        Override("CVE-0000-1", "2999-01-01")

def test_override_fields() -> None:
    """Override stores id, expiry, and reason."""
    override = Override("CVE-1", "2999-01-01", "justified")
    assert override.vuln_id == "CVE-1"

def test_filter_multiple_findings() -> None:
    """Filtering handles mixed covered/uncovered lists."""
    overrides = [Override("CVE-1", "2999-01-01", "ok")]
    remaining = filter_findings(["CVE-1", "CVE-2"], overrides, "2026-07-01")
    assert remaining == ["CVE-2"]
