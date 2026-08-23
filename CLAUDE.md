# CLAUDE.md

## Project

**VoltQuery** — Electrical Engineering Problem Search & Verifiable Reasoning Engine.

VoltQuery is intended to become a professional problem-search, retrieval, structured understanding, deterministic solving, and verification platform for Electrical Engineering (EE). It is **not** an LLM-first homework-answering wrapper.

Current development stage: **pre-v0.1 / research baseline**.

Primary v0.1 domain:
- Circuit Theory / 电路原理

Probe domain:
- Analog Electronics / 模拟电子技术

Long-term domains may include:
- Circuit Theory
- Analog Electronics
- Digital Electronics
- Signals and Systems
- Automatic Control
- Power Electronics
- Electrical Machines
- Power Systems
- Electromagnetics
- RF / Microwave
- Embedded / Digital Systems

---

## Core Product Principle

The system priority is:

> **Search First. Verify Always. Solve When Supported. Explain Last.**

A retrieved answer with explicit provenance is preferred over a newly generated answer.

Never present model-generated content as a retrieved source.

Never present an unverified result as verified.

Never silently convert uncertainty into confidence.

---

## Current Milestone

The current milestone is:

> **M2 — Document → Problem Ingestion**

M0 is complete (40-problem public Gold corpus: 32 Circuit Theory / 8 Analog
Electronics, license-verified, validated by `milestone m0`).

M1 — `EEProblemIR` v0.1 — is complete and **frozen**:
1. `EEProblemIR` v0.1 contract with explicit `schema_version = "v0.1"`.
2. A derived `benchmarks/seed/problem_ir.jsonl` — one record per seed, holding
   the seed's identity fields plus structure: `parts`, typed `inputs`
   (quantity/table), three-axis `assets` (kind × role × origin), `targets`,
   and `formulas`.
3. A strict parity guarantee: `voltquery ir validate` enforces one-to-one id
   parity with the seed corpus and per-record agreement on source / domain /
   topics / verbatim statement / multipart shape / source facts / document refs.
4. `answer` stays `None` by convention — `answer_available` is a source fact
   (observable). Capturing the source's own answer / worked-solution text is a
   deferred M2 (Document → Problem) ingestion concern. Deterministic solving is a
   v0.3 concern and is not part of M2.

Do **not** start M2 work before this milestone banner is honored: M2 is now the
current milestone, so M2 development may begin. M2 excludes OCR/search/solver
work beyond Document → Problem ingestion; solving remains a v0.3 concern.

---

## License

VoltQuery's own code is MIT (see `LICENSE`). Per-source corpus documents are
licensed independently via `data/sources.yaml` (predominantly CC-BY) and the two
are never conflated: the MIT code license does not re-license any source material.

---

## Python and Tooling

Target Python:

```text
Python >=3.12,<3.13
```

Preferred package/environment manager:
- `uv`

Preferred project layout:
- `src/` layout
- `pytest`
- `ruff`
- `mypy`

Recommended baseline:

```toml
requires-python = ">=3.12,<3.13"
```

Heavy dependencies must remain optional or adapter-scoped whenever possible.

Do not make `voltquery-core` depend directly on every OCR / ML / simulation runtime.

---

## Engineering Rules

### 1. Contract-first, not implementation-first

Public interfaces and intermediate representations must be explicitly defined.

Avoid undocumented dictionaries such as:

```python
data = {"foo": ..., "bar": ...}
```

for cross-module contracts.

Prefer typed models and explicit enums.

Initial contract families are expected to become:

- `SourceRef`
- `SeedProblemRecord`
- `EEProblem`
- `MathIR`
- `CircuitIR`
- `DiagramIR`
- `RetrievalResult`
- `VerificationRecord`

Do not prematurely freeze final `EEProblemIR` before the seed corpus has been studied.

---

### 2. Adapters around replaceable dependencies

OCR, embedding, reranking, vision, simulation, and model runtimes are replaceable.

Code should depend on interfaces such as:

```python
FormulaRecognizer
DocumentParser
TextEmbedder
Reranker
CircuitSolver
Verifier
```

not directly on one vendor/model throughout the codebase.

---

### 3. Provenance is mandatory

Every indexed problem must preserve traceable source metadata.

At minimum:

- source ID
- title/document
- page or logical location when available
- problem identifier when available
- original source URL when applicable
- license metadata
- import timestamp/version
- asset reference

No indexed public corpus item without known provenance.

---

### 4. License metadata is data, not documentation

