"""Load and validate the M0 seed corpus (``problems.jsonl``)."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from voltquery.contracts import DocumentRef, SeedProblemRecord, Source

from .documents import load_documents
from .issues import ValidationIssue, format_validation_error
from .sources import load_sources


def load_problems(path: str | Path) -> list[SeedProblemRecord]:
    """Parse ``problems.jsonl`` into validated ``SeedProblemRecord`` models.

    Loader semantics are fail-fast: a missing file raises ``FileNotFoundError``
    and malformed JSON / schema errors propagate. Use ``validate_corpus`` when
    you want issues collected rather than raised.
    """

    problems_path = Path(path)
    if not problems_path.exists():
        raise FileNotFoundError(f"corpus file not found: {problems_path}")

    records: list[SeedProblemRecord] = []
    with problems_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            data = json.loads(line)
            records.append(SeedProblemRecord.model_validate(data))
    return records


def validate_corpus(
    problems_path: str | Path,
    sources_path: str | Path,
    assets_root: str | Path,
    documents_path: str | Path,
) -> list[ValidationIssue]:
    """Validate the seed corpus, returning structured issues."""

    problems_file = Path(problems_path)
    assets = Path(assets_root)
    issues: list[ValidationIssue] = []

    if not problems_file.exists():
        issues.append(
            ValidationIssue(
                code="corpus_missing",
                path=str(problems_file),
                message="corpus file does not exist",
            )
        )
        return issues

    sources = _registered_sources(sources_path)
    documents = _registered_documents(documents_path)

    seen_ids: set[str] = set()
    with problems_file.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            ref = f"{problems_file}:{lineno}"
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                record = SeedProblemRecord.model_validate(data)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        code="problem_record_invalid_json",
                        path=ref,
                        message=f"invalid JSON: {exc}",
                    )
                )
                continue
            except ValidationError as exc:
                issues.append(
                    ValidationIssue(
                        code="problem_record_invalid",
                        path=ref,
                        message=f"record failed validation: {format_validation_error(exc)}",
                    )
                )
                continue

            if record.id in seen_ids:
                issues.append(
                    ValidationIssue(
                        code="duplicate_problem_id",
                        path=ref,
                        message=f"duplicate problem id '{record.id}'",
                    )
                )
            seen_ids.add(record.id)

            if record.source.source_id not in sources:
                issues.append(
                    ValidationIssue(
                        code="problem_source_unknown",
                        path=ref,
                        message=(
                            f"problem '{record.id}' references unknown source id "
                            f"'{record.source.source_id}'"
                        ),
                    )
                )
            else:
                _check_source_domain(record, sources, ref, issues)

            _check_document_ref(record, documents, ref, issues)

            for asset in record.assets:
                asset_path = (assets / asset.path).resolve()
                if not asset_path.is_relative_to(assets.resolve()):
                    issues.append(
                        ValidationIssue(
                            code="problem_asset_escape",
                            path=ref,
                            message=(
                                f"problem '{record.id}' references asset outside "
                                f"the corpus root: '{asset.path}'"
                            ),
                        )
                    )
                elif not asset_path.exists():
                    issues.append(
                        ValidationIssue(
                            code="problem_asset_missing",
                            path=ref,
                            message=(
                                f"problem '{record.id}' references missing asset "
                                f"'{asset.path}'"
                            ),
                        )
                    )

    return issues


def _registered_sources(sources_path: str | Path) -> dict[str, Source]:
    source_path = Path(sources_path)
    if not source_path.exists():
        return {}
    try:
        return {source.id: source for source in load_sources(source_path)}
    except (ValueError, ValidationError):
        # An unreadable registry means no source can be resolved.
        return {}


def _check_source_domain(
    record: SeedProblemRecord,
    sources: dict[str, Source],
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    source = sources[record.source.source_id]
    if record.domain not in source.domains:
        issues.append(
            ValidationIssue(
                code="problem_source_domain_mismatch",
                path=ref,
                message=(
                    f"problem '{record.id}' is '{record.domain.value}' but source "
                    f"'{source.id}' only declares "
                    f"{sorted(domain.value for domain in source.domains)}"
                ),
            )
        )


def _registered_documents(documents_path: str | Path) -> dict[str, DocumentRef]:
    doc_path = Path(documents_path)
    if not doc_path.exists():
        return {}
    try:
        return {doc.id: doc for doc in load_documents(doc_path)}
    except (ValueError, ValidationError):
        # An unreadable registry means no document can be resolved.
        return {}


def _check_document_ref(
    record: SeedProblemRecord,
    documents: dict[str, DocumentRef],
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    document_id = record.source.document_id
    if document_id is None:
        issues.append(
            ValidationIssue(
                code="problem_document_missing",
                path=ref,
                message=(
                    f"problem '{record.id}' has no document_id "
                    "(document provenance is mandatory)"
                ),
            )
        )
        return
    if document_id not in documents:
        issues.append(
            ValidationIssue(
                code="problem_document_unknown",
                path=ref,
                message=(
                    f"problem '{record.id}' references unknown document id "
                    f"'{document_id}'"
                ),
            )
        )
        return
    if documents[document_id].source_id != record.source.source_id:
        issues.append(
            ValidationIssue(
                code="problem_document_source_mismatch",
                path=ref,
                message=(
                    f"problem '{record.id}' references document '{document_id}' "
                    f"belonging to source '{documents[document_id].source_id}' "
                    f"but the problem source is '{record.source.source_id}'"
                ),
            )
        )
