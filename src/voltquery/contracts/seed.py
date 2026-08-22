"""Seed problem record contract for the M0 benchmark corpus."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from ._base import ContractModel
from .enums import AssetKind, Domain
from .source import SourceRef

# Open topic slug: lowercase, underscore-separated. The vocabulary is NOT
# frozen; it grows as the seed corpus reveals what EEProblemIR needs.
TOPIC_SLUG_PATTERN = r"^[a-z][a-z0-9_]*$"
TopicSlug = Annotated[str, Field(pattern=TOPIC_SLUG_PATTERN)]


class AssetRef(ContractModel):
    """A local asset referenced by a seed problem.

    ``path`` is relative to the corpus root (``benchmarks/seed``) and must be a
    POSIX-style relative path: no absolute paths, no ``..`` traversal, no drive
    letters or URIs.
    """

    path: str
    kind: AssetKind = AssetKind.FIGURE

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
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


class SeedProblemRecord(ContractModel):
    """Observational record of a seed problem.

    Explicitly not the final EEProblemIR: used to discover what the real IR
    needs. Problem shape is captured by observable boolean flags rather than a
    single exclusive ``form`` field.
    """

    id: str
    source: SourceRef
    domain: Domain
    topics: list[TopicSlug]
    question_text: str
    has_formula: bool
    has_circuit_figure: bool
    is_multipart: bool
    answer_available: bool
    assets: list[AssetRef] = Field(default_factory=list)
