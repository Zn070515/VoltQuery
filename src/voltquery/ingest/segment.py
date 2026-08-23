"""Deterministic page → candidate-unit segmentation (no ML).

The segmenter turns a :class:`ParsedPage` into an ordered list of
:class:`SegmentUnit`. Each unit is a contiguous run of prose on the page that a
handler would present as one candidate problem. The rule set below is pure and
deterministic — it is a documented heuristic, deliberately simple, and tuned in
phase 1.5; here it only has to be *reviewable and honest*, not F1-optimal.

Rule set (module constants + this docstring):

1. **Noise filter.** Text blocks that are narrow are schematic *annotations*
   (vector-drawn circuit labels such as ``Battery``, ``+``, ``-``, ``1\\n2``,
   ``(break)``) that PyMuPDF emits as separate blocks. A block is retained as
   content when its width is at least ``_MIN_PROSE_WIDTH_RATIO`` of the widest
   block on the page. This drops the labels but keeps prose paragraphs (which
   span the full content column) and section headers (wide but short).

2. **Markers.** A retained block starts a new unit when its normalized text
   matches a ``MARKER_PATTERN``:

   * section header ``1.5.`` / ``N.N. <Words>`` (e.g. ``1.5. RESISTANCE``)
   * chapter header ``Chapter N``
   * review/summary header ``• REVIEW:``
   * worked ``Example:``
   * numbered question ``N.`` / ``1.`` / lettered sub-part ``(a)``

   The marker block is kept as the first block of the unit it starts.

3. **Unit text.** ``statement`` is the verbatim join of the unit's retained
   ``text_blocks``. Markers and headers are part of the statement so provenance
   to the printed heading is preserved.

4. **Figure attach.** Each figure region is attached to the unit whose content
   bounding box (union of its text-block bboxes) has the largest overlap with the
   figure's bbox. If no unit overlaps, the figure is attached to the unit that
   vertically contains its midpoint (falling back to the first unit). This keeps
   every retained figure on the page owned by exactly one unit (no orphaning).
"""

from __future__ import annotations

import re

from voltquery.contracts import ContractModel, CropRect

from .parser import FigureRegion, ParsedPage, TextBlock

# A block is kept as content when its width is >= this fraction of the *page*
# width. Prose columns in the baseline span roughly 0.8 of the page width;
# schematic labels are a few percent. Comparing against the page width (rather
# than against the widest block on the page) means a schematic-only page — where
# every block is a narrow label — is correctly recognized as having no prose,
# and the orchestrator records it in ``dropped_pages`` rather than emitting a
# junk "Battery"-only unit.
_MIN_PROSE_WIDTH_RATIO: float = 0.4

# Block-start markers. Applied to whitespace-normalized text. Leftmost match wins;
# the block is a marker if ANY pattern matches (order here is cosmetic).
MARKER_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\d+\.\d+\.?\s*[A-Za-z]", re.I),  # "1.5. Resistance", "7.3.1 Example"
    re.compile(r"^chapter\s+\d+", re.I),  # "Chapter 1. Basic concepts..."
    re.compile(r"^•\s*review:", re.I),  # "• REVIEW:"
    re.compile(r"^example\b", re.I),  # "Example:"
    re.compile(r"^solution\b", re.I),  # "Solution:" — stops the problem unit
    re.compile(r"^answer\b", re.I),  # "Answer:" — stops the problem unit
    re.compile(r"^\d+\s*[.)]\s*\S"),  # "12." / "12) ..." numbered question
    re.compile(r"^\([a-z]\)\s*\S", re.I),  # "(a) ..." lettered sub-part
)


class SegmentUnit(ContractModel):
    """A contiguous problem region on a page, before identity/provenance binding.

    ``statement`` is the verbatim text the handler would present as the candidate's
    problem statement. ``figure_regions`` are the raster figures owned by this unit.
    """

    page_index: int
    statement: str
    text_blocks: list[TextBlock]
    figure_regions: list[FigureRegion]


def segment_page(page: ParsedPage) -> list[SegmentUnit]:
    """Segment one parsed page into candidate units.

    Pure and deterministic; raises nothing. A page with only schematic labels (no
    prose) yields an empty list — the orchestrator records that page in
    ``IngestReport`` rather than silently dropping a candidate.
    """
    retained = _retain_prose(page.text_blocks, page.page_width)
    if not retained:
        return []
    units = _split_on_markers(retained, page.page_index)
    _attach_figures(units, page.figure_regions)
    return units


def _retain_prose(blocks: list[TextBlock], page_width: float) -> list[TextBlock]:
    if not blocks:
        return []
    threshold = page_width * _MIN_PROSE_WIDTH_RATIO
    kept: list[TextBlock] = []
    for block in blocks:
        w = block.bbox.x1 - block.bbox.x0
        if w < threshold:
            continue
        # A degenerate zero-area block cannot be content.
        if block.bbox.x1 <= block.bbox.x0 or block.bbox.y1 <= block.bbox.y0:
            continue
        kept.append(block)
    return kept


def _is_marker(block: TextBlock) -> bool:
    normalized = re.sub(r"\s+", " ", block.text).strip()
    return any(pattern.search(normalized) for pattern in MARKER_PATTERNS)


def _split_on_markers(blocks: list[TextBlock], page_index: int) -> list[SegmentUnit]:
    # A marker always begins a unit, so the first block (which is usually a
    # header) seeds the first unit; subsequent markers split from there.
    groups: list[list[TextBlock]] = []
    current: list[TextBlock] = []
    for block in blocks:
        if _is_marker(block) and current:
            groups.append(current)
            current = [block]
        else:
            current.append(block)
    groups.append(current)

    return [
        SegmentUnit(
            page_index=page_index,
            statement="\n".join(b.text for b in group).strip(),
            text_blocks=group,
            figure_regions=[],
        )
        for group in groups
    ]


def _attach_figures(units: list[SegmentUnit], figures: list[FigureRegion]) -> None:
    if not units:
        return
    for figure in figures:
        unit = _best_unit_for(units, figure)
        unit.figure_regions.append(figure)


def _best_unit_for(units: list[SegmentUnit], figure: FigureRegion) -> SegmentUnit:
    """Largest-bbox-overlap unit; else the one vertically containing midpoint; else first."""
    best: SegmentUnit | None = None
    best_overlap = 0.0
    for unit in units:
        overlap = _bbox_overlap(_content_bbox(unit), figure.bbox)
        if overlap > best_overlap:
            best_overlap = overlap
            best = unit
    if best is not None and best_overlap > 0:
        return best
    for unit in units:
        cy = (figure.bbox.y0 + figure.bbox.y1) / 2
        if _content_bbox(unit).y0 <= cy <= _content_bbox(unit).y1:
            return unit
    return units[0]


def _content_bbox(unit: SegmentUnit) -> CropRect:
    if not unit.text_blocks:
        return CropRect(x0=0, y0=0, x1=0, y1=0)
    return CropRect(
        x0=min(b.bbox.x0 for b in unit.text_blocks),
        y0=min(b.bbox.y0 for b in unit.text_blocks),
        x1=max(b.bbox.x1 for b in unit.text_blocks),
        y1=max(b.bbox.y1 for b in unit.text_blocks),
    )


def _bbox_overlap(a: CropRect, b: CropRect) -> float:
    width = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    height = max(0.0, min(a.y1, b.y1) - max(a.y0, b.y0))
    return width * height
