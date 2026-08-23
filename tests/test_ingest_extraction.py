"""End-to-end ``ingest_pdf`` tests. Skipped when PyMuPDF is not installed."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytest.importorskip("pymupdf")

from voltquery.ingest.extraction import ingest_pdf  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ingest_binds_provenance(sample_pdf: Path, tmp_path: Path) -> None:
    report = ingest_pdf(
        sample_pdf,
        source_id="fixture-source",
        document_id="fixture-doc",
        output_dir=tmp_path,
    )
    assert report.document_id == "fixture-doc"
    assert report.source_id == "fixture-source"
    assert report.document_sha256 == _sha256(sample_pdf)
    assert report.pages_seen == 1
    assert report.candidates == 1
    assert report.figures_retained == 1
    assert report.dropped_pages == []
    assert report.warnings == []


def test_ingest_writes_candidate_store(sample_pdf: Path, tmp_path: Path) -> None:
    ingest_pdf(sample_pdf, "fixture-source", "fixture-doc", output_dir=tmp_path)
    store = tmp_path / "candidates.jsonl"
    assert store.exists()
    lines = store.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_ingest_asset_is_written_with_source_page(sample_pdf: Path, tmp_path: Path) -> None:
    ingest_pdf(sample_pdf, "fixture-source", "fixture-doc", output_dir=tmp_path)
    assets_dir = tmp_path / "assets"
    pngs = list(assets_dir.glob("*.png"))
    assert len(pngs) == 1
    assert pngs[0].read_bytes()


def test_ingest_candidate_fields(sample_pdf: Path, tmp_path: Path) -> None:
    ingest_pdf(sample_pdf, "fixture-source", "fixture-doc", output_dir=tmp_path)
    store = (tmp_path / "candidates.jsonl").read_text(encoding="utf-8")
    candidate = store.splitlines()[0]

    import json

    c = json.loads(candidate)
    assert c["id"] == "fixture-doc-p0-u0"
    assert c["source"]["source_id"] == "fixture-source"
    assert c["source"]["document_id"] == "fixture-doc"
    assert c["source"]["page_index"] == 0
    assert c["provenance"]["document_sha256"] == _sha256(sample_pdf)
    assert c["observables"]["has_circuit_figure"] is False
    asset = c["assets"][0]
    assert asset["kind"] == "figure"
    assert asset["role"] == "content_crop"
    assert asset["origin"] == "source"
    assert asset["page_index"] == 0
    assert asset["crop_rect"] is not None


def test_ingest_page_range_bounds_the_spike(sample_pdf: Path, tmp_path: Path) -> None:
    # page_range "1" on a 1-page doc is a single page — no dropped pages.
    report = ingest_pdf(
        sample_pdf,
        "fixture-source",
        "fixture-doc",
        page_range="1",
        output_dir=tmp_path,
    )
    assert report.pages_seen == 1
    assert report.dropped_pages == []


def test_ingest_page_range_out_of_bound_raises(sample_pdf: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        ingest_pdf(
            sample_pdf,
            "fixture-source",
            "fixture-doc",
            page_range="99-100",
            output_dir=tmp_path,
        )
