# Seed Corpus Findings

Status: **pending** — to be filled after the first 40 manually reviewed seed
problems are collected into `benchmarks/seed/problems.jsonl`.

The seed corpus is the requirements document for `EEProblemIR` v0.1. Record
observations here rather than freezing the IR ahead of real data.

## Questions to answer

1. Can a problem have multiple figures?
2. Can a figure belong to only one part?
3. Can one source image contain multiple problems?
4. How often are formulas inline vs display?
5. How should subproblems be represented?
6. How often is the answer a scalar vs expression vs explanation?
7. Are units explicit?
8. What does Analog require that Circuit Theory does not?
9. What source location metadata is always available?
10. What must be represented in `EEProblemIR` v0.1?

## Findings

_Anchored to the first 5 recorded problems (vq_seed_0001–0005). These are the
minimum-deliverable M0 seed set; the schema gaps below are what they actually
revealed, captured now so `EEProblemIR` v0.1 does not freeze ahead of more data._

### 1. Can a problem have multiple figures?

Yes, in principle — nothing in `SeedProblemRecord` forbids `assets: list[AssetRef]`
of length > 1. But the first 5 problems each use a single figure at most, and that
figure is always a schematic (`kind: schematic`). No seed problem yet combines, say,
a schematic + a waveform plot in the same item. The asset list is homogeneous.

### 2. Can a figure belong to only one part?

The current model has no notion of a figure belonging to a specific subpart, because
there is no subpart structure at all — `assets` is a flat list on the problem record.
For multipart problems (vq_seed_0003: V_AB/V_BC/V_CD; vq_seed_0004: Vc at 6 time
points) the figure is shared across all parts. If a future problem gives *different*
figures per part, this flat list will be insufficient and will need a part→figure
association.

### 3. Can one source image contain multiple problems?

Yes. vq_seed_0003 (dc_sp.pdf p19, Q26) and vq_seed_0004 (time2.pdf p15, Q24) were
extracted from pages that also contain adjacent problems. In acquisition this is
handled by cropping a sub-region of the page (`data/raw/crop_figure.py`), which is
why figure captures are rectangular crops, not full pages. The asset records only a
problem-relative path; it does not record the source page's crop rectangle, so the
crop geometry is not yet reproducible from the record alone.

### 4. How often are formulas inline vs display?

Not yet cleanly observable from the schema. `has_formula: bool` only says *a* formula
is involved; it cannot distinguish:
- formula stated in the problem (vq_seed_0001: Ohm's law; vq_seed_0004: RC step
  response; vq_seed_0005: transistor equation),
- formula that must be *derived* by the student from data (vq_seed_0002: find the
  V–I relationship from a data table).

Inline vs display layout is currently not distinguished at all. This is a real gap
for `EEProblemIR` — neither the presence nor the layout of formulas is sufficient to
represent the problem.

### 5. How should subproblems be represented?

`is_multipart: bool` is insufficient. vq_seed_0003 is genuinely 3 parts (three
voltages), vq_seed_0004 is 6 parts (six time points). Neither can enumerate parts,
their ordering, or per-part answers. The boolean is a weak signal; EEProblemIR will
need structured subparts.

### 6. How often is the answer a scalar vs expression vs explanation?

Across the 5 problems, the answer form is heterogeneous:
- scalar: vq_seed_0001 (V = 3.45 V),
- verbal explanation: vq_seed_0002 (linear V–I relationship),
- table of scalars: vq_seed_0004 (Vc at 6 times), vq_seed_0005 (Vout vs Vin),
- multiple scalars + spoken reason: vq_seed_0005 (table + why "emitter follower").

No single `answer` field shape covers these. `answer_available: bool` is all that is
stored; the actual answers are not representable. This must be resolved in v0.1.

### 7. Are units explicit?

No. Units are embedded in prose: µA, MΩ, kΩ, µF, ms, V, KΩ. There are no typed
quantity/value+unit fields. This matters for solvers and unit validation (per
CLAUDE.md unit validation is a first-class concern), so it is a genuine gap. Note the
inconsistency "kΩ" vs "KΩ" across problems — untyped prose invites exactly this.

### 8. What does Analog require that Circuit Theory does not?

vq_seed_0005 (common-collector BJT) requires a device model beyond the resistor-only
world: a forward junction voltage (0.7 V) plus the KVL relation that makes
Vout = Vin − 0.7 V. Circuit Theory items are linear/deterministic (Ohm, series-parallel
dividers, RC time constants) and need only network + equation modeling. Analog
requires device-level semantic knowledge (transistor operating region, diode drop)
that is not expressible as a generic circuit network. It is the single strongest
reason the corpus is not homogeneous.

### 9. What source location metadata is always available?

For all 5: `source_id`, `document`, `page_index` (0-based), `page_label` (printed),
and `question_number`. That is consistent because the seed set is drawn entirely from
Socratic compiled PDFs. `page_label` and `page_index` can differ (page_index 10 has
printed label "10" here, but page_index 19 is "19", page_index 15 is "15", page_index
2 is "2", page_index 3 is "3" — equal in this set, but not guaranteed). A PDF's 0-based
index and its printed label are not inherently the same, so both should be kept.

### 10. What must be represented in `EEProblemIR` v0.1?

From these 5, minimally:
- structured **answer** (scalar-with-unit / table / explanation / ordered subparts),
- structured **inputs** — the data tables embedded in vq_seed_0002/0004/0005 and the
  values-at-nodes in vq_seed_0003/0005 are prose today; a table/quantity model is
  needed,
- **subparts** enumeration (replacing `is_multipart: bool`),
- **figure** that can be tied to (a) part(s) and carries a source crop rectangle,
- **typed units** separate from prose (and normalized spellings),
- **formula role** (stated vs to-derive) in addition to presence.

The existing `SeedProblemRecord` (its flat asset list, coarse booleans, prose-only
question, bool-only answer availability) is an adequate *M0 ingest* shape but is not
yet an `EEProblem`/`EEProblemIR`: it can record provenance and presence, not the
problem's structure.

### Additional observation: license version discrepancy

All compiled worksheet PDFs carry a footer saying "Creative Commons Attribution
License, **version 1.0**". The authoritative Socratic site root and `data/sources.yaml`
record **CC-BY-3.0-US**. Both are permissive and permit redistribution + derivatives,
so the data policy is unchanged (PUBLIC_REDISTRIBUTABLE), but the *version* differs
between the PDF imprint and the site's declared license. This should be reconciled at
the source level (pick the authoritative site license) and noted as provenance, not
silently assumed.
