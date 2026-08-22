# Seed Benchmark Corpus

Target: **40 manually reviewed** seed problems.

- Circuit Theory: 32
- Analog Electronics probe: 8

`problems.jsonl` is the input to the M0 validation framework and the M3+
retrieval benchmark. It is populated by the content task with manually reviewed
problems sourced from verified licenses.

Current status: **24 / 40 problems collected** (18 Circuit Theory,
6 Analog Electronics). Each is fully annotated per
[`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md).

The corpus spans **4 independent, verified source families**:

- `socratic-electronics` — 19 problems across 11 worksheet documents
  (Ohm's law, series/parallel, Thevenin/Norton, RC/RL time constants,
  transformer/op-amp, MOSFET identification, mesh current, superposition,
  Kirchhoff's laws).
- `umass-ee-fundamentals` (web-only Pressbooks chapters) — 2 problems:
  `vq_seed_0017` diode/LED forward-bias, and `vq_seed_0018` the 6.4
  negative-feedback inverting-op-amp example (Figure 6.27 schematic asset).
- `janzen-electricity-magnetism-circuits` (whole-book Pressbooks XHTML export)
  — 2 problems: `vq_seed_0019` Thévenin equivalent (Example 7.3.1, text-faithful,
  egress-gated figure so no asset), and `vq_seed_0020` RLC-series AC (Example
  12.3.1).
- `lessons-electric-circuits-dc` (Kuphaldt, Volume I) — 1 problem:
  `vq_seed_0021` node-voltage method (Chapter 10 worked example, real vector
  figure assets).

`vq_seed_0016` (OpenStax University Physics Vol 2, Ch 10) — the first
lettered-subpart problem and the first genuinely independent candidate — has
been **moved out of the public Gold corpus** to `benchmarks/research/held.jsonl`.
Its source is under `LICENSE_REVIEW_REQUIRED` (the pinned PDF prints CC-BY-4.0,
but the current OpenStax collection license is CC-BY-NC-SA-4.0 with an
additional no-LLM-training clause), so it is **not counted toward the public
Gold gate** and no further OpenStax items are collected until the governing
license is confirmed. The full question text + crops are held local-only under
the gitignored `data/raw/hold/vq_seed_0016/`; only locator/metadata is public.

KSU Engineering Electronics (CC BY-NC) and Fiore's semiconductor lab
(CC BY-NC-SA 3.0) were verified as **non-commercial and rejected** for the
public corpus — see
[`docs/development/SEED_CORPUS_FINDINGS.md`](../../docs/development/SEED_CORPUS_FINDINGS.md).

## Gold / Silver / Bronze

- **Bronze** — raw imported material, no parsing guarantee.
- **Silver** — automatically parsed candidates, optionally sampled for review.
- **Gold** — manually checked evaluation set, isolated from automatic
  regeneration.

`problems.jsonl` is the Gold benchmark. Local assets live under `assets/`.
