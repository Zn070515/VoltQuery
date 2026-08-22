# VoltQuery Architecture Principles

## 1. The Center of the System Is Not the Model

VoltQuery is organized around stable contracts and EE semantics.

Replaceable:
- OCR model
- embedding model
- reranker
- vision model
- LLM
- circuit solver backend
- simulation backend

Owned by VoltQuery:
- source/provenance contract
- problem contract
- mathematical/circuit intermediate representations
- retrieval orchestration
- verification protocol
- evaluation methodology

---

## 2. Intended High-level Architecture

```text
                     Inputs
              ┌────────┼─────────┐
              │        │         │
            Image     PDF       Text
              │        │         │
              └────────┼─────────┘
                       ▼
                    Ingest
                       │
                       ▼
                  EEProblemIR
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
       Retrieval                 Solver
           │                       │
           ▼                       ▼
       Evidence                Candidate
           └───────────┬───────────┘
                       ▼
                  Verification
                       │
                       ▼
                Final Result
```

---

## 3. Future IR Stack

```text
EEProblemIR
├─ TextIR
├─ MathIR
├─ DiagramIR
│  ├─ CircuitIR
│  ├─ WaveformIR
│  ├─ BlockDiagramIR
│  └─ future diagram types
├─ SourceRef
├─ Quantity / Unit
├─ Target
└─ VerificationRecord
```

Do not implement all of this at once.

The seed corpus determines which pieces are required first.

---

## 4. Retrieval Should Be Multi-signal

Long-term candidate scoring may combine:

```text
Sparse text
Dense semantic
Formula structure
Formula semantics
Visual similarity
Circuit topology
Metadata
```

Conceptually:

```text
Score =
  wt * text
+ wf * formula
+ wv * vision
+ wc * circuit
+ wm * metadata
```

Do not hard-code this equation as a permanent API.

Treat signals as composable retrieval features.

---

## 5. Search Is Distinct from Solve

Retrieval result:

```text
"This problem matches source X, page Y."
```

Solver result:

```text
"Given interpreted inputs, solver backend produced Z."
```

They are different evidence types.

They must never be merged into one opaque "answer".

---

## 6. Solver Routing

Long-term:

```text
EEProblemIR
    ↓
SolverRouter
    ├─ Math
    ├─ Circuit
    ├─ Control
    ├─ Logic
    ├─ Numerical
    └─ Future domains
```

Each solver declares:
- supported problem classes
- required inputs
- output type
- verification capabilities
- limitations

---

## 7. Verification Is an Independent Layer

A solver must not self-certify simply because it returned a value.

Possible checks:

```text
SourceCheck
UnitCheck
EquationCheck
SymbolicCheck
NumericCheck
TopologyCheck
SimulationCheck
InitialConditionCheck
FinalValueCheck
CrossBackendCheck
```

Verification produces an explicit record.

---

## 8. Dependency Boundaries

Preferred package responsibilities:

```text
voltquery-core
    contracts
    IR
    orchestration
    validation

voltquery-document
    parsing adapters

voltquery-formula
    formula OCR/parser adapters

voltquery-retrieval
    index/search/rerank

voltquery-circuit
    CircuitIR / circuit recognition

voltquery-solver-*
    backend adapters

voltquery-eval
    benchmarks / metrics
```

A monorepo may initially contain these as modules rather than independently published packages.

Heavy optional runtimes should not leak into core imports.

---

## 9. No Side Effects at Import Time

Avoid:
- network requests at import
- model download at import
- GPU initialization at import
- index opening at import
- model loading at import

Initialization must be explicit.

---

## 10. Local-first Early Architecture

Pre-v1 should prefer:
- local files
- local database/index
- local CLI
- deterministic reproducibility

Do not start with:
- microservices
- distributed queues
- cloud-only storage
- user auth
- multi-tenant architecture

Those can be added after product value is proven.

---

## 11. Data Layers

Recommended conceptual layers:

```text
Bronze
raw imported material

Silver
parsed problem candidates

Gold
manually checked benchmark/evaluation data
```

Gold data must never be silently regenerated from the same pipeline being evaluated.

---

## 12. Research vs Redistributable Data

Data must carry policy metadata.

At minimum distinguish:

```text
PUBLIC_REDISTRIBUTABLE
RESEARCH_ONLY
PRIVATE_LOCAL
UNKNOWN
```

Unknown should default to restrictive behavior.

---

## 13. Security

Never use unrestricted `eval()` on:
- OCR output
- LaTeX
- model output
- user input

Mathematical expressions should pass through controlled parsing/IR validation.

Any generated code path must be treated as untrusted.

---

## 14. Observability

Important pipeline steps should produce structured records:

- input ID
- source ID
- parser/model version
- index version
- retrieval pipeline version
- solver version
- verification version
- latency
- warnings/errors

This is essential for later regression analysis.

---

## 15. Reproducibility

Every benchmark result should be attributable to:

```text
code revision
dataset revision
model revision
config
hardware/runtime
```

Do not accept anonymous benchmark numbers in project decisions.

---

## 16. Architectural North Star

VoltQuery should remain capable of answering:

```text
What did we observe?
What did we retrieve?
What did we infer?
What did we calculate?
What did we verify?
What remains uncertain?
```

If the architecture cannot preserve those distinctions, it is too opaque.
