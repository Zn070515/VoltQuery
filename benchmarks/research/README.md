# Research / On-Hold Benchmark Material

This directory is the **public, tracked** shelf for material that is *not*
eligible for the public Gold corpus (`benchmarks/seed/`) but is useful as a
locator/metadata index.

## Boundary contract

`benchmarks/seed/` is the public-redistributable Gold corpus. It is kept
**physically** public-only: every record there is fully verifiable and the
corpus count equals the Gold count. Nothing is filtered out at runtime — a
problem's presence in `benchmarks/seed/problems.jsonl` *means* it belongs to
the public Gold gate.

`benchmarks/research/` is for items whose **locator + metadata** are public
and redistributable, but whose **full question text and/or crop assets are
not** — either because the governing license is unresolved, or because only
the descriptive metadata may be published.

## What is public here

For each on-hold/held item only metadata is published:

- identifier
- source ID + source/document URL
- document checksum (SHA-256)
- page locator (0-based index + printed label) and question number
- domain / topic tags
- license status

## What stays local-only

The full question narrative and any crop assets are **never** committed to
the public repo. They live under the gitignored `data/raw/` tree (e.g.
`data/raw/hold/vq_seed_0016/`). `data/raw/` is excluded from git.

## Held items

See `held.jsonl`. Currently it holds only `vq_seed_0016` (OpenStax University
Physics Vol 2, Ch 10 problem 37), whose source is `LICENSE_REVIEW_REQUIRED`
because its document imprint (CC-BY-4.0) conflicts with the current OpenStax
collection license (CC-BY-NC-SA-4.0 + no-LLM/generative-AI-training clause).
See `docs/development/SEED_CORPUS_FINDINGS.md` → *Source policy ≠ Document
policy*.
