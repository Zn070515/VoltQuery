# Seed Corpus Findings

Status: **pending**. Core analysis is anchored to the first 15 manually reviewed
seed problems (two tranches: `vq_seed_0001–0005`, then `vq_seed_0006–0015`) in
`benchmarks/seed/problems.jsonl`. M0 is RED (15 < 40), so this is a running
requirements ledger for `EEProblemIR` v0.1, not a completion report. Observations
below reflect the latest facts at 15 problems — not the earlier pilot-only view.

The seed corpus is the requirements document for `EEProblemIR` v0.1. Record
observations here rather than freezing the IR ahead of real data. Historical
change is tracked by Git; this document carries the current truth, not a changelog.

## Composition at 15

- 15 problems: **12 circuit_theory, 3 analog_electronics**.
- All 15 come from a **single source** (`socratic-electronics`, Kuphaldt Socratic
  worksheets). This is the corpus's most serious gap — see *Source diversity*.
- Topics observed: ohm_law, series, parallel, voltage_divider, thevenin, norton,
  equivalent_circuit, led, capacitor, rc_time_constant, rl_time_constant,
  inductor, algebraic_manipulation, bjt, emitter_follower, op_amp, voltage_gain,
  feedback, voltage_follower. Open slugs; vocabulary is not frozen.

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

### 1. Can a problem have multiple figures?

Yes. Five problems carry **two** assets — a full-question crop (`kind: figure`)
plus a circuit crop (`kind: schematic`): `vq_seed_0009`, `0010`, `0011`, `0014`,
`0015`. `assets: list[AssetRef]` of length > 1 is exercised. The asset list is
still homogeneous in `kind` (figure = question crop, schematic = circuit crop);
no problem yet combines, say, a schematic + a waveform plot in the same item. The
`kind` enum is genuinely used: `vq_seed_0006` embeds a *pictorial* (power-supply
box + 24 VDC motor drawing) that is **not** a circuit and so is `figure`-only.
See *AssetKind ≠ AssetRole* for the role distinction this exposes.

### 2. Can a figure belong to only one part?

Not yet observable. The model has no subpart structure — `assets` is a flat list,
and no problem has lettered subparts to bind a figure to one of them. For
multi-target problems the one figure is shared across all targets (`vq_seed_0003`
V_AB/V_BC/V_CD; `vq_seed_0004` six time points; `vq_seed_0009` eight terminal
pairs). If a future problem gives *different* figures per part, this flat list is
insufficient and needs a part→figure association (which is why a figure must
eventually carry a source crop rectangle — see section 3).

### 3. Can one source image contain multiple problems?

Yes, and often. `vq_seed_0003` (dc_sp.pdf p19, Q26) and `vq_seed_0004`
(time2.pdf p15, Q24) sit on pages with adjacent questions; same page holds
`vq_seed_0002`+`0003` on ohm_law p3, `vq_seed_0007`+`0008` on dc_s p11, and
`vq_seed_0014`+`0015` share the opamp3 page. Figures are rectangular crops of a
page region, not full pages. The record stores a problem-relative asset path but
**not** the source crop rectangle, so crop geometry is not yet reproducible from
the record alone.

### 4. How often are formulas inline vs display?

Cleaner at 15 than at 5, but still coarse. `has_formula: bool` means the source
**displays** a formula; it says nothing about layout or about formulas the problem
requires but does not print. Observed:

- **Displayed** (`has_formula: true`): `vq_seed_0008` (`R = R1 + R2 + R3`),
  `vq_seed_0013` (RC/LR universal step response
  `V(t) = (Vf − V0)(1 − 1/e^(t/τ)) + V0` and its current twin), `vq_seed_0014`
  (`AV = Vout / Vin(+)`).
