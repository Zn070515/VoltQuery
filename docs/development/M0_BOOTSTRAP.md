# M0 Bootstrap — Seed Corpus + Benchmark Contract

## Objective

Turn the empty `VoltQuery/` directory into a measurable research project before adding OCR, LLMs, circuit recognition, or solvers.

M0 is about creating the **first trustworthy project asset**:

```text
benchmarks/seed/problems.jsonl
```

Models will change. The benchmark is the ruler used to judge those changes.

---

# 1. Initialize the Project

Recommended:

```powershell
uv init --package --python 3.12
```

Then ensure:

```toml
requires-python = ">=3.12,<3.13"
```

Suggested baseline development dependencies:

```powershell
uv add pydantic pyyaml
uv add --dev pytest ruff mypy
```

Do not install large OCR/ML frameworks yet.

---

# 2. Initial Repository Structure

```text
VoltQuery/
├─ CLAUDE.md
├─ README.md
├─ pyproject.toml
├─ .gitignore
│
├─ docs/
│  ├─ vision.md
│  ├─ roadmap.md
│  ├─ version-spec.md
│  ├─ architecture.md
│  ├─ development/
│  │  ├─ M0_BOOTSTRAP.md
│  │  └─ SEED_CORPUS_FINDINGS.md
│  └─ superpowers/
│
├─ data/
│  ├─ README.md
│  ├─ sources.yaml
│  ├─ raw/
│  └─ seed/
│
├─ benchmarks/
│  └─ seed/
│     ├─ README.md
│     ├─ problems.jsonl
│     └─ assets/
│
├─ src/
│  └─ voltquery/
│
└─ tests/
```

Initially keep `data/raw/` out of Git unless every source is clearly redistributable and the repository policy explicitly permits inclusion.

---

# 3. Create `data/sources.yaml`

Start with a small source registry.

Example schema:

```yaml
sources:
  - id: example-source
    title: Example Source
    author: Example Author

    domains:
      - circuit_theory

    license:
      id: CC-BY-4.0
      redistribution: true
      derivatives: true
      commercial: true
      attribution_required: true

    source_url: https://example.org
    status: approved
```

Initial candidate source families previously identified for evaluation include:
- Socratic Electronics
- Lessons in Electric Circuits
- open Circuits I materials

Before redistributing copied content, independently verify the exact license applying to the specific file/version being used.

---

# 4. Select the First 40 Problems

Do this manually.

Target:

```text
Circuit Theory       32
Analog Electronics    8
```

Suggested Circuit Theory distribution:

```text
8  Ohm / series / parallel
6  KCL / KVL
6  node / mesh / network analysis
4  Thevenin / Norton
4  capacitor / inductor
4  AC / impedance / phasor
```

Analog probe:

```text
2 diode
2 BJT
2 MOSFET
2 op-amp
```

The Analog items are schema probes, not a commitment to an Analog solver in v0.1.

---

# 5. Seed Record — Do Not Overdesign

Use an observational record before final EEProblemIR.

Example:

```json
{
  "id": "vq_seed_0001",
  "source": {
    "source_id": "source-id",
    "document": "document-name",
    "page": 12,
    "question_number": "Q3"
  },
  "domain": "circuit_theory",
  "topic": [
    "kcl",
    "node_voltage"
  ],
  "question_text": "…",
  "has_formula": true,
  "has_circuit_figure": true,
  "answer_available": true,
  "assets": {
    "question_image": "assets/vq_seed_0001.png"
  }
}
```

This is **not** the final EEProblemIR.

Use it to discover what the real IR needs.

---

# 6. Required Problem Shapes

The 40-problem seed should contain examples of:

### Text-only

```text
A resistor carries ...
```

### Text + formula

```text
Given ...
```

### Text + circuit figure

```text
Find I in the circuit shown.
```

### Figure-dominant problem

Most information is inside the diagram.

### Multipart

```text
(a) ...
(b) ...
(c) ...
```

### Analog device problem

Diode/BJT/MOSFET/op-amp.

The purpose is to stress the future schema.

---

# 7. Tests to Write During M0

At minimum:

```text
test_source_ids_unique
test_problem_ids_unique
test_problem_source_exists
test_source_license_present
test_problem_assets_exist
test_problem_record_valid
```

Optional:

```text
test_topic_names_valid
test_domain_names_valid
test_problem_count
test_required_probe_coverage
```

Do not build ML tests yet.

---

# 8. Build Query Variants

Once seed problems exist, generate or manually construct query variants.

For a problem `P0017`:

```text
P0017-original
P0017-crop
P0017-rotate
P0017-perspective
P0017-shadow
P0017-blur
P0017-text
P0017-zh-paraphrase
P0017-circuit-only
```

All point to:

```text
target_problem_id = P0017
```

This becomes the basis for later Recall@1 / Recall@5 evaluation.

---

# 9. Gold / Silver / Bronze Policy

## Bronze

Raw imported material.

No guarantee of clean parsing.

## Silver

Automatically parsed problems, optionally sampled for review.

## Gold

Manually checked evaluation set.

Gold must be isolated from automatic regeneration.

---

# 10. Write `SEED_CORPUS_FINDINGS.md`

After the first 40 problems, answer:

1. Can a problem have multiple figures?
2. Can a figure belong to only one part?
3. Can one source image contain multiple problems?
4. How often are formulas inline vs display?
5. How should subproblems be represented?
6. How often is the answer a scalar vs expression vs explanation?
7. Are units explicit?
8. What does Analog require that Circuit Theory does not?
9. What source location metadata is always available?
10. What must be represented in EEProblemIR v0.1?

Only then design M1.

---

# 11. M0 Definition of Done

- [ ] Git repository initialized
- [ ] Python 3.12 range frozen
- [ ] source registry exists
- [ ] at least 3 source entries
- [ ] explicit license metadata
- [ ] 40 manually reviewed seed problems
- [ ] Circuit + Analog probe coverage
- [ ] typed seed record
- [ ] JSONL validation
- [ ] asset validation
- [ ] benchmark query-variant format
- [ ] seed findings document

---

# 12. What Not to Do During M0

Do not:

- train OCR
- integrate multiple OCR frameworks
- build a frontend
- build Android/iOS
- write CircuitIR
- write a circuit solver
- implement custom MNA
- add ngspice
- add PyTorch math runtime
- add LLM agents
- deploy to cloud
- design user accounts
- scrape questionable proprietary problem banks

M0 should remain deliberately small.

---

# 13. Next Milestone

After M0:

> **M1 — EEProblemIR v0.1**

The seed corpus becomes the requirements document for the IR.
