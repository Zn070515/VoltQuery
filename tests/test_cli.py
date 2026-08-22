"""Smoke tests for the validate CLI."""

from __future__ import annotations

from pathlib import Path

from voltquery.cli import main


def test_validate_fixture_clean(
    fixture_sources_path: Path,
    fixture_corpus_path: Path,
    fixture_assets_root: Path,
) -> None:
    code = main(
        [
            "validate",
            "--sources",
            str(fixture_sources_path),
            "--corpus",
            str(fixture_corpus_path),
            "--assets",
            str(fixture_assets_root),
        ]
    )
    assert code == 0


def test_milestone_m0_fixture_reports_count_gates(
    fixture_sources_path: Path,
    fixture_corpus_path: Path,
    fixture_assets_root: Path,
) -> None:
    code = main(
        [
            "milestone",
            "m0",
            "--sources",
            str(fixture_sources_path),
            "--corpus",
            str(fixture_corpus_path),
            "--assets",
            str(fixture_assets_root),
        ]
    )
    # The fixture corpus is structurally valid but under the 40/32/8 targets.
    assert code == 1