License information belongs in machine-readable source metadata.

For each source, track when known:

```yaml
license:
  id:
  redistribution:
  derivatives:
  commercial:
  attribution_required:
```

Do not assume that "available online" means redistributable.

Research-only and redistributable corpora must remain separable.

---

### 5. Evaluation before optimization

Every major capability must have a benchmark before optimization work begins.

Examples:

- retrieval → Recall@1 / Recall@5 / MRR / nDCG
- formula parsing → parse success / canonical-equivalence success
- circuit recognition → component / connection / topology metrics
- solver → supported-domain correctness
- verification → false-confidence rate

Do not justify a model change with subjective impressions when a measurable test is possible.

---

### 6. Failure is a first-class result

Supported result states should eventually include:

- `VERIFIED`
- `PARTIALLY_VERIFIED`
- `UNVERIFIED`
- `UNSUPPORTED`
- `CONFLICT`

Returning `UNSUPPORTED` is better than fabricating an answer.

---

### 7. LLMs are planners/explainers, not the source of truth

An LLM may eventually help with:

- semantic extraction
- query rewriting
- problem classification
- solver routing
- explanation
- ambiguity resolution

An LLM must not replace:

- source provenance
- deterministic retrieval
- unit validation
- symbolic verification
- circuit simulation
- exact graph checks

when those mechanisms are available.

---

## v0.1 Non-goals

Do not allow scope creep into:

- full automatic understanding of arbitrary schematics
- universal EE solving
- nationwide/public commercial problem bank
- native Android/iOS application
- cloud SaaS
- social/community features
- user accounts
- full LLM tutor
- custom OCR training
- custom MNA implementation
- broad circuit simulation engine

These are later-stage capabilities.

---

## Initial Data Strategy

Current development must use open/publicly usable material.

Priority source categories:

1. Open EE worksheets and textbooks with clear licenses.
2. Public research benchmarks.
3. Research-only datasets kept separate when redistribution is restricted.

Initial seed target:

```text
40 manually reviewed problems
```

Suggested distribution:

```text
Circuit Theory:       32
Analog Electronics:    8
```

Suggested Circuit Theory coverage:

- Ohm's law
- series / parallel
- KCL / KVL
- node / mesh analysis
- Thevenin / Norton
- capacitor / inductor
- AC / impedance / phasor

Suggested Analog probe coverage:

- diode
- BJT
- MOSFET
- op-amp

---

## Development Sequence

Follow this order unless an explicit decision changes it:

```text
M0  Seed Corpus + Benchmark Contract
M1  EEProblemIR v0.1
M2  Document → Problem ingestion
M3  Text retrieval baseline
M4  Hybrid retrieval + reranking
M5  Formula-aware retrieval
M6  Visual retrieval
------------------------------------
v0.1 Open EE Search Prototype
------------------------------------
v0.2 CircuitIR + topology extraction
v0.3 Circuit solver + verifier
v0.4 Larger knowledge/retrieval system
v0.5 Mobile/PWA client
v0.6 Signals & Systems + Control
v0.7 Analog/Digital expansion
v0.8 Personalized learning
v0.9 Public/shared corpus governance
v1.0 Stable EE search platform
```

---

## Code Review Checklist

Before accepting a change, check:

1. Does it respect current milestone scope?
2. Does it add a dependency that should be behind an adapter?
3. Does it preserve provenance?
4. Does it preserve license metadata?
5. Does it introduce an untyped cross-module contract?
6. Is there an automated test?
7. If behavior changed, is there a benchmark or regression case?
8. Does it distinguish unsupported/unverified from verified?
9. Does it make future mobile/server separation harder?
10. Is the implementation simpler than the problem requires?

---

## Preferred Development Style

- Small, reviewable commits.
- Strong type boundaries.
- Tests near contracts.
- Explicit failure modes.
- Reproducible experiments.
- No silent fallback.
- No hidden network calls.
- No model download at import time.
- No heavy runtime initialization at module import time.
- No premature microservices.
- No premature distributed architecture.
- On every push, report the actual remote CI status (the GitHub Actions run
  result), not just local gate results. Treat a commit's own claim of "passing"
  as unverified until the Actions run is observed.

VoltQuery should begin as a well-structured local application/library and earn complexity only when real usage requires it.

---

## Guiding Statement

VoltQuery should eventually answer:

> "What problem is this, where did it come from, what electrical-engineering structure does it contain, can we solve it with a trusted tool, and can we verify the result?"

Every major architectural decision should move the project closer to answering that question reliably.
