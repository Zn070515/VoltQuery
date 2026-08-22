"""Machine-readable license metadata contract."""

from __future__ import annotations

from pydantic import BaseModel

from .enums import DataPolicy


class LicenseMetadata(BaseModel):
    """License/provenance metadata owned by a source.

    Restrictive defaults: an unverified source defaults to ``UNKNOWN`` policy
    and must not be treated as redistributable until ``verified`` is true.
    """

    id: str = "UNKNOWN"
    redistribution: bool | None = None
    derivatives: bool | None = None
    commercial: bool | None = None
    attribution_required: bool | None = None
    data_policy: DataPolicy = DataPolicy.UNKNOWN
    verified: bool = False
