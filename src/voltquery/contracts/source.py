"""Source registry and per-problem provenance contracts."""

from __future__ import annotations

from pydantic import Field

from ._base import ContractModel
from .enums import Domain, SourceStatus
from .license import LicenseMetadata


class Source(ContractModel):
    """A registered source entry in ``data/sources.yaml``."""

    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    institution: str | None = None
    edition: str | None = None
    published_year: int | None = None
    domains: list[Domain]
    license: LicenseMetadata
    source_url: str | None = None
    status: SourceStatus = SourceStatus.CANDIDATE
    notes: str | None = None


class SourceRef(ContractModel):
    """Provenance of a single problem within a registered source."""

    source_id: str
    document: str | None = None
    page_index: int | None = None
    page_label: str | None = None
    question_number: str | None = None
