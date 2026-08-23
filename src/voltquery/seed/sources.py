"""Load and validate the source registry (``data/sources.yaml``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from voltquery.contracts import Source

from .issues import Severity, ValidationIssue, format_validation_error


def load_sources(path: str | Path) -> list[Source]:
    """Parse ``data/sources.yaml`` into validated ``Source`` models."""

    return _parse_sources(Path(path))


def _parse_sources(path: Path) -> list[Source]:
    data = _read_yaml(path)
    raw = data.get("sources", [])
    return [Source.model_validate(item) for item in raw]


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return data


def _source_line_numbers(path: Path) -> dict[str, int]:
    """Map each source ``id`` to its 1-based line number in the registry."""

    mapping: dict[str, int] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return mapping
    for lineno, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("- id:"):
            value = stripped[len("- id:"):].strip().strip("'\"")
            mapping[value] = lineno
    return mapping


def validate_sources(path: str | Path) -> list[ValidationIssue]:
    """Validate the source registry, returning structured issues."""

    source_path = Path(path)
    issues: list[ValidationIssue] = []

    if not source_path.exists():
        issues.append(
            ValidationIssue(
                code="source_registry_missing",
                path=str(source_path),
                message="source registry file does not exist",
            )
        )
        return issues

    try:
        data = _read_yaml(source_path)
    except ValueError as exc:
        issues.append(
            ValidationIssue(
                code="source_registry_invalid_format",
                path=str(source_path),
                message=str(exc),
            )
        )
        return issues

    raw_sources = data.get("sources", [])
    if not isinstance(raw_sources, list):
        issues.append(
            ValidationIssue(
                code="source_registry_invalid_format",
                path=str(source_path),
                message="'sources' must be a list",
            )
        )
        return issues

    id_line_map = _source_line_numbers(source_path)
    seen_ids: set[str] = set()
    for idx, item in enumerate(raw_sources):
        entry_id = item.get("id") if isinstance(item, dict) else None
        fallback = idx + 2
        line_no = id_line_map.get(entry_id, fallback) if isinstance(entry_id, str) else fallback
        ref = f"{source_path}:{line_no}"
        if not isinstance(item, dict):
            issues.append(
                ValidationIssue(
                    code="source_invalid_record",
                    path=ref,
                    message=f"source entry #{idx} is not a mapping",
                )
            )
            continue

        if "license" not in item or not isinstance(item.get("license"), dict):
            issues.append(
                ValidationIssue(
                    code="source_license_missing",
                    path=ref,
                    message=(
                        f"source entry #{idx} has no 'license' metadata block "
                        "(provenance is mandatory)"
                    ),
                )
            )

        try:
            source = Source.model_validate(item)
        except ValidationError as exc:
            issues.append(
                ValidationIssue(
                    code="source_record_invalid",
                    path=ref,
                    message=(
                        f"source entry #{idx} failed validation: "
                        f"{format_validation_error(exc)}"
                    ),
                )
            )
            continue

        if source.id in seen_ids:
            issues.append(
                ValidationIssue(
                    code="duplicate_source_id",
                    path=ref,
                    message=f"duplicate source id '{source.id}'",
                )
            )
        seen_ids.add(source.id)

        if not source.license.verified:
            issues.append(
                ValidationIssue(
                    code="source_license_unverified",
                    path=ref,
                    message=(
                        f"source '{source.id}' license is not verified; "
                        "do not redistribute until verified"
                    ),
                    severity=Severity.WARNING,
                )
            )

    return issues
