"""Rule-set tests for the M2 deterministic segmenter."""

from __future__ import annotations

from voltquery.contracts import CropRect
from voltquery.ingest.parser import FigureRegion, ParsedPage, TextBlock
from voltquery.ingest.segment import segment_page

# Synthetic pages use a 540pt-wide text column (like the Kuphaldt baseline).
PAGE_WIDTH = 540.0
PAGE_HEIGHT = 720.0


def text(block_text: str, x0: float, y0: float, x1: float, y1: float) -> TextBlock:
    return TextBlock(text=block_text, bbox=CropRect(x0=x0, y0=y0, x1=x1, y1=y1))


def figure(x0: float, y0: float, x1: float, y1: float) -> FigureRegion:
    return FigureRegion(
        bbox=CropRect(x0=x0, y0=y0, x1=x1, y1=y1),
        xobject_name="xref1",
        image_format="png",
        image=b"",
    )


def page(
    blocks: list[TextBlock],
    *,
    figures: list[FigureRegion] | None = None,
    index: int = 0,
) -> ParsedPage:
    return ParsedPage(
        page_index=index,
        page_label=str(index + 1),
        page_width=PAGE_WIDTH,
        page_height=PAGE_HEIGHT,
        text_blocks=blocks,
        figure_regions=figures or [],
    )


def test_numbered_sections_split_into_units() -> None:
    parsed = page(
        [
            text("1.5. RESISTANCE 25", 108, 98, 540, 108),
            text("This is a switch mounted on the wall of a house.", 108, 126, 540, 208),
            text("1.6. VOLTAGE AND CURRENT 27", 108, 300, 540, 310),
            text("Because it takes energy to force electrons to flow.", 108, 330, 540, 400),
        ]
    )
    units = segment_page(parsed)
    assert len(units) == 2
    assert units[0].statement.startswith("1.5. RESISTANCE")
    assert units[1].statement.startswith("1.6. VOLTAGE")


def test_multipart_lettered_subparts_split() -> None:
    parsed = page(
        [
            text("Question 2", 200, 100, 500, 140),
            text("(a) Compute the current.", 200, 160, 500, 200),
            text("(b) Compute the voltage.", 200, 220, 500, 260),
        ],
        index=1,
    )
    units = segment_page(parsed)
    assert len(units) == 3
    assert units[1].statement.startswith("(a)")
    assert units[2].statement.startswith("(b)")


def test_solution_block_stops_the_problem_unit() -> None:
    parsed = page(
        [
            text("1.5. RESISTANCE 25", 108, 98, 540, 108),
            text("A knife switch is a conductive lever.", 108, 126, 540, 208),
            text("Solution:", 108, 300, 540, 310),
            text("The switch opens the circuit.", 108, 330, 540, 400),
        ],
        index=2,
    )
    units = segment_page(parsed)
    assert len(units) == 2
    assert "Solution:" in units[1].statement
    assert "Solution:" not in units[0].statement


def test_narrow_schematic_labels_are_filtered() -> None:
    parsed = page(
        [
            text("1.5. RESISTANCE 25", 108, 98, 540, 108),
            text("Battery", 176, 208, 211, 224),
            text("-", 216, 190, 220, 206),
            text("no flow!", 264, 245, 303, 260),
        ],
        index=3,
    )
    units = segment_page(parsed)
    assert len(units) == 1
    assert len(units[0].text_blocks) == 1  # only the wide header survives


def test_figure_attaches_to_overlapping_unit() -> None:
    parsed = page(
        [
            text("1.5. RESISTANCE 25", 108, 98, 540, 108),
            text("This is a switch mounted on the wall.", 108, 126, 540, 208),
            text("1.6. VOLTAGE AND CURRENT 27", 108, 360, 540, 370),
            text("Because it takes energy to force electrons.", 108, 390, 540, 460),
        ],
        figures=[figure(150, 150, 300, 300)],
        index=4,
    )
    units = segment_page(parsed)
    assert len(units) == 2
    fig_units = [u for u in units if u.figure_regions]
    assert len(fig_units) == 1
    assert fig_units[0].figure_regions[0] == figure(150, 150, 300, 300)
    assert fig_units[0].statement.startswith("1.5.")


def test_page_with_only_labels_yields_no_units() -> None:
    parsed = page(
        [
            text("Battery", 176, 208, 211, 224),
            text("-", 216, 190, 220, 206),
        ],
        index=5,
    )
    assert segment_page(parsed) == []
