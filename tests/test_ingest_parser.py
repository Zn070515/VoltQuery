"""Parser adapter tests. Skipped wholesale when PyMuPDF is not installed."""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

import pytest

pytest.importorskip("pymupdf")

from voltquery.ingest.parser import PyMuPDFParser, parse_page_range  # noqa: E402


def test_page_count(sample_pdf: Path) -> None:
    parser = PyMuPDFParser()
    assert parser.page_count(sample_pdf) == 1


def test_parse_yields_verbatim_text_with_bbox(sample_pdf: Path) -> None:
    parser = PyMuPDFParser()
    pages = parser.parse(sample_pdf)
    assert len(pages) == 1
    page = pages[0]
    assert page.page_index == 0
    assert len(page.text_blocks) >= 1
    block = page.text_blocks[0]
    assert block.text.strip().startswith("Question 1")
    # bbox is a real, positive-area source region
    assert block.bbox.x1 > block.bbox.x0
    assert block.bbox.y1 > block.bbox.y0


def test_parse_yields_one_figure_region(sample_pdf: Path) -> None:
    parser = PyMuPDFParser()
    pages = parser.parse(sample_pdf)
    figure = pages[0].figure_regions[0]
    assert figure.image
    assert figure.image_format == "png"
    assert figure.bbox.x1 > figure.bbox.x0
    assert figure.bbox.y1 > figure.bbox.y0


def test_page_range_spec_is_1_based() -> None:
    assert parse_page_range("1", page_count=5) is not None
    assert parse_page_range("1", page_count=5).start == 0
    assert parse_page_range("1-3", page_count=5).end == 2


def test_page_range_exceeds_page_count_raises() -> None:
    with pytest.raises(ValueError):
        parse_page_range("99-100", page_count=5)


def test_thev_env_absent_raises_runtimeerror(monkeypatch) -> None:
    """When ``import pymupdf`` fails, the parser raises a clear RuntimeError.

    Simulated by monkeypatching ``__import__`` to reject ``pymupdf`` even though
    it is installed in the test environment.
    """
    real_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "pymupdf":
            raise ImportError("simulated missing pymupdf")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "pymupdf", raising=False)

    parser = PyMuPDFParser()
    with pytest.raises(RuntimeError, match="PyMuPDF is required"):
        parser.page_count(Path("whatever.pdf"))
