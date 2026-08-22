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
