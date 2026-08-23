# Seed Corpus Findings

Status: **complete at 40**. Core analysis is anchored to the seed problems studied: the
40 public Gold items in `benchmarks/seed/problems.jsonl` (`vq_seed_0001–0015`,
`vq_seed_0022–0025`, `vq_seed_0033`, `vq_seed_0034` Socratic worksheets +
`vq_seed_0017`, `vq_seed_0018` UMass + `vq_seed_0020`, `vq_seed_0026`, `vq_seed_0027`,
`vq_seed_0040`–`0042` Janzen + `vq_seed_0021` Lessons DC +
`vq_seed_0028`–`0032`, `vq_seed_0035`–`0039` KSU Circuits I) plus the two held items
(`vq_seed_0016` OpenStax, `vq_seed_0019` Janzen Thévenin). M0 is GREEN (40 problem /
32 circuit / 8 analog), so this is a running requirements ledger for `EEProblemIR`
v0.1 anchored to a complete seed corpus, not a completion report by itself.
Observations below reflect the latest facts — not an earlier pilot-only view.
**Note:** `vq_seed_0016` has been **physically isolated** out of the public Gold
corpus: it is no longer in `problems.jsonl` and its crops are no longer under
`benchmarks/seed/assets/`. It is now an on-hold item, with only locator/metadata
public in `benchmarks/research/held.jsonl` and full text + crops local-only under
`data/raw/hold/vq_seed_0016/`. Its source is held in `LICENSE_REVIEW_REQUIRED`
(see *Source policy ≠ Document policy*), so it is **not** counted toward the
public Gold gate. **`vq_seed_0019`** (Janzen Thévenin) was also held out: its
Figure 7.3.1(a) is egress-gated and unretrieved, and the earlier Gold record
re-encoded the un-fetched schematic into `question_text` (R1∥R2 in series with
R3), which violates the no-re-encode rule and leaks solution structure. Re-add it
only once the figure is retrieved. The public Gold is therefore **40 (32 circuit,
8 analog)**. Both held items remain valid data-shape observations for
`EEProblemIR`.

The seed corpus is the requirements document for `EEProblemIR` v0.1. Record
observations here rather than freezing the IR ahead of real data. Historical
change is tracked by Git; this document carries the current truth, not a changelog.

Those requirements are now encoded as **M1 — EEProblemIR v0.1**: the contract
in `src/voltquery/contracts/problem.py` (typed `inputs` as a quantity/table
union, three-axis assets with a `Waveform` kind, `parts`, `targets`,
`formulas`, explicit `schema_version`) and the 40-record projection in
`benchmarks/seed/problem_ir.jsonl`, gated by `voltquery ir validate` for
seed↔IR parity.

### M1 v0.1 encoding status (current truth)

The sections below describe the **M0 observations** that drove the contract; the
frozen-now "what each observation became" mapping is:

- §2 figure↔part association → `ProblemAsset.parts` (a subproblem-label list);
- §3 shared-page / crop geometry → `ProblemAsset.crop_rect` + `page_index`
  (for source-reproducible crops) + `parts` binding;
- §4 formula role & layout → `Formula.role` (`FormulaRole`:
  given/displayed/derived) × `Formula.layout` (`FormulaLayout`: inline/display);
- §5 subparts → recursive `Part.parts` (replacing the bool-only `is_multipart`);
- §6 structured answers → `Answer` (open `{type, content}` — not a rigid union,
  since a real answer blends scalar + drawing + explanation);
- §7 typed units → `Unit` (`symbol` + `normalized` spelling) beside prose, with
  a required unit plate (empty symbol = dimensionless);
- §10 table/quantity inputs → `Input` discriminated union
  (`QuantityInput | TableInput`).

Still deferred beyond v0.1 (M2 / v0.2+): capturing the source's own machine-parseable
answer/solution text, `CircuitGraph`/`MathIR`, and the source-answer rendering of
images-of-values fidelity.

## Composition at 40

