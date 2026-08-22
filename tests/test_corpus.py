"""Tests for seed corpus validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from voltquery.contracts import SeedProblemRecord
from voltquery.seed import load_problems, validate_corpus


def corpus_codes(problems_path: Path, sources_path: Path, assets_root: Path) -> set[str]:
    issues = validate_corpus(problems_path, sources_path, assets_root)
    return {issue.code for issue in issues}


def test_problem_record_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "problem_record_invalid" not in codes
    assert "problem_record_invalid_json" not in codes


def test_problem_source_exists(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "problem_source_unknown" not in codes


def test_problem_ids_unique(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "duplicate_problem_id" not in codes


def test_problem_assets_exist(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "problem_asset_missing" not in codes


def test_topic_names_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "problem_record_invalid" not in codes


def test_domain_names_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    codes = corpus_codes(fixture_corpus_path, fixture_sources_path, fixture_assets_root)
    assert "problem_record_invalid" not in codes


def test_problem_asset_missing_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    record = SeedProblemRecord(
        id="vq_seed_9999",
        source={"source_id": "fixture-source"},
        domain="circuit_theory",
        topics=["ohm_law"],
        question_text="[fixture] missing asset test",
        has_formula=False,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=False,
        assets=[{"path": "assets/nope.svg", "kind": "figure"}],
    )
    corpus = tmp_path / "problems.jsonl"
    corpus.write_text(record.model_dump_json() + "\n", encoding="utf-8")
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root)
    assert "problem_asset_missing" in codes


def test_load_problems_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_problems(tmp_path / "nope.jsonl")


def test_load_problems_malformed_json_raises(tmp_path: Path) -> None:
    corpus = tmp_path / "problems.jsonl"
    corpus.write_text("{not valid json}\n", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_problems(corpus)


def test_asset_traversal_blocked_at_ingestion(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    # Write the raw line, bypassing the model, so validate_corpus is the thing
    # that has to reject a path-traversal asset reference.
    corpus = tmp_path / "problems.jsonl"
    corpus.write_text(
        '{"id": "vq_seed_9998", '
        '"source": {"source_id": "fixture-source"}, '
        '"domain": "circuit_theory", '
        '"topics": ["ohm_law"], '
        '"question_text": "[fixture] traversal test", '
        '"has_formula": false, '
        '"has_circuit_figure": false, '
        '"is_multipart": false, '
        '"answer_available": false, '
        '"assets": [{"path": "../escape.svg", "kind": "figure"}]}\n',
        encoding="utf-8",
    )
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root)
    assert "problem_record_invalid" in codes
