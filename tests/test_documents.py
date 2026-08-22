"""Tests for document registry validation."""

from __future__ import annotations

from pathlib import Path

from voltquery.seed import load_documents, validate_documents
from voltquery.seed.issues import Severity


def _write_documents(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "documents.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _error_codes(path: Path) -> set[str]:
    issues = validate_documents(path)
    return {issue.code for issue in issues if issue.severity == Severity.ERROR}


def test_fixture_documents_have_no_errors(fixture_documents_path: Path) -> None:
    assert _error_codes(fixture_documents_path) == set()


def test_fixture_documents_load(fixture_documents_path: Path) -> None:
    docs = load_documents(fixture_documents_path)
    assert docs
    assert all(doc.sha256 for doc in docs)
    assert all(doc.retrieved_at for doc in docs)
    assert all(doc.url for doc in docs)


def test_document_missing_sha256(tmp_path: Path) -> None:
    path = _write_documents(
        tmp_path,
        "documents:\n"
        "  - id: d1\n"
        "    source_id: s\n"
        "    filename: a.pdf\n"
        "    url: https://x/a.pdf\n"
        "    retrieved_at: 2026-08-22\n",
    )
    assert "document_missing_sha256" in _error_codes(path)


def test_duplicate_document_id(tmp_path: Path) -> None:
    path = _write_documents(
        tmp_path,
        "documents:\n"
        "  - id: d1\n"
        "    source_id: s\n"
        "    filename: a.pdf\n"
        "    url: https://x/a.pdf\n"
        "    sha256: '0000000000000000000000000000000000000000000000000000000000000000'\n"
        "    retrieved_at: 2026-08-22\n"
        "  - id: d1\n"
        "    source_id: s\n"
        "    filename: b.pdf\n"
        "    url: https://x/b.pdf\n"
        "    sha256: '1111111111111111111111111111111111111111111111111111111111111111'\n"
        "    retrieved_at: 2026-08-22\n",
    )
    assert "duplicate_document_id" in _error_codes(path)


def test_document_registry_missing(tmp_path: Path) -> None:
    assert "document_registry_missing" in _error_codes(tmp_path / "nope.yaml")
