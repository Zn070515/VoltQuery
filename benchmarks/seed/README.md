# Seed Benchmark Corpus

Target: **40 manually reviewed** seed problems.

- Circuit Theory: 32
- Analog Electronics probe: 8

`problems.jsonl` is the input to the M0 validation framework and the M3+
retrieval benchmark. It is populated by the content task with manually reviewed
problems sourced from verified licenses.

Current status: **16 / 40 problems collected** (13 Circuit Theory,
3 Analog Electronics). Each is fully annotated per
[`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md).

15 problems are from the `socratic-electronics` source; 1 (`vq_seed_0016`) is from
`openstax-university-physics-v2` (University Physics Vol 2, Ch 10) — the first
genuinely independent, non-Kuphaldt source and the first lettered-subpart problem
in the corpus. The next tranche continues from the OpenStax source for the
coverage OpenStax supports (KCL/KVL, RC, AC/phasor/impedance) and falls back to
Socratic for nodal/mesh, superposition, diode, and MOSFET — see
[`docs/development/SEED_CORPUS_FINDINGS.md`](../../docs/development/SEED_CORPUS_FINDINGS.md).

## Gold / Silver / Bronze

- **Bronze** — raw imported material, no parsing guarantee.
- **Silver** — automatically parsed candidates, optionally sampled for review.
- **Gold** — manually checked evaluation set, isolated from automatic
  regeneration.

`problems.jsonl` is the Gold benchmark. Local assets live under `assets/`.
