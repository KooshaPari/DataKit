# DataKit

Comprehensive data management and integration platform for modern data pipelines. Provides type-safe data modeling, schema evolution, ETL pipeline orchestration, data quality validation, and lineage tracking across multiple storage backends (SQL, NoSQL, cloud data warehouses).

## Overview

**DataKit** is the unified data layer for the Phenotype ecosystem, bridging operational systems and analytics platforms. It provides declarative data pipelines, automatic schema evolution, built-in quality controls, and consistent APIs across all data storage systems while maintaining full auditability and lineage.

**Core Mission**: Eliminate data integration complexity through type-safe modeling, schema versioning, automated quality validation, and unified pipeline orchestration.

## Technology Stack

- **Languages**: Python (primary), Rust (performance-critical components), Go (for stream processing)
- **Core Components**:
  - Data modeling with schema versioning and evolution
  - ETL pipeline orchestration (Airflow, Temporal compatible)
  - Data quality frameworks (Great Expectations integration)
  - Schema registry and versioning
  - Lineage tracking and data governance
- **Storage Backends**: PostgreSQL, MongoDB, Snowflake, BigQuery, Redshift, Parquet
- **Serialization**: Protocol Buffers, Parquet, JSON Schema
- **Observability**: Structured logging, lineage metrics, pipeline monitoring

## Key Features

- **Type-Safe Data Modeling**: Declarative schemas with strong type guarantees across languages
- **Schema Evolution**: Automatic detection and migration of schema changes
- **ETL Orchestration**: Declarative pipeline definitions with DAG-based scheduling
- **Data Quality Validation**: Built-in validators and custom rule engines
- **Lineage Tracking**: Complete data provenance from source to destination
- **Multi-Backend Support**: Unified API across SQL, NoSQL, and cloud DW systems
- **Consistency Guarantees**: ACID semantics with automatic conflict resolution
- **Data Governance**: Audit trails, access control, PII detection

## Quick Start

```bash
# Clone and explore
git clone <repo-url>
cd DataKit

# Review governance and architecture
cat CLAUDE.md          # Project governance & development philosophy
cat PRD.md             # Full product requirements
cat AGENTS.md          # Agent operating contract

# Explore structure
ls -la python/         # Python data models
ls -la rust/           # Rust performance components
ls -la go/             # Go stream processing
ls -la docs/           # Documentation and examples

# Build and test (Python)
cd python && pip install -e .
pytest tests/
```

## Project Structure

```
DataKit/
├── python/            # Python data modeling & orchestration
│   ├── datakit/
│   │   ├── models/    # Schema definitions, validators
│   │   ├── pipeline/  # ETL pipeline orchestration
│   │   ├── quality/   # Data quality frameworks
│   │   └── storage/   # Backend adapters
│   └── tests/
├── rust/              # Performance-critical components
│   ├── crates/
│   │   └── datakit-core/  # Schema validation, lineage
│   └── Cargo.toml
├── go/                # Stream processing components
├── docs/              # Full documentation
└── CLAUDE.md, AGENTS.md, PRD.md
```

## Use Cases

| Scenario | DataKit Feature | Example |
|----------|-----------------|---------|
| Schema Evolution | Auto-detection & migration | App adds new field → DW auto-updates |
| Data Quality | Validation rules & monitoring | Missing values flagged before load |
| Lineage | Full provenance tracking | Trace data from source → analytics |
| ETL Orchestration | Declarative pipelines | Define data flows as code |
| Multi-Backend | Unified API | Same code for Postgres, BigQuery, Snowflake |

## Related Phenotype Projects

- **[cloud](../cloud)** — Uses DataKit for multi-tenant data isolation and pipelines
- **[PhenoLibs](../PhenoLibs)** — Shared data models and utilities
- **[PhenoObservability](../PhenoObservability)** — Data quality metrics and observability integration
