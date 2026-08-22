"""Seed problem record contract for the M0 benchmark corpus."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .enums import AssetKind, Domain, Topic
from .source import SourceRef


class AssetRef(BaseModel):
    """A local asset referenced by a seed problem.

    ``path`` is relative to the corpus root (``benchmarks/seed``).
    """

    path: str
    kind: AssetKind = AssetKind.FIGURE


class SeedProblemRecord(BaseModel):
    """Observational record of a seed problem.

    Explicitly not the final EEProblemIR: used to discover what the real IR
    needs. Problem shape is captured by observable boolean flags rather than a
    single exclusive ``form`` field.
    """

    id: str
    source: SourceRef
    domain: Domain
    topics: list[Topic]
    question_text: str
    has_formula: bool
    has_circuit_figure: bool
    is_multipart: bool
    answer_available: bool
    assets: list[AssetRef] = Field(default_factory=list)
