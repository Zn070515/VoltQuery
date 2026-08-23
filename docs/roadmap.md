# VoltQuery Roadmap

## Roadmap Philosophy

VoltQuery should evolve by removing one technical risk at a time.

Do not develop all modalities simultaneously.

Do not train custom models before a benchmark shows a real need.

Do not build a mobile application before the core retrieval system is useful.

Do not introduce a general LLM dependency before deterministic baselines exist.

---

# Pre-v0.1 Research Milestones

> **Current milestone: M1 — EEProblemIR v0.1.** M0 (Seed Corpus + Benchmark
> Contract) is complete; the M1 IR schema, its 40-record `problem_ir.jsonl`
> projection, and the `voltquery ir validate` parity gate are in place.

## M0 — Seed Corpus + Benchmark Contract

### Goal

Create the first trustworthy EE dataset owned and understood by the project.

### Scope

- initialize repository and Python package
- define source registry
- define machine-readable license metadata
- manually select 40 seed problems
- preserve source provenance
- build the first benchmark format
- write validation tests
- document observations from real EE problems

### Suggested seed composition

```text
Circuit Theory:       32
Analog Electronics:    8
```

### Output

- `data/sources.yaml`
- `benchmarks/seed/problems.jsonl`
- benchmark assets
- source/license tests
- `docs/development/SEED_CORPUS_FINDINGS.md`

### Exit condition

No final `EEProblemIR` is frozen until seed findings exist.

---

## M1 — EEProblemIR v0.1

### Goal

Define the first stable representation of an EE problem.

### Initial concepts

- source
- prompt
- parts
- text blocks
- formulas
- figures
- domain
- topics
- givens
- targets
- answer metadata
- future circuit/diagram extension points

### Requirements

- typed
- versioned
- serializable
- source-preserving
- backward-compatible within v0.x where practical

### Exit condition

All seed problems can be represented without ad-hoc escape fields.

---

## M2 — Document → Problem Ingestion

### Goal

Convert supported open documents into problem candidates.

### Initial scope

- PDF ingestion
- page extraction
- problem segmentation
- text extraction/OCR
- figure preservation
- source coordinates/page preservation

### Explicit non-goals

- perfect circuit understanding
- perfect formula semantics
- universal document parsing

### Evaluation

Measure:
- problem segmentation accuracy
- missing/merged problem rate
- text quality
- figure retention
- provenance retention

---

## M3 — Text Retrieval Baseline

### Goal

Prove that VoltQuery can retrieve an exact or near-duplicate problem.

### Baseline

- normalized text
- sparse search / BM25
- dense embedding
- Top-K retrieval

### Required metrics

- Recall@1
- Recall@5
- MRR
- query latency

### Exit condition

The system has a reproducible baseline before adding formula or image signals.

---

## M4 — Hybrid Retrieval + Reranking

### Goal

Improve retrieval robustness for paraphrases, OCR noise, and cross-language queries.

### Capabilities

- sparse + dense candidate generation
- fusion
- reranker
- configurable scoring

### Evaluation

Ablation comparison against M3.

---

## M5 — Formula-aware Retrieval

### Goal

Use mathematical structure as an independent retrieval signal.

### Pipeline

```text
formula image/text
→ LaTeX
→ normalization
→ mathematical parse
→ canonical structure
→ formula fingerprint / similarity
```

### Candidate tools

Replaceable adapters around:
- formula OCR
- LaTeX parser
- SymPy-based normalization

### Evaluation

Measure incremental retrieval gain on:
- same formula, different formatting
- equivalent expression
- formula-heavy questions
- OCR-damaged formulas

---

## M6 — Visual Retrieval

### Goal

Use page/circuit visual information without requiring perfect circuit parsing.

### Scope

- circuit/figure crop
- visual embedding
- visual candidate retrieval
- multimodal fusion

### Evaluation

Test:
- text-poor problems
- circuit-heavy questions
- layout changes
- screenshots
- perspective/blur/shadow variants

---

# v0.1.0 — Open EE Search Prototype

## Product Goal

A local Electrical Engineering problem-search prototype built on open/research-safe material.

Primary domain:
- Circuit Theory

Probe domain:
- Analog Electronics

## Capabilities

- import supported documents
- convert content into indexed problems
- preserve source provenance
- search by screenshot/text
- sparse+dense hybrid retrieval
- reranking
- formula-aware retrieval
- basic visual retrieval
- benchmark CLI
- exact / near / similar candidate display

