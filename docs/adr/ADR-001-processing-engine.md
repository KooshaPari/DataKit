# ADR-001: Data Processing Engine Architecture

**Document ID:** PHENOTYPE_DATAKIT_ADR_001  
**Status:** Accepted  
**Last Updated:** 2026-04-03  
**Author:** Phenotype Architecture Team  
**Deciders:** Phenotype Architecture Team  
**Technical Story:** DataKit multi-language data processing foundation

---

## Table of Contents

1. [Context](#context)
2. [Decision](#decision)
3. [Consequences](#consequences)
4. [Architecture](#architecture)
5. [Code Examples](#code-examples)
6. [Cross-References](#cross-references)

---

## Context

The Phenotype ecosystem requires a robust data processing engine that can handle event sourcing, real-time event distribution, caching, storage abstraction, and database management across multiple programming languages. The system must serve diverse workloads:

- **Event Sourcing**: Audit-heavy domains requiring cryptographic integrity verification of all state changes
- **Real-Time Communication**: Decoupled service-to-service communication with backpressure handling
- **Multi-Tier Caching**: Performance optimization through hierarchical cache with automatic promotion
- **Storage Abstraction**: Unified interface across S3, local filesystem, Supabase, and in-memory backends
- **Database Management**: Multi-platform database access (PostgreSQL, Supabase, Neon) with connection pooling

### Requirements

| Requirement | Priority | Description |
|-------------|----------|-------------|
| Cryptographic integrity | Critical | All events must be tamper-evident |
| Multi-language support | High | Rust, Go, Python implementations |
| Async-first | High | Non-blocking I/O for all operations |
| Pluggable backends | High | Storage and database abstraction |
| Performance | High | Sub-millisecond for in-memory operations |
| Audit capability | Critical | Complete event replay and verification |
| Developer ergonomics | Medium | Simple APIs with sensible defaults |

### Constraints

- Must integrate with existing Phenotype infrastructure (Infrakit, contracts)
- Must support eventual migration to persistent backends
- Must maintain backward compatibility across language boundaries
- Must operate within resource constraints of containerized deployments

### Options Considered

#### Option 1: Single-Language Core (Rust Only)

```
┌─────────────────────────────────────┐
│         Rust Core Only              │
├─────────────────────────────────────┤
│  All data processing in Rust        │
│  FFI bindings for Python/Go         │
│  Single codebase, single source     │
│  of truth                           │
└─────────────────────────────────────┘
```

**Pros:**
- Single implementation to maintain
- Maximum performance
- Strong type safety across boundaries
- No serialization overhead between components

**Cons:**
- FFI complexity for Python/Go integration
- Steep learning curve for Python developers
- Larger binary size
- Slower iteration for non-performance-critical features

#### Option 2: EventStoreDB + External Components

```
┌─────────────────────────────────────┐
│     EventStoreDB + External         │
├─────────────────────────────────────┤
│  Use EventStoreDB for event store   │
│  Redis for caching                  │
│  NATS for event bus                 │
│  Minimal custom code                │
└─────────────────────────────────────┘
```

**Pros:**
- Battle-tested components
- Built-in projections
- Commercial support available
- Cluster-ready out of the box

**Cons:**
- Heavy infrastructure requirements
- Operational complexity (3+ services)
- No Blake3 hash chain support
- Vendor lock-in to EventStoreDB
- Overkill for current scale

#### Option 3: Multi-Language Native (Selected)

```
┌─────────────────────────────────────┐
│    Multi-Language Native            │
├─────────────────────────────────────┤
│  Rust: Performance-critical core    │
│    - Event sourcing with Blake3     │
│    - Event bus (tokio)              │
│    - Two-tier cache                 │
│    - In-memory stores               │
│                                     │
│  Go: Service infrastructure         │
│    - Storage modules                │
│    - Cache modules                  │
│    - Event modules                  │
│    - Persistence modules            │
│                                     │
│  Python: Developer-facing services  │
│    - pheno-events (NATS)            │
│    - pheno-caching (LRU/TTL)        │
│    - pheno-database (adapters)      │
│    - pheno-storage (backends)       │
│    - db-kit (unified client)        │
└─────────────────────────────────────┘
```

**Pros:**
- Each language used for its strengths
- No FFI complexity
- Developer-friendly Python APIs
- Rust performance where it matters
- Go for service infrastructure
- Gradual migration path to persistent backends

**Cons:**
- Three codebases to maintain
- Cross-language consistency challenges
- Potential for divergent implementations
- More complex testing strategy

---

## Decision

We will implement **Option 3: Multi-Language Native** with the following architecture:

### Rust Core (Performance-Critical)

The Rust workspace provides the foundation for performance-critical operations:

```
rust/
├── Cargo.toml                    # Workspace definition
├── phenotype-event-sourcing/     # Event sourcing with Blake3 hash chains
│   ├── src/
│   │   ├── lib.rs                # Public API + metrics
│   │   ├── event.rs              # EventEnvelope<T> with hash chain
│   │   ├── hash.rs               # Blake3 hash computation & verification
│   │   ├── store.rs              # EventStore trait (sync)
│   │   ├── async_store.rs        # AsyncEventStore trait
│   │   ├── memory.rs             # InMemoryEventStore
│   │   ├── snapshot.rs           # Snapshot management
│   │   └── error.rs              # Error types
│   └── examples/usage.rs
├── phenotype-event-bus/          # Async event publishing
│   └── src/lib.rs                # EventBus trait + InMemoryEventBus
├── phenotype-cache-adapter/      # Two-tier cache
│   └── src/lib.rs                # TwoTierCache<K, V>
└── phenotype-in-memory-store/    # Generic in-memory store
    └── src/lib.rs                # Store<K, V> + TTL variant
```

### Go Modules (Service Infrastructure)

```
go/
├── go.work                       # Go workspace
├── pheno-storage/                # Storage abstraction
├── pheno-cache/                  # Caching utilities
├── pheno-events/                 # Event handling
└── pheno-persistence/            # Persistence layer
```

### Python Packages (Developer-Facing)

```
python/
├── pheno-events/                 # Event system with NATS
│   └── src/pheno_events/
│       ├── core/
│       │   ├── event_store.py    # EventStore with JSONL persistence
│       │   └── event_bus.py      # EventBus + SimpleEventBus
│       ├── nats_bus.py           # NATS JetStream integration
│       ├── nats_factory.py       # NATS connection factory
│       ├── jetstream_utils.py    # JetStream management
│       └── webhooks/             # Webhook delivery with retry
├── pheno-caching/                # Multi-tier caching
│   └── src/pheno_caching/
│       ├── hot/query_cache.py    # LRU/TTL query cache
│       ├── cold/disk_cache.py    # Disk-backed cache
│       └── dry/decorators.py     # Caching decorators
├── pheno-database/               # Database abstraction
│   └── src/pheno_database/
│       ├── core/engine.py        # Database facade
│       ├── adapters/             # PostgreSQL, Supabase, Neon
│       ├── pooling/              # Connection pooling
│       ├── realtime/             # Real-time subscriptions
│       └── platforms/            # Platform-specific clients
├── pheno-storage/                # Storage backends
│   └── src/pheno_storage/
│       ├── backends/             # S3, Supabase, local, memory
│       └── repositories/         # Repository pattern
└── db-kit/                       # Unified database toolkit
    └── (superset of pheno-database)
```

### Key Design Decisions

1. **Blake3 for Hash Chains**: Fastest cryptographic hash (1.4+ GB/s), parallelizable, SIMD-optimized
2. **Tokio Channels for Rust Event Bus**: Zero-copy, async-native, backpressure through bounded channels
3. **NATS JetStream for Python**: Persistent, replayable, lightweight (10MB footprint)
4. **Two-Tier Cache Architecture**: L1 (hot, small) + L2 (warm, larger) with automatic promotion
5. **Multi-Backend Storage**: Unified interface across S3, Supabase, local, memory
6. **Adapter Pattern for Databases**: Pluggable database adapters (PostgreSQL, Supabase, Neon)

---

## Consequences

### Positive Consequences

1. **Cryptographic Audit Trail**: Blake3 hash chains provide tamper-evident event storage with 1.4+ GB/s throughput, exceeding SHA-256 by 7x while maintaining equivalent security. Every event append creates a verifiable chain link.

2. **Language-Optimized Performance**: Rust handles performance-critical paths (event sourcing, hashing, cache operations) with zero-cost abstractions. Python provides developer-friendly APIs for business logic. Go bridges service infrastructure.

3. **Zero FFI Overhead**: Each language operates natively without cross-language function calls. Communication happens through well-defined protocols (NATS, JSON) rather than FFI bindings.

4. **Gradual Migration Path**: In-memory implementations serve as reference implementations. Persistent backends (PostgreSQL, S3) can be added incrementally without changing the public API.

5. **Backpressure by Design**: Rust event bus uses bounded tokio channels (default capacity: 100). NATS JetStream provides persistent backpressure. Python event bus uses asyncio with bounded task groups.

6. **Metrics Integration**: Built-in observability through `phenotype_observability` integration. Event append counting, cache hit/miss tracking, and structured logging are first-class concerns.

7. **Test Isolation**: In-memory stores enable fast, deterministic testing without external dependencies. TTL stores support time-based test scenarios.

8. **Pluggable Architecture**: Storage backends, database adapters, and event bus implementations are swappable through trait/protocol interfaces.

### Negative Consequences

1. **Triple Maintenance**: Three language implementations require parallel updates for shared concepts. A change to the event envelope structure must be reflected in Rust, Go, and Python.

2. **Cross-Language Consistency**: Ensuring identical behavior across implementations requires comprehensive integration testing. Subtle differences in JSON serialization, timestamp handling, or error propagation can cause issues.

3. **No Distributed Transactions**: Without a unified transaction manager, cross-component operations rely on eventual consistency. Event sourcing mitigates this through append-only semantics.

4. **Operational Complexity**: Running NATS JetStream alongside Rust services and Python workers increases deployment complexity compared to a single monolithic service.

5. **Serialization Overhead**: Cross-language communication via JSON introduces serialization/deserialization overhead compared to in-process FFI calls.

6. **Debugging Complexity**: Issues spanning multiple languages require correlating logs across Rust (tracing), Python (logging), and Go (slog) with different formats and correlation IDs.

---

## Architecture

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DataKit Processing Engine                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        Rust Core Layer                            │  │
│  │                                                                   │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │  │
│  │  │ Event Sourcing  │  │ Event Bus       │  │ Cache Adapter    │  │  │
│  │  │                 │  │                 │  │                  │  │  │
│  │  │ EventEnvelope<T>│  │ EventBus trait  │  │ TwoTierCache<K,V>│  │  │
│  │  │ Blake3 chains   │  │ InMemoryEventBus│  │ L1: Hot (small)  │  │  │
│  │  │ verify_chain()  │  │ EventStream     │  │ L2: Warm (large) │  │  │
│  │  │ SnapshotStore   │  │ FilteredStream  │  │ MetricsHook      │  │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘  │  │
│  │           │                    │                    │            │  │
│  │  ┌────────▼────────────────────▼────────────────────▼─────────┐  │  │
│  │  │              In-Memory Store                                │  │  │
│  │  │  ┌──────────────────┐  ┌───────────────────────────────┐   │  │  │
│  │  │  │ InMemoryStore    │  │ InMemoryStoreWithTTL          │   │  │  │
│  │  │  │ (RwLock<Hash>)   │  │ (TTL expiration)              │   │  │  │
│  │  │  │ Store<K,V> trait │  │ StoreBuilder<K,V>             │   │  │  │
│  │  │  └──────────────────┘  └───────────────────────────────┘   │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌─────────────────────────────────┼─────────────────────────────────┐  │
│  │                        Go Layer │                                 │  │
│  │  ┌──────────────┐ ┌───────────▼─┐ ┌──────────────┐ ┌───────────┐ │  │
│  │  │ pheno-storage│ │pheno-cache  │ │pheno-events  │ │pheno-     │ │  │
│  │  │              │ │             │ │              │ │persistence│ │  │
│  │  │ Storage      │ │ Cache       │ │ Event        │ │ Persistence│ │  │
│  │  │ interfaces   │ │ strategies  │ │ handlers     │ │ layer      │ │  │
│  │  └──────────────┘ └─────────────┘ └──────────────┘ └───────────┘ │  │
│  └─────────────────────────────────┼─────────────────────────────────┘  │
│                                    │                                    │
│  ┌─────────────────────────────────┼─────────────────────────────────┐  │
│  │                     Python Layer│                                 │  │
│  │  ┌──────────────┐ ┌───────────▼─┐ ┌──────────────┐ ┌───────────┐ │  │
│  │  │ pheno-events │ │pheno-caching│ │pheno-database│ │pheno-stor │ │  │
│  │  │              │ │             │ │              │ │age        │ │  │
│  │  │ EventBus     │ │ QueryCache  │ │ Database     │ │ Storage   │ │  │
│  │  │ EventStore   │ │ DiskCache   │ │ Adapters     │ │ Backends  │ │  │
│  │  │ NATS Bus     │ │ Decorators  │ │ Pooling      │ │ Repos     │ │  │
│  │  │ Webhooks     │ │             │ │ Realtime     │ │           │ │  │
│  │  └──────────────┘ └─────────────┘ └──────┬───────┘ └───────────┘ │  │
│  │                                           │                       │  │
│  │  ┌────────────────────────────────────────┴─────────────────────┐ │  │
│  │  │                    db-kit                                    │ │  │
│  │  │  Unified database client with migrations, tenancy, vector    │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌─────────────────────────────────▼─────────────────────────────────┐  │
│  │                   External Integrations                           │  │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────┐ ┌───────────────┐  │  │
│  │  │  NATS   │ │ Supabase │ │  S3    │ │ Neon │ │  PostgreSQL   │  │  │
│  │  │JetStream│ │ Storage  │ │        │ │      │ │               │  │  │
│  │  └─────────┘ └──────────┘ └────────┘ └──────┘ └───────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Write Path:
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│  Client  │───>│  Event Bus   │───>│ Event Store  │───>│  Storage    │
│  Request │    │  (Publish)   │    │ (Blake3)     │    │  (Persist)  │
└──────────┘    └──────┬───────┘    └──────┬───────┘    └──────┬──────┘
                       │                   │                   │
                       ▼                   ▼                   ▼
                 ┌───────────┐      ┌───────────┐      ┌───────────┐
                 │ Handlers  │      │ Hash Chain│      │ S3/Local  │
                 │ (async)   │      │ Verified  │      │ Supabase  │
                 └───────────┘      └───────────┘      └───────────┘

Read Path:
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│  Client  │───>│  Cache       │───>│  Event Store │───>│  Storage    │
│  Query   │    │  (L1 → L2)   │    │  (Read)      │    │  (Fetch)    │
└──────────┘    └──────┬───────┘    └──────┬───────┘    └──────┬──────┘
                       │                   │                   │
                       ▼                   ▼                   ▼
                 ┌───────────┐      ┌───────────┐      ┌───────────┐
                 │ Cache Hit │      │ Replay    │      │ Deserialize│
                 │ (fast)    │      │ Aggregate │      │ JSON/Binary│
                 └───────────┘      └───────────┘      └───────────┘
```

---

## Code Examples

### Rust: Event Sourcing with Blake3

```rust
use phenotype_event_sourcing::{
    EventEnvelope, EventStore, InMemoryEventStore,
    verify_chain, ZERO_HASH,
};
use serde::{Serialize, Deserialize};

#[derive(Clone, Serialize, Deserialize)]
struct UserCreated {
    user_id: String,
    email: String,
    name: String,
}

#[derive(Clone, Serialize, Deserialize)]
struct EmailVerified {
    user_id: String,
    verified_at: chrono::DateTime<chrono::Utc>,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create event store
    let mut store = InMemoryEventStore::new();

    // Append events
    let event1 = UserCreated {
        user_id: "user-123".to_string(),
        email: "user@example.com".to_string(),
        name: "Alice".to_string(),
    };
    store.append("user-123", event1)?;

    let event2 = EmailVerified {
        user_id: "user-123".to_string(),
        verified_at: chrono::Utc::now(),
    };
    store.append("user-123", event2)?;

    // Read and verify
    let events: Vec<EventEnvelope<UserCreated>> = store.read("user-123", 0)?;
    verify_chain(&events)?;

    println!("Stored {} events with verified hash chain", events.len());
    Ok(())
}
```

### Python: Event Bus with NATS

```python
"""
Event bus with NATS JetStream integration.
"""
import asyncio
from pheno_events.core.event_bus import EventBus
from pheno_events.core.event_store import EventStore
from pheno_events.nats_factory import NatsFactory


async def main():
    # Create event bus
    bus = EventBus()

    # Register handlers
    @bus.on("user.created")
    async def handle_user_created(event):
        print(f"User created: {event.data['email']}")
        # Store event
        await event_store.append(
            event_type="UserCreated",
            aggregate_id=event.data["user_id"],
            aggregate_type="User",
            data=event.data,
        )

    @bus.on("user.*")  # Wildcard
    async def handle_all_user_events(event):
        print(f"User event: {event.name}")

    # Publish events
    await bus.publish(
        "user.created",
        data={"user_id": "user-123", "email": "user@example.com"},
        correlation_id="corr-001",
    )

    # With NATS (distributed)
    factory = NatsFactory(servers=["nats://localhost:4222"])
    nc, js = await factory.create_connection()

    # Publish to JetStream
    await js.publish(
        "events.user.created",
        b'{"user_id": "user-123", "email": "user@example.com"}',
    )

    await nc.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### Go: Storage Abstraction

```go
package storage

import (
    "context"
    "io"
)

// StorageBackend defines the storage interface
type StorageBackend interface {
    Upload(ctx context.Context, bucket, path string, data io.Reader, opts UploadOptions) (string, error)
    Download(ctx context.Context, bucket, path string) (io.ReadCloser, error)
    Delete(ctx context.Context, bucket, path string) error
    Exists(ctx context.Context, bucket, path string) (bool, error)
    ListFiles(ctx context.Context, bucket string, prefix string, limit int) ([]FileInfo, error)
}

// S3Backend implements StorageBackend for AWS S3
type S3Backend struct {
    client *s3.Client
}

func (b *S3Backend) Upload(ctx context.Context, bucket, path string, data io.Reader, opts UploadOptions) (string, error) {
    result, err := b.client.PutObject(ctx, &s3.PutObjectInput{
        Bucket:      aws.String(bucket),
        Key:         aws.String(path),
        Body:        data,
        ContentType: aws.String(opts.ContentType),
    })
    if err != nil {
        return "", err
    }
    return *result.ETag, nil
}

// LocalBackend implements StorageBackend for local filesystem
type LocalBackend struct {
    basePath string
}

func (b *LocalBackend) Upload(ctx context.Context, bucket, path string, data io.Reader, opts UploadOptions) (string, error) {
    fullPath := filepath.Join(b.basePath, bucket, path)
    os.MkdirAll(filepath.Dir(fullPath), 0755)

    file, err := os.Create(fullPath)
    if err != nil {
        return "", err
    }
    defer file.Close()

    _, err = io.Copy(file, data)
    return fullPath, err
}
```

---

## Cross-References

### Related ADRs

- [ADR-002: Streaming vs Batch Processing Strategy](ADR-002-streaming-strategy.md) — Justifies the streaming-first approach with batch fallback
- [ADR-003: Schema Evolution Strategy](ADR-003-schema-evolution.md) — Defines how data schemas evolve across the processing engine

### Related Research

- [Data Processing SOTA](../research/DATA_PROCESSING_SOTA.md) — Comprehensive analysis of data processing technologies
- [DataKit Specification](../SPEC.md) — Complete system specification

### External References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html) — Martin Fowler
- [CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs) — Microsoft Architecture Center
- [Blake3 Hash Function](https://github.com/BLAKE3-team/BLAKE3) — Official implementation
- [NATS Documentation](https://docs.nats.io/) — NATS official docs
- [Tokio Runtime](https://tokio.rs/) — Async runtime for Rust

### Phenotype Ecosystem

- [PhenoSpecs](https://github.com/KooshaPari/PhenoSpecs) — Specifications and ADRs
- [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) — Patterns and guidelines
- [HexaKit](https://github.com/KooshaPari/HexaKit) — Templates and scaffolding
- [Infrakit](../../Infrakit/) — Infrastructure toolkit (observability integration)

---

*This ADR was accepted on 2026-04-03 by the Phenotype Architecture Team.*
