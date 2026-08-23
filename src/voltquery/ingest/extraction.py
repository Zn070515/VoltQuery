"""M2 ingest orchestration: PDF path → candidate store + ingest report.

This module wires the parser and the segmenter together into an end-to-end,
deterministic document → candidate pipeline. It produces a ``ProblemCandidate``
per segment unit, writes the candidate store (``candidates.jsonl``, one model per
line) plus each retained figure raster under ``<output_dir>/assets/``, and returns
an ``IngestReport`` that records exactly what happened — including every page that
produced no candidate, so no page is ever silently dropped.

Identity/provenance binding happens here (not in the segmenter): a ``SegmentUnit``
is pure page-local geometry, and does not know its document/source. The candidate
consumes the source/document so ``SourceRef``/``ParserProvenance`` are fully
resolved and traceable.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from voltquery.contracts import (
    AssetKind,
    AssetOrigin,
    AssetRole,
    ContractModel,
    ProblemAsset,
    ProblemCandidate,
    ProblemObservables,
    SourceRef,
)
from voltquery.contracts.ingest import (
    ParserProvenance,
    SourceBlock,
)

from .parser import DocumentParser, PyMuPDFParser, parse_page_range
from .segment import SegmentUnit, segment_page

# Deterministic identifier for the parser implementation that produced a candidate.
PARSER_NAME = "voltquery-ingest"
PARSER_VERSION = "m2-doc.v0.1"


class IngestReport(ContractModel):
    """What an ``ingest_pdf`` run did, as data (not a log string).

    ``dropped_pages`` records every parsed page that yielded no candidate. It is
    empty in the happy path; non-empty only when a page had no retained prose, so
    "no silent page drop" is auditable.
    """

    document_id: str
    source_id: str
    document_sha256: str
    pages_seen: int
    candidates: int
    figures_retained: int
    warnings: list[str] = []
    dropped_pages: list[int] = []


def _sha256(pdf_path: Path) -> str:
    digest = hashlib.sha256()
    with pdf_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate_id(document_id: str, page_index: int, unit_index: int) -> str:
    """A filesystem-safe deterministic id: no colons, no separators in identity.

    ``document_id`` itself must not contain ``/`` or ``:`` (it comes from the
    registry), so dashes below are safe to use in filenames.
    """
    return f"{document_id}-p{page_index}-u{unit_index}"


def _asset_relative_path(candidate_id: str, xobject_name: str, image_format: str) -> str:
    ext = _normalize_ext(image_format)
    return f"assets/{candidate_id}-{xobject_name}.{ext}"


def _normalize_ext(image_format: str) -> str:
    """Map PyMuPDF's image ``ext`` token to a safe file extension.

    PyMuPDF reports e.g. ``png``/``jpeg``/``xpm``; ``jpeg`` is written as ``.jpg``
    so the file is web/OS friendly. Anything unexpected is left as-is but passed
    through ``isalnum`` guard so it cannot inject path separators.
    """
    fmt = (image_format or "png").lower().lstrip(".")
    if fmt == "jpeg" or fmt == "jpg":
        return "jpg"
    if not fmt or not fmt.isalnum():
        return "png"
    return fmt


def ingest_pdf(
    pdf_path: str | Path,
    source_id: str,
    document_id: str,
    *,
    page_range: str | None = None,
    output_dir: str | Path,
    parser: DocumentParser | None = None,
) -> IngestReport:
    """Ingest a PDF into a candidate store, returning an :class:`IngestReport`.

    ``page_range`` is a human 1-based spec (``"12-15"``) or ``None`` for all
    pages. Raises ``ValueError`` on an invalid spec or an unbounded page range;
    propagates a ``RuntimeError`` from the parser if PyMuPDF is unavailable.
    """
    pdf = Path(pdf_path)
    output = Path(output_dir)
    doc = parser or PyMuPDFParser()

    document_sha256 = _sha256(pdf)
    page_count = doc.page_count(pdf)
    bounds = parse_page_range(page_range, page_count=page_count)

    warnings: list[str] = []
    dropped_pages: list[int] = []
    candidates: list[ProblemCandidate] = []
    figures_retained = 0

    parsed_pages = doc.parse(pdf, page_range=bounds)
    for page in parsed_pages:
        units = segment_page(page)
        if not units:
            dropped_pages.append(page.page_index)
            continue
        for unit_index, unit in enumerate(units):
            candidate = _build_candidate(
                unit,
                unit_index=unit_index,
                source_id=source_id,
                document_id=document_id,
                document_sha256=document_sha256,
                page_label=page.page_label,
                warnings=warnings,
            )
            _write_figures(unit, candidate.id, output)
            candidates.append(candidate)
            figures_retained += len(unit.figure_regions)

    _write_store(candidates, output)
    return IngestReport(
        document_id=document_id,
        source_id=source_id,
        document_sha256=document_sha256,
        pages_seen=len(parsed_pages),
        candidates=len(candidates),
        figures_retained=figures_retained,
        warnings=warnings,
        dropped_pages=dropped_pages,
    )


def _build_candidate(
    unit: SegmentUnit,
    *,
    unit_index: int,
    source_id: str,
    document_id: str,
    document_sha256: str,
    page_label: str | None,
    warnings: list[str],
) -> ProblemCandidate:
    candidate_id = _candidate_id(document_id, unit.page_index, unit_index)

    assets: list[ProblemAsset] = []
    source_blocks: list[SourceBlock] = []
    for block in unit.text_blocks:
        source_blocks.append(
            SourceBlock(kind="text", text=block.text, bbox=block.bbox, asset_path=None)
        )
    for figure in unit.figure_regions:
        asset_path = _asset_relative_path(candidate_id, figure.xobject_name, figure.image_format)
        assets.append(
            ProblemAsset(
                path=asset_path,
                kind=AssetKind.FIGURE,
                role=AssetRole.CONTENT_CROP,
                origin=AssetOrigin.SOURCE,
                page_index=unit.page_index,
                crop_rect=figure.bbox,
            )
        )
        source_blocks.append(
            SourceBlock(
                kind="figure",
                text=None,
                bbox=figure.bbox,
                asset_path=asset_path,
            )
        )

    return ProblemCandidate(
        id=candidate_id,
        source=SourceRef(
            source_id=source_id,
            document_id=document_id,
            page_index=unit.page_index,
            page_label=page_label,
        ),
        domain=None,
        topics=[],
        statement=unit.statement,
        text=unit.statement,
        parts=None,
        inputs=[],
        targets=[],
        formulas=[],
        observables=ProblemObservables(
            has_circuit_figure=False,
            has_formula=False,
            answer_available=False,
        ),
        assets=assets,
        provenance=ParserProvenance(
            parser=PARSER_NAME,
            parser_version=PARSER_VERSION,
            document_sha256=document_sha256,
            document_id=document_id,
            page_index=unit.page_index,
            extraction_warnings=list(warnings),
            source_blocks=source_blocks,
        ),
    )


def _write_figures(unit: SegmentUnit, candidate_id: str, output: Path) -> None:
    """Write each retained raster to ``<output>/assets/``, matching the asset path."""
    for figure in unit.figure_regions:
        rel = _asset_relative_path(candidate_id, figure.xobject_name, figure.image_format)
        dest = output / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(figure.image)


def _write_store(candidates: list[ProblemCandidate], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    candidates_jsonl = output / "candidates.jsonl"
    with candidates_jsonl.open("w", encoding="utf-8") as fh:
        for candidate in candidates:
            fh.write(candidate.model_dump_json() + "\n")
