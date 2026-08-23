"""M2 ingestion contracts — ``ProblemCandidate`` and its provenance trace.

M1 froze ``EEProblemIR`` v0.1 as the *curated* shape of a Gold problem. M2
(Document → Problem Ingestion) produces a looser, extraction-first object: a
``ProblemCandidate`` carries whatever a deterministic parser could pull out of a
page — identity fields, a verbatim statement, retained figure assets, and a
``ParserProvenance`` block that makes the original document/page traceable.
It is deliberately **not** a ``SEED`` and does **not** enter ``problem_ir.jsonl``:
promotion to a seed + ``EEProblemIR`` is a curation step (see
``data/raw/ksu/_migrate_ir.py`` for how curation currently works).

Conventions (documented, not enforced):
* ``SourceRef.page_index`` = the 0-based physical PDF page (matches ``page.number``).
* ``SourceRef.page_label`` = the printed page number / section header when
  extractable, else the physical page number.
* Extracted figure regions are emitted as ``kind=FIGURE, role=CONTENT_CROP,
  origin=SOURCE`` (never ``SCHEMATIC``) with ``page_index`` + ``crop_rect`` set, so
  ``has_circuit_figure`` stays ``False`` until curation classifies a schematic —
  keeping the strict three-axis asset check honest.
* ``inputs`` / ``targets`` / ``formulas`` / ``parts`` are left empty (``[]`` /
  ``None``): phase-1 extraction is identity + statement + figures + provenance +
  conservative observables, not semantic annotation.
"""

from __future__ import annotations

from typing import Literal

from ._base import ContractModel
from .enums import Domain
from .problem import CropRect, Formula, Input, Part, ProblemAsset, ProblemObservables
from .seed import TopicSlug
from .source import SourceRef

# Candidate contracts are versioned independently of ``EEProblemIR`` (v0.1):
# candidates are a live ingestion shape that can evolve without unfreezing M1.
CANDIDATE_SCHEMA_VERSION: Literal["candidate.v0.1"] = "candidate.v0.1"


class SourceBlock(ContractModel):
    """The executable trace unit: one region of a source page that seeded a candidate.

    ``kind`` distinguishes prose from an extracted figure raster or a table. For a
    ``figure`` block, ``asset_path`` points at the retained crop; ``bbox`` pins the
    source region so the block is auditable against the original page. Either
    ``text`` (for ``text``/``table``) or ``asset_path`` (for ``figure``) is
    populated; never both, and never neither.
    """

    kind: Literal["text", "figure", "table"]
    text: str | None = None
    bbox: CropRect | None = None
    asset_path: str | None = None


class ParserProvenance(ContractModel):
    """Who/how extracted the candidate, plus its exact source location.

    ``document_sha256`` + ``document_id`` + ``page_index`` uniquely pin the source
    artifact, satisfying the M2 "original document and page can always be traced"
    acceptance criterion. ``source_blocks`` is the ordered list of regions that
    produced the candidate.
    """

    parser: str
    parser_version: str | None = None
    document_sha256: str
    document_id: str
    page_index: int | None = None
    extraction_warnings: list[str] = []
    source_blocks: list[SourceBlock] = []


class ProblemCandidate(ContractModel):
    """An extraction-first, pre-curation representation of a problem from a page.

    ``schema_version`` is ``candidate.v0.1``. ``domain``/``topics`` may be
    unset (``None``/``[]``) until curated; ``statement`` is the verbatim text the
    parser attributed to this problem; ``assets`` holds the retained figure crops.
    """

    schema_version: Literal["candidate.v0.1"] = CANDIDATE_SCHEMA_VERSION
    id: str
    source: SourceRef
    domain: Domain | None = None
    topics: list[TopicSlug] = []
    statement: str
    text: str
    parts: list[Part] | None = None
    inputs: list[Input] = []
    targets: list[str] = []
    formulas: list[Formula] = []
    observables: ProblemObservables
    assets: list[ProblemAsset] = []
    provenance: ParserProvenance
