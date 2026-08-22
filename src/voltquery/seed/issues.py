"""Structured validation issues for the M0 seed corpus."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ValidationError


class Severity(str, Enum):
    """Severity of a validation issue."""

    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    """A single validation issue.

    Failures are first-class results returned as lists, never swallowed.
    """

    code: str
    path: str
    message: str
    severity: Severity = Severity.ERROR


def format_validation_error(exc: ValidationError) -> str:
    """Render a concise, single-line summary of a pydantic ``ValidationError``."""

    return "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc']) or '<field>'}: {err['msg']}"
        for err in exc.errors()
    )
