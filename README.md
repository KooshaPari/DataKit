# DataKit — Moved

> **DataKit has moved to [`KooshaPari/phenotype-python-sdk`](https://github.com/KooshaPari/phenotype-python-sdk/tree/main/packages/data-kit).**
>
> This repository is **archived and read-only** as of 2026-06-12. It is retained
> as a husk per `RATIONALIZATION_PLAN.md` (org invariant: "Husks remain as
> archived redirects — never deleted."). All new work, issues, and PRs should
> be opened against the SDK monorepo.

## New home

| Was (this repo, archived) | Is now (active) |
|---|---|
| `KooshaPari/DataKit` (this repo) | [`KooshaPari/phenotype-python-sdk/packages/data-kit/`](https://github.com/KooshaPari/phenotype-python-sdk/tree/main/packages/data-kit) |
| Python: `pheno-database`, `pheno-caching`, `pheno-storage`, `pheno-events`, `db-kit` | Python: `pheno_database`, `pheno_caching`, `pheno_storage`, `pheno_events`, `db_kit` (same packages, underscore-named under uv workspace) |
| Go bindings: `go/` | Go bindings: `packages/data-kit/go/` |
| Rust bindings: `rust/` (workspace crates) | Rust bindings: `packages/data-kit/rust/` |
| Standalone PyPI: `pheno-db-kit` | Published from `packages/data-kit/python/db_kit` with extras `[supabase]`, `[neon]`, `[turso]`, `[all]`, `[dev]` |

The SDK monorepo also publishes the high-level `pheno-db-kit` package as a
standalone PyPI artifact with the same feature surface that was previously
distributed from this repo's `db-kit/` subdirectory.

## What this archive contains

This repo is preserved for **historical reference and provenance** only. The
following records live here:

- **51 PRs** (48 merged, 1 open, 2 closed-unmerged) documenting the original
  standalone build-out, hygiene bootstrap, and event-sourcing migration.
- **The branch history** showing the full evolution from
  `feat/journey-impl` → cargo-deny → event-bus hardening → eventual merge into
  the SDK monorepo (see PR #2 on `phenotype-python-sdk`:
  *"feat: absorb AuthKit/DataKit/McpKit/ObservabilityKit/ResilienceKit/TestingKit/PhenoKits into python SDK monorepo (rationalization)"*).
- **ADR records** at `ADR.md` and `docs/adr/` — these were copied verbatim
  into `phenotype-python-sdk/packages/data-kit/ADR.md` and
  `phenotype-python-sdk/packages/data-kit/docs/adr/`.

## Migration history

| Date | Event |
|---|---|
| 2026-04-05 | Repo created (commit `0119338` + `d86c48e` + `22ec9ed`) |
| 2026-04-24 | License, hygiene, CI, security, scorecard baseline merged |
| 2026-04-26 | `chore/migrate-vendored-to-phenoshared` merged (#19) — `phenotype-cache-adapter` and `phenotype-event-sourcing` Rust crates moved to canonical `phenoShared` |
| 2026-04-28 | `feat/journey-impl` merged (#40) — journey-traceability + iconography |
| 2026-05-01 | `chore: FUNDING.yml + SECURITY.md + python migration` (#41) |
| 2026-05-04 | `chore(ci): add cargo-deny workflow` (#44) — final standalone commit on `main` |
| 2026-05-31 | **`phenotype-python-sdk` PR #2 merged**: *"feat: absorb AuthKit/DataKit/McpKit/ObservabilityKit/ResilienceKit/TestingKit/PhenoKits into python SDK monorepo (rationalization)"* — the canonical merger event |
| 2026-06-12 | This redirect README installed; PR #51 closed as superseded |

## Open work in this archive

- **PR #51** (`chore(gitignore): adopt shared python template from phenotype-tooling`)
  was part of a fleet-wide rollout (V14-T3-1e wave 2). The equivalent change
  must be applied in the SDK monorepo at
  `phenotype-python-sdk/.gitignore` (it is currently still using the pre-merge
  gitignore). Re-open as a PR against `phenotype-python-sdk` to complete the
  rollout for the SDK.

## License

Dual-licensed under Apache-2.0 OR MIT. See `LICENSE-APACHE` and `LICENSE-MIT`
in this archive, or the equivalent files in
[`phenotype-python-sdk`](https://github.com/KooshaPari/phenotype-python-sdk).

---

*Redirect installed 2026-06-12 per `RATIONALIZATION_PLAN.md` §"ARCHIVE / HUSK"
(DataKit → phenotype-python-sdk).*
