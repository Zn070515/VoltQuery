# Seed Corpus Findings

Status: **pending** — core analysis below is anchored to the first 15 manually
reviewed seed problems (two tranches: vq_seed_0001–0005, then vq_seed_0006–0015),
collected into `benchmarks/seed/problems.jsonl`. It still does NOT satisfy the M0
count (15 < 40), so M0 is RED; this doc is a running requirements ledger, not a
completion report.

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

_Anchored to the first 15 recorded problems (vq_seed_0001–0015), across two
tranches. The schema gaps below are what they actually revealed, captured now so
`EEProblemIR` v0.1 does not freeze ahead of more data. The per-section evidence
is updated where tranche 2 changed the picture; a consolidated tranche-2 review
follows the numbered list._

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

### Additional observation: annotation semantics at 15 problems

Under the observable rules in `benchmarks/seed/ANNOTATION_GUIDE.md`, across the
15 problems:

- `has_formula` is **no longer uniformly false**. Three problems display an
  explicit formula: vq_seed_0008 (`R = R1 + R2 + R3`), vq_seed_0013 (the RC/LR
  universal step response, `V(t) = (Vf − V0)(1 − 1/e^(t/τ)) + V0` and its
  current twin), and vq_seed_0014 (`AV = Vout / Vin(+)`). The "formula-displaying"
  shape is now represented. Note vq_seed_0001 (Ohm's law) and vq_seed_0012 (RL
  time constant) *involve* a formula but do not display it — confirming the
  stated-vs-displayed distinction flagged in section 4.
- `is_multipart` is still **uniformly false**. No problem uses explicit `(a)(b)(c)`
  subparts. Multi-target problems are expressed as a single task with several
  bullet targets (vq_seed_0009: 8 terminal-pair/current targets), or as a
  multi-row table (vq_seed_0005, vq_seed_0015), or the worksheet already splits
  at the "Question N" level.

This is a genuine corpus finding, not a defect. The pilot set now covers
formula-displaying shapes, but it does not contain (and, for this source family,
cannot contain) lettered `(a)(b)(c)` subparts — see the tranche-2 review below.
Documented here so M1 does not assume lettered subparts are observed.

### Additional observation: license version discrepancy

All compiled worksheet PDFs carry a footer saying "Creative Commons Attribution
License, **version 1.0**". The authoritative Socratic site root and `data/sources.yaml`
record **CC-BY-3.0-US**. Both are permissive and permit redistribution + derivatives,
so the data policy is unchanged (PUBLIC_REDISTRIBUTABLE), but the *version* differs
between the PDF imprint and the site's declared license. This should be reconciled at
the source level (pick the authoritative site license) and noted as provenance, not
silently assumed.

## Tranche-2 re-review (vq_seed_0006–0015)

Re-review of `SEED_CORPUS_FINDINGS.md` at 15 problems, per the 15-collection
milestone. Adds 10 problems from four more Socratic worksheets (dc_s, thev,
time2, opamp3), three of which were not yet in `data/documents.yaml` and have been
registered.

### 1. Corpus composition at 15

- 12 circuit_theory, 3 analog_electronics. Analog remains the deliberate probe
  minority: vq_seed_0005 (BJT emitter follower), vq_seed_0014 (op-amp transfer
  function + negative feedback), vq_seed_0015 (op-amp voltage follower table).
- Topics expanded: thevenin, norton, equivalent_circuit, led, rl_time_constant,
  algebraic_manipulation, op_amp, voltage_gain, feedback, voltage_follower —
  topping the original Ohm/series/power set. None are frozen; open slugs let the
  vocabulary grow.

### 2. Formula-displaying shape is now observed

vq_seed_0008 (`R = R1 + R2 + R3`, manipulation to solve for R1), vq_seed_0013
(RC/LR universal step response, define each term), vq_seed_0014 (`AV = Vout/Vin(+)`,
derive the closed-loop gain). This closes the "no formula-displaying problem" gap
the first-5 note flagged. But the *layout* question (inline vs display) is still
unresolved: all three are display formulas; no seed problem yet shows an inline
formula mid-sentence.

### 3. Explicit `(a)(b)(c)` subparts are absent across the source family

Scanned ohm_law, dc_s, dc_sp, time2, thev, bjtbias, and opamp3 for `(a)/(b)/(c)`
markers (`data/raw/scan.py`): **none found.** The Socratic worksheets simply do not
letter their subparts. Multi-task items appear as either (i) a single task with
several bullet targets (vq_seed_0009: voltage-divider terminal pairs), (ii) a
multi-row table to complete (vq_seed_0005, vq_seed_0015), or (iii) pre-split
"Question N" headers in the worksheet. This is an honest limitation of the source:
**a lettered `(a)(b)(c)` subpart may be unobservable from this entire corpus
family, so M1 must not assume that shape is present.** Multi-part structure must
still be representable — vq_seed_0009 (8 targets), vq_seed_0003 (3 targets),
vq_seed_0005/0015 (data tables) all have internal structure — but that structure is
*target/table* form, not lettered subparts.

### 4. Pictorial vs schematic figure

vq_seed_0006's question figure is a *pictorial* (a power-supply box + 24 VDC motor
drawing) with `has_circuit_figure: false`, so its asset is `kind: figure` only —
no `schematic` asset. This is the first non-schematic "figure" in the corpus and
confirms the `kind` enum is genuinely used: `figure` = pictorial/prose-figure,
`schematic` = a circuit drawing. It also resolved an annotation call: 0006 was
NOT given a circuit crop (the drawing is not a circuit schematic), which is why it
has exactly one asset.

### 5. Multiple assets per problem confirmed

Five problems now carry two assets (question figure + schematic): vq_seed_0009,
0010, 0011, 0014, 0015. The flat `assets: list[AssetRef]` handles this, but none
yet binds a figure to a specific subpart (consistent with section 2 — no subpart
structure exists).

### 6. Device-level vs network-level semantics (strengthens section 8)

Tranche 2 adds op-amp problems that are *not* just a resistor network: vq_seed_0014
requires the ideal-op-amp negative-feedback model (noninverting gain for a
unity-gain-feedback connection) and vq_seed_0015 the voltage-follower (unity buffer)
relation. Together with the 0.7 V BJT drop in vq_seed_0005, Analog's requirement for
device/semantic modeling — beyond what a generic circuit graph can express — is now
observed in two device families (BJT and op-amp).

### 7. Answer-form heterogeneity grows

vq_seed_0006 (draw a picture — the answer is a *drawing*), vq_seed_0010/t0011
(derived *equivalent circuit* + numeric), vq_seed_0012 (single scalar), vq_seed_0013
(explain each formula term — a "define the terms" prose answer), vq_seed_0014
(derive a gain expression + compute a scalar), vq_seed_0015 (complete a table).
`answer_available: bool` cannot represent any of these — the structured-answer gap
in section 6 is now wider and more clearly heterogeneous.

### 8. Provenance: page_label vs page_index

Across the 15, `question_number` and `page_label` (printed footer) are present for
every record; `page_index` (0-based) is stored as the reading index. In this family
`page_label` always equals the printed number and `page_index` is that minus one
(e.g. thev p22 → printed "23"), but both are kept because the printed label and the
0-based index are not inherently the same. No seed problem yet needs them to differ.
