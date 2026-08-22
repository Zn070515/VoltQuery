"""Machine-readable license metadata contract."""

from __future__ import annotations

from datetime import date

from ._base import ContractModel
from .enums import DataPolicy


class LicenseMetadata(ContractModel):
    """License/provenance metadata owned by a source.

    Restrictive defaults: an unverified source defaults to ``UNKNOWN`` policy
    and must not be treated as redistributable until ``verified`` is true.

    ``verification_url`` / ``verified_at`` / ``verification_note`` record the
    evidence behind a ``verified=True`` claim so the reason stays auditable.
    """

    id: str = "UNKNOWN"
    redistribution: bool | None = None
    derivatives: bool | None = None
    commercial: bool | None = None
    attribution_required: bool | None = None
    data_policy: DataPolicy = DataPolicy.UNKNOWN
    verified: bool = False
    verification_url: str | None = None
    verified_at: date | None = None
    verification_note: str | None = None
