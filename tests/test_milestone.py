"""Tests for the M0 milestone completeness gate."""

from __future__ import annotations

from pathlib import Path

from voltquery.seed import check_m0
from voltquery.seed.issues import Severity


def _error_codes(issues: list) -> set[str]:
    return {
        issue.code for issue in issues if issue.severity == Severity.ERROR
    }


def test_m0_missing_corpus(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    issues = check_m0(tmp_path / "nope.jsonl", fixture_sources_path, fixture_assets_root)
    assert "milestone_corpus_missing" in _error_codes(issues)


def test_m0_unpopulated_corpus_reports_counts(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    # The fixture corpus has 4 circuit_theory records and 0 analog ones; the
    # fixture source is approved+verified, so only the count gates fail.
    issues = check_m0(
        fixture_corpus_path,
        fixture_sources_path,
        fixture_assets_root,
    )
    codes = _error_codes(issues)
    assert "milestone_problem_count" in codes
    assert "milestone_circuit_count" in codes
    assert "milestone_analog_count" in codes
    assert "milestone_source_unapproved" not in codes
    assert "milestone_source_unverified" not in codes
