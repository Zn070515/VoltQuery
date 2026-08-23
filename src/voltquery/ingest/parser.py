"""Deterministic page extraction from a PDF.

The adapter surface. ``PyMuPDFParser`` turns each page into a ``ParsedPage``: an
ordered set of verbatim text blocks (with their bounding boxes) and figure
regions (with their placed bbox and raw raster), plus a page label. This is the
exact positional info the segmenter needs and the provenance the candidate needs.

PyMuPDF is imported lazily inside the parser method only, so importing this module
(and ``voltquery.ingest``) never requires it; a base install without ``pymupdf``
still imports cleanly and raises a clear ``RuntimeError`` only once parsing is
attempted.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Protocol

from voltquery.contracts import ContractModel, CropRect

# Default: no page bound, parse the whole document.
_PAGE_RANGE_RE = re.compile(r"^(?P<start>\d+)(-(?P<end>\d+))?$")


class PageRange:
    """A 0-based inclusive [$start, $end] slice of a PDF's pages.

    The CLI/human-facing spec is *1-based* (``--pages "12-15"`` = pages 12..15
    inclusive); this is the resolved, 0-based form used to index ``page.number``.
    """

    def __init__(self, start: int, end: int) -> None:
        if start < 0 or end < start:
            raise ValueError(f"invalid page range [{start}, {end}]")
        self.start = start
        self.end = end

    def clamp(self, page_count: int) -> PageRange:
        end = min(self.end, page_count - 1)
        if end < self.start:
            raise ValueError(f"page range [{self.start}, {self.end}] exceeds {page_count} pages")
        return PageRange(self.start, end)

    def __contains__(self, page_index: int) -> bool:
        return self.start <= page_index <= self.end

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"PageRange([{self.start}, {self.end}])"


def parse_page_range(spec: str | None, *, page_count: int) -> PageRange | None:
    """Parse a human 1-based spec (``"12"``, ``"12-15"``) into a clamped PageRange.

    ``None``/empty means "all pages". Returns ``None`` when no bound was given.
    """
    if spec is None or not spec.strip():
        return None
    match = _PAGE_RANGE_RE.match(spec.strip())
    if not match:
        raise ValueError(f"invalid page range '{spec}' (expected 'N' or 'N-M')")
    start_1 = int(match.group("start"))
    end_1 = int(match.group("end")) if match.group("end") else start_1
    if start_1 < 1:
        raise ValueError("page range is 1-based; must be >= 1")
    if end_1 < start_1:
        raise ValueError(f"page range '{spec}' has end < start")
    return PageRange(start_1 - 1, end_1 - 1).clamp(page_count)


class TextBlock(ContractModel):
    """A verbatim prose region on the page, with its bounding box."""

    text: str
    bbox: CropRect


class FigureRegion(ContractModel):
    """A placed, rasterized figure on the page.

    ``image`` is the raw bytes (PNG/JPEG) pulled from the PDF; ``bbox`` pins its
    placement so it can be cropped/re-examined against the source page.
    """

    bbox: CropRect
    xobject_name: str
    image_format: str
    image: bytes


class ParsedPage(ContractModel):
    """The deterministic output of parsing one page."""

    page_index: int
    page_label: str | None
    page_width: float
    page_height: float
    text_blocks: list[TextBlock] = []
    figure_regions: list[FigureRegion] = []


class DocumentParser(Protocol):
    """Interface for a page extractor. Implementations must be deterministic."""

    def page_count(self, pdf_path: Path) -> int: ...

    def parse(self, pdf_path: Path, *, page_range: PageRange | None = None) -> list[ParsedPage]: ...


class PyMuPDFParser:
    """A :class:`DocumentParser` backed by PyMuPDF, imported lazily.

    Deterministic: text blocks and figure regions are produced purely from the
    PDF's content stream, in reading order, with no ML and no hidden state.
    """

    def __init__(self, *, max_figure_bytes: int = 8_000_000) -> None:
        self._max_figure_bytes = max_figure_bytes

    def _load(self) -> Any:  # pragma: no cover - trivial dependency guard
        try:
            import pymupdf  # noqa: PLC0415 - intentional lazy import (adapter boundary)
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for PDF ingestion; install `voltquery[document]` "
                "or add `pymupdf` to your environment."
            ) from exc
        return pymupdf

    def page_count(self, pdf_path: Path) -> int:
        pymupdf = self._load()
        with pymupdf.open(str(pdf_path)) as doc:
            return doc.page_count

    def parse(self, pdf_path: Path, *, page_range: PageRange | None = None) -> list[ParsedPage]:
        pymupdf = self._load()
        parsed: list[ParsedPage] = []
        with pymupdf.open(str(pdf_path)) as doc:
            bounds = _resolve_bounds(page_range, doc.page_count)
            for index in range(bounds.start, bounds.end + 1):
                page = doc[index]
                parsed.append(
                    ParsedPage(
                        page_index=index,
                        page_label=_page_label(page, index),
                        page_width=page.rect.width,
                        page_height=page.rect.height,
                        text_blocks=_text_blocks(page),
                        figure_regions=_figure_regions(page, doc, self._max_figure_bytes),
                    )
                )
        return parsed


def _resolve_bounds(page_range: PageRange | None, page_count: int) -> PageRange:
    if page_range is not None:
        return page_range.clamp(page_count)
    return PageRange(0, page_count - 1)


def _page_label(page: Any, index: int) -> str | None:
    """A printed label (page label / section header) when available, else None."""
    label = getattr(page, "get_label", None)
    if label is not None:
        try:
            value = label()
        except Exception:
            value = None
        if value:
            return str(value)
    return None


def _text_blocks(page: Any) -> list[TextBlock]:
    blocks: list[TextBlock] = []
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text, _, block_type = block
        if block_type != 0:  # 0 == text block; 1 == image block
            continue
        text = (text or "").strip()
        if not text:
            continue
        if x1 <= x0 or y1 <= y0:
            continue
        blocks.append(TextBlock(text=text, bbox=CropRect(x0=x0, y0=y0, x1=x1, y1=y1)))
    return blocks


def _figure_regions(page: Any, doc: Any, max_figure_bytes: int) -> list[FigureRegion]:
    regions: list[FigureRegion] = []
    seen_xrefs: set[int] = set()
    for img in page.get_images(full=True):
        xref = int(img[0])
        if xref in seen_xrefs:
            continue
        seen_xrefs.add(xref)
        rects = page.get_image_rects(xref)
        for rect in rects:
            if not (rect.width > 0 and rect.height > 0):
                continue
            try:
                data = doc.extract_image(xref)
            except Exception:
                continue
            image = data.get("image", b"") if data else b""
            if not image or len(image) > max_figure_bytes:
                continue
            regions.append(
                FigureRegion(
                    bbox=CropRect(x0=rect.x0, y0=rect.y0, x1=rect.x1, y1=rect.y1),
                    xobject_name=f"xref{xref}",
                    image_format=data.get("ext", "png") if data else "png",
                    image=image,
                )
            )
    return regions
