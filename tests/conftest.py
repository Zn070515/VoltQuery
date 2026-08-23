"""Shared pytest fixtures for VoltQuery tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def fixture_sources_path() -> Path:
    return FIXTURES / "sources.yaml"


@pytest.fixture
def fixture_corpus_path() -> Path:
    return FIXTURES / "problems.jsonl"


@pytest.fixture
def fixture_documents_path() -> Path:
    return FIXTURES / "documents.yaml"


@pytest.fixture
def fixture_assets_root() -> Path:
    return FIXTURES


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """A tiny 1-page text-layer PDF with one text block and one embedded raster.

    Skipped (via ``importorskip``) when PyMuPDF is not installed, so a base
    install without the ``document`` extra still collects the ingest tests.
    """
    pymupdf = pytest.importorskip("pymupdf")
    path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    # insert_textbox wraps to a full-width column, reproducing a real prose block
    # (spans most of the page width) rather than a short line.
    page.insert_textbox(
        pymupdf.Rect(50, 60, 550, 200),
        "Question 1: Example problem statement text for a simple circuit. " * 6,
        fontname="helv",
        fontsize=11,
    )
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40))
    pix.set_rect(pymupdf.IRect(0, 0, 40, 40), (255, 102, 0))
    page.insert_image(pymupdf.Rect(200, 300, 360, 420), stream=pix.tobytes("png"))
    doc.save(path)
    doc.close()
    return path
