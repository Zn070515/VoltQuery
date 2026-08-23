# VoltQuery

**Electrical Engineering Problem Search & Verifiable Reasoning Engine**

VoltQuery is an early-stage project exploring professional problem retrieval, structured understanding, deterministic solving, and verification for Electrical Engineering.

> **Search First. Verify Always. Solve When Supported. Explain Last.**

## Current Stage

Current milestone:

**M1 — EEProblemIR v0.1**

M0 is complete: a 40-problem (32 Circuit Theory / 8 Analog Electronics)
manually reviewed, license-verified public Gold corpus plus its source registry
and benchmark contract live at `benchmarks/seed/problems.jsonl`.

M1 is the first stable typed representation of an EE problem — `EEProblemIR`
v0.1 (`benchmarks/seed/problem_ir.jsonl`), a versioned one-record-per-seed
projection of the corpus with structured parts, typed inputs (quantity/table),
three-axis assets, targets, and formulas. The project is intentionally **not**
starting with a large OCR/LLM stack.

The corpus and its IR are being built to later measure:
- document parsing
- OCR
- retrieval
- formula understanding
- visual retrieval
- circuit understanding
- solvers
- verification

## Initial Domain

Primary:
- Circuit Theory / 电路原理

Probe:
- Analog Electronics / 模拟电子技术

## Target Python

```text
Python >=3.12,<3.13
```

## Documentation

- `CLAUDE.md` — coding-agent instructions and development constraints
- `docs/vision.md` — long-term product goal
- `docs/roadmap.md` — milestone/version roadmap
- `docs/version-spec.md` — version features and acceptance criteria
- `docs/architecture.md` — architecture rules
- `docs/development/M0_BOOTSTRAP.md` — the completed M0 bootstrap plan
- `docs/development/SEED_CORPUS_FINDINGS.md` — lessons learned from the seed corpus (the requirements ledger for `EEProblemIR` v0.1)

## Long-term Direction

```text
Photo / Screenshot / PDF / Text
            ↓
       EEProblemIR
            ↓
   ┌────────┴────────┐
   ↓                 ↓
Retrieval          Solvers
   ↓                 ↓
Evidence        Candidate result
   └────────┬────────┘
            ↓
       Verification
            ↓
      Final response
```

VoltQuery is not intended to become an opaque "image → LLM → answer" wrapper.

The long-term objective is to make every result distinguish:
- what was observed
- what was retrieved
- what was inferred
- what was calculated
- what was verified
- what remains uncertain
