> **Work-state:** active | `[##########]` | 100%
>
> Data transformation and ETL toolkit for Phenotype.
> First real implementation increment with hexagonal-architecture core.

# DataKit

**Data transformation and ETL framework** for the Phenotype ecosystem.

## Overview

DataKit is a unified data transformation and ETL (Extract-Transform-Load) framework providing:

- **Streaming data pipelines** — orchestrate data flows with source → transform → sink
- **Type-safe transformations** — compile-time guarantees via the port/trait pattern
- **Multi-backend support** — pluggable adapters for files, databases, APIs, and more
- **Hexagonal architecture** — domain core isolated from infrastructure through trait ports

## Architecture

```
┌──────────────────────────────────────────┐
│               Pipeline                    │
│   (orchestrates source → transforms → sink)│
└──────┬──────────┬────────────┬───────────┘
       │          │            │
  ┌────▼──┐  ┌────▼────┐  ┌───▼────┐
  │Source │  │Transforms│  │  Sink  │
  │(Port) │  │  (Port)  │  │ (Port) │
  └───┬───┘  └────┬────┘  └───┬────┘
      │           │           │
  ┌───▼────┐  ┌───▼────┐  ┌──▼─────┐
  │ CsvSrc │  │ Upper  │  │JsonSink│
  │(Adapt) │  │(Adapt) │  │(Adapt) │
  └────────┘  └────────┘  └────────┘
```

### Layers

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **Domain** | `src/domain/` | Core types (`Record`, `Pipeline`) — no external dependencies |
| **Port** | `src/port/` | Trait interfaces (`DataSource`, `DataSink`, `Transform`) |
| **Adapter** | `src/adapter/` | Concrete implementations (`CsvSource`, `JsonSink`, `UppercaseTransform`) |

## Usage

### Add to your project

```toml
[dependencies]
datakit = { git = "https://github.com/KooshaPari/DataKit" }
```

### Quick start

```rust
use datakit::{
    adapter::{csv_source::CsvSource, json_sink::JsonSink, uppercase_transform::UppercaseTransform},
    domain::pipeline::Pipeline,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let source = CsvSource::new("input.csv");
    let sink = JsonSink::new("output.json");
    let transform = UppercaseTransform::new("name");

    let mut pipeline = Pipeline::new(
        Box::new(source),
        vec![Box::new(transform)],
        Box::new(sink),
    );

    pipeline.run()?;
    println!("Pipeline completed successfully");
    Ok(())
}
```

## Status

**ACTIVE** — First real implementation increment. Core hexagonal architecture is in place with:

- `Record` domain type (field map with serde support)
- `Pipeline` orchestrator (batch + streaming modes)
- `DataSource` / `DataSink` / `Transform` port traits
- `CsvSource`, `JsonSink`, `UppercaseTransform` adapter implementations
- Unit tests on every module + integration tests
- \>=85% line coverage on new code

## Development

```bash
# Build
cargo build

# Run all tests
cargo test

# Check lint
cargo clippy -- -D warnings

# Check formatting
cargo fmt --check

# Generate coverage report (requires cargo-tarpaulin)
cargo tarpaulin
```

## License

MIT — see [LICENSE](./LICENSE).
