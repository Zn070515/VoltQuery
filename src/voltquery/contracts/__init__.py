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
from .ingest import CANDIDATE_SCHEMA_VERSION, ParserProvenance, ProblemCandidate, SourceBlock
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
    "CANDIDATE_SCHEMA_VERSION",
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
    "ParserProvenance",
    "Part",
    "ProblemAsset",
    "ProblemCandidate",
    "ProblemObservables",
    "QuantityInput",
    "SeedProblemRecord",
    "Source",
    "SourceBlock",
    "SourceRef",
    "SourceStatus",
    "TableInput",
    "TOPIC_SLUG_PATTERN",
    "TopicSlug",
    "Unit",
]