- **Public Gold** (`benchmarks/seed/problems.jsonl`): **40 problems —
  32 circuit_theory, 8 analog_electronics.** Source mix: **21 from
  `socratic-electronics`** (Kuphaldt Socratic worksheets, 11 documents) + **2 from
  `umass-ee-fundamentals`** (`vq_seed_0017`, a diode worked example;
  `vq_seed_0018`, an inverting op-amp closed-loop-gain worked example) + **6 from
  `janzen-electricity-magnetism-circuits`** (`vq_seed_0020`, an RLC-series AC
  example; `vq_seed_0026`, RLC resonance/power; `vq_seed_0027`, a parallel-circuit
  equivalent-resistance example; `vq_seed_0040` battery emf / internal resistance;
  `vq_seed_0041` series-parallel reduction; `vq_seed_0042` RLC impedance + rms +
  average power) + **1 from `lessons-electric-circuits-dc`**
  (`vq_seed_0021`, a node-voltage method worked example) + **10 from
  `ksu-circuits-i-2022`** (`vq_seed_0028`, Lab 5 Prelab Task 1 nodal analysis of
  the Fig 1 complex DC circuit; `vq_seed_0029`, Lab 3 Prelab Task 1b series
  circuit of Fig 1; `vq_seed_0030`, Lab 8 Prelab Task 1 AC source-signal
  parameters; `vq_seed_0031`, Lab 6 Prelab Task 1 maximum-power-transfer /
  Thévenin design; `vq_seed_0032`, Lab 7 Prelab Task 1 superposition;
  `vq_seed_0035`–`0039`, Lab 9 Prelab Tasks 1/2/4, Lab 10 Prelab Task 1, and
  Lab 5 Prelab Task 2 mesh analysis). This file
  is physically public-only; its count equals the Gold count. The batch
  0022–0025 (Socratic igfet MOSFET, dcmesh mesh current, super superposition, kvl
  Kirchhoff) closes the remaining named topic gaps (mesh/KVL, superposition,
  MOSFET); 0026/0027 add Janzen (independent ecosystem) examples for resonance
  and parallel resistance; 0028 establishes KSU Circuits I as the 4th truly
  independent ecosystem, 0029 deepens it with a second problem, and
  0030/0031/0032 deepen it to five (AC params, MPT/Thévenin, superposition).
  0033/0034 close the analog probe at 8/8 with two answer-bearing Socratic analog
  problems (`vq_seed_0033`, BJT quiescent base current; `vq_seed_0034`,
  MOSFET + RC time delay), accepting the Kuphaldt concentration trade-off.
  0035–0039 take KSU to ten (transient RC/RL, RLC phasor, mesh) and
  0040–0042 take Janzen to six (DC/internal-resistance and AC power examples),
  which lands the final +8 circuit_theory to reach 32.
- **On hold** (`benchmarks/research/held.jsonl`): **2 items** — `vq_seed_0016`
  (`openstax-university-physics-v2`, University Physics Vol 2, Ch 10), held from
  the public Gold gate pending license review (imprint CC-BY-4.0 vs current
  collection CC-BY-NC-SA-4.0 + AI-training restriction); and `vq_seed_0019`
  (`janzen-electricity-magnetism-circuits`, Thévenin-equivalent), held for an
  unretrieved egress-gated figure. For both, only locator/metadata is public; full
  text + crops are local-only. See *Source diversity* and *Source policy ≠
  Document policy*.
- The analysis in *Findings* below is anchored to the 42 problems studied (40
  public Gold + the two held items). `vq_seed_0017`/`vq_seed_0018` are the first
  public problems from a web-only independent source, `vq_seed_0020`/`0026`/`0027`
  establish the Janzen independent ecosystem, `vq_seed_0021` adds the Lessons
  DC collection (still Kuphaldt/Open Book Project), and `vq_seed_0028`/`0029` give
  KSU Circuits I as the **4th truly independent author/institution ecosystem** —
  even though collection families number 5. Socratic and Lessons are both
  Kuphaldt/Open Book Project, so they count once; the independent count is
  Kuphaldt, McLaughlin/UMass, Janzen, KSU/University System of Georgia — see
  *Source diversity* and *Web-source provenance*.
- Topics observed: ohm_law, series, parallel, voltage_divider, thevenin, norton,
  equivalent_circuit, led, capacitor, rc_time_constant, rl_time_constant,
  inductor, algebraic_manipulation, bjt, emitter_follower, op_amp, voltage_gain,
  feedback, voltage_follower, **negative_feedback**, **inverting_amplifier**,
  **closed_loop_gain**, **node_voltage**, **nodal_analysis**, **kcl**,
  **mesh**, **mesh_current**, **kvl**, **bridge**, **unbalanced_bridge**,
  **superposition**, **superposition_theorem**, **current_source**,
  **ac**, **phasor**, **impedance**, **mosfet**, **insulated_gate_fet**,
  **depletion**, **enhancement**, **n_channel**, **p_channel**,
  **voltage_polarity**, **voltage_drop**, **series_voltage**, **resonance**,
  **quality_factor**, **bandwidth**, **average_power**,
  **equivalent_resistance**, **kirchhoff_junction**, **power_dissipation**.
  Open slugs; vocabulary is not frozen.

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

