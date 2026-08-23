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

from typing import Annotated, Any, Literal

from pydantic import Field, field_validator, model_validator

from ._base import ContractModel
from .enums import AssetKind, AssetOrigin, AssetRole, Domain, FormulaLayout, FormulaRole
from .seed import TopicSlug
from .source import SourceRef

# Current contract version. Bumping ``schema_version`` is a breaking change and
# must ride with an explicit migration (no silent drift on ``problem_ir.jsonl``).
SCHEMA_VERSION: Literal["v0.1"] = "v0.1"


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
    """A source-page rectangle (points, top-left origin) for an asset crop.

    A rectangle is degenerate/meaningless unless it has positive area and a
    non-negative origin on the page; reject anything that cannot name a real
    region.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    @model_validator(mode="after")
    def _well_formed(self) -> CropRect:
        if self.x1 <= self.x0:
            raise ValueError("x1 must be greater than x0")
        if self.y1 <= self.y0:
            raise ValueError("y1 must be greater than y0")
        if self.x0 < 0 or self.y0 < 0:
            raise ValueError("crop origin must be non-negative")
        return self


class Unit(ContractModel):
    """A typed unit, kept separate from prose with a normalized spelling."""

    symbol: str
    normalized: str | None = None


class QuantityInput(ContractModel):
    """A named, quantified *given* of a problem.

    ``name`` binds the quantity to the object it denotes in the problem (``Vs``,
    ``R1``, ``open_loop_gain``). It is optional in v0.1 because ingestion does not
    always resolve the binding; a ``None`` name is an honest "unbound" rather
    than an invented one. Unitless (dimensionless) quantities use
    ``unit=Unit(symbol="", normalized=None)`` -- the unit plate is required so a
    reader never mistakes a missing unit for a known one.

    ``note`` is the extension slot for uncertainty / tolerance.
    """

    type: Literal["quantity"] = "quantity"
    name: str | None = None
    value: float | str
    unit: Unit
    note: str | None = None


class TableInput(ContractModel):
    """A tabular *given* of a problem (e.g. a resistor/current table).

    Minimal v0.1 shape: a binding ``name``, the column names, and an open ``rows``
    payload. ``columns``/``rows`` are optional so a table whose values live only
    in a schematic asset can be declared as a placeholder without inventing rows.
    """

    type: Literal["table"] = "table"
    name: str | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    note: str | None = None


# A problem's ``inputs`` mix singular quantities and tabular givens. The
# ``type`` discriminator keeps the union unambiguous.
Input = Annotated[QuantityInput | TableInput, Field(discriminator="type")]


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
    """One subproblem of a multipart problem (replaces ``is_multipart: bool``).

    ``parts`` lets a subproblem carry its own nested subparts (e.g. 0032's
    (i)/(ii)/(iii) inside part b) rather than flattening them into ``target``.
    ``None`` = not resolved, ``[]`` = no nested subparts, ``[Part, ...]`` = nested.
    """

    label: str
    statement: str
    target: str | None = None
    answer: Answer | None = None
    parts: list[Part] | None = None


class Formula(ContractModel):
    """A formula occurrence with its source role and textual layout."""

    content: str
    role: FormulaRole = FormulaRole.GIVEN
    layout: FormulaLayout = FormulaLayout.INLINE


class ProblemAsset(ContractModel):
    """An asset carried by an IR problem, richer than M0's ``AssetRef``.

    Three orthogonal axes replace M0's single ``kind``:
      * ``kind``   -- what the asset *is* (figure/schematic/waveform/table/...)
      * ``role``   -- what it is *for* (question crop vs. content crop, ...)
      * ``origin`` -- where it came from (source provenance vs. generated)

    A source schematic is ``kind=SCHEMATIC, role=CONTENT_CROP, origin=SOURCE``; a
    generated OCR crop is ``kind=FIGURE, role=CONTENT_CROP, origin=GENERATED``. A
    ``crop_rect`` pins a source region and therefore requires a ``page_index``.
    ``parts`` binds an asset to a specific subproblem label.
    """

    path: str
    kind: AssetKind = AssetKind.FIGURE
    role: AssetRole = AssetRole.CONTENT_CROP
    origin: AssetOrigin = AssetOrigin.SOURCE
    page_index: int | None = None
    crop_rect: CropRect | None = None
    parts: list[str] | None = None

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        return _validate_asset_path(value)

    @model_validator(mode="after")
    def _crop_requires_page(self) -> ProblemAsset:
        if self.crop_rect is not None and self.page_index is None:
            raise ValueError("crop_rect requires a source page_index")
        return self


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

    schema_version: Literal["v0.1"]
    id: str
    source: SourceRef
    domain: Domain
    topics: list[TopicSlug]
    statement: str
    parts: list[Part] | None = None
    inputs: list[Input] = Field(default_factory=list)
    targets: list[str] = Field(default_factory=list)
    answer: Answer | None = None
    assets: list[ProblemAsset] = Field(default_factory=list)
    formulas: list[Formula] = Field(default_factory=list)
    observables: ProblemObservables
