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
    fixture_documents_path: Path,
) -> None:
    issues = check_m0(
        tmp_path / "nope.jsonl",
        fixture_sources_path,
        fixture_assets_root,
        fixture_documents_path,
    )
    assert "milestone_corpus_missing" in _error_codes(issues)


def test_m0_unpopulated_corpus_reports_counts(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    # The fixture corpus has 4 circuit_theory records and 0 analog ones; the
    # fixture source is approved+verified+public_redistributable, so only the
    # count gates fail.
    issues = check_m0(
        fixture_corpus_path,
        fixture_sources_path,
        fixture_assets_root,
        fixture_documents_path,
    )
    codes = _error_codes(issues)
    assert "milestone_problem_count" in codes
    assert "milestone_circuit_count" in codes
    assert "milestone_analog_count" in codes
    assert "milestone_source_unapproved" not in codes
    assert "milestone_source_unverified" not in codes
    assert "milestone_source_not_redistributable" not in codes
    assert "milestone_source_no_redistribution" not in codes


def test_m0_blocks_research_only_source(
    tmp_path: Path,
    fixture_corpus_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        "sources:\n"
        "  - id: fixture-source\n"
        "    title: Fixture Source\n"
        "    authors: [VoltQuery Fixtures]\n"
        "    domains: [circuit_theory]\n"
        "    license:\n"
        "      id: CC-BY-NC-4.0\n"
        "      redistribution: false\n"
        "      derivatives: true\n"
        "      commercial: false\n"
        "      attribution_required: true\n"
        "      data_policy: research_only\n"
        "      verified: true\n"
        "    status: approved\n",
        encoding="utf-8",
    )
    issues = check_m0(fixture_corpus_path, sources, fixture_assets_root, fixture_documents_path)
    codes = _error_codes(issues)
    assert "milestone_source_not_redistributable" in codes
    assert "milestone_source_no_redistribution" in codes
    # The source is still approved and verified; only the data-policy gates trip.
    assert "milestone_source_unapproved" not in codes
    assert "milestone_source_unverified" not in codes


def test_m0_excludes_license_review_source(
    tmp_path: Path,
    fixture_corpus_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    # A source whose document imprint and collection license conflict is held in
    # LICENSE_REVIEW and must be excluded from the public Gold corpus, with a
    # distinct reason rather than being silently blocked as a bare unapproved
    # candidate.
    sources = tmp_path / "sources.yaml"
    sources.write_text(
        "sources:\n"
        "  - id: fixture-source\n"
        "    title: Fixture Source\n"
        "    authors: [VoltQuery Fixtures]\n"
        "    domains: [circuit_theory]\n"
        "    license:\n"
        "      id: CC-BY-NC-SA-4.0\n"
        "      redistribution: false\n"
        "      derivatives: false\n"
        "      commercial: false\n"
        "      attribution_required: true\n"
        "      data_policy: research_only\n"
        "      verified: false\n"
        "    status: license_review\n",
        encoding="utf-8",
    )
    issues = check_m0(fixture_corpus_path, sources, fixture_assets_root, fixture_documents_path)
    codes = _error_codes(issues)
    assert "milestone_source_license_review" in codes
    assert "milestone_source_unapproved" not in codes
    assert "milestone_source_not_redistributable" not in codes
