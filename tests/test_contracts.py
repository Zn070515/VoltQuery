"""Tests for the contract models and enums."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from voltquery.contracts import (
    AssetRef,
    DataPolicy,
    Domain,
    LicenseMetadata,
    SeedProblemRecord,
)


def test_domain_enum_values() -> None:
    assert Domain("circuit_theory") is Domain.CIRCUIT_THEORY
    assert Domain("analog_electronics") is Domain.ANALOG_ELECTRONICS


def test_license_defaults_are_restrictive() -> None:
    license_meta = LicenseMetadata()
    assert license_meta.id == "UNKNOWN"
    assert license_meta.data_policy is DataPolicy.UNKNOWN
    assert license_meta.verified is False


def test_seed_record_round_trip() -> None:
    record = SeedProblemRecord(
        id="vq_seed_0001",
        source={"source_id": "fixture-source", "page": 1},
        domain="circuit_theory",
        topics=["ohm_law"],
        question_text="[fixture] round trip",
        has_formula=True,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=True,
        assets=[],
    )
    restored = SeedProblemRecord.model_validate(record.model_dump())
    assert restored == record


def test_unknown_field_rejected() -> None:
    with pytest.raises(ValidationError):
        SeedProblemRecord.model_validate(
            {
                "id": "vq_seed_x",
                "source": {"source_id": "fixture-source"},
                "domain": "circuit_theory",
                "topics": ["ohm_law"],
                "question_text": "[fixture] unknown field",
                "has_formula": False,
                "has_circuit_figure": False,
                "is_multipart": False,
                "answer_available": False,
                "assets": [],
                "extra_field": "must be rejected",
            }
        )


def test_open_topic_slug_accepted() -> None:
    record = SeedProblemRecord(
        id="vq_seed_topic",
        source={"source_id": "fixture-source"},
        domain="circuit_theory",
        topics=["ohm_law", "thevenin", "a1_test"],
        question_text="[fixture] open topic slugs",
        has_formula=False,
        has_circuit_figure=False,
        is_multipart=False,
        answer_available=False,
        assets=[],
    )
    assert record.topics == ["ohm_law", "thevenin", "a1_test"]


@pytest.mark.parametrize(
    "slug",
    ["Ohm_law", "1abc", "kcl-2", "", "node voltage", "a..b"],
)
def test_invalid_topic_slug_rejected(slug: str) -> None:
    with pytest.raises(ValidationError):
        SeedProblemRecord(
            id="vq_seed_slug",
            source={"source_id": "fixture-source"},
            domain="circuit_theory",
            topics=[slug],
            question_text="[fixture] invalid slug",
            has_formula=False,
            has_circuit_figure=False,
            is_multipart=False,
            answer_available=False,
            assets=[],
        )


def test_asset_path_valid() -> None:
    asset = AssetRef(path="assets/figure.svg")
    assert asset.path == "assets/figure.svg"


@pytest.mark.parametrize(
    "path",
    ["", "/etc/passwd", "a\\b", "..", "a/../b", "C:/x.svg", "a//b"],
)
def test_asset_path_invalid(path: str) -> None:
    with pytest.raises(ValidationError):
        AssetRef(path=path)
