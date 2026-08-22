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


# NOTE: Topic is deliberately NOT an enum during M0. The real topic taxonomy
# is unknown until the seed corpus is populated, so topics are stored as open
# lowercase slugs (see ``contracts.seed.TopicSlug``) and only frozen as a
# ``Topic taxonomy v0.1`` in M1, after the real problems are observed.
