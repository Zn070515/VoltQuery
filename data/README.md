# Data

VoltQuery source material and provenance metadata. Content policy mirrors the
Gold / Silver / Bronze layers of the benchmark:

```text
Bronze  raw imported material                       (not redistributable by default)
Silver  parsed problem candidates                   (reviewed on demand)
Gold    the public benchmark, manually checked      (never silently regenerated)
```

## Layout

- `sources.yaml` — the source registry. Every source entry carries machine-readable
  license metadata (`LicenseMetadata`); license is data, not documentation.
- `raw/` — downloaded source material. Git-ignored until a specific file/version is
  verified as redistributable and repo policy permits inclusion.
- `seed/` — reserved for curated, verified local assets. The manual, checked Gold
  corpus itself is committed at `benchmarks/seed/` (see the repo root).

## Data policy

`data_policy` is one of `public_redistributable`, `research_only`, `private_local`,
or `unknown`. Unknown is treated as restrictive: content is **not** copied into the
public Gold corpus until the exact license of the specific file/version in use has
been independently verified and `license.verified` is `true`.

Public Gold data must be `PUBLIC_REDISTRIBUTABLE` and must explicitly allow
`redistribution`. Research-only or private-local material is kept in a separate
corpus profile, never mixed into the public benchmark.
