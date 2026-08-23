# Seed Benchmark Corpus

Target: **40 manually reviewed** seed problems.

- Circuit Theory: 32
- Analog Electronics probe: 8

`problems.jsonl` is the input to the M0 validation framework and the M3+
retrieval benchmark. It is populated by the content task with manually reviewed
problems sourced from verified licenses.

`problem_ir.jsonl` is the derived **M1 IR corpus**: one `EEProblemIR` v0.1
record per seed problem (same id set, verified by `voltquery ir validate`),
carrying the seed's identity fields verbatim plus structure — `parts`, typed
`inputs`, three-axis `assets`, `targets`, and `formulas`. `answer` is `None` by
convention (see `docs/development/SEED_CORPUS_FINDINGS.md`).

Current status: **40 / 40 problems collected** (32 Circuit Theory,
8 Analog Electronics). Each is fully annotated per
[`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md). **M0 is complete** — the
`milestone m0` gate is GREEN (40 problem / 32 circuit / 8 analog). **M1 is in
progress** — all 40 records populate `problem_ir.jsonl` and `ir validate`
reports 0 issues.

The corpus now spans **4 truly independent author/institution ecosystems**. The
Kuphaldt / Open Book Project works (`socratic-electronics` and the `lessons-*`
volumes) are one ecosystem, so they count once for independence — no more than a
single stylistic/authorial axis.

- **Kuphaldt / Open Book Project** — 21 problems from `socratic-electronics`
  across 11+ worksheet documents (Ohm's law, series/parallel, Thevenin/Norton,
  RC/RL time constants, op-amp, MOSFET, BJT, mesh current, superposition,
  Kirchhoff's laws; the analog records `vq_seed_0005` common-collector BJT,
  `vq_seed_0014`/`0015` op-amp, `vq_seed_0022` MOSFET ID, and the closing pair
  `vq_seed_0033` BJT quiescent base current + `vq_seed_0034` MOSFET RC time
  delay) + 1 problem from `lessons-electric-circuits-dc`: `vq_seed_0021`
  node-voltage method (Chapter 10 worked example, real vector figure assets).
- **McLaughlin / UMass Amherst** (`umass-ee-fundamentals`, web-only Pressbooks
  chapters) — 2 problems: `vq_seed_0017` diode/LED forward-bias, and
  `vq_seed_0018` the 6.4 negative-feedback inverting-op-amp example (Figure 6.27
  schematic asset).
- **Janzen / CircuitBread** (`janzen-electricity-magnetism-circuits`,
  whole-book Pressbooks XHTML export) — 6 problems, all fully self-contained
  text problems stating every value verbatim with no figure dependency:
  `vq_seed_0020` (Example 12.3.1 RLC-series AC, R/L/C/f/V),
  `vq_seed_0026` (Example 12.5.2 power transfer in an RLC series circuit at
  resonance, R/L/C/V), `vq_seed_0027` (Example 6.2.2 analysis of a parallel
  circuit, R₁/R₂/R₃/V), `vq_seed_0040` (Example 6.1.1 battery internal
  resistance / terminal voltage / load power), `vq_seed_0041` (Example 6.2.4
  series-parallel reduction to find the supply voltage), and `vq_seed_0042`
  (Example 12.4.1 RLC impedance + rms voltage + average power).
- **Das / Chin / Hill, University System of Georgia** (`ksu-circuits-i-2022`,
  `ksu-circuits-i-lab-manual` DOCX) — 10 problems:
  - `vq_seed_0028` Lab Exercise #5 Prelab Task 1, nodal analysis of the Fig 1
    complex DC circuit (R1=1 kΩ, R2=2.2 kΩ, R3=820 Ω, R4=220 Ω, R5=470 Ω,
    R6=330 Ω, Vs=8 V; full question crop + real vector schematic asset).
  - `vq_seed_0029` Lab Exercise #3 Prelab Task 1b, the Fig 1 series circuit
    (Vs=9 V; R1=Green–Blue–Brown, R2=Red–Red–Brown; find VR2 and I; authentic
    series-schematic asset).
  - `vq_seed_0030` Lab Exercise #8 Prelab Task 1, AC source-signal parameters
    (VS(t)=5sin(12566.4t); R1=2.2 kΩ, R2=820 Ω, C=82 nF, L=68 mH; find
    frequency/period/amplitude/peak-to-peak/rms; symbolic series-schematic
    asset; has_formula true).
  - `vq_seed_0031` Lab Exercise #6 Prelab Task 1, maximum-power-transfer design
    via Thévenin (RTH=RL=1 kΩ, VTH=VOC=6.47 V; VS=10 V, R3=470 Ω; design
    R1/R2; network-schematic asset).
  - `vq_seed_0032` Lab Exercise #7 Prelab Task 1, superposition (12 V/5 V
    sources, RL to find; power 87.11 mW / 3.44 mW; circuit-schematic asset;
    is_multipart true for (i)(ii)(iii)).
  - `vq_seed_0035` Lab Exercise #9 Prelab Task 1 (Circuit 1), LTspice simulation
    of Circuit 1: sketch the series resistive divider (R1=1 kΩ, R2=2.2 kΩ on
    Fig 8), set Vs as a 2 V Pulse (Von=2 V, Ton=0.5 ms, Tperiod=1 ms,
    Trise/Tfall=10 ns), then run a Transient analysis to 2 ms.
  - `vq_seed_0036` Lab Exercise #9 Prelab Task 2 (Circuit 2), series RC
    transient (R1=1 kΩ, C1=82 nF; find Vc/Vr across time + τ).
  - `vq_seed_0037` Lab Exercise #9 Prelab Task 4 (Circuit 3), RL transient
    (R1=2.2 kΩ, R2=10 kΩ, L1=68 mH, R3=220 Ω; find inductor current + τ via
    the Thévenin resistance at L1).
  - `vq_seed_0038` Lab Exercise #10 Prelab Task 1, series RLC phasor/resonance
    (R1=820 Ω, C1=82 nF, L1=68 mH, Vs=4 Vpp sine; jXL/−jXC/Z(polar)/VR1/PF at
    1–4 kHz + resonant frequency; is_multipart true for Task 1a/1b).
  - `vq_seed_0039` Lab Exercise #5 Prelab Task 2, mesh analysis of the same
    Fig 1 circuit as `vq_seed_0028` (compute mesh currents I1/I2/I3).
  Each of the ten ships a **full question crop** (`kind: figure`, a DOCX-rendered
  Prelab page) plus its **schematic crop** (`kind: schematic`).
  This is the 4th truly independent ecosystem; CC-BY-4.0 and verified.
  `answer_available` is false for all ten — they are student prelab exercises
  and the manual prints no answer.

`vq_seed_0019` (Janzen Thévenin, Example 7.3.1) has been **held out of the public
Gold corpus** to `benchmarks/research/held.jsonl`. Its Figure 7.3.1(a) is
egress-gated (CircuitBread 403 / openpress 401 / repo ~8 KB/s) and not yet
retrieved; the earlier Gold record re-encoded the un-fetched schematic into
`question_text` (R1∥R2 in series with R3), which violates the annotation guide's
no-re-encode rule and leaks solution structure. Re-add it only once the figure is
obtained and the record ships real assets.

`vq_seed_0016` (OpenStax University Physics Vol 2, Ch 10) — the first
lettered-subpart problem and the first genuinely independent candidate — has
been **moved out of the public Gold corpus** to `benchmarks/research/held.jsonl`.
Its source is under `LICENSE_REVIEW_REQUIRED` (the pinned PDF prints CC-BY-4.0,
but the current OpenStax collection license is CC-BY-NC-SA-4.0 with an
additional no-LLM-training clause), so it is **not counted toward the public
Gold gate** and no further OpenStax items are collected until the governing
license is confirmed. The full question text + crops are held local-only under
the gitignored `data/raw/hold/vq_seed_0016/`; only locator/metadata is public.

KSU Engineering Electronics is held under **`license_review`** (genuine
version-conflict: the earlier GALILEO record said CC BY-NC, the current OpenALG
project page and GALILEO `/2` record both declare CC BY-4.0 — do not promote on
the page claim alone; pin the exact artifact's license first). Fiore's
semiconductor lab (CC BY-NC-SA 3.0) was verified as **non-commercial and
rejected** for the public corpus — see
[`data/source_candidates.yaml`](../../data/source_candidates.yaml) and
[`docs/development/SEED_CORPUS_FINDINGS.md`](../../docs/development/SEED_CORPUS_FINDINGS.md).

## Gold / Silver / Bronze

- **Bronze** — raw imported material, no parsing guarantee.
- **Silver** — automatically parsed candidates, optionally sampled for review.
- **Gold** — manually checked evaluation set, isolated from automatic
  regeneration.

`problems.jsonl` is the Gold benchmark. Local assets live under `assets/`.
