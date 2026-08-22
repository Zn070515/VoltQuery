"""Tests for source registry validation."""

from __future__ import annotations

from pathlib import Path

from voltquery.seed import validate_sources
from voltquery.seed.issues import Severity


def _write_sources(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "sources.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _error_codes(path: Path) -> set[str]:
    issues = validate_sources(path)
    return {issue.code for issue in issues if issue.severity == Severity.ERROR}


def test_fixture_sources_have_no_errors(fixture_sources_path: Path) -> None:
    assert _error_codes(fixture_sources_path) == set()


def test_source_license_present(fixture_sources_path: Path) -> None:
    issues = validate_sources(fixture_sources_path)
    assert "source_license_missing" not in {issue.code for issue in issues}


def test_duplicate_source_id(tmp_path: Path) -> None:
    path = _write_sources(
        tmp_path,
        "sources:\n"
        "  - id: a\n"
        "    title: A\n"
        "    domains: [circuit_theory]\n"
        "    license:\n"
        "      id: UNKNOWN\n"
        "      data_policy: unknown\n"
        "      verified: false\n"
        "  - id: a\n"
        "    title: B\n"
        "    domains: [circuit_theory]\n"
        "    license:\n"
        "      id: UNKNOWN\n"
        "      data_policy: unknown\n"
        "      verified: false\n",
    )
    assert "duplicate_source_id" in _error_codes(path)


def test_source_license_missing(tmp_path: Path) -> None:
    path = _write_sources(
        tmp_path,
        "sources:\n"
        "  - id: a\n"
        "    title: A\n"
        "    domains: [circuit_theory]\n",
    )
    assert "source_license_missing" in _error_codes(path)
