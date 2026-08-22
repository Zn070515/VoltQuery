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
    """Kind of local asset referenced by a seed problem."""

    FIGURE = "figure"
    FORMULA = "formula"
    SCHEMATIC = "schematic"
    OTHER = "other"


class AssetRole(str, Enum):
    """What an asset *is for*, orthogonal to ``AssetKind`` (what it *is*).

    ``observed``-role assets come straight from the source and are the retrieval
    targets; ``generated`` assets (a CircuitIR render, an OCR-derived crop) are
    produced by VoltQuery and are NOT source provenance.
    """

    QUESTION_CROP = "question_crop"
    FIGURE = "figure"
    SCHEMATIC = "schematic"
    FORMULA = "formula"
    TABLE = "table"
    ANSWER = "answer"
    SOLUTION = "solution"
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
