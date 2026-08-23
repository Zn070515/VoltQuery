"""Schema tests for the M2 ingestion contracts (``ProblemCandidate`` v0.1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from voltquery.contracts import (
    CropRect,
    ProblemAsset,
    ProblemCandidate,
    SourceBlock,
)
from voltquery.contracts.ingest import ParserProvenance


def make_candidate(**overrides):
    """Build a minimal valid ``ProblemCandidate`` with a couple of overrides."""
    data = {
        "id": "fixture-cand",
        "source": {"source_id": "fixture-source", "document_id": "fixture-doc"},
        "domain": None,
        "topics": [],
        "statement": "Consider the circuit.",
        "text": "Consider the circuit.",
        "parts": None,
        "inputs": [],
        "targets": [],
        "formulas": [],
        "observables": {
            "has_circuit_figure": False,
            "has_formula": False,
            "answer_available": False,
        },
        "assets": [],
        "provenance": {
            "parser": "voltquery-ingest",
            "document_sha256": "a" * 64,
            "document_id": "fixture-doc",
            "source_blocks": [
                {
                    "kind": "text",
                    "text": "Consider the circuit.",
                    "bbox": {"x0": 0, "y0": 0, "x1": 10, "y1": 10},
                },
            ],
        },
    }
    data.update(overrides)
    return ProblemCandidate.model_validate(data)


def test_round_trip() -> None:
    candidate = make_candidate()
    assert ProblemCandidate.model_validate(candidate.model_dump()) == candidate


def test_schema_version_is_pinned() -> None:
    assert make_candidate().schema_version == "candidate.v0.1"


def test_schema_version_defaults_to_candidate() -> None:
    # Unlike EEProblemIR (where schema_version is required), ProblemCandidate's
    # schema_version is pinned with a default, so it can be omitted.
    data = make_candidate().model_dump()
    del data["schema_version"]
    candidate = ProblemCandidate.model_validate(data)
    assert candidate.schema_version == "candidate.v0.1"


# --- extra="forbid": the candidate and its nested contracts reject unknown keys ---
def test_extra_forbid_on_candidate() -> None:
    data = make_candidate().model_dump()
    data["surprise"] = True
    with pytest.raises(ValidationError):
        ProblemCandidate.model_validate(data)


def test_extra_forbid_on_provenance() -> None:
    data = make_candidate().model_dump()
    data["provenance"]["surprise"] = True
    with pytest.raises(ValidationError):
        ProblemCandidate.model_validate(data)


def test_extra_forbid_on_source_block() -> None:
    data = make_candidate().model_dump()
    data["provenance"]["source_blocks"][0]["surprise"] = True
    with pytest.raises(ValidationError):
        ProblemCandidate.model_validate(data)


# --- empty vs populated defaults ---
def test_defaults_are_empty_until_populated() -> None:
    candidate = make_candidate()
    assert candidate.topics == []
    assert candidate.inputs == []
    assert candidate.targets == []
    assert candidate.formulas == []
    assert candidate.assets == []
    assert candidate.parts is None
    assert candidate.domain is None


def test_provenance_defaults() -> None:
    provenance = ParserProvenance(
        parser="voltquery-ingest",
        document_sha256="b" * 64,
        document_id="fixture-doc",
    )
    assert provenance.parser_version is None
    assert provenance.page_index is None
    assert provenance.extraction_warnings == []
    assert provenance.source_blocks == []


# --- a figure source_block carries asset_path, not text ---
def test_source_block_figure_populates_asset_only() -> None:
    block = SourceBlock(
        kind="figure",
        bbox=CropRect(x0=0, y0=0, x1=10, y1=10),
        asset_path="assets/cand-xref1.png",
    )
    assert block.text is None
    assert block.asset_path is not None


# --- ProblemAsset: a crop_rect requires a page_index and a safe relative path ---
def test_asset_crop_requires_page_index() -> None:
    with pytest.raises(ValidationError):
        ProblemAsset(
            path="assets/x.png",
            crop_rect=CropRect(x0=0, y0=0, x1=1, y1=1),
        )


def test_asset_rejects_absolute_or_traversal_path() -> None:
    with pytest.raises(ValidationError):
        ProblemAsset(path="/abs/assets/x.png")
    with pytest.raises(ValidationError):
        ProblemAsset(path="assets/../x.png")
