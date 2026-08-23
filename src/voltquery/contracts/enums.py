"""Contract enums for the VoltQuery M0 seed corpus."""

from __future__ import annotations

from enum import Enum


class DataPolicy(str, Enum):
    """Distribution policy owned by a data source."""

    PUBLIC_REDISTRIBUTABLE = "public_redistributable"
    RESEARCH_ONLY = "research_only"
    PRIVATE_LOCAL = "private_local"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    """Electrical-engineering domains targeted by VoltQuery."""

    CIRCUIT_THEORY = "circuit_theory"
    ANALOG_ELECTRONICS = "analog_electronics"


class SourceStatus(str, Enum):
    """Lifecycle status of a registered source."""

    CANDIDATE = "candidate"
    APPROVED = "approved"
    LICENSE_REVIEW = "license_review"
    REJECTED = "rejected"


class AssetKind(str, Enum):
    """What a local asset *is*, independent of its purpose.

    Orthogonal to ``AssetRole`` (what it is *for*). A schematic drawing is
    ``kind=SCHEMATIC`` whether it is a source crop or a rendered ``CircuitIR``
    output; that distinction lives on ``AssetOrigin`` instead.
    """

    FIGURE = "figure"
    SCHEMATIC = "schematic"
    WAVEFORM = "waveform"
    TABLE = "table"
    FORMULA = "formula"
    OTHER = "other"


class AssetRole(str, Enum):
    """What an asset *is for* (its role), orthogonal to ``AssetKind``.

    A role never repeats the kind: a schematic crop is ``kind=SCHEMATIC,
    role=CONTENT_CROP``, not ``role=SCHEMATIC``. ``content_crop`` is a generic
    "this crop carries the diagram/visual content" label; ``question_crop`` is
    strictly the retrievable question-text region.
    """

    QUESTION_CROP = "question_crop"
    CONTENT_CROP = "content_crop"
    ANSWER_CROP = "answer_crop"
    SOLUTION_CROP = "solution_crop"


class AssetOrigin(str, Enum):
    """Where an asset came from, orthogonal to ``kind`` and ``role``.

    ``source`` assets are provenance (a crop or file pulled from the source).
    ``generated`` assets (an OCR-derived crop, a ``CircuitIR`` render) are
    produced by VoltQuery and are NOT source provenance.
    """

    SOURCE = "source"
    GENERATED = "generated"


class FormulaRole(str, Enum):
    """Whether a formula is given by the source, merely displayed, or to derive.

    An EE problem *gives* ``V = IR`` rather than "stating" it; so the source
    narrative carries ``given`` formulas, a figure/table may *display* one, and a
    problem may ask the student to ``derived`` a relation.
    """

    GIVEN = "given"
    DISPLAYED = "displayed"
    DERIVED = "derived"


class FormulaLayout(str, Enum):
    """Textual layout of a formula occurrence."""

    INLINE = "inline"
    DISPLAY = "display"


# NOTE: Topic is deliberately NOT an enum during M0. The real topic taxonomy
# is unknown until the seed corpus is populated, so topics are stored as open
# lowercase slugs (see ``contracts.seed.TopicSlug``) and only frozen as a
# ``Topic taxonomy v0.1`` in M1, after the real problems are observed.
