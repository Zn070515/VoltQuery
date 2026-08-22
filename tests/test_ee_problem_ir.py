"""Schema tests for the M1 ``EEProblemIR`` contract (v0.1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from voltquery.contracts import (
    Answer,
    AssetRole,
    EEProblemIR,
    FormulaRole,
    ProblemAsset,
    Quantity,
)


def make_ir(**overrides):
    """Build a minimal valid ``EEProblemIR`` with a couple of overrides."""
    data = {
        "id": "vq_ir_test",
        "source": {"source_id": "fixture-source"},
        "domain": "circuit_theory",
        "topics": ["nodal_analysis"],
        "statement": "Consider the circuit.",
        "parts": None,
        "inputs": [],
        "answer": None,
        "assets": [],
        "formulas": [],
        "observables": {
            "has_circuit_figure": False,
            "has_formula": False,
            "answer_available": False,
        },
    }
    data.update(overrides)
    return EEProblemIR.model_validate(data)


def test_round_trip() -> None:
    ir = make_ir()
    assert EEProblemIR.model_validate(ir.model_dump()) == ir


# --- parts: three-state (None = unparsed, [] = no subparts, [Part] = multipart) ---
def test_parts_none_is_unparsed() -> None:
    assert make_ir().parts is None


def test_parts_empty_is_single() -> None:
    assert make_ir(parts=[]).parts == []


def test_parts_list_is_multipart() -> None:
    ir = make_ir(
        parts=[
            {
                "label": "a",
                "statement": "Find Vc.",
                "target": "Vc",
                "answer": {"type": "scalar", "content": {"value": 3.0, "unit": "V"}},
            },
            {"label": "b", "statement": "Find the time constant.", "target": "tau"},
        ]
    )
    assert len(ir.parts) == 2
    assert ir.parts[0].label == "a"
    assert ir.parts[0].answer.type == "scalar"


# --- answer: open {type, content}, deliberately not a rigid union ---
def test_answer_is_open_type_content() -> None:
    # A real answer can bundle scalar + drawing + explanation; content stays open.
    answer = Answer(
        type="structured",
        content={"scalar": {"Rth": "1 kΩ"}, "drawing_ref": "assets/x.png", "explanation": "..."},
    )
    assert answer.type == "structured"
    assert answer.content["scalar"]["Rth"] == "1 kΩ"


# --- role axis is orthogonal to kind; AssetRole is wide ---
def test_asset_role_broader_than_kind() -> None:
    asset = ProblemAsset(path="assets/vq_schematic.png", kind="schematic", role="schematic")
    assert asset.role is AssetRole.SCHEMATIC
    # a generated (not source) asset is a distinct role, not a source kind
    gen = ProblemAsset(path="assets/vq_ocr_crop.png", kind="figure", role="generated")
    assert gen.role is AssetRole.GENERATED


def test_asset_crop_rect_and_parts_binding() -> None:
    asset = ProblemAsset(
        path="assets/vq_question.png",
        kind="figure",
        role="question_crop",
        page_index=31,
        crop_rect={"x0": 0, "y0": 400, "x1": 612, "y1": 705},
        parts=["a", "b"],
    )
    assert asset.page_index == 31
    assert asset.crop_rect.x0 == 0
    assert asset.crop_rect.y1 == 705
    assert asset.parts == ["a", "b"]


@pytest.mark.parametrize(
    "path",
    ["", "/etc/passwd", "a\\b", "..", "a/../b", "C:/x.svg", "a//b"],
)
def test_asset_path_invalid(path: str) -> None:
    with pytest.raises(ValidationError):
        ProblemAsset(path=path)


# --- formula role renamed: given / displayed / derived ---
def test_formula_role_values() -> None:
    assert FormulaRole("given") is FormulaRole.GIVEN
    assert FormulaRole("displayed") is FormulaRole.DISPLAYED
    assert FormulaRole("derived") is FormulaRole.DERIVED
    with pytest.raises(ValueError):
        FormulaRole("stated")  # old M0 vocabulary is gone
        FormulaRole("to_derive")


# --- quantity carries value/unit/normalized; note is the extension slot ---
def test_quantity_typed_unit() -> None:
    q = Quantity(value="Vs", unit={"symbol": "V"})
    assert q.value == "Vs"
    assert q.unit.symbol == "V"
    assert q.note is None


# --- observables are source facts, independent of assets ---
def test_observables_independent_of_assets() -> None:
    # source references a figure we could not fetch -> has_circuit_figure true, assets empty
    ir = make_ir(
        assets=[],
        observables={"has_circuit_figure": True, "has_formula": False, "answer_available": False},
    )
    assert ir.observables.has_circuit_figure is True
    assert ir.assets == []


# --- extra='forbid' still enforced on the new contract ---
def test_unknown_field_rejected() -> None:
    with pytest.raises(ValidationError):
        make_ir(extra_field="must be rejected")
