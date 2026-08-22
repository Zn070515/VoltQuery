# VoltQuery — Project Vision

## 1. Mission

VoltQuery aims to become a professional Electrical Engineering problem-search and verifiable reasoning platform.

The long-term user experience is simple:

1. Take a photo, screenshot, paste text, or import a document.
2. VoltQuery understands the problem as an EE problem rather than generic text.
3. It searches for the exact problem and highly similar problems.
4. It preserves and displays trustworthy source provenance.
5. If no reliable source answer is available, it routes supported problems to deterministic tools.
6. It verifies results with symbolic, numerical, unit, topology, or simulation checks.
7. It explains the final result in a form useful to EE students.

The product is not intended to become a generic "AI answers homework" interface.

---

## 2. Product Positioning

VoltQuery occupies the space between traditional problem-search software and general-purpose AI solvers.

Traditional problem-search systems are strong at:
- large problem banks
- exact/near-duplicate lookup
- existing answer retrieval

but are usually weak at:
- mathematical structure
- circuit topology
- circuit diagrams
- deterministic verification
- EE-specific semantics

General AI solvers are strong at:
- natural language
- open-ended reasoning
- explanation
- flexible input

but may be weak at:
- provenance
- repeatability
- exact retrieval
- deterministic correctness
- topology-heavy circuit reasoning
- distinguishing known facts from generated output

VoltQuery's intended advantage is:

```text
Professional Retrieval
        +
EE-specific Structure
        +
Deterministic Tools
        +
Verification
        +
AI Explanation
```

---

## 3. Core Principle

> **Search First. Verify Always. Solve When Supported. Explain Last.**

Priority:

```text
Exact source match
    ↓
Near-duplicate / similar problem retrieval
    ↓
Professional structured understanding
    ↓
Deterministic solver
    ↓
Verification
    ↓
Explanation
```

The system must never blur the distinction between:
- retrieved answers
- calculated answers
- generated explanations

---

## 4. Long-term Input Types

VoltQuery should eventually accept:

- camera photo
- screenshot
- cropped formula
- circuit diagram
- textbook page
- PDF
- handwritten formula
- typed problem text
- waveform
- control block diagram
- phasor diagram
- device circuit

---

## 5. Long-term Internal Model

The long-term architecture centers around `EEProblemIR`.

```text
                    Input
                      │
          ┌───────────┼────────────┐
          │           │            │
        Text        Formula      Figure
          │           │            │
          ▼           ▼            ▼
       TextIR       MathIR      DiagramIR
                                   │
                              CircuitIR ...
          └───────────┬────────────┘
                      ▼
                 EEProblemIR
                      │
          ┌───────────┴────────────┐
          ▼                        ▼
      Retrieval                 Solvers
          │                        │
          └───────────┬────────────┘
                      ▼
                 Verification
                      │
                      ▼
               Evidence + Answer
```

---

## 6. Intended Domain Expansion

### Stage A — Circuit Theory

The first deep domain.

Target topics:
- Ohm's law
- series / parallel networks
- KCL / KVL
- node-voltage analysis
- mesh-current analysis
- source transformation
- Thevenin / Norton
- superposition
- maximum power transfer
- RC / RL / RLC
- sinusoidal steady state
- phasors
- impedance
- controlled sources
- two-port basics
- state-space basics

Circuit Theory is the ideal first domain because it combines:
- text
- formulas
- diagrams
- complex numbers
- differential equations
- matrices
- deterministic verification

### Stage B — Analog Electronics

Target topics:
- diodes
- rectifiers
- clippers / clampers
- BJT
- MOSFET
- bias
- operating point
- small-signal analysis
- op-amps
- frequency response

Analog Electronics will initially be retrieval-first because model assumptions and device regions make automatic solving more subtle.

### Stage C — Signals and Control

Target topics:
- signals
- convolution
- Laplace / Fourier
- transfer functions
- frequency response
- state space
- feedback
- stability
- time-domain response

### Stage D — Broader EE

Possible future domains:
- digital electronics
- power electronics
- electrical machines
- power systems
- electromagnetics
- RF / microwave
- embedded systems
- EDA / PCB

---

## 7. Long-term Solver Architecture

VoltQuery should not build a single universal solver.

Use domain-specific backends:

```text
EEProblemIR
    │
    ▼
SolverRouter
    │
    ├─ MathSolver
    ├─ CircuitSolver
    ├─ ControlSolver
    ├─ LogicSolver
    ├─ NumericalSolver
    └─ future domain solvers
```

Candidate technologies may include:
- SymPy
- Lcapy
- ngspice
- python-control
- PyTorch
- scikit-rf
- future power-system / electromagnetic tools

The backend is replaceable. The contract is owned by VoltQuery.

---

## 8. Verification Philosophy

The system should prefer deterministic evidence over self-reported AI confidence.

Future verification mechanisms may include:

- source match verification
- symbolic equivalence
- unit / dimension checking
- numerical substitution
- circuit topology validation
- symbolic circuit analysis
- SPICE cross-check
- initial/final condition checks
- truth-table exhaustive verification
- state-space / control response checks
- cross-backend consistency

Standard result states should eventually include:

```text
VERIFIED
PARTIALLY_VERIFIED
UNVERIFIED
UNSUPPORTED
CONFLICT
```

---

## 9. Reliability Metrics

A primary long-term metric should be:

```text
Reliable Answer Rate
=
correct answers with trustworthy provenance or verification
/
all queries
```

A critical negative metric should be:

```text
False Confidence Rate
=
incorrect answers presented as trustworthy
/
all answered queries
```

VoltQuery should prefer a correct `UNSUPPORTED` result over an incorrect confident answer.

---

## 10. Data as a Core Asset

The long-term database should evolve beyond:

```text
question
answer
```

toward:

```text
Problem
Solution
Course
Chapter
Concept
Method
Difficulty

TextIR
MathIR
CircuitIR
DiagramIR

TextEmbedding
FormulaFingerprint
VisualEmbedding
CircuitFingerprint

Source
License
Edition
Page

VerificationRecord
SolutionQuality
```

The project's durable value will come from:
- structured EE problems
- high-quality benchmarks
- source provenance
- domain semantics
- retrieval signals
- verification records

Models are replaceable.

---

## 11. Mobile Vision

Mobile is an important product surface, but not an early architectural driver.

Early mobile responsibility:

```text
Camera
→ crop / rectify
→ lightweight preprocessing
→ query package
→ backend retrieval
→ result display
```

The first mobile client does not need to contain every solver or ML runtime.

Possible later runtimes:
- ONNX Runtime Mobile
- WebGPU / ONNX Runtime Web
- ExecuTorch
- Core ML / NNAPI integrations

---

## 12. Success Definition

VoltQuery succeeds when a student can take a photo of a real EE problem and the system can reliably answer:

1. **What problem is this?**
2. **Where did it come from?**
3. **What EE concepts and structures are present?**
4. **Have we seen the same or a similar problem before?**
5. **Can a trusted tool solve it?**
6. **Can the result be independently verified?**
7. **Can the reasoning be explained without hiding uncertainty?**

That is the long-term product goal.