Yes. Twenty public problems carry **two** assets — a full-question crop
(`kind: figure`) plus a circuit crop (`kind: schematic`): `vq_seed_0002`–`0005`,
`0009`–`0011`, `0014`, `0015`, `vq_seed_0017`, and all ten KSU Circuits I items
`vq_seed_0028`–`0032`, `vq_seed_0035`–`0039` (the held `vq_seed_0016` also
does). The KSU question crops are **DOCX→PDF-rendered Prelab pages** (a
`docx`/`doc` source, so the inline-formula-web exception in the Annotation
Guide does not apply — the figure is obtained and both assets ship). `assets:
list[AssetRef]` of length 2 is exercised. The asset list is still
homogeneous in `kind` (figure = question crop, schematic = circuit crop);
no problem yet combines, say, a schematic + a waveform plot in the same item. The
`kind` enum is genuinely used: `vq_seed_0006` embeds a *pictorial* (power-supply
box + 24 VDC motor drawing) that is **not** a circuit and so is `figure`-only. See
*AssetKind ≠ AssetRole* for the role distinction this exposes.

### 2. Can a figure belong to only one part?

Still not observable. The model has no subpart structure — `assets` is a flat list,
and no problem binds a figure to one lettered part. `vq_seed_0016` is the first
lettered-subpart problem and its single schematic holds **both** sub-circuits (a)
and (b), so the shared-figure case is what we observe, not a per-part figure. If a
future problem gives *different* figures per part, this flat list is insufficient
and needs a part→figure association (which is why a figure must eventually carry a
source crop rectangle — see section 3).

### 3. Can one source image contain multiple problems?

Yes, and often. `vq_seed_0003` (dc_sp.pdf p19, Q26) and `vq_seed_0004`
(time2.pdf p15, Q24) sit on pages with adjacent questions; same page holds
`vq_seed_0002`+`0003` on ohm_law p3, `vq_seed_0007`+`0008` on dc_s p11, and
`vq_seed_0014`+`0015` share the opamp3 page. The OpenStax source adds a **two-column
page** hazard: `vq_seed_0016`'s problem 37 shares page 481 with problem 38, and both
circuits of 37 occupy a narrow left-column band. Figures are rectangular crops of a
region, not full pages. The record stores a problem-relative asset path but **not**
the source crop rectangle, so crop geometry is not yet reproducible from the record
alone.

### 4. How often are formulas inline vs display?

Cleaner at 16 than at 5, but still coarse. `has_formula: bool` means the source
**displays** a formula; it says nothing about layout or about formulas the problem
requires but does not print. Observed:

- **Displayed** (`has_formula: true`): `vq_seed_0008` (`R = R1 + R2 + R3`),
  `vq_seed_0013` (RC/LR universal step response
  `V(t) = (Vf − V0)(1 − 1/e^(t/τ)) + V0` and its current twin), `vq_seed_0014`
  (`AV = Vout / Vin(+)`), `vq_seed_0042` (the ac-generator emf
  `v(t) = (4.00 V)sin[(1.00×10⁴ rad/s)t]`).
