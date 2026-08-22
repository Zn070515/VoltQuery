"""M0 milestone completeness gate.

Unlike ``validate_corpus`` (which reports structural problems in the seed data),
this module answers the question "is M0 done?" It enforces the quantitative and
policy gates that define milestone completion.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from voltquery.contracts import SeedProblemRecord, Source
from voltquery.contracts.enums import DataPolicy, Domain, SourceStatus

from .corpus import load_problems, validate_corpus
from .issues import ValidationIssue
from .sources import load_sources

TARGET_TOTAL = 40
TARGET_CIRCUIT = 32
TARGET_ANALOG = 8


def check_m0(
    problems_path: str | Path,
    sources_path: str | Path,
    assets_root: str | Path,
    documents_path: str | Path,
) -> list[ValidationIssue]:
    """Return issues blocking M0 completion. An empty list means M0 is done."""

    problems_file = Path(problems_path)
    issues: list[ValidationIssue] = []

    if not problems_file.exists():
        issues.append(
            ValidationIssue(
                code="milestone_corpus_missing",
                path=str(problems_file),
                message="corpus file does not exist",
            )
        )
        return issues

    issues.extend(validate_corpus(problems_path, sources_path, assets_root, documents_path))

    try:
        records = load_problems(problems_file)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        issues.append(
            ValidationIssue(
                code="milestone_problems_unreadable",
                path=str(problems_file),
                message=f"could not load records for counting: {exc}",
            )
        )
        return issues

    _check_counts(records, str(problems_file), issues)
    _check_sources(records, Path(sources_path), issues)

    return issues


def _check_counts(
    records: list[SeedProblemRecord],
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    if len(records) < TARGET_TOTAL:
        issues.append(
            ValidationIssue(
                code="milestone_problem_count",
                path=ref,
                message=f"found {len(records)} problem(s), need {TARGET_TOTAL}",
            )
        )

    circuit = sum(1 for record in records if record.domain is Domain.CIRCUIT_THEORY)
    if circuit < TARGET_CIRCUIT:
        issues.append(
            ValidationIssue(
                code="milestone_circuit_count",
                path=ref,
                message=(
                    f"found {circuit} circuit_theory problem(s), "
                    f"need {TARGET_CIRCUIT}"
                ),
            )
        )

    analog = sum(1 for record in records if record.domain is Domain.ANALOG_ELECTRONICS)
    if analog < TARGET_ANALOG:
        issues.append(
            ValidationIssue(
                code="milestone_analog_count",
                path=ref,
                message=(
                    f"found {analog} analog_electronics problem(s), "
                    f"need {TARGET_ANALOG}"
                ),
            )
        )


def _check_sources(
    records: list[SeedProblemRecord],
    source_path: Path,
    issues: list[ValidationIssue],
) -> None:
    sources = _load_source_map(source_path)
    referenced = sorted({record.source.source_id for record in records})

    for source_id in referenced:
        source = sources.get(source_id)
        if source is None:
            issues.append(
                ValidationIssue(
                    code="milestone_source_unknown",
                    path=source_id,
                    message=f"referenced source '{source_id}' is not registered",
                )
            )
            continue
        if source.status is SourceStatus.LICENSE_REVIEW:
            issues.append(
                ValidationIssue(
                    code="milestone_source_license_review",
                    path=source_id,
                    message=(
                        f"source '{source_id}' license is under review "
                        "(LICENSE_REVIEW_REQUIRED); excluded from the public "
                        "Gold corpus until the governing license is confirmed"
                    ),
                )
            )
            continue
        if source.status is not SourceStatus.APPROVED:
            issues.append(
                ValidationIssue(
                    code="milestone_source_unapproved",
                    path=source_id,
                    message=(
                        f"source '{source_id}' is {source.status.value}; "
                        "must be approved"
                    ),
                )
            )
        if not source.license.verified:
            issues.append(
                ValidationIssue(
                    code="milestone_source_unverified",
                    path=source_id,
                    message=f"source '{source_id}' license metadata not verified",
                )
            )
        if source.license.data_policy is not DataPolicy.PUBLIC_REDISTRIBUTABLE:
            issues.append(
                ValidationIssue(
                    code="milestone_source_not_redistributable",
                    path=source_id,
                    message=(
                        f"source '{source_id}' data policy is "
                        f"{source.license.data_policy.value}; the public Gold "
                        "corpus requires public_redistributable"
                    ),
                )
            )
        if source.license.redistribution is not True:
            issues.append(
                ValidationIssue(
                    code="milestone_source_no_redistribution",
                    path=source_id,
                    message=(
                        f"source '{source_id}' does not explicitly allow "
                        "redistribution"
                    ),
                )
            )


def _load_source_map(path: Path) -> dict[str, Source]:
    if not path.exists():
        return {}
    try:
        return {source.id: source for source in load_sources(path)}
    except (ValueError, ValidationError):
        return {}
