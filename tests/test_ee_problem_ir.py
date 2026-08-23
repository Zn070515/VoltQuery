"""Schema tests for the M1 ``EEProblemIR`` contract (v0.1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from voltquery.contracts import (
    SCHEMA_VERSION,
    Answer,
    AssetKind,
    AssetOrigin,
    AssetRole,
    CropRect,
    EEProblemIR,
    FormulaRole,
    LicenseMetadata,
    ProblemAsset,
    QuantityInput,
    SourceRef,
    TableInput,
)


def make_ir(**overrides):
    """Build a minimal valid ``EEProblemIR`` with a couple of overrides."""
    data = {
        "schema_version": SCHEMA_VERSION,
        "id": "vq_ir_test",
        "source": {"source_id": "fixture-source"},
        "domain": "circuit_theory",
        "topics": ["nodal_analysis"],
        "statement": "Consider the circuit.",
        "parts": None,
        "inputs": [],
        "targets": [],
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


# --- schema_version is a required, literal-pinned contract version ---
def test_schema_version_is_pinned() -> None:
    assert make_ir().schema_version == "v0.1"


def test_schema_version_required() -> None:
    data = make_ir().model_dump()
    del data["schema_version"]
    with pytest.raises(ValidationError):
        EEProblemIR.model_validate(data)


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


def test_part_can_nest_subparts() -> None:
    ir = make_ir(
        parts=[
            {
                "label": "b",
                "statement": "Find the currents.",
                "target": "current through RL",
                "parts": [
                    {"label": "i", "statement": "Only the 12V source.", "target": "I_RL(12V)"},
                    {"label": "ii", "statement": "Only the 5V source.", "target": "I_RL(5V)"},
                ],
            }
        ]
    )
    assert len(ir.parts[0].parts) == 2
    assert ir.parts[0].parts[0].label == "i"
    assert ir.parts[0].parts[1].target == "I_RL(5V)"


# --- answer: open {type, content}, deliberately not a rigid union ---
def test_answer_is_open_type_content() -> None:
    # A real answer can bundle scalar + drawing + explanation; content stays open.
    answer = Answer(
        type="structured",
        content={"scalar": {"Rth": "1 kΩ"}, "drawing_ref": "assets/x.png", "explanation": "..."},
    )
    assert answer.type == "structured"
    assert answer.content["scalar"]["Rth"] == "1 kΩ"


# --- top-level targets capture what the whole problem asks for ---
def test_top_level_targets() -> None:
    ir = make_ir(targets=["equivalent resistance", "source current"])
    assert ir.targets == ["equivalent resistance", "source current"]
    assert make_ir().targets == []


# --- inputs: discriminated union of quantity and table givens ---
def test_input_discriminated_union() -> None:
    ir = make_ir(
        inputs=[
            {"type": "quantity", "name": "Vs", "value": 10, "unit": {"symbol": "V"}},
            {"type": "table", "name": "bias_table", "columns": ["R", "I"],
             "rows": [{"R": "1k", "I": "2mA"}]},
        ]
    )
    assert isinstance(ir.inputs[0], QuantityInput)
    assert isinstance(ir.inputs[1], TableInput)
    assert ir.inputs[0].name == "Vs"
    assert ir.inputs[1].rows[0]["R"] == "1k"


def test_quantity_input_typed_unit() -> None:
    q = QuantityInput(name="Vs", value="Vs", unit={"symbol": "V"})
    assert q.type == "quantity"
    assert q.name == "Vs"
    assert q.value == "Vs"
    assert q.unit.symbol == "V"
    assert q.note is None


def test_quantity_input_dimensionless() -> None:
    # A unitless given uses an empty symbol + no normalized spelling.
    q = QuantityInput(value=100_000, unit={"symbol": ""})
    assert q.unit.symbol == ""
    assert q.unit.normalized is None


def test_table_input_defaults() -> None:
    t = TableInput(name="gain_table")
    assert t.columns == []
    assert t.rows == []
    assert t.type == "table"


# --- role and origin are orthogonal to kind; none repeats another ---
def test_asset_three_axes_orthogonal() -> None:
    src_schematic = ProblemAsset(
        path="assets/vq_schematic.png", kind="schematic",
        role="content_crop", origin="source")
    assert src_schematic.kind is AssetKind.SCHEMATIC
    assert src_schematic.role is AssetRole.CONTENT_CROP
    assert src_schematic.origin is AssetOrigin.SOURCE

    gen_crop = ProblemAsset(
        path="assets/vq_ocr_crop.png", kind="figure",
        role="content_crop", origin="generated")
    assert gen_crop.kind is AssetKind.FIGURE
    assert gen_crop.role is AssetRole.CONTENT_CROP
    assert gen_crop.origin is AssetOrigin.GENERATED

    question = ProblemAsset(
        path="assets/vq_question.png", kind="figure",
        role="question_crop", origin="source")
    assert question.role is AssetRole.QUESTION_CROP


def test_asset_crop_rect_and_parts_binding() -> None:
    asset = ProblemAsset(
        path="assets/vq_question.png",
        kind="figure",
        role="question_crop",
        origin="source",
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


# --- crop rect invariants: positive area, non-negative page origin ---
def test_crop_rect_accepts_valid() -> None:
    r = CropRect(x0=0, y0=400, x1=612, y1=705)
    assert (r.x0, r.x1, r.y0, r.y1) == (0, 612, 400, 705)


@pytest.mark.parametrize(
    "rect",
    [
        {"x0": 10, "y0": 0, "x1": 5, "y1": 20},   # x1 < x0
        {"x0": 0, "y0": 10, "x1": 20, "y1": 5},   # y1 < y0
        {"x0": 0, "y0": 0, "x1": 0, "y1": 5},     # zero width (x1 == x0)
        {"x0": -1, "y0": 0, "x1": 20, "y1": 5},   # negative origin
    ],
)
def test_crop_rect_invariants(rect) -> None:
    with pytest.raises(ValidationError):
        CropRect(**rect)


def test_crop_rect_requires_page() -> None:
    with pytest.raises(ValidationError):
        ProblemAsset(
            path="assets/q.png", role="question_crop",
            crop_rect={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
        )


@pytest.mark.parametrize("val", [float("nan"), float("inf"), float("-inf")])
def test_crop_rect_rejects_non_finite(val) -> None:
    with pytest.raises(ValidationError):
        CropRect(x0=val, y0=0, x1=612, y1=705)


def test_problem_asset_rejects_negative_page() -> None:
    with pytest.raises(ValidationError):
        ProblemAsset(path="assets/q.png", page_index=-1)


def test_source_ref_rejects_negative_page() -> None:
    with pytest.raises(ValidationError):
        SourceRef(source_id="fixture-source", page_index=-1)


# --- license verified=True must carry auditable evidence ---
def test_license_verified_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        LicenseMetadata(verified=True)
    lic = LicenseMetadata(
        verified=True,
        verification_url="https://example.org/license",
        verified_at="2026-08-22",
        verification_note="Verified against the published notice.",
    )
    assert lic.verified is True


# --- formula role renamed: given / displayed / derived ---
def test_formula_role_values() -> None:
    assert FormulaRole("given") is FormulaRole.GIVEN
    assert FormulaRole("displayed") is FormulaRole.DISPLAYED
    assert FormulaRole("derived") is FormulaRole.DERIVED
    with pytest.raises(ValueError):
        FormulaRole("stated")  # old M0 vocabulary is gone


def test_formula_role_rejects_old_to_derive() -> None:
    with pytest.raises(ValueError):
        FormulaRole("to_derive")


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