- **Required, not displayed** (`has_formula: false`): `vq_seed_0001` (Ohm's law),
  `vq_seed_0012` (RL time constant).
- **To be derived from data** (`has_formula: false`): `vq_seed_0002` (find the V–I
  relationship from a data table).

So the single boolean conflates "involved", "stated", and "to-derive", and cannot
distinguish inline from display. M1 resolves this with `Formula.role`
(`FormulaRole`: given/displayed/derived) × `Formula.layout` (`FormulaLayout`:
inline/display). Of the captured formulas, most are **display** formulas
(`vq_seed_0008`, `vq_seed_0013`, `vq_seed_0030`, `vq_seed_0042`); `vq_seed_0014`
is the one **inline** occurrence (`AV = Vout / Vin(+)` appears mid-sentence).
The OpenStax
source introduces a *different* value-form: component values and computed answers
are rendered as **images** (rasterized math), so the extracted narrative simply has
a gap where the number sits (`R1 = 2 kΩ` survives as text only because the OpenStax
circuit labels are vector text, but inline "a resistance of [image]" values are
lost). This is a transcription fidelity issue, distinct from `has_formula`.

### 5. How should subproblems be represented?

For the first time, `is_multipart: bool` is **true**: `vq_seed_0016` (OpenStax Ch 10
problem 37) uses explicit labeled subparts `(a)… (b)… (c)… (d)…`. This is the
cross-source shape the corpus set out to confirm — the Socratic family is confirmed
**not** to contain lettered subparts (scan of ohm_law, dc_s, dc_sp, time2, thev,
bjtbias, opamp3 for `(a)/(b)/(c)` markers found none), and OpenStax does. The
remaining multi-work problems are expressed as:

- a single task with several bullet targets — `vq_seed_0009` (8 terminal-pair /
  current targets), `vq_seed_0003` (3 voltages),
- a multi-row table to complete — `vq_seed_0005`, `vq_seed_0015`,
- pre-split "Question N" headers already in the worksheet.

The boolean is still too weak regardless: it cannot enumerate parts, order them, or
attach per-part answers. M1 replaces it with **recursive `Part.parts`** (which
also lets a subpart carry its own nested subparts, e.g. 0032's (i)/(ii)/(iii)).
Being able to
verify `is_multipart` across two sources is itself a useful contract test: OpenStax answers
**only odd-numbered** problems, so a multipart problem is only `answer_available`
if its number is odd (problem 37 is odd). Caveat: `vq_seed_0016` is the sole
carrier of the lettered-subpart observation, and its source is **not** in the
released/public set until the license is resolved — so the "cross-source
subparts" claim is a *data-shape* observation, not a *public Gold* one yet.

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
- OpenStax answers are shown as numeric values in a back-of-book answer key, some
  as text, some as images (e.g. problem 31 → "a. 0.74 A; b. 0.742 A"; problem 37 →
  four image-embedded values).

`answer_available: bool` cannot represent any of these. The structured-answer gap
is the widest single gap for `EEProblemIR`.

### 7. Are units explicit?

No. Units are embedded in prose (µA, MΩ, kΩ, µF, ms, V). In M0 the inconsistent
spellings ("kΩ" vs "KΩ" across problems) were a symptom of untyped prose; M1
encodes a **typed `Unit`** (`symbol` + `normalized` spelling) beside the prose
value, with a required unit plate so a missing unit is never mistaken for a known
one (an empty symbol marks a dimensionless quantity). OpenStax uses typographic
subscripts (`V₁`, `R₁`) and formatted units (`2 kΩ`) in vector text in its
*figures*, and rasterized values in its *body text*. This still blocks solver and
unit-validation work on rasterized values and is a genuine gap.

### 8. What does Analog require that Circuit Theory does not?

Analog problems need **device/semantic models** beyond a resistor network:
- `vq_seed_0005` (common-collector BJT) needs a forward junction drop (0.7 V) plus
  the KVL relation `Vout = Vin − 0.7 V`,
- `vq_seed_0014` needs the ideal-op-amp negative-feedback model,
- `vq_seed_0015` needs the voltage-follower (unity buffer) relation.

Circuit Theory items are linear/deterministic (Ohm, series-parallel dividers, RC
time constants, and now OpenStax Kirchhoff/power) and need only network + equation
modeling. Analog therefore requires semantic knowledge (transistor/diode operating
region, op-amp rules) that is not expressible as a generic circuit graph. Device
coverage is still partial: BJT, op-amp, diode (`vq_seed_0017`), and now MOSFET
(`vq_seed_0022`, Socratic igfet Question 13) are observed.

### 9. What source location metadata is always available?

`source_id` and `document_id` are always available. `page_index` is **not** a
source-format-agnostic provenance field: the Socratic worksheets and OpenStax PDF
have a 0-based `page_index` + printed `page_label`, but the UMass web-only source
has `page_index = null` and uses `page_label` for the section title. So location
provenance must not assume a page index exists — that is a real M1
`EEProblemIR` requirement. Across the PDF sources, `page_label` and `page_index`
are **not** guaranteed to be offset by one: Socratic `thev` p22 → printed "23"
(indeed `page_index + 1`), but OpenStax `upv2` page_index 481 → printed "470"
(a fixed ~11-page offset from this PDF's front-matter). Keeping both the 0-based
index and the printed label is therefore required. OpenStax also has a per-chapter
answer key at the back, which is how answers are located — the problem number is
the lookup key, and only odd numbers appear.

### 10. What must be represented in `EEProblemIR` v0.1?

From 40 problems, minimally:
- structured **answer** — scalar-with-unit / table / expression / explanation /
  ordered subparts / drawing,
- structured **inputs** — data tables embedded in `vq_seed_0002/0004/0005/0015`
  and values-at-nodes in `vq_seed_0003/0005/0009` are prose today; a
  table/quantity model is needed,
- **subparts** enumeration (replacing `is_multipart: bool`) — now confirmed needed
  for real, by two sources,
- **asset role vs asset kind** — see *AssetKind ≠ AssetRole*,
- **figure** bound to (a) part(s), carrying a source crop rectangle,
- **typed units** separate from prose, with normalized spellings,
- **formula role** (given/displayed/derived) and **layout** (inline/display).

The M0 `SeedProblemRecord` — flat asset list, coarse booleans, prose-only
question, bool-only answer availability — records provenance and presence, not the
problem's structure. That is the deliberate M0 *ingest* shape; the requirements it
surfaced are now encoded as **M1 `EEProblemIR` v0.1** (see the *M1 v0.1 encoding
status* note), and v0.1 is the frozen target rather than a final IR — the
solving-adjacent structure (`CircuitGraph`, `MathIR`, `AnswerSchema`,
`SolutionPath`) and the source-answer capture remain deferred to M2 / v0.2+.

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

M0 resolved `role` from the filename convention (`*_question.png` vs
`*_circuit.png`) plus the `has_circuit_figure` boolean. M1 v0.1 makes this
explicit as three orthogonal axes, `kind × role × origin` (`AssetKind` ×
`AssetRole` × `AssetOrigin`), so a source schematic is `kind=schematic,
role=content_crop, origin=source` and a generated OCR crop is `kind=figure,
role=content_crop, origin=generated`.

## Source diversity (most serious gap)

**22 of the 40 public Gold problems are from the Kuphaldt/Open Book Project
ecosystem (`socratic-electronics` 21 + `lessons-electric-circuits-dc` 1); eighteen
are from three other independent ecosystems (`vq_seed_0017`, `vq_seed_0018`
UMass; `vq_seed_0020`, `vq_seed_0026`, `vq_seed_0027`, `vq_seed_0040`–`0042`
Janzen; `vq_seed_0028`–`0032`, `vq_seed_0035`–`0039` KSU Circuits I). The other independent items — `vq_seed_0016`
OpenStax and `vq_seed_0019` Janzen Thévenin — are on hold in
`benchmarks/research/held.jsonl` (license review; unretrieved figure,
respectively).** Collection families number 5 (Socratic, UMass, Janzen, Lessons
DC, KSU Circuits I) but Socratic and Lessons are both Kuphaldt, so the
**independent author/institution ecosystem count is 4** (Kuphaldt,
McLaughlin/UMass, Janzen, KSU/University System of Georgia). Diversity still
leans on a single authorial axis (Kuphaldt, 22 of 40), which remains the main
open question for the next tranche — the 4th ecosystem (KSU Circuits I,
CC-BY-4.0, via `vq_seed_0028`–`0032`, `vq_seed_0035`–`0039`) is in place and now carries ten
problems — rather than topic coverage (see *Next tranche*).
OpenStax University Physics Vol 2 is genuinely independent, but it is registered
as `status: license_review` (NOT approved/public) because its document imprint
(CC-BY-4.0) conflicts with its current collection license (CC-BY-NC-SA-4.0 +
explicit no-LLM-training clause). So it cannot yet contribute to a public Gold
corpus, and its record has been physically isolated out of `problems.jsonl` and
the public crops. Its other costs stand regardless: two-column pages, rasterized
body values, and odd-numbered-only answers each add per-problem work.

The real content gaps (KCL/KVL now covered by `vq_seed_0025`; nodal covered by
`vq_seed_0021`; mesh by `vq_seed_0023`; superposition by `vq_seed_0024`;
AC/phasor/impedance by `vq_seed_0020`; resonance & parallel resistance by
`vq_seed_0026`/`0027` from the Janzen ecosystem; MOSFET by `vq_seed_0022`) are
closed; the remaining lettered-subparts and the heavy Kuphaldt concentration
(22 of 40) are the driver of the next tranche.

## License version discrepancy

All compiled Socratic worksheets carry a footer "Creative Commons Attribution
License, **version 1.0**", while the authoritative Socratic site root and
`data/sources.yaml` record **CC-BY-3.0-US**. Both are permissive and permit
redistribution + derivatives, so the data policy is unchanged
(PUBLIC_REDISTRIBUTABLE) — but the *version* differs between the PDF imprint and
the site's declared license. This should be reconciled at the source level (pick
the authoritative site license) and noted as provenance, not silently assumed.
OpenStax is the sharper case: its **pinned PDF** prints **CC-BY-4.0**, while the
**current OpenStax pages** declare **CC-BY-NC-SA-4.0** plus an explicit
no-LLM/generative-AI-training clause. The two do not agree — see *Source policy
≠ Document policy*.

## Source policy ≠ Document policy

The Socratic license discrepancy (PDF imprint CC-BY-1.0 vs site CC-BY-3.0-US) is a
*version* mismatch that does not change the permissive policy. OpenStax is a
different animal: the license **type** differs (BY vs BY-NC-SA) and a substantive
use restriction is added (no LLM/GA training without permission). Both matter to
our pipeline.

- **Document-level license** (the artifact we pinned, sha256 `32b49efd…`): the
  compiled PDF prints "CC BY 4.0" on its title page — verified verbatim.
- **Collection-level license** (current OpenStax pages for University Physics
  Vol 2): "Creative Commons Attribution-NonCommercial-ShareAlike License" plus
  "may not be used to train large language models or in a generative-AI offering
  without OpenStax's permission."
- **Aggregator records** (BC Campus, Open Textbook Library, archive.org full
  text) still list CC BY 4.0 — likely the original 2016 edition.

These cannot be reconciled by assumption. The source is therefore in
`LICENSE_REVIEW_REQUIRED` and excluded from the public Gold corpus until the
license governing the specific artifact is confirmed. The system must support a
`Source`-level policy that is **not** simply derived from a `Document`-level
imprint: the same source can carry a document that prints a different (older)
notice than the collection currently declares. This is the concrete requirement
`vq_seed_0016` forced out, and it is a better M0 finding than the diversity gap.

## Web-source provenance (UMass, Janzen)

UMass is a **web-only Pressbooks book** — no paginated PDF, hence no
`page_index`. It is the first public problem to exercise a web-source provenance
pattern, and it fits the **existing** contracts without changes:

- `DocumentRef` is documented as "PDF/HTML" — a chapter page is registered as an
  HTML document (`url` = chapter URL, `sha256` = hash of the **fetched HTML
  bytes**, `retrieved_at`). Provenance stays reproducible.
- `SourceRef.page_index` is `null`; `page_label` carries the section title
  ("4.3 Diode Circuit Models"); `question_number` identifies the example.
- **Figure assets**: the problem carries the source's **schematic image directly**
  (`kind: schematic`) as the circuit crop, plus a **rendered-page screenshot crop**
  of the worked example as the question crop (`kind: figure`). The Annotation Guide
  defines an HTML/web-source `question_crop` as a rendered-page screenshot (not a
  PDF crop), with `page_index` null. `vq_seed_0017_question.png` was produced by
  headless page render (Edge) of the chapter.
- **A rendered crop is only trustworthy when the prompt isn't inline-formula-dense.**
  `vq_seed_0018` (6.4, inverting-gain worked example) has most of its problem
  statement as inline `quicklatex` formula images. Under a `file://` render those
  inline formula PNGs do not resolve into the element box, so the captured crop
  shows the prose with blank gaps where the values should be — a misleading
  "question" image. Rather than commit that, `vq_seed_0018` ships the **authentic
  circuit figure (Figure 6.27) as the `schematic` asset** and puts the whole
  question in `question_text` with the exact values (A = ∞, Vi = 2 V, R_I = 1 kΩ,
  R_f = 10 kΩ, 24 V unipolar supply, G = −R_f/R_I = −10). It therefore has **one**
  asset, not two, and no question_crop. Recorded as the current behavior; a better
  crop pipeline (render the formulas offline or embed a MathML/LaTeX renderer) is
  an M1+ concern.
- **Web provenance requires artifact preservation, not a URL alone.** A PDF is
  re-fetchable from its URL; a CMS page can change or disappear under the same URL.
  The `sha256` thus proves the exact bytes seen at `retrieved_at`, not future
  reproducibility. For public-redistributable HTML sources, keep a raw snapshot
  (`data/snapshots/<doc>.html` + `content_sha256` + `retrieved_at` +
  `canonical_url`) or a WARC/raw local archive. Recorded here; not an M0 blocker.
- **Answer policy**: UMass's per-chapter **"Problems" sections give no
  answers**. The answer-bearing content is the **worked "Example:" boxes** in the
  concept sections. Per the seed policy, `vq_seed_0017` is mined from a worked
  *example* (real problem + its stated solution) so `answer_available: true`.
- **Formulas are rasterized** (Pressbooks renders math as `quicklatex` PNGs) —
  same fidelity gap as OpenStax body text; `has_formula` records presence, the
  expression itself is not extractable text.

Both UMass and the Janzen work show that the genuinely-verified independent
CC-BY sources are **textbooks**, not problem-set-heavy worksheets: they are
usable but need worked-example mining (answer-bearing) rather than a straight
"Problems" lift.
- **Janzen (3rd ecosystem), vq_seed_0019 — held out for an unretrieved figure.**
  The Thévenin worked example (Example 7.3.1) is complete in the source text, but
  its circuit snapshot (Figure 7.3.1(a)) is **not obtainable** under the current
  acquisition constraints: CircuitBread is Cloudflare-gated (403), the
  openpress.usask.ca mirror is egress-gated (401, and the figure asset returned a
  tiny HTML error), and the eCampusOntario repo serves the PDF at ~8 KB/s (48 MB ≈
  100 min). Rather than reconstruct a schematic from prose (which the golden rule
  forbids), 0019 was *initially* recorded with a narrative re-encode plus
  `has_circuit_figure: false`. That was wrong on two counts: it re-encoded the
  un-fetched circuit (R1∥R2 in series with R3) into `question_text` and leaked
  solution structure, and it flipped the observable `has_circuit_figure` to reflect
  fetch success instead of source content. It is therefore **held out of Gold**
  (`benchmarks/research/held.jsonl`) until Figure 7.3.1(a) is retrieved and the
  record ships real assets. The figure gap remains an **access follow-up**. This is
  the correction that sharpened the Annotation Guide rule (§`assets`).

## Next tranche (0033+)

- **OpenStax is on hold** — `vq_seed_0016` stays in the corpus but is excluded
  from the public Gold gate, and **no further OpenStax problems are collected**
  until its license is confirmed. Its KCL/KVL, RC, and (Ch 15) AC/phasor/impedance
  slots are deferred, not filled.
- **Diversify to genuinely independent, verified CC-BY sources** instead. A-grades
  were independently verified 2026-08-22 (see `data/source_candidates.yaml`):
  - **VERIFIED CC BY 4.0** (promoted to `approved` public and now mined):
    - UMass **Applied Electrical Engineering Fundamentals** (David J. McLaughlin,
      ECE 361) — 2 problems (`vq_seed_0017`, `vq_seed_0018`),
    - Daryl Janzen **Introduction to Electricity, Magnetism, and Circuits** — 6
      problems (`vq_seed_0020`, `vq_seed_0026`, `vq_seed_0027`, `vq_seed_0040`,
      `vq_seed_0041`, `vq_seed_0042`),
    - **KSU Circuits I** (`ksu-circuits-i-2022`, CC-BY-4.0, University System of
      Georgia) — 10 problems (`vq_seed_0028`, Lab 5 Prelab Task 1 nodal analysis;
      `vq_seed_0029`, Lab 3 Prelab Task 1b series circuit; `vq_seed_0030`, Lab 8
      Prelab Task 1 AC signal parameters; `vq_seed_0031`, Lab 6 Prelab Task 1
      MPT/Thévenin design; `vq_seed_0032`, Lab 7 Prelab Task 1 superposition;
      `vq_seed_0035`–`0039`, Lab 9 Prelab Tasks 1/2/4, Lab 10 Prelab Task 1, and
      Lab 5 Prelab Task 2 mesh analysis);
      this is the **4th truly independent ecosystem**, now carrying 10 problems,
  - **NOT public-redistributable** (rejected under the public policy; keep
    research-local only — both are *NonCommercial*):
    - KSU **Laboratory Manual for Engineering Electronics** — was **rejected** as
      non-commercial (GALILEO OLM record listed CC BY-NC), but **re-opened as
      `license_review` 2026-08-22**: the *current* OpenALG project page AND the
      *current* GALILEO `/2` record (EE 3401, Summer 2019) both declare **CC BY
      4.0**. Genuine version/date conflict with the earlier BY-NC reading — do
      **not** promote on the page claim alone (see `data/source_candidates.yaml`);
      pin the exact artifact's printed license first. Fills diode/BJT/MOSFET/op-amp
      analog gap **if** confirmed,
    - Fiore **Semiconductor Devices: Theory and Application Lab Manual** —
      author's own MVCC page licenses it **CC BY-NC-SA 3.0** (the per-work NC-SA
      trap is confirmed; only a pressbooks catalog row said CC BY).
  - LibreTexts **page/book-level** CC-BY-4.0 works (e.g. Charles Kann Digital
    Circuit Projects) — never treat `libretexts.org` as a single source license.
- **Topic coverage is largely closed** — nodal (`vq_seed_0021`, `vq_seed_0028`),
  mesh (`vq_seed_0023`), superposition (`vq_seed_0024`), KCL/KVL (`vq_seed_0025`),
  MOSFET (`vq_seed_0022`) are filled; AC/phasor/impedance via `vq_seed_0020`;
  resonance and parallel-resistance via `vq_seed_0026`/`0027`. The remaining open
  driver is **independent-ecosystem diversity**, not topic coverage: 22 of 40
  public Gold problems are still from the Kuphaldt ecosystem (Socratic 21 +
  Lessons 1). 0026–0027 strengthened Janzen and **0028 delivered the 4th ecosystem
  (KSU Circuits I)**, deepened by **0029 (Lab 3 series circuit)** and then by
  **0030 (Lab 8 AC) / 0031 (Lab 6 MPT) / 0032 (Lab 7 superposition)** and
  **0035–0039 (Lab 9 transient, Lab 10 RLC phasor, Lab 5 mesh)** — KSU now
  carries ten problems. M0 is GREEN (40 / 32 circuit / 8 analog), so the seed
  corpus is complete; further independent sources would push Kuphaldt below 22 of
  40 but are post-M0 follow-up. Note `answer_available` is usually false for the
  KSU student prelabs.
- **Analog probe is at 8/8 (done)**: BJT, op-amp ×3, diode, MOSFET — now closed by
  `vq_seed_0033` (BJT quiescent base current, Socratic bjtbias Q13) and
  `vq_seed_0034` (MOSFET + RC time delay, Socratic igfet Q31). The 2026-08-22
  re-run confirmed KSU Engineering Electronics' artifact prints NO license, so it
  stays `license_review` and is NOT counted for public Gold; the two remaining
  analog items were therefore pulled from the already-verified-permissive
  Kuphaldt Socratic worksheets (accepting the concentration trade-off the
  composition notes above). Both ship a question crop + a circuit crop, and,
  unlike the KSU prelabs, print their answers (IB = 38.3 µA; tdelay = 2.05 s),
  so `answer_available: true` for both.

The `vq_seed_0020`/`0026`/`0027` Janzen, `vq_seed_0021` Lessons DC, and
`vq_seed_0028`–`0032` KSU items establish the non-Socratic collections; independence is
now **4 ecosystems** (Kuphaldt, McLaughlin/UMass, Janzen, KSU/University System of
Georgia) — Lessons DC adds a collection, not an ecosystem. Circuit
set now covers Ohm, series/parallel divider, Thevenin/Norton, RC/RL time constants,
nodal, mesh, superposition, KVL, AC/phasor/impedance, resonance, and parallel
resistance.

**KSU acquisition succeeded** (this replaces the earlier "remains blocked"
reading). The deepened crawler — Stoke `CrawlerClient` with curl-cffi `chrome120`
TLS impersonation + browserforge request headers + per-host rate limiter, plus
content-type-aware byte persistence and a sha256 manifest (`data/raw/acq.py`) —
fetched the full KSU Circuits I resource set: the lab manual
(`circuits_i_lab_manual.docx`, 11.5 MB, also extracted to text/PDF and its
figures) and all six binary attachments (Prelab-2..10 and Lab-1..10 datasheets,
the App-install guide, etc.). The working entry point was the OpenALG/MathWorks
CDN (`cdn.alg.manifoldapp.org`), which served the artifacts directly. The primary
`oer.galileo.usg.edu` gateway remains Cloudflare JavaScript bot-gated and was not
forced (per the anti-scraping rule). From this acquisition `vq_seed_0028`–`0032`
and `vq_seed_0035`–`0039` were mined (ten problems). KSU's own App-guide PDF is CC BY 4.0; the manual's
prelabs print no answers, so `answer_available: false` for the mined items.