- **Required, not displayed** (`has_formula: false`): `vq_seed_0001` (Ohm's law),
  `vq_seed_0012` (RL time constant).
- **To be derived from data** (`has_formula: false`): `vq_seed_0002` (find the V–I
  relationship from a data table).

So the single boolean conflates "involved", "stated", and "to-derive", and cannot
distinguish inline from display. All three displayed formulas are **display
formulas**; no seed problem shows an inline formula mid-sentence. Both gaps are
real for `EEProblemIR` and remain unresolved.

### 5. How should subproblems be represented?

`is_multipart: bool` is observed **uniformly false** across all 15, by rule: true
only for explicit labeled `(a)(b)(c)` subparts, none of which occur in this source
family (scan of ohm_law, dc_s, dc_sp, time2, thev, bjtbias, opamp3 for
`(a)/(b)/(c)` markers found none). Multi-work problems are expressed as:

- a single task with several bullet targets — `vq_seed_0009` (8 terminal-pair /
  current targets), `vq_seed_0003` (3 voltages),
- a multi-row table to complete — `vq_seed_0005`, `vq_seed_0015`,
- pre-split "Question N" headers already in the worksheet.

The Socratic family therefore **does not contain and likely cannot contain
lettered subparts** — to observe that shape, the next tranche must change source
(see *Source diversity* and *Next tranche*). Independently, the boolean is too
weak regardless: it cannot enumerate parts, order them, or attach per-part
answers. `EEProblemIR` needs structured subparts.

### 6. How often is the answer a scalar vs expression vs explanation?

Heterogeneous and wide:

- scalar: `vq_seed_0001` (V), `vq_seed_0012` (inductor current),
- verbal/explanation: `vq_seed_0002` (linear V–I relation), `vq_seed_0013`
  (define each formula term),
- table of scalars: `vq_seed_0004` (Vc at 6 times), `vq_seed_0005` (Vout vs Vin),
  `vq_seed_0015` (voltage-follower table),
- expression + scalar: `vq_seed_0008` (manipulated formula), `vq_seed_0010`/`0011`
  (derived equivalent circuit + numeric), `vq_seed_0014` (gain expression + Vout),
- a *drawing*: `vq_seed_0006` ("draw a picture").

`answer_available: bool` cannot represent any of these. The structured-answer gap
is the widest single gap for `EEProblemIR`.

### 7. Are units explicit?

No. Units are embedded in prose (µA, MΩ, kΩ, µF, ms, V). There are no typed
value+unit fields; the inconsistent spellings ("kΩ" vs "KΩ" across problems) are
a symptom of untyped prose. This blocks solver and unit-validation work (a
first-class concern in CLAUDE.md) and is a genuine gap.

### 8. What does Analog require that Circuit Theory does not?

Analog problems need **device/semantic models** beyond a resistor network:
- `vq_seed_0005` (common-collector BJT) needs a forward junction drop (0.7 V) plus
  the KVL relation `Vout = Vin − 0.7 V`,
- `vq_seed_0014` needs the ideal-op-amp negative-feedback model,
- `vq_seed_0015` needs the voltage-follower (unity buffer) relation.

Circuit Theory items are linear/deterministic (Ohm, series-parallel dividers, RC
time constants) and need only network + equation modeling. Analog therefore
requires semantic knowledge (transistor/diode operating region, op-amp rules)
that is not expressible as a generic circuit graph. Device coverage is still
partial: BJT and op-amp are observed; **diode and MOSFET are not yet in the
corpus** (see *Next tranche*).

### 9. What source location metadata is always available?

For all 15: `source_id`, **`document_id`**, `page_index` (0-based), `page_label`
(printed), and `question_number`. This is consistent because the set is drawn
entirely from Socratic compiled PDFs. `page_label` and `page_index` can differ; in
this family `page_label` is always `page_index + 1` (thev p22 → printed "23"), but
that is not guaranteed across sources. Both are kept because the 0-based index and
the printed label are not inherently the same.

### 10. What must be represented in `EEProblemIR` v0.1?

From 15 problems, minimally:
- structured **answer** — scalar-with-unit / table / expression / explanation /
  ordered subparts / drawing,
- structured **inputs** — data tables embedded in `vq_seed_0002/0004/0005/0015`
  and values-at-nodes in `vq_seed_0003/0005/0009` are prose today; a
  table/quantity model is needed,
- **subparts** enumeration (replacing `is_multipart: bool`),
- **asset role vs asset kind** — see *AssetKind ≠ AssetRole*,
- **figure** bound to (a) part(s), carrying a source crop rectangle,
- **typed units** separate from prose, with normalized spellings,
- **formula role** (stated vs displayed vs to-derive) and **layout** (inline vs
  display).

The current `SeedProblemRecord` — flat asset list, coarse booleans, prose-only
question, bool-only answer availability — is an adequate M0 *ingest* shape but is
not yet `EEProblem`/`EEProblemIR`: it can record provenance and presence, not the
problem's structure. That distinction is deliberate: it is the observable
requirements contract for M1, not a frozen final IR.

## AssetKind ≠ AssetRole

The `kind` enum (`figure` / `schematic` / `formula` / `table` / `waveform` /
`other`) describes **what the asset is**, not **what it is for**. Today both the
full **question crop** and an internal pictorial (e.g. `vq_seed_0006`'s
power-supply + motor drawing) are `kind: figure`, distinguished only by the
filename convention (`*_question.png` vs `*_circuit.png`). This conflates two
different roles:

- **question_crop** — the whole problem as printed (future screenshot /
  layout-retrieval target),
- **content_crop** — a figure/diagram *inside* the question (future
  visual-retrieval / `CircuitIR` target).

M1 will likely need a separate `role` axis alongside `kind`, e.g. `kind:
{schematic, formula, figure, table, waveform}` × `role: {question_crop,
content_crop}`. This is recorded now and is **not** a blocker for M0 — filename
convention plus the `has_circuit_figure` boolean are sufficient to finish M0.

## Source diversity (most serious gap)

**All 15 problems are from `socratic-electronics`.** At 5 problems this was fine;
at 15 it is no longer acceptable. The corpus currently only supports the claim
"VoltQuery on Kuphaldt Socratic worksheets," not "VoltQuery on university EE
problems with varied layouts, writing, and sources." Approved and registered
sources already available: Lessons in Electric Circuits DC, AC, Semiconductors
(CC-BY-4.0), and KSU Circuits I (CC-BY-4.0). The next tranche should
preferentially draw from these, halting the run of Socratic-first collection.

## License version discrepancy

All compiled Socratic worksheets carry a footer "Creative Commons Attribution
License, **version 1.0**", while the authoritative Socratic site root and
`data/sources.yaml` record **CC-BY-3.0-US**. Both are permissive and permit
redistribution + derivatives, so the data policy is unchanged
(PUBLIC_REDISTRIBUTABLE) — but the *version* differs between the PDF imprint and
the site's declared license. This should be reconciled at the source level (pick
the authoritative site license) and noted as provenance, not silently assumed.
The Lessons and KSU sources are each declared CC-BY-4.0 with no such imprint
discrepancy expected.

## Next tranche (0016–0025)

The corpus's current content gaps (KCL, KVL, nodal, mesh, superposition, AC
fundamentals, phasor, impedance, diode, MOSFET) are all absent, and the
lettered-subpart and non-Socratic-layout shapes require a source change. The next
10 problems should shift sources (Lessons DC / AC / Semiconductors, KSU) and cover
roughly: Circuit 7 (KCL/KVL ×2, node/mesh ×2, superposition ×1, AC/phasor/impedance
×2) + Analog 3 (diode ×1, MOSFET ×1, one more analog shape). At 25 problems the
corpus begins to be a genuine cross-source benchmark.
