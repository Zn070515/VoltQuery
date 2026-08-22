# Gold Annotation Guide

Rules for manually recording a Gold seed problem into `problems.jsonl`. Gold is a
faithful, reproducible record of the source; it is **not** the place to normalize,
restructure, or semantically complete the problem. Derived/silver layers may do that
later.

## `question_text` — faithful narrative only

`question_text` is a transcription of the problem's **narrative text**. It must not
re-encode visual or schematic data into prose, and must not flatten structured tables
into a sentence:

- Component values that appear only in a **schematic / diagram** (e.g. `31 V`,
  `R = 27 kΩ`, `+15 V`, `150 Ω`) are not narrative text.
- Values given as a **table** (data tables, output-voltage tables, time columns) are
  structure, not narrative.

Keep the narrative verbatim; carry the visual content in the figure assets. Do not add
summarising clauses such as `Circuit: source 31 V, R = 27 kΩ` that the source never
wrote. This keeps a future text-only retrieval benchmark from leaking figure
semantics, and keeps `normalized_text` (a derived layer) as the place for structure.

## `has_formula` — explicit in the source

`has_formula` is an **observable**: `true` only when the source problem itself displays
a mathematical formula or equation. It is *not* "this problem needs a formula to be
solved". A problem that merely *requires* Ohm's law but does not print `E = IR`
therefore has `has_formula: false`.

A formula printed for a **different** question on the same page does not count.

## `is_multipart` — explicit structured subparts

`is_multipart: true` only when the source uses explicit, labeled subparts such as
`(a) … (b) … (c) …`. The following are **not** multipart:

- multiple targets in one task (`Calculate V_AB, V_BC, V_CD`),
- a table with several rows (a set of time points / input values),
- multiple sub-questions separated by prose without `(a)/(b)/(c)` labels.

Record the count/structure of subparts in a later `EEProblemIR` (M1), not here.

## `assets`

Every problem should carry at least one full **question crop** (the whole problem as
printed, `kind: figure`), and a **schematic crop** (`kind: schematic`) when a circuit
appears. The question crop is the future screenshot / layout-retrieval target; the
schematic crop is the future `CircuitIR` / visual-retrieval target. Keep both.

For HTML / web sources, `question_crop` is a rendered-page screenshot crop (a portion
of the problem as it appears in a browser), not a PDF crop. `page_index` is `null` for
such sources; the `page_label` records the section title instead.

When a web worked example's problem statement is mostly inline formula images (e.g.
UMass `quicklatex` PNGs), a rendered crop shows blank gaps where the values belong, so
it is NOT a faithful question image. In that case record the problem by its authentic
circuit figure (`kind: schematic`) plus a complete `question_text` with the exact
values, and omit the `question_crop` (one asset, not two). `vq_seed_0018` is the
example of this rule; `vq_seed_0017` is the rendered-crop case.

When the **circuit figure itself** cannot be obtained (egress-gated host, 401/403,
or prohibitive download), record the problem **text-faithfully**: the verbatim prompt
plus the source's own narrative description of the circuit, with `assets: []` and
`has_circuit_figure: false`, and record the figure gap as an **access follow-up**
rather than reconstructing a schematic from prose (reconstruction is fabrication and
is forbidden). `vq_seed_0019` (Janzen Thévenin, Figure 7.3.1(a) unreachable) is the
example. This is a deliberate, recorded deviation — not a license to invent values or
topology; only what the source's own text states may be transcribed.

## Provenance

- `source_id` — a registered source in `data/sources.yaml`.
- `document_id` — a registered document in `data/documents.yaml` (URL + SHA256 +
  fetched-at), so the exact artifact is reproducible.
- `page_index` — the **0-based** PDF page the question appears on.
- `page_label` — the printed page number (often `page_index + 1`, not guaranteed).
- `question_number` — the worksheet's own number for the question.
