"""Tests for the M1 problem IR validator and seed<->IR parity."""

from __future__ import annotations

from pathlib import Path

import pytest
from voltquery.contracts import SCHEMA_VERSION, EEProblemIR, SeedProblemRecord
from voltquery.seed import load_problem_ir, validate_problem_ir


def _seed(
    *,
    questions: str = "Find the current.",
    topics: list[str] | None = None,
    multipart: bool = False,
    answer_available: bool = False,
    has_formula: bool = False,
) -> SeedProblemRecord:
    return SeedProblemRecord(
        id="vq_ir_0001",
        source={"source_id": "fixture-source", "document_id": "fixture-worksheet"},
        domain="circuit_theory",
        topics=topics or ["ohm_law"],
        question_text=questions,
        has_formula=has_formula,
        has_circuit_figure=False,
        is_multipart=multipart,
        answer_available=answer_available,
        assets=[],
    )


def _ir(
    seed: SeedProblemRecord,
    *,
    statement: str | None = None,
    parts: list | None = None,
    answer_available: bool | None = None,
    has_formula: bool | None = None,
    **overrides,
) -> EEProblemIR:
    parts = [] if parts is None else parts
    has_formula_eff = seed.has_formula if has_formula is None else has_formula
    answer_available_eff = seed.answer_available if answer_available is None else answer_available
    data = {
        "schema_version": SCHEMA_VERSION,
        "id": seed.id,
        "source": seed.source,
        "domain": seed.domain,
        "topics": seed.topics,
        "statement": statement if statement is not None else seed.question_text,
        "parts": parts,
        "inputs": [],
        "targets": [],
        "answer": None,
        "assets": [],
        "formulas": [],
        "observables": {
            "has_circuit_figure": False,
            "has_formula": has_formula_eff,
            "answer_available": answer_available_eff,
        },
    }
    data.update(overrides)
    return EEProblemIR.model_validate(data)


def _write(tmp_path: Path, seed: SeedProblemRecord, ir: EEProblemIR) -> tuple[Path, Path]:
    corpus = tmp_path / "problems.jsonl"
    ir_file = tmp_path / "problem_ir.jsonl"
    corpus.write_text(seed.model_dump_json() + "\n", encoding="utf-8")
    # Revalidate so model_copy(update={raw dict}) survives serialization cleanly.
    payload = EEProblemIR.model_validate(ir.model_dump()).model_dump_json() + "\n"
    ir_file.write_text(payload, encoding="utf-8")
    return corpus, ir_file


def _codes(
    tmp_path: Path,
    seed: SeedProblemRecord,
    ir: EEProblemIR,
    sources_path: Path,
    documents_path: Path,
) -> set[str]:
    corpus, ir_file = _write(tmp_path, seed, ir)
    issues = validate_problem_ir(corpus, ir_file, sources_path, documents_path)
    return {issue.code for issue in issues}


def test_ir_corpus_clean_when_matching(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed()
    ir = _ir(seed)
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert codes == set()


def test_load_problem_ir_round_trip(tmp_path: Path) -> None:
    seed = _seed()
    ir = _ir(seed)
    corpus, ir_file = _write(tmp_path, seed, ir)
    assert load_problem_ir(ir_file) == [ir]


def test_load_problem_ir_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_problem_ir(tmp_path / "nope.jsonl")


def test_ir_file_missing_detected(tmp_path: Path) -> None:
    # A missing IR file is reported directly, not as a cascade of unknown ids.
    corpus = tmp_path / "problems.jsonl"
    corpus.write_text(_seed().model_dump_json() + "\n", encoding="utf-8")
    issues = validate_problem_ir(corpus, tmp_path / "nope.jsonl", Path("x"), Path("y"))
    assert "problem_ir_missing" in {i.code for i in issues}


def test_orphan_ir_and_missing_for_seed_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    # The IR has one record that does not correspond to any seed, and the only
    # seed has no IR record -> both id-parity violations are reported.
    seed = _seed()
    orphan = _ir(seed, id="vq_orphan_9999")
    codes = _codes(tmp_path, seed, orphan, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_orphan" in codes
    assert "problem_ir_missing_for_seed" in codes


def test_source_mismatch_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed()
    ir = _ir(seed, source={"source_id": "other-source", "document_id": "doc-other"})
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_source_mismatch" in codes


def test_domain_mismatch_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed()
    ir = _ir(seed, domain="analog_electronics")
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_domain_mismatch" in codes


def test_topics_mismatch_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed(topics=["ohm_law"])
    ir = _ir(seed, topics=["kcl"], statement="Find.")
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_topics_mismatch" in codes


def test_statement_mismatch_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed(questions="Find the current.")
    ir = _ir(seed, statement="Different narration.")
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_statement_mismatch" in codes


def test_multipart_missing_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed(multipart=True, questions="(a) Find V. (b) Find I.")
    ir = _ir(seed, parts=[])
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_multipart_missing" in codes


def test_unexpected_multipart_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed()  # single-part
    ir = _ir(seed, parts=[{"label": "a", "statement": "Find V.", "target": "V"}])
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_unexpected_multipart" in codes


def test_observable_answer_inconsistent_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed(answer_available=True)
    ir = _ir(seed, answer_available=False)
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_observable_answer_inconsistent" in codes


def test_document_missing_detected(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    seed = _seed()
    ir = _ir(seed, source={"source_id": "fixture-source"})
    codes = _codes(tmp_path, seed, ir, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_document_missing" in codes


def test_broken_ir_json_reported_as_record_error(
    tmp_path: Path,
    fixture_sources_path: Path,
    fixture_documents_path: Path,
) -> None:
    corpus = tmp_path / "problems.jsonl"
    ir_file = tmp_path / "problem_ir.jsonl"
    corpus.write_text(_seed().model_dump_json() + "\n", encoding="utf-8")
    ir_file.write_text("{not valid json}\n", encoding="utf-8")
    issues = validate_problem_ir(corpus, ir_file, fixture_sources_path, fixture_documents_path)
    assert "problem_ir_record_invalid_json" in {i.code for i in issues}
