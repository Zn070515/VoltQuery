# VoltQuery Version Features and Acceptance Criteria

This document defines the expected user-visible capability and engineering acceptance criteria for major VoltQuery versions.

Acceptance criteria are project targets. They may be adjusted after the first reproducible benchmark establishes realistic baselines.

---

# M0 — Seed Corpus + Benchmark Contract

Status: **complete** (40 / 32 / 8; `milestone m0` GREEN).

## Features

- repository initialized
- Python 3.12 project
- source registry
- explicit license metadata
- 40 manually checked seed problems
- benchmark dataset format
- seed asset references
- schema validation tests

## Acceptance Criteria

- [x] `requires-python = ">=3.12,<3.13"`
- [x] at least 3 registered sources
- [x] every source has license/provenance metadata
- [x] 40 seed problems exist
- [x] at least 32 Circuit Theory problems
- [x] at least 8 Analog Electronics probe problems
- [x] all problem IDs are unique
- [x] every problem resolves to a registered source
- [x] every referenced local asset exists
- [x] problem records load through typed validation
- [x] seed corpus includes text-only, formula, circuit-figure, and multipart forms
- [x] findings document records schema implications and observed edge cases

---

# M1 — EEProblemIR v0.1

Status: **in progress** (schema, corpus projection, and parity gate in place;
`answer` population deferred to M2).

## Features

- typed EE problem schema
- source references
- problem parts
- formulas
- figures
- domain/topic tags
- givens/targets extension points
- serialization

## Acceptance Criteria

- [x] 100% of seed problems can be represented
- [x] no seed problem requires an untyped "misc" catch-all for essential semantics
- [x] schema round-trip serialization test passes
- [x] schema version is explicit
- [x] source provenance survives serialization
- [x] backwards-compatibility policy documented

---

# M2 — Document → Problem

## Features

- document ingestion adapter
- page-level source preservation
- problem segmentation
- text extraction/OCR
- figure retention
- Problem candidate creation

## Acceptance Criteria

Initial target on curated validation documents:

- [ ] problem boundary F1 is measured
- [ ] figure retention rate is measured
- [ ] provenance retention is 100%
- [ ] parser errors are structured
- [ ] no silent page drop
- [ ] original document and page can always be traced from a generated problem

Target thresholds after baseline:
- problem segmentation F1: ≥ 0.95 on supported layouts
- figure retention: ≥ 0.98 on supported layouts

---

# M3 — Text Retrieval Baseline

## Features

- text normalization
- sparse retrieval
- dense retrieval
- Top-K results
- evaluation CLI

## Acceptance Criteria

On seed-derived benchmark:

- [ ] Recall@1 reported
- [ ] Recall@5 reported
- [ ] MRR reported
- [ ] p50/p95 search latency reported
- [ ] results reproducible from a clean environment

Provisional targets:
- exact/near-duplicate Recall@1 ≥ 0.90
- exact/near-duplicate Recall@5 ≥ 0.98

---

# M4 — Hybrid Retrieval + Reranking

## Features

- sparse+dense fusion
- reranker
- configurable retrieval pipeline
- ablation report

## Acceptance Criteria

- [ ] hybrid pipeline outperforms or matches M3 on Recall@1
- [ ] no material regression on Recall@5
- [ ] OCR-noise subset improves
- [ ] paraphrase subset improves
- [ ] cross-language subset is measured
- [ ] ablation identifies contribution of fusion/reranking

---

# M5 — Formula-aware Retrieval

## Features

- formula extraction input contract
- LaTeX normalization
- math parse adapter
- canonical representation
- formula similarity/fingerprint
- retrieval fusion

## Acceptance Criteria

- [ ] supported formula parse success ≥ 0.95
- [ ] formatting-only formula variants map to equivalent canonical form
- [ ] formula-heavy retrieval subset improves over M4
- [ ] parser failures are explicit and do not crash search
- [ ] untrusted input is never executed directly

---

# M6 — Visual Retrieval

## Features

- image/circuit crop representation
- visual embedding
- visual search
- multimodal fusion

## Acceptance Criteria

- [ ] visual-only subset is measurable
- [ ] circuit-heavy subset improves over M5
- [ ] synthetic phone degradation benchmark exists
- [ ] perspective/blur/shadow variants are evaluated
- [ ] visual model can be replaced through an adapter

---

# v0.1.0 — Open EE Search Prototype

## User Features

- import supported EE documents
- build a local problem index
- search from text
- search from screenshot/image
- return Top-K problems
- show source/document/page
- distinguish exact / near / similar candidates
- formula-aware matching
- basic visual matching
- reproducible benchmark command

## Engineering Acceptance Criteria

### Retrieval

Provisional targets:

- [ ] exact/near-duplicate Recall@1 ≥ 0.95
- [ ] exact/near-duplicate Recall@5 ≥ 0.99
- [ ] match-classification accuracy ≥ 0.95
- [ ] indexed public answers have 100% provenance

### Reliability

- [ ] retrieved result and generated/calculated result are visibly distinguishable
- [ ] no unknown-source content is labeled as retrieved evidence
- [ ] failures use structured error states
- [ ] no hidden external network requirement for baseline local search