## Explicit Non-goals

- full automatic circuit-netlist understanding
- general EE solver
- mobile native app
- public cloud product
- public nationwide problem bank
- AI tutor

---

# v0.2 — CircuitIR + Topology

## Goal

Understand circuit diagrams as electrical structures.

## New capabilities

- component detection
- wire extraction
- junction/crossing handling
- label association
- node clustering
- circuit graph representation
- netlist generation for supported diagrams
- topology-aware retrieval
- graph fingerprints

## Evaluation

Separate metrics for:
- component detection
- label-value binding
- node recovery
- edge recovery
- complete topology match
- netlist validity

---

# v0.3 — Circuit Solver + Verifier

## Goal

Turn supported CircuitIR problems into deterministically checked answers.

## Candidate backends

- SymPy
- Lcapy
- ngspice

## Supported direction

- KCL / KVL
- node voltage
- mesh current
- Thevenin / Norton
- superposition
- RC / RL / RLC
- phasor / impedance
- controlled-source linear networks
- basic state-space

## Verification

Possible checks:
- units
- symbolic equivalence
- numerical substitution
- Lcapy result
- ngspice result
- backend consistency
- initial/final conditions

---

# v0.4 — Knowledge and Retrieval Expansion

## Goal

Scale corpus quality and search intelligence.

## Capabilities

- larger corpus
- structured concepts
- course/chapter taxonomy
- method taxonomy
- knowledge graph foundations
- formula fingerprints
- circuit fingerprints
- problem deduplication
- cross-document source linking
- solution quality metadata

---

# v0.5 — Mobile / PWA Client

## Goal

Make photo-based search convenient.

## Responsibilities

Mobile:
- camera
- crop
- rectify
- lightweight preprocessing/OCR where useful
- upload/query
- display source and results

Backend/local workstation:
- heavy retrieval
- reranking
- solver
- simulation
- larger models

Possible technologies:
- PWA
- ONNX Runtime Web
- Android/iOS with ONNX Runtime Mobile
- ExecuTorch when justified

---

# v0.6 — Signals & Systems + Automatic Control

## Goal

Add domains that reuse the mathematical foundation.

## New structures

- signal
- system
- transfer function
- state-space
- poles/zeros
- frequency response
- time response

## Candidate backend

- python-control
- SymPy
- numerical backend

---

# v0.7 — Analog + Digital Expansion

## Analog

- diode
- BJT
- MOSFET
- operating point
- device region
- small-signal model
- op-amp
- nonlinear/device assumptions
- SPICE-assisted verification

## Digital

- Boolean expressions
- truth tables
- Karnaugh maps
- FSM
- timing diagrams
- exhaustive verification where possible

---

# v0.8 — Personal Learning System

## Goal

Move beyond one-shot search.

Potential features:
- wrong-answer notebook
- concept mastery
- weak-area analysis
- similar-problem recommendations
- review scheduling
- problem clustering
- personal course corpus
- private local materials

---

# v0.9 — Shared/Public Corpus Governance

## Goal

Prepare for multi-user/public data.

Potential capabilities:
- accounts
- sync
- shared problem packs
- contribution workflow
- moderation
- copyright/license workflow
- deduplication
- corpus versioning
- takedown procedures

Do not implement until the local/core product is proven.

---

# v1.0 — Stable EE Search Platform

## Definition

VoltQuery v1.0 is not "supports every EE course."

It is the first stable release suitable for regular student use.

Expected maturity example:

```text
Circuit Theory          A
Signals & Systems       A-
Automatic Control       A-
Analog Electronics      B
Digital Electronics     B
```

Where:

```text
A  = retrieval + structured understanding + solver + verifier
B  = retrieval + partial structured understanding + limited solver
```

## v1.0 requirements

- stable data contracts
- stable provenance
- reproducible benchmarks
- low false-confidence rate
- robust retrieval
- reliable failure states
- documented plugin/backend boundaries
- mobile/web usable surface
- tested upgrade/migration path

---

# Post-v1.0

Potential staged domain expansion:

- v1.1 Power Electronics
- v1.2 Electrical Machines
- v1.3 Power Systems
- v1.4 Electromagnetics
- v1.5 RF / Microwave
- v1.6 Embedded / Digital Systems
- v1.7 EDA / PCB workflows

Each domain should add its own:
- IR extensions
- taxonomy
- solver adapters
- verification rules
- benchmark
