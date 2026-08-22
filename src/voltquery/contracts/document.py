"""Per-document provenance contract (``data/documents.yaml``)."""

from __future__ import annotations

from datetime import date

from pydantic import Field

from ._base import ContractModel


class DocumentRef(ContractModel):
    """A specific retrieved artifact (PDF/HTML) a problem was sourced from.

    ``SourceRef`` locates a problem inside a document by ``document_id``.
    ``sha256`` plus ``retrieved_at`` pin the exact bytes that were read, so
    provenance is reproducible. ``license_evidence`` records the license notice
    actually printed on the artifact, which can differ from the collection-level
    ``Source`` license -- e.g. the Socratic worksheets print a CC-BY-1.0 imprint
    while the site (and ``Source``) declares CC-BY-3.0-US.
    """

    id: str
    source_id: str
    filename: str
    url: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieved_at: date
    license_evidence: list[str] = Field(default_factory=list)
