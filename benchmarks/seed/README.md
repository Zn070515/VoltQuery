# Seed Benchmark Corpus

Target: **40 manually reviewed** seed problems.

- Circuit Theory: 32
- Analog Electronics probe: 8

`problems.jsonl` is the input to the M0 validation framework and the M3+
retrieval benchmark. It is populated by the content task with manually reviewed
problems sourced from verified licenses.

Current status: **15 / 40 problems collected** (12 Circuit Theory,
3 Analog Electronics). Each is fully annotated per
[`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md).

All 15 problems are currently drawn from the `socratic-electronics` source. The
next tranche should diversify across the approved Lessons in Electric Circuits
(DC/AC/Semiconductors) and KSU Circuits I sources — see
[`docs/development/SEED_CORPUS_FINDINGS.md`](../../docs/development/SEED_CORPUS_FINDINGS.md).

## Gold / Silver / Bronze

- **Bronze** — raw imported material, no parsing guarantee.
- **Silver** — automatically parsed candidates, optionally sampled for review.
- **Gold** — manually checked evaluation set, isolated from automatic
  regeneration.

`problems.jsonl` is the Gold benchmark. Local assets live under `assets/`.
