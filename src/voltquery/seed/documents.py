"""Load and validate the document registry (``data/documents.yaml``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from voltquery.contracts import DocumentRef

from .issues import ValidationIssue, format_validation_error


def load_documents(path: str | Path) -> list[DocumentRef]:
    """Parse ``data/documents.yaml`` into validated ``DocumentRef`` models."""

    return _parse_documents(Path(path))


def _parse_documents(path: Path) -> list[DocumentRef]:
    data = _read_yaml(path)
    raw = data.get("documents", [])
    return [DocumentRef.model_validate(item) for item in raw]


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


def validate_documents(path: str | Path) -> list[ValidationIssue]:
    """Validate the document registry, returning structured issues.

    Provenance reproducibility is mandatory, so every document is required to
    carry at least a URL, a SHA256, and a retrieval date.
    """

    doc_path = Path(path)
    issues: list[ValidationIssue] = []

    if not doc_path.exists():
        issues.append(
            ValidationIssue(
                code="document_registry_missing",
                path=str(doc_path),
                message="document registry file does not exist",
            )
        )
        return issues

    try:
        data = _read_yaml(doc_path)
    except ValueError as exc:
        issues.append(
            ValidationIssue(
                code="document_registry_invalid_format",
                path=str(doc_path),
                message=str(exc),
            )
        )
        return issues

    raw_docs = data.get("documents", [])
    if not isinstance(raw_docs, list):
        issues.append(
            ValidationIssue(
                code="document_registry_invalid_format",
                path=str(doc_path),
                message="'documents' must be a list",
            )
        )
        return issues

    seen_ids: set[str] = set()
    for idx, item in enumerate(raw_docs):
        ref = f"{doc_path}:#{idx + 2}"
        if not isinstance(item, dict):
            issues.append(
                ValidationIssue(
                    code="document_invalid_record",
                    path=ref,
                    message=f"document entry #{idx} is not a mapping",
                )
            )
            continue

        for field, code in (
            ("url", "document_missing_url"),
            ("sha256", "document_missing_sha256"),
            ("retrieved_at", "document_missing_retrieved_at"),
        ):
            if not item.get(field):
                issues.append(
                    ValidationIssue(
                        code=code,
                        path=ref,
                        message=f"document entry #{idx} has no {field}",
                    )
                )

        try:
            doc = DocumentRef.model_validate(item)
        except ValidationError as exc:
            issues.append(
                ValidationIssue(
                    code="document_record_invalid",
                    path=ref,
                    message=(
                        f"document entry #{idx} failed validation: "
                        f"{format_validation_error(exc)}"
                    ),
                )
            )
            continue

        if doc.id in seen_ids:
            issues.append(
                ValidationIssue(
                    code="duplicate_document_id",
                    path=ref,
                    message=f"duplicate document id '{doc.id}'",
                )
            )
        seen_ids.add(doc.id)

    return issues
