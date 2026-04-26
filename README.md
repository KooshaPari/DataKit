# DataKit

Storage and events SDK for the Phenotype ecosystem. Polyglot building blocks for databases, caches, object storage, and event streams — shipped as Go, Rust, and Python bindings from a single source of truth.

**Part of the [Phenotype org](https://github.com/KooshaPari) ecosystem.** Shares CI reusables and conventions with [phenoShared](https://github.com/KooshaPari/phenoShared). Follows org conventions: conventional commits, `<type>/<topic>` branching, Apache-2.0 + MIT dual license.

## What it does

Every Phenotype service eventually needs the same things: a key/value cache, a relational or document store, an object bucket, and an event bus. DataKit provides idiomatic Go, Rust, and Python wrappers around those primitives so services never have to pick (or misconfigure) a client library ad-hoc.

The Python bindings are the most mature surface today; Go and Rust bindings mirror the same contracts.

## Status

**Active.** Core Python packages (`pheno-database`, `pheno-caching`, `pheno-storage`, `pheno-events`, `db-kit`) are in use by downstream services. See [CHANGELOG.md](./CHANGELOG.md).

## Requirements

- **Python** (primary): 3.11+ with `uv` or `pip`
- **Go**: 1.22+
- **Rust**: stable, edition 2021
- Backing services at runtime depend on which adapter you use: Postgres, Redis, MinIO/S3, NATS, etc.

## Quick start

### Python

```bash
cd python
uv sync                    # or: pip install -e '.[dev]'
uv run pytest              # or: pytest
uv run ruff check .
uv run mypy .
```

### Go

```bash
cd go
go build ./...
go test ./...
```

### Rust

```bash
cd rust
cargo build --workspace
cargo test --workspace
cargo clippy --workspace --all-targets -- -D warnings
```

## Structure

```
python/
  pheno-database/   # SQL/NoSQL database client primitives
  pheno-caching/    # Cache adapters (Redis, in-memory, tiered)
  pheno-storage/    # Object storage (MinIO / S3-compatible)
  pheno-events/     # Event bus adapters (NATS, etc.)
  db-kit/           # Higher-level database convenience layer
go/                 # Go bindings mirroring the Python contracts
rust/               # Rust bindings mirroring the Python contracts
```

## Design principles

- **Contracts first.** Each binding implements the same logical contract; semantic drift is a bug.
- **Wrap, do not hand-roll.** Uses well-maintained upstream clients (psycopg, redis-py, minio, nats.py, etc.); adds Phenotype policy on top.
- **Fail loudly.** Missing required config (connection URL, credentials) is a hard error; no silent fallback to in-memory stubs in production.
- **Observability baked in.** Adapters emit structured events suitable for Phenotype's observability stack.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Ownership lives in [CODEOWNERS](./CODEOWNERS). Report security issues per [SECURITY.md](./SECURITY.md).

## License

Dual-licensed under Apache-2.0 OR MIT. See [LICENSE-APACHE](./LICENSE-APACHE) and [LICENSE-MIT](./LICENSE-MIT).
