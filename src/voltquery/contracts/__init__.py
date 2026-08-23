"""Typed contracts for VoltQuery. M0 supply the seed-corpus / provenance
contracts; the M1 additions supply ``EEProblemIR``."""

from ._base import ContractModel
from .document import DocumentRef
from .enums import (
    AssetKind,
    AssetOrigin,
    AssetRole,
    DataPolicy,
    Domain,
    FormulaLayout,
    FormulaRole,
    SourceStatus,
)
from .license import LicenseMetadata
from .problem import (
    SCHEMA_VERSION,
    Answer,
    CropRect,
    EEProblemIR,
    Formula,
    Input,
    Part,
    ProblemAsset,
    ProblemObservables,
    QuantityInput,
    TableInput,
    Unit,
)
from .seed import TOPIC_SLUG_PATTERN, AssetRef, SeedProblemRecord, TopicSlug
from .source import Source, SourceRef

__all__ = [
    "SCHEMA_VERSION",
    "Answer",
    "AssetKind",
    "AssetOrigin",
    "AssetRef",
    "AssetRole",
    "ContractModel",
    "CropRect",
    "DataPolicy",
    "DocumentRef",
    "Domain",
    "EEProblemIR",
    "Formula",
    "FormulaLayout",
    "FormulaRole",
    "Input",
    "LicenseMetadata",
    "Part",
    "ProblemAsset",
    "ProblemObservables",
    "QuantityInput",
    "SeedProblemRecord",
    "Source",
    "SourceRef",
    "SourceStatus",
    "TableInput",
    "TOPIC_SLUG_PATTERN",
    "TopicSlug",
    "Unit",
]
