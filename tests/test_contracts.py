"""Tests for the contract models and enums."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from voltquery.contracts import DataPolicy, Domain, LicenseMetadata, SeedProblemRecord, Topic


def test_domain_enum_values() -> None:
    assert Domain("circuit_theory") is Domain.CIRCUIT_THEORY
    assert Domain("analog_electronics") is Domain.ANALOG_ELECTRONICS


def test_topic_enum_accepts_known_values() -> None:
    assert Topic("kcl") is Topic.KCL
    assert Topic("opamp") is Topic.OPAMP


def test_topic_enum_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        Topic("definitely_not_a_topic")


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


def test_unknown_topic_rejected_in_record() -> None:
    with pytest.raises(ValidationError):
        SeedProblemRecord(
            id="vq_seed_x",
            source={"source_id": "fixture-source"},
            domain="circuit_theory",
            topics=["not_a_real_topic"],
            question_text="[fixture] invalid topic",
            has_formula=False,
            has_circuit_figure=False,
            is_multipart=False,
            answer_available=False,
            assets=[],
        )
