"""Load and validate the M1 problem IR corpus (``problem_ir.jsonl``).

The IR corpus is a derived, version-shaped projection of the M0 seed corpus. Its
load-bearing invariant is *parity*: every seed problem has exactly one IR record,
and the IR record's identity fields (source / domain / topics / verbatim
statement / multipart shape / source facts) agree with the seed record. The IR
adds structure (parts, targets, inputs, formulas, assets) on top of that floor.

``answer`` is deliberately kept ``None`` by the corpus convention: the Gold
corpus is not treated as a solver eval set, and ``answer_available`` is a source
fact (observable) rather than a captured machine answer (a deferred M2 concern).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from voltquery.contracts import EEProblemIR, Part, ProblemAsset, SeedProblemRecord
from voltquery.contracts.enums import AssetKind, AssetRole, Domain

from .corpus import _registered_documents, _registered_sources, load_problems
from .issues import ValidationIssue, format_validation_error


def load_problem_ir(path: str | Path) -> list[EEProblemIR]:
    """Parse ``problem_ir.jsonl`` into validated ``EEProblemIR`` models.

    Fail-fast loader: a missing file raises ``FileNotFoundError`` and malformed
    JSON / schema errors propagate. Use ``validate_problem_ir`` to collect issues.
    """

    ir_path = Path(path)
    if not ir_path.exists():
        raise FileNotFoundError(f"problem IR file not found: {ir_path}")

    records: list[EEProblemIR] = []
    with ir_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            records.append(EEProblemIR.model_validate_json(line))
    return records


def validate_problem_ir(
    problems_path: str | Path,
    ir_path: str | Path,
    sources_path: str | Path,
    documents_path: str | Path,
    assets_root: str | Path | None = None,
) -> list[ValidationIssue]:
    """Validate the IR corpus, including seed<->IR parity, returning issues."""

    ir_file = Path(ir_path)
    issues: list[ValidationIssue] = []

    if not ir_file.exists():
        issues.append(
            ValidationIssue(
                code="problem_ir_missing",
                path=str(ir_file),
                message="problem IR file does not exist",
            )
        )
        return issues

    # Parse records first, so a broken IR file is reported as exactly the
    # malformed lines rather than a cascade of unknown-id errors.
    by_id: dict[str, tuple[EEProblemIR, str]] = {}
    with ir_file.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            ref = f"{ir_file}:{lineno}"
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        code="problem_ir_record_invalid_json",
                        path=ref,
                        message=f"invalid JSON: {exc}",
                    )
                )
                continue
            try:
                ir = EEProblemIR.model_validate(data)
            except ValidationError as exc:
                issues.append(
                    ValidationIssue(
                        code="problem_ir_record_invalid",
                        path=ref,
                        message=f"record failed validation: {format_validation_error(exc)}",
                    )
                )
                continue
            if ir.id in by_id:
                issues.append(
                    ValidationIssue(
                        code="duplicate_problem_ir_id",
                        path=ref,
                        message=f"duplicate problem ir id '{ir.id}'",
                    )
                )
                continue
            by_id[ir.id] = (ir, ref)

    try:
        seeds = load_problems(problems_path)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        issues.append(
            ValidationIssue(
                code="problem_ir_seed_unreadable",
                path=str(problems_path),
                message=f"could not load seed records for parity: {exc}",
            )
        )
        return issues

    seed_by_id = {seed.id: seed for seed in seeds}
    sources = _registered_sources(sources_path)
    documents = _registered_documents(documents_path)

    # Id parity: the IR corpus mirrors the seed corpus one-to-one.
    for seed_id in seed_by_id:
        if seed_id not in by_id:
            issues.append(
                ValidationIssue(
                    code="problem_ir_missing_for_seed",
                    path=seed_id,
                    message=f"seed problem '{seed_id}' has no problem IR record",
                )
            )
    for ir_id in by_id:
        if ir_id not in seed_by_id:
            issues.append(
                ValidationIssue(
                    code="problem_ir_orphan",
                    path=ir_id,
                    message=f"problem IR '{ir_id}' has no matching seed problem",
                )
            )

    # Per-record parity for items that appear in both sides.
    for seed_id, seed in seed_by_id.items():
        hit = by_id.get(seed_id)
        if hit is None:
            continue
        ir, ref = hit
        _check_parity(seed, ir, ref, sources, documents, issues)
        _check_assets(seed.id, ir, assets_root, ref, issues)

    return issues


def _check_parity(
    seed: SeedProblemRecord,
    ir: EEProblemIR,
    ref: str,
    sources: dict,
    documents: dict,
    issues: list[ValidationIssue],
) -> None:
    tag = f"problem '{seed.id}'"

    if ir.source != seed.source:
        issues.append(
            ValidationIssue(
                code="problem_ir_source_mismatch",
                path=ref,
                message=(
                    f"{tag} IR source provenance {ir.source.model_dump()} != seed "
                    f"{seed.source.model_dump()}"
                ),
            )
        )
    if ir.source.source_id not in sources:
        issues.append(
            ValidationIssue(
                code="problem_ir_source_unknown",
                path=ref,
                message=f"{tag} references unknown source id '{ir.source.source_id}'",
            )
        )
    else:
        _check_source_domain(seed.id, ir.domain, ir.source.source_id, sources, ref, issues)

    if ir.domain is not seed.domain:
        issues.append(
            ValidationIssue(
                code="problem_ir_domain_mismatch",
                path=ref,
                message=f"{tag} IR domain '{ir.domain.value}' != seed domain '{seed.domain.value}'",
            )
        )

    if ir.topics != seed.topics:
        issues.append(
            ValidationIssue(
                code="problem_ir_topics_mismatch",
                path=ref,
                message=f"{tag} IR topics {ir.topics} != seed topics {seed.topics}",
            )
        )

    if ir.statement != seed.question_text:
        issues.append(
            ValidationIssue(
                code="problem_ir_statement_mismatch",
                path=ref,
                message=f"{tag} IR statement is not the verbatim seed question_text",
            )
        )

    if seed.is_multipart:
        if ir.parts is None or len(ir.parts) == 0:
            issues.append(
                ValidationIssue(
                    code="problem_ir_multipart_missing",
                    path=ref,
                    message=(
                        f"{tag} is multipart but IR has no parsed parts"
                    ),
                )
            )
    elif ir.parts is not None and len(ir.parts) > 0:
        issues.append(
            ValidationIssue(
                code="problem_ir_unexpected_multipart",
                path=ref,
                message=f"{tag} is single-part but IR has parsed parts",
            )
        )

    _check_observables(seed, ir, ref, issues)
    _check_document_ref(seed.id, ir, documents, ref, issues)


def _check_source_domain(
    problem_id: str,
    domain: Domain,
    source_id: str,
    sources: dict,
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    source = sources[source_id]
    if domain not in source.domains:
        issues.append(
            ValidationIssue(
                code="problem_ir_source_domain_mismatch",
                path=ref,
                message=(
                    f"problem '{problem_id}' is '{domain.value}' but source "
                    f"'{source_id}' only declares "
                    f"{sorted(d.value for d in source.domains)}"
                ),
            )
        )


def _check_observables(
    seed: SeedProblemRecord,
    ir: EEProblemIR,
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    tag = f"problem '{seed.id}'"

    # All three source facts are carried verbatim and must agree exactly (M0 is
    # frozen; the one-way tolerance for under-flagging no longer applies).
    if ir.observables.answer_available is not seed.answer_available:
        issues.append(
            ValidationIssue(
                code="problem_ir_observable_answer_inconsistent",
                path=ref,
                message=(
                    f"{tag} IR answer_available={ir.observables.answer_available} "
                    f"!= seed {seed.answer_available}"
                ),
            )
        )

    if ir.observables.has_formula is not seed.has_formula:
        issues.append(
            ValidationIssue(
                code="problem_ir_observable_formula_inconsistent",
                path=ref,
                message=(
                    f"{tag} IR has_formula={ir.observables.has_formula} "
                    f"!= seed {seed.has_formula}"
                ),
            )
        )
    if ir.formulas and not ir.observables.has_formula:
        issues.append(
            ValidationIssue(
                code="problem_ir_observable_formula_inconsistent",
                path=ref,
                message=f"{tag} IR has formulas but records has_formula=False",
            )
        )

    if ir.observables.has_circuit_figure is not seed.has_circuit_figure:
        issues.append(
            ValidationIssue(
                code="problem_ir_observable_figure_inconsistent",
                path=ref,
                message=(
                    f"{tag} IR has_circuit_figure={ir.observables.has_circuit_figure} "
                    f"!= seed {seed.has_circuit_figure}"
                ),
            )
        )
    if _has_diagram_asset(ir.assets) and not ir.observables.has_circuit_figure:
        issues.append(
            ValidationIssue(
                code="problem_ir_observable_figure_inconsistent",
                path=ref,
                message=f"{tag} IR has a diagram asset but records has_circuit_figure=False",
            )
        )


def _has_diagram_asset(assets: list[ProblemAsset]) -> bool:
    """True if an asset carries the visual diagram (not the question-text crop)."""
    for asset in assets:
        if asset.role is AssetRole.CONTENT_CROP and asset.kind in (
            AssetKind.FIGURE,
            AssetKind.SCHEMATIC,
            AssetKind.WAVEFORM,
        ):
            return True
    return False


def _check_assets(
    problem_id: str,
    ir: EEProblemIR,
    assets_root: str | Path | None,
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    if assets_root is None:
        return
    root = Path(assets_root).resolve()
    for asset in ir.assets:
        asset_path = (root / asset.path).resolve()
        if not asset_path.is_relative_to(root):
            issues.append(
                ValidationIssue(
                    code="problem_ir_asset_escape",
                    path=ref,
                    message=(
                        f"problem '{problem_id}' references asset outside the "
                        f"corpus root: '{asset.path}'"
                    ),
                )
            )
        elif not asset_path.exists():
            issues.append(
                ValidationIssue(
                    code="problem_ir_asset_missing",
                    path=ref,
                    message=(
                        f"problem '{problem_id}' references missing asset "
                        f"'{asset.path}'"
                    ),
                )
            )
        if asset.parts:
            labels = _collect_part_labels(ir.parts)
            for label in asset.parts:
                if label not in labels:
                    issues.append(
                        ValidationIssue(
                            code="problem_ir_asset_part_unknown",
                            path=ref,
                            message=(
                                f"problem '{problem_id}' binds asset '{asset.path}' "
                                f"to unknown part '{label}'"
                            ),
                        )
                    )


def _collect_part_labels(parts: list[Part] | None) -> list[str]:
    labels: list[str] = []
    for part in parts or []:
        labels.append(part.label)
        labels.extend(_collect_part_labels(part.parts))
    return labels


def _check_document_ref(
    problem_id: str,
    ir: EEProblemIR,
    documents: dict,
    ref: str,
    issues: list[ValidationIssue],
) -> None:
    document_id = ir.source.document_id
    if document_id is None:
        issues.append(
            ValidationIssue(
                code="problem_ir_document_missing",
                path=ref,
                message=(
                    f"problem '{problem_id}' has no document_id "
                    "(document provenance is mandatory)"
                ),
            )
        )
        return
    if document_id not in documents:
        issues.append(
            ValidationIssue(
                code="problem_ir_document_unknown",
                path=ref,
                message=(
                    f"problem '{problem_id}' references unknown document id "
                    f"'{document_id}'"
                ),
            )
        )
        return
    if documents[document_id].source_id != ir.source.source_id:
        issues.append(
            ValidationIssue(
                code="problem_ir_document_source_mismatch",
                path=ref,
                message=(
                    f"problem '{problem_id}' references document '{document_id}' "
                    f"belonging to source '{documents[document_id].source_id}' "
                    f"but the IR source is '{ir.source.source_id}'"
                ),
            )
        )
