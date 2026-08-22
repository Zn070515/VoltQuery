"""Contract enums for the VoltQuery M0 seed corpus."""

from __future__ import annotations

from enum import Enum


class DataPolicy(str, Enum):
    """Distribution policy owned by a data source."""

    PUBLIC_REDISTRIBUTABLE = "public_redistributable"
    RESEARCH_ONLY = "research_only"
    PRIVATE_LOCAL = "private_local"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    """Electrical-engineering domains targeted by VoltQuery."""

    CIRCUIT_THEORY = "circuit_theory"
    ANALOG_ELECTRONICS = "analog_electronics"


class SourceStatus(str, Enum):
    """Lifecycle status of a registered source."""

    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"


class AssetKind(str, Enum):
    """Kind of local asset referenced by a seed problem."""

    FIGURE = "figure"
    FORMULA = "formula"
    SCHEMATIC = "schematic"
    OTHER = "other"


class Topic(str, Enum):
    """Controlled topic vocabulary for seed problems.

    Intentionally an open vocabulary that grows as the seed corpus reveals
    what EEProblemIR must represent. Not frozen yet.
    """

    # Circuit Theory
    OHM_LAW = "ohm_law"
    SERIES_PARALLEL = "series_parallel"
    KCL = "kcl"
    KVL = "kvl"
    NODE_VOLTAGE = "node_voltage"
    MESH_CURRENT = "mesh_current"
    THEVENIN = "thevenin"
    NORTON = "norton"
    SUPERPOSITION = "superposition"
    RC = "rc"
    RL = "rl"
    AC_PHASOR = "ac_phasor"
    IMPEDANCE = "impedance"

    # Analog probe
    DIODE = "diode"
    BJT = "bjt"
    MOSFET = "mosfet"
    OPAMP = "opamp"
