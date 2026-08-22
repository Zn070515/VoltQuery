"""Load and validate the M0 seed corpus (``problems.jsonl``)."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from voltquery.contracts import SeedProblemRecord

from .issues import ValidationIssue, format_validation_error
from .sources import load_sources


def load_problems(path: str | Path) -> list[SeedProblemRecord]:
    """Parse ``problems.jsonl`` into validated ``SeedProblemRecord`` models."""

    problems_path = Path(path)
    records: list[SeedProblemRecord] = []
    if not problems_path.exists():
        return records

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

    source_ids = _registered_source_ids(sources_path)

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

            if record.source.source_id not in source_ids:
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

            for asset in record.assets:
                if not (assets / asset.path).exists():
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


def _registered_source_ids(sources_path: str | Path) -> set[str]:
    source_path = Path(sources_path)
    if not source_path.exists():
        return set()
    try:
        return {source.id for source in load_sources(source_path)}
    except (ValueError, ValidationError):
        # An unreadable registry means no source can be resolved.
        return set()
