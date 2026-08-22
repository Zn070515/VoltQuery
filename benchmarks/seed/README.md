# Seed Benchmark Corpus

Target: **40 manually reviewed** seed problems.

- Circuit Theory: 32
- Analog Electronics probe: 8

`problems.jsonl` is the input to the M0 validation framework and the M3+
retrieval benchmark. It is populated by the content task with manually reviewed
problems sourced from verified licenses.

Current status: **16 / 40 problems collected** (12 Circuit Theory,
4 Analog Electronics). Each is fully annotated per
[`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md).

15 of the 16 problems are from the `socratic-electronics` source;
`vq_seed_0017` is the first from the independently verified UMass
`umass-ee-fundamentals` source (a web-only Pressbooks chapter, source format
HTML). `vq_seed_0016` (OpenStax University Physics Vol 2, Ch 10)
— the first lettered-subpart problem and the first genuinely independent
candidate — has been **moved out of the public Gold corpus** to `benchmarks/research/held.jsonl`. Its source is under
`LICENSE_REVIEW_REQUIRED` (the pinned PDF prints CC-BY-4.0, but the current
OpenStax collection license is CC-BY-NC-SA-4.0 with an additional no-LLM-training
clause), so it is **not counted toward the public Gold gate** and no further
OpenStax items are collected until the governing license is confirmed. The
full question text + crops are held local-only under the gitignored
`data/raw/hold/vq_seed_0016/`; only locator/metadata is public. The next tranche
pursues independently verified CC BY 4.0 sources (UMass `umass-ee-fundamentals`,
Janzen `janzen-electricity-magnetism-circuits`) and falls back to Socratic for
nodal/mesh, superposition, and MOSFET. KSU Engineering Electronics (CC BY-NC)
and Fiore's semiconductor lab (CC BY-NC-SA 3.0) were verified as
**non-commercial and rejected** for the public corpus — see
[`docs/development/SEED_CORPUS_FINDINGS.md`](../../docs/development/SEED_CORPUS_FINDINGS.md).

## Gold / Silver / Bronze

- **Bronze** — raw imported material, no parsing guarantee.
- **Silver** — automatically parsed candidates, optionally sampled for review.
- **Gold** — manually checked evaluation set, isolated from automatic
  regeneration.

`problems.jsonl` is the Gold benchmark. Local assets live under `assets/`.
