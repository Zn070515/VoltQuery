"""Shared pytest fixtures for VoltQuery tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def fixture_sources_path() -> Path:
    return FIXTURES / "sources.yaml"


@pytest.fixture
def fixture_corpus_path() -> Path:
    return FIXTURES / "problems.jsonl"


@pytest.fixture
def fixture_documents_path() -> Path:
    return FIXTURES / "documents.yaml"


@pytest.fixture
def fixture_assets_root() -> Path:
    return FIXTURES