### Performance

On the primary development workstation:

- [ ] pure indexed search p95 target < 2 seconds
- [ ] repeated query does not trigger unnecessary model reload
- [ ] indexing and search runtime are separately measurable

### Quality

- [ ] automated tests cover contracts
- [ ] benchmark is versioned
- [ ] dependency/licenses documented
- [ ] no required custom-trained model

---

# v0.2 — CircuitIR + Topology

## User Features

- detect supported circuit components
- recover circuit connectivity
- produce inspectable circuit graph
- topology-aware matching
- netlist export for supported cases

## Acceptance Criteria

Metrics must be reported separately:

- [ ] component detection precision/recall
- [ ] label/value association accuracy
- [ ] junction/crossing classification
- [ ] node recovery F1
- [ ] edge recovery F1
- [ ] complete topology exact-match rate
- [ ] generated netlist validity rate

Safety requirement:

- [ ] uncertain topology must not be silently accepted as certain

---

# v0.3 — Circuit Solver + Verifier

## User Features

For supported Circuit Theory problems:
- solve selected linear circuits
- show deterministic calculation path
- check units
- run symbolic/numerical verification
- report verification status

## Acceptance Criteria

Within explicitly supported domain:

- [ ] solver correctness ≥ 0.95
- [ ] unit check runs for 100% of solver outputs
- [ ] unsupported-domain false-solve rate approaches 0
- [ ] backend disagreement produces `CONFLICT`
- [ ] verifier status is never inferred solely from LLM confidence
- [ ] source/solver/verification evidence is inspectable

Target result states:

```text
VERIFIED
PARTIALLY_VERIFIED
UNVERIFIED
UNSUPPORTED
CONFLICT
```

---

# v0.4 — Knowledge / Corpus Expansion

## User Features

- larger corpus
- concept/topic browsing
- problem deduplication
- cross-source related problems
- structured course taxonomy

## Acceptance Criteria

- [ ] corpus import is reproducible
- [ ] duplicate detection benchmark exists
- [ ] every public corpus item has machine-readable source/license metadata
- [ ] research-only sources remain separable from redistributable sources
- [ ] concept taxonomy is versioned

---

# v0.5 — Mobile / PWA

## User Features

- take photo
- crop/rectify
- submit query
- browse matches
- view sources
- optionally run lightweight local recognition

## Acceptance Criteria

- [ ] mobile client does not require full desktop ML stack
- [ ] camera-to-results happy path is tested
- [ ] low-connectivity/error state is explicit
- [ ] model/runtime downloads are user-visible
- [ ] no heavy model initializes before needed

---

# v0.6 — Signals & Control

## User Features

- transfer-function problems
- state-space problems
- time/frequency response
- pole/zero analysis
- control-related search and selected solving

## Acceptance Criteria

- [ ] domain-specific benchmark exists
- [ ] IR extensions are versioned
- [ ] solver adapter is isolated
- [ ] numerical/symbolic results can be cross-checked where possible
- [ ] Circuit Theory behavior does not regress

---

# v0.7 — Analog / Digital

## Analog Acceptance Direction

- [ ] model assumptions are represented explicitly
- [ ] device operating region is represented where relevant
- [ ] solver does not hide model choice
- [ ] SPICE-assisted checks available for supported circuits

## Digital Acceptance Direction

- [ ] Boolean expressions have structured IR
- [ ] truth-table generation is deterministic
- [ ] exhaustive verification available for bounded problems
- [ ] FSM/timing support has independent benchmarks

---

# v0.8 — Personal Learning

## User Features

- wrong-problem notebook
- personal corpus
- concept weakness tracking
- related problem recommendation
- study history

## Acceptance Criteria

- [ ] recommendation evidence is inspectable
- [ ] learning analytics derive from structured concepts, not only embeddings
- [ ] private user corpus remains logically separate from public corpus
- [ ] deletion/export paths exist for personal data

---

# v0.9 — Shared/Public Corpus

## Acceptance Criteria

Before release:

- [ ] copyright/license workflow documented
- [ ] corpus provenance complete
- [ ] contribution moderation exists
- [ ] duplicate management exists
- [ ] takedown/removal procedure exists
- [ ] shared/private visibility is explicit

---

# v1.0 — Stable EE Search Platform

## Product Acceptance

- [ ] Circuit Theory production-grade retrieval
- [ ] at least one domain has mature structured solving + verification
- [ ] mobile/web usable search surface
- [ ] stable public contracts
- [ ] migration policy
- [ ] reproducible benchmark suite
- [ ] source/provenance UX
- [ ] reliable unsupported/unverified behavior

## Reliability Targets

Targets should be frozen from empirical v0.x data, but v1.0 should explicitly track:

- Reliable Answer Rate
- False Confidence Rate
- Recall@1
- Recall@5
- solver correctness
- verification coverage
- unsupported detection accuracy
- p95 latency
- crash/error rate

A v1.0 release is blocked by unacceptably high false-confidence behavior even if raw answer accuracy is high.
