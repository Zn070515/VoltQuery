"""Tests for seed corpus validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from voltquery.contracts import SeedProblemRecord
from voltquery.seed import load_problems, validate_corpus


def corpus_codes(
    problems_path: Path,
    sources_path: Path,
    assets_root: Path,
    documents_path: Path,
) -> set[str]:
    issues = validate_corpus(problems_path, sources_path, assets_root, documents_path)
    return {issue.code for issue in issues}


def _write_problem(corpus: Path, record: SeedProblemRecord) -> None:
    corpus.write_text(record.model_dump_json() + "\n", encoding="utf-8")


def _write_corpus(corpus: Path, raw_line: str) -> None:
    corpus.write_text(raw_line, encoding="utf-8")


def test_problem_record_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "problem_record_invalid" not in codes
    assert "problem_record_invalid_json" not in codes


def test_problem_source_exists(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "problem_source_unknown" not in codes


def test_problem_ids_unique(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "duplicate_problem_id" not in codes


def test_problem_assets_exist(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "problem_asset_missing" not in codes


def test_topic_names_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "problem_record_invalid" not in codes


def test_domain_names_valid(
    fixture_corpus_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    codes = corpus_codes(
        fixture_corpus_path, fixture_sources_path, fixture_assets_root, fixture_documents_path
    )
    assert "problem_record_invalid" not in codes


def test_problem_asset_missing_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    record = SeedProblemRecord(
        id="vq_seed_9999",
        source={
            "source_id": "fixture-source",
            "document_id": "fixture-worksheet",
        },
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
    _write_problem(corpus, record)
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root, fixture_documents_path)
    assert "problem_asset_missing" in codes


def test_problem_document_missing_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    record = SeedProblemRecord(
        id="vq_seed_9997",
        source={"source_id": "fixture-source"},
        domain="circuit_theory",
        topics=["ohm_law"],
        question_text="[fixture] no document id",
        has_formula=False,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=False,
        assets=[],
    )
    corpus = tmp_path / "problems.jsonl"
    _write_problem(corpus, record)
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root, fixture_documents_path)
    assert "problem_document_missing" in codes


def test_problem_document_unknown_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
    fixture_documents_path: Path,
) -> None:
    record = SeedProblemRecord(
        id="vq_seed_9996",
        source={
            "source_id": "fixture-source",
            "document_id": "does-not-exist",
        },
        domain="circuit_theory",
        topics=["ohm_law"],
        question_text="[fixture] unknown document id",
        has_formula=False,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=False,
        assets=[],
    )
    corpus = tmp_path / "problems.jsonl"
    _write_problem(corpus, record)
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root, fixture_documents_path)
    assert "problem_document_unknown" in codes


def test_problem_document_source_mismatch_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_assets_root: Path,
) -> None:
    # A document registered under a different source than the one the problem
    # declares is a provenance break and must be flagged.
    documents = tmp_path / "documents.yaml"
    documents.write_text(
        "documents:\n"
        "  - id: doc-k\n"
        "    source_id: other-source\n"
        "    filename: k.pdf\n"
        "    url: https://x/k.pdf\n"
        "    sha256: '0000000000000000000000000000000000000000000000000000000000000000'\n"
        "    retrieved_at: 2026-08-22\n",
        encoding="utf-8",
    )
    record = SeedProblemRecord(
        id="vq_seed_9995",
        source={
            "source_id": "fixture-source",
            "document_id": "doc-k",
        },
        domain="circuit_theory",
        topics=["ohm_law"],
        question_text="[fixture] mismatched document source",
        has_formula=False,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=False,
        assets=[],
    )
    corpus = tmp_path / "problems.jsonl"
    _write_problem(corpus, record)
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root, documents)
    assert "problem_document_source_mismatch" in codes


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
    fixture_documents_path: Path,
) -> None:
    # Write the raw line, bypassing the model, so validate_corpus is the thing
    # that has to reject a path-traversal asset reference.
    corpus = tmp_path / "problems.jsonl"
    _write_corpus(
        corpus,
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
    )
    codes = corpus_codes(corpus, fixture_sources_path, fixture_assets_root, fixture_documents_path)
    assert "problem_record_invalid" in codes
