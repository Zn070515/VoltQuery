"""Source registry and per-problem provenance contracts."""

from __future__ import annotations

from pydantic import BaseModel

from .enums import Domain, SourceStatus
from .license import LicenseMetadata


class Source(BaseModel):
    """A registered source entry in ``data/sources.yaml``."""

    id: str
    title: str
    author: str | None = None
    domains: list[Domain]
    license: LicenseMetadata
    source_url: str | None = None
    status: SourceStatus = SourceStatus.CANDIDATE
    notes: str | None = None


class SourceRef(BaseModel):
    """Provenance of a single problem within a registered source."""

    source_id: str
    document: str | None = None
    page: int | None = None
    question_number: str | None = None
