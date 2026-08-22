"""Typed contracts for VoltQuery. M0 supply the seed-corpus / provenance
contracts; the M1 additions supply ``EEProblemIR``."""

from ._base import ContractModel
from .document import DocumentRef
from .enums import (
    AssetKind,
    AssetRole,
    DataPolicy,
    Domain,
    FormulaLayout,
    FormulaRole,
    SourceStatus,
)
from .license import LicenseMetadata
from .problem import (
    Answer,
    CropRect,
    EEProblemIR,
    Formula,
    Part,
    ProblemAsset,
    ProblemObservables,
    Quantity,
    Unit,
)
from .seed import TOPIC_SLUG_PATTERN, AssetRef, SeedProblemRecord, TopicSlug
from .source import Source, SourceRef

__all__ = [
    "Answer",
    "AssetKind",
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
    "LicenseMetadata",
    "Part",
    "ProblemAsset",
    "ProblemObservables",
    "Quantity",
    "SeedProblemRecord",
    "Source",
    "SourceRef",
    "SourceStatus",
    "TOPIC_SLUG_PATTERN",
    "TopicSlug",
    "Unit",
]
