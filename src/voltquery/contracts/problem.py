"""``EEProblemIR`` — the v0.1 machine representation of an EE problem.

M0's ``SeedProblemRecord`` answers "what did we observe about the source?"; this
contract answers "what does the problem mean?". It is deliberately scoped to what
the 40-problem Gold corpus actually proves is needed (see
``docs/development/SEED_CORPUS_FINDINGS.md`` §10), and defers solving-adjacent
structure (``CircuitGraph``, ``MathIR``, ``AnswerSchema``, ``SolutionPath``) to
M2 / v0.2+ rather than freezing it early. ``answer`` is intentionally a thin
``{type, content}`` pair — a real answer can combine scalar + drawing +
explanation, so a rigid per-shape union is premature.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from ._base import ContractModel
from .enums import AssetKind, AssetRole, Domain, FormulaLayout, FormulaRole
from .seed import TopicSlug
from .source import SourceRef


def _validate_asset_path(value: str) -> str:
    if not value:
        raise ValueError("asset path must not be empty")
    if "\\" in value:
        raise ValueError("asset path must use POSIX-style separators")
    if value.startswith("/"):
        raise ValueError("asset path must be relative, not absolute")
    parts = value.split("/")
    if any(part in {"", ".."} for part in parts):
        raise ValueError("asset path must not contain empty or '..' segments")
    if ":" in value:
        raise ValueError("asset path must not contain a drive letter or scheme")
    return value


class CropRect(ContractModel):
    """A source-page rectangle (points, top-left origin) for an asset crop."""

    x0: float
    y0: float
    x1: float
    y1: float


class Unit(ContractModel):
    """A typed unit, kept separate from prose with a normalized spelling."""

    symbol: str
    normalized: str | None = None


class Quantity(ContractModel):
    """A numeric or symbolic quantity with an explicit unit.

    ``note`` is the extension slot for uncertainty / tolerance (deliberately not
    a first-class field in v0.1), so the model can grow without a breaking change.
    """

    value: float | str
    unit: Unit
    normalized: str | None = None
    note: str | None = None


class Answer(ContractModel):
    """A structured answer, kept deliberately non-rigid.

    ``type`` is a soft label (e.g. ``"scalar"``, ``"table"``, ``"expression"``,
    ``"explanation"``, ``"drawing"``, ``"structured"``); ``content`` is an open
    payload because one answer can mix several shapes. Freezing this into a
    discriminated union in v0.1 would be premature.
    """

    type: str
    content: Any = None


class Part(ContractModel):
    """One subproblem of a multipart problem (replaces ``is_multipart: bool``)."""

    label: str
    statement: str
    target: str | None = None
    answer: Answer | None = None


class Formula(ContractModel):
    """A formula occurrence with its source role and textual layout."""

    content: str
    role: FormulaRole = FormulaRole.GIVEN
    layout: FormulaLayout = FormulaLayout.INLINE


class ProblemAsset(ContractModel):
    """An asset carried by an IR problem, richer than M0's ``AssetRef``.

    Adds a ``role`` axis (what it is *for*) alongside the M0 ``kind`` (what it
    *is*), a source ``crop_rect`` (with the source ``page_index``), and an
    optional binding to subproblem ``parts``.
    """

    path: str
    kind: AssetKind = AssetKind.FIGURE
    role: AssetRole = AssetRole.FIGURE
    page_index: int | None = None
    crop_rect: CropRect | None = None
    parts: list[str] | None = None

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        return _validate_asset_path(value)


class ProblemObservables(ContractModel):
    """Observables of the *source*, deliberately independent of our assets.

    ``has_circuit_figure`` is a fact about the world ("the printed problem
    references a circuit figure"), not about whether we fetched it; so it is
    never derived from ``assets``. A source that references a figure but whose
    figure we could not fetch has ``has_circuit_figure: true`` and
    ``assets: []``.
    """

    has_circuit_figure: bool
    has_formula: bool
    answer_available: bool


class EEProblemIR(ContractModel):
    """The v0.1 intermediate representation of an electrical-engineering problem.

    ``parts`` is three-state: ``None`` = not yet resolved as multipart or single,
    ``[]`` = confirmed single-part problem, ``[Part, ...]`` = multipart. Kept as
    ``| None`` (not an empty-list sentinel) so an OCR/ingestion pass that could
    not parse the subparts is distinguishable from a genuinely single-part item.
    """

    id: str
    source: SourceRef
    domain: Domain
    topics: list[TopicSlug]
    statement: str
    parts: list[Part] | None = None
    inputs: list[Quantity] = Field(default_factory=list)
    answer: Answer | None = None
    assets: list[ProblemAsset] = Field(default_factory=list)
    formulas: list[Formula] = Field(default_factory=list)
    observables: ProblemObservables
