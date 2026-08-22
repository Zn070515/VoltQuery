# VoltQuery

**Electrical Engineering Problem Search & Verifiable Reasoning Engine**

VoltQuery is an early-stage project exploring professional problem retrieval, structured understanding, deterministic solving, and verification for Electrical Engineering.

> **Search First. Verify Always. Solve When Supported. Explain Last.**

## Current Stage

Current milestone:

**M0 — Seed Corpus + Benchmark Contract**

The project is intentionally **not** starting with a large OCR/LLM stack.

The first goal is to build a small, trustworthy open EE seed corpus and benchmark that can later measure:
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
- `docs/development/PROJECT_VISION.md` — long-term product goal
- `docs/development/ROADMAP.md` — milestone/version roadmap
- `docs/development/VERSION_SPEC.md` — version features and acceptance criteria
- `docs/development/ARCHITECTURE_PRINCIPLES.md` — architecture rules
- `docs/development/M0_BOOTSTRAP.md` — immediate starting work
- `docs/development/SEED_CORPUS_FINDINGS.md` — lessons learned from the seed corpus

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
