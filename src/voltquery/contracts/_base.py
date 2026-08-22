"""Base contract model shared by all VoltQuery typed contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ContractModel(BaseModel):
    """Base for all VoltQuery contracts.

    ``extra='forbid'`` makes an unknown or misspelled field surface as a
    validation error instead of being silently dropped (no silent fallback).
    This matters for a Gold benchmark corpus where a typo'd field must never
    disappear unnoticed.
    """

    model_config = ConfigDict(extra="forbid")
