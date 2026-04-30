# DataKit Specification

**Document ID:** PHENOTYPE_DATAKIT_SPEC_001  
**Status:** Active  
**Last Updated:** 2026-04-03  
**Author:** Phenotype Architecture Team  
**Version:** 2.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Functionality Specification](#3-functionality-specification)
4. [Technical Architecture](#4-technical-architecture)
5. [API Reference](#5-api-reference)
6. [Error Handling](#6-error-handling)
7. [Security](#7-security)
8. [Performance](#8-performance)
9. [Testing](#9-testing)
10. [Deployment](#10-deployment)
11. [Migration Guide](#11-migration-guide)
12. [Glossary](#12-glossary)

---

## 1. Project Overview

### 1.1 Purpose

DataKit is the data processing toolkit for the Phenotype ecosystem. It provides multi-language implementations of core data patterns: event sourcing with cryptographic integrity, async event communication, hierarchical caching, storage abstraction, and database management.

### 1.2 Scope

DataKit spans three programming languages with 131+ files across the following domains:

| Domain | Rust | Go | Python | Description |
|--------|------|-----|--------|-------------|
| Event Sourcing | `phenotype-event-sourcing` | -- | `pheno-events/core` | Append-only event storage with Blake3 hash chains |
| Event Bus | `phenotype-event-bus` | `pheno-events` | `pheno-events` | Async publish/subscribe messaging |
| Caching | `phenotype-cache-adapter` | `pheno-cache` | `pheno-caching` | Multi-tier cache with L1/L2 |
| Storage | -- | `pheno-storage` | `pheno-storage` | Unified storage backend abstraction |
| Database | -- | -- | `pheno-database`, `db-kit` | Multi-platform database management |
| In-Memory Store | `phenotype-in-memory-store` | -- | -- | Generic key-value store with TTL |

### 1.3 Design Principles

1. **Cryptographic Integrity First**: All events carry Blake3 hash chains for tamper evidence
2. **Async-Default**: Non-blocking I/O across all languages and components
3. **Pluggable Backends**: Storage, database, and event bus implementations are swappable
4. **Multi-Language Native**: Each language uses idiomatic patterns, not FFI wrappers
5. **In-Memory Reference**: In-memory implementations serve as both production components and test doubles
6. **Observability Built-In**: Metrics, tracing, and structured logging are first-class concerns

### 1.4 Technology Stack

```
+----------------------------------------------------------------+
|                    DataKit Technology Stack                    |
+----------------------------------------------------------------+
|                                                                |
|  Rust (Edition 2021):                                          |
|  +----------------------------------------------------------+  |
|  | tokio          | Async runtime                           |  |
|  | serde          | Serialization/deserialization           |  |
|  | blake3         | Cryptographic hash chains               |  |
|  | dashmap        | Concurrent hash map                     |  |
|  | thiserror      | Error type derivation                   |  |
|  | async-trait    | Async trait support                     |  |
|  | uuid           | Unique identifiers                      |  |
|  | chrono         | Date/time handling                      |  |
|  | tracing        | Structured logging                      |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Go (1.22+):                                                   |
|  +----------------------------------------------------------+  |
|  | go.work          | Workspace management                  |  |
|  | context          | Request lifecycle                     |  |
|  | sync             | Concurrency primitives                |  |
|  | io               | I/O abstractions                      |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python (3.12+):                                               |
|  +----------------------------------------------------------+  |
|  | asyncio          | Async runtime                         |  |
|  | dataclasses      | Data structures                       |  |
|  | nats-py          | NATS JetStream client                 |  |
|  | pydantic         | Data validation                       |  |
|  | supabase-py      | Supabase client                       |  |
|  | httpx            | HTTP client                           |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 1.5 Project Structure

```
DataKit/
├── docs/
│   ├── SPEC.md                          # This specification
│   ├── adr/
│   │   ├── ADRS.md                      # ADR index
│   │   ├── ADR-001-processing-engine.md # Processing engine architecture
│   │   ├── ADR-002-streaming-strategy.md# Streaming vs batch strategy
│   │   └── ADR-003-schema-evolution.md  # Schema evolution strategy
│   ├── research/
│   │   └── DATA_PROCESSING_SOTA.md      # State of the art research
│   └── sota/
│       └── SOTA.md                      # Original SOTA research
├── rust/
│   ├── Cargo.toml                       # Workspace definition
│   ├── phenotype-event-sourcing/        # Event sourcing with Blake3
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   ├── lib.rs                   # Public API + metrics
│   │   │   ├── event.rs                 # EventEnvelope<T>
│   │   │   ├── hash.rs                  # Blake3 hash operations
│   │   │   ├── store.rs                 # EventStore trait
│   │   │   ├── async_store.rs           # AsyncEventStore trait
│   │   │   ├── memory.rs                # InMemoryEventStore
│   │   │   ├── snapshot.rs              # Snapshot management
│   │   │   └── error.rs                 # Error types
│   │   └── examples/
│   │       └── usage.rs
│   ├── phenotype-event-bus/             # Async event bus
│   │   ├── Cargo.toml
│   │   └── src/lib.rs                   # EventBus trait + impl
│   ├── phenotype-cache-adapter/         # Two-tier cache
│   │   ├── Cargo.toml
│   │   └── src/lib.rs                   # TwoTierCache<K, V>
│   └── phenotype-in-memory-store/       # Generic in-memory store
│       ├── Cargo.toml
│       └── src/lib.rs                   # Store<K, V> + TTL
├── go/
│   ├── go.work                          # Go workspace
│   ├── pheno-storage/                   # Storage abstraction
│   ├── pheno-cache/                     # Caching utilities
│   ├── pheno-events/                    # Event handling
│   └── pheno-persistence/               # Persistence layer
└── python/
    ├── pheno-events/                    # Event system
    │   └── src/pheno_events/
    │       ├── __init__.py
    │       ├── bus.py
    │       ├── nats_bus.py
    │       ├── nats_factory.py
    │       ├── jetstream_utils.py
    │       ├── core/
    │       │   ├── __init__.py
    │       │   ├── event_store.py
    │       │   └── event_bus.py
    │       ├── streaming/
    │       │   └── __init__.py
    │       └── webhooks/
    │           ├── __init__.py
    │           ├── signature.py
    │           ├── webhook_manager.py
    │           ├── retry.py
    │           └── nats_delivery.py
    ├── pheno-caching/                   # Multi-tier caching
    │   └── src/pheno_caching/
    │       ├── __init__.py
    │       ├── hot/
    │       │   ├── __init__.py
    │       │   └── query_cache.py
    │       ├── cold/
    │       │   ├── __init__.py
    │       │   └── disk_cache.py
    │       └── dry/
    │           ├── __init__.py
    │           └── decorators.py
    ├── pheno-database/                  # Database abstraction
    │   └── src/pheno_database/
    │       ├── __init__.py
    │       ├── client.py
    │       ├── supabase_client.py
    │       ├── core/
    │       │   ├── __init__.py
    │       │   └── engine.py
    │       ├── adapters/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   ├── postgres.py
    │       │   ├── supabase.py
    │       │   └── neon.py
    │       ├── pooling/
    │       │   ├── __init__.py
    │       │   ├── connection_pool.py
    │       │   └── pool_manager.py
    │       ├── storage/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   └── supabase.py
    │       ├── realtime/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   └── supabase.py
    │       ├── query/
    │       │   └── __init__.py
    │       ├── vector/
    │       │   └── __init__.py
    │       ├── tenancy/
    │       │   └── __init__.py
    │       └── platforms/
    │           └── neon/
    │               └── __init__.py
    ├── pheno-storage/                   # Storage backends
    │   └── src/pheno_storage/
    │       ├── __init__.py
    │       ├── client.py
    │       ├── core/
    │       │   ├── client.py
    │       │   └── file.py
    │       ├── backends/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   ├── s3.py
    │       │   ├── local.py
    │       │   ├── memory.py
    │       │   ├── supabase.py
    │       │   ├── sqlalchemy.py
    │       │   ├── sqlalchemy_model.py
    │       │   ├── factory.py
    │       │   ├── exceptions.py
    │       │   └── adapter.py
    │       └── repositories/
    │           ├── __init__.py
    │           ├── base.py
    │           ├── sqlalchemy.py
    │           ├── sqlalchemy_model.py
    │           ├── memory.py
    │           ├── factory.py
    │           ├── exceptions.py
    │           └── adapter.py
    └── db-kit/                          # Unified database toolkit
        ├── __init__.py
        ├── client.py
        ├── supabase_client.py
        ├── core/
        │   ├── __init__.py
        │   └── engine.py
        ├── adapters/
        │   ├── __init__.py
        │   ├── base.py
        │   ├── postgres.py
        │   ├── supabase.py
        │   └── neon.py
        ├── storage/
        │   ├── __init__.py
        │   ├── base.py
        │   └── supabase.py
        ├── realtime/
        │   ├── __init__.py
        │   ├── base.py
        │   └── supabase.py
        ├── query/
        │   └── __init__.py
        ├── vector/
        │   └── __init__.py
        ├── tenancy/
        │   └── __init__.py
        ├── rls/
        │   └── __init__.py
        ├── pooling/
        │   ├── __init__.py
        │   ├── connection_pool.py
        │   └── pool_manager.py
        ├── migrations/
        │   ├── __init__.py
        │   ├── migration.py
        │   └── engine.py
        └── platforms/
            ├── supabase/
            │   ├── __init__.py
            │   └── client.py
            ├── neon/
            │   ├── __init__.py
            │   └── client.py
            └── turso/
                └── __init__.py
```

---

## 2. Architecture

### 2.1 System Architecture

```
+-------------------------------------------------------------------------+
|                          DataKit Architecture                           |
+-------------------------------------------------------------------------+
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                        Rust Core Layer                            |  |
|  |                                                                   |  |
|  |  +------------------+  +------------------+  +------------------+  |  |
|  |  | Event Sourcing   |  | Event Bus        |  | Cache Adapter    |  |  |
|  |  |                  |  |                  |  |                  |  |  |
|  |  | EventEnvelope<T> |  | EventBus trait   |  | TwoTierCache<K,V>|  |  |
|  |  | Blake3 chains    |  | InMemoryEventBus |  | L1: Hot (small)  |  |  |
|  |  | verify_chain()   |  | EventStream      |  | L2: Warm (large) |  |  |
|  |  | SnapshotStore    |  | FilteredStream   |  | MetricsHook      |  |  |
|  |  +--------+---------+  +--------+---------+  +--------+---------+  |  |
|  |           |                    |                    |             |  |
|  |  +--------v--------------------v--------------------v---------+  |  |
|  |  |              In-Memory Store                                |  |  |
|  |  |  +------------------+  +--------------------------------+   |  |  |
|  |  |  | InMemoryStore    |  | InMemoryStoreWithTTL           |   |  |  |
|  |  |  | (RwLock<Hash>)   |  | (TTL expiration)               |   |  |  |
|  |  |  | Store<K,V> trait |  | StoreBuilder<K,V>              |   |  |  |
|  |  |  +------------------+  +--------------------------------+   |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |                        Go Layer                                   |  |
|  |  +--------------+ +---------------+ +--------------+ +-----------+ |  |
|  |  | pheno-storage| | pheno-cache   | | pheno-events | | pheno-    | |  |
|  |  |              | |               | |              | |persistence| |  |
|  |  | Storage      | | Cache         | | Event        | | Persistence| |  |
|  |  | interfaces   | | strategies    | | handlers     | | layer      | |  |
|  |  +--------------+ +---------------+ +--------------+ +-----------+ |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |                     Python Layer                                  |  |
|  |  +--------------+ +---------------+ +--------------+ +-----------+ |  |
|  |  | pheno-events | | pheno-caching | | pheno-database| |pheno-stor | |  |
|  |  |              | |               | |              | |age        | |  |
|  |  | EventBus     | | QueryCache    | | Database     | | Storage   | |  |
|  |  | EventStore   | | DiskCache     | | Adapters     | | Backends  | |  |
|  |  | NATS Bus     | | Decorators    | | Pooling      | | Repos     | |  |
|  |  | Webhooks     | |               | | Realtime     | |           | |  |
|  |  +--------------+ +---------------+ +------+-------+ +-----------+ |  |
|  |                                           |                       |  |
|  |  +----------------------------------------v---------------------+ |  |
|  |  |                    db-kit                                    | |  |
|  |  |  Unified database client with migrations, tenancy, vector    | |  |
|  |  +--------------------------------------------------------------+ |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |                   External Integrations                           |  |
|  |  +---------+ +----------+ +--------+ +------+ +---------------+  |  |
|  |  |  NATS   | | Supabase | |  S3    | | Neon | |  PostgreSQL   |  |  |
|  |  |JetStream| | Storage  | |        | |      | |               |  |  |
|  |  +---------+ +----------+ +--------+ +------+ +---------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
+-------------------------------------------------------------------------+
```

### 2.2 Data Flow Architecture

```
+-------------------------------------------------------------------------+
|                        Data Flow Architecture                           |
+-------------------------------------------------------------------------+
|                                                                         |
|  WRITE PATH:                                                            |
|  +----------+    +--------------+    +--------------+    +------------+ |
|  | Client   |--->| Event Bus    |--->| Event Store  |--->| Storage    | |
|  | Request  |    | (Publish)    |    | (Blake3)     |    | (Persist)  | |
|  +----------+    +------+-------+    +------+-------+    +-----+------+ |
|                         |                  |                  |         |
|                         v                  v                  v         |
|                   +-----------+      +-----------+      +-----------+   |
|                   | Handlers  |      | Hash Chain|      | S3/Local  |   |
|                   | (async)   |      | Verified  |      | Supabase  |   |
|                   +-----------+      +-----------+      +-----------+   |
|                                                                         |
|  READ PATH:                                                             |
|  +----------+    +--------------+    +--------------+    +------------+ |
|  | Client   |--->| Cache        |--->| Event Store  |--->| Storage    | |
|  | Query    |    | (L1 -> L2)   |    | (Read)       |    | (Fetch)    | |
|  +----------+    +------+-------+    +------+-------+    +-----+------+ |
|                         |                  |                  |         |
|                         v                  v                  v         |
|                   +-----------+      +-----------+      +-----------+   |
|                   | Cache Hit |      | Replay    |      | Deserialize|  |
|                   | (fast)    |      | Aggregate |      | JSON/Binary|  |
|                   +-----------+      +-----------+      +-----------+   |
|                                                                         |
|  EVENT-DRIVEN CACHE INVALIDATION:                                       |
|  +----------+    +--------------+    +--------------+    +------------+ |
|  | Data     |--->| Event Bus    |--->| Cache        |--->| Invalidate | |
|  | Change   |    | (Publish)    |    | Listener     |    | Entry      | |
|  +----------+    +--------------+    +--------------+    +------------+ |
|                                                                         |
+-------------------------------------------------------------------------+
```

### 2.3 Component Relationships

```
+-------------------------------------------------------------------------+
|                      Component Dependency Graph                         |
+-------------------------------------------------------------------------+
|                                                                         |
|  phenotype-event-sourcing                                               |
|  +---> blake3 (hash chains)                                             |
|  +---> serde (serialization)                                            |
|  +---> phenotype_infrakit (observability)                               |
|                                                                         |
|  phenotype-event-bus                                                    |
|  +---> tokio (async runtime)                                            |
|  +---> dashmap (concurrent channels)                                    |
|  +---> serde (event serialization)                                      |
|                                                                         |
|  phenotype-cache-adapter                                                |
|  +---> dashmap (concurrent cache)                                       |
|  +---> phenotype_contracts (MetricsHook)                                |
|                                                                         |
|  phenotype-in-memory-store                                              |
|  +---> tokio (async RwLock)                                             |
|  +---> serde (serialization)                                            |
|  +---> chrono (TTL timestamps)                                          |
|                                                                         |
|  pheno-events (Python)                                                  |
|  +---> asyncio (async runtime)                                          |
|  +---> nats-py (NATS JetStream)                                         |
|  +---> pheno-caching (query caching)                                    |
|                                                                         |
|  pheno-database (Python)                                                |
|  +---> supabase-py (Supabase client)                                    |
|  +---> httpx (HTTP client for Neon)                                     |
|  +---> pheno-storage (storage abstraction)                              |
|                                                                         |
|  pheno-storage (Python)                                                 |
|  +---> boto3 (S3 backend)                                               |
|  +---> supabase-py (Supabase backend)                                   |
|  +---> sqlalchemy (SQL backend)                                         |
|                                                                         |
|  db-kit (Python)                                                        |
|  +---> pheno-database (superset with migrations, tenancy, vector)       |
|  +---> pheno-storage (storage integration)                              |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## 3. Functionality Specification

### 3.1 Event Sourcing

#### 3.1.1 Core Concepts

Event sourcing stores application state as an immutable sequence of events. Each event represents a state change and is cryptographically linked to its predecessor via a Blake3 hash chain.

```
+--------------------------------------------------------------+
|                    Event Stream Structure                    |
+--------------------------------------------------------------+
|                                                              |
|  Stream: "order-123"                                         |
|                                                              |
|  +-----------+    +-----------+    +-----------+             |
|  | Event 0   |--->| Event 1   |--->| Event 2   | ...        |
|  |           |    |           |    |           |             |
|  | prev_hash:|    | prev_hash:|    | prev_hash:|             |
|  | 0x0000... |    | 0xABCD... |    | 0x1234... |             |
|  | hash:     |    | hash:     |    | hash:     |             |
|  | 0xABCD... |    | 0x1234... |    | 0x5678... |             |
|  | seq: 0    |    | seq: 1    |    | seq: 2    |             |
|  +-----------+    +-----------+    +-----------+             |
|                                                              |
|  ZERO_HASH = [0; 32] (first event's previous_hash)           |
|                                                              |
+--------------------------------------------------------------+
```

#### 3.1.2 EventEnvelope Specification

The `EventEnvelope<T>` wraps event payloads with cryptographic metadata:

| Field | Type | Description |
|-------|------|-------------|
| `payload` | `T` | The event data (generic, serializable) |
| `hash` | `[u8; 32]` | Blake3 hash of this event |
| `previous_hash` | `[u8; 32]` | Blake3 hash of the previous event |
| `timestamp` | `DateTime<Utc>` | Event creation time |
| `sequence` | `u64` | Position in the stream (0-indexed) |

**Hash Computation:**

```
hash = blake3(serialize(payload) || previous_hash || sequence_le_bytes)
```

Where:
- `serialize(payload)`: JSON serialization of the payload
- `previous_hash`: 32-byte hash of the previous event
- `sequence_le_bytes`: 8-byte little-endian sequence number

#### 3.1.3 EventStore Trait

```rust
pub trait EventStore {
    fn append<E: Serialize + Clone>(
        &mut self,
        aggregate_id: &str,
        event: E,
    ) -> Result<u64, EventSourcingError>;

    fn read<E: for<'de> Deserialize<'de>>(
        &self,
        aggregate_id: &str,
        from_sequence: u64,
    ) -> Result<Vec<EventEnvelope<E>>, EventSourcingError>;

    fn current_sequence(&self, aggregate_id: &str)
        -> Result<u64, EventSourcingError>;
}
```

**Behavioral Requirements:**

| Operation | Input | Output | Error Conditions |
|-----------|-------|--------|-----------------|
| `append` | aggregate_id, event | sequence number | Serialization error, store error |
| `read` | aggregate_id, from_sequence | Vec of envelopes | Deserialization error, stream not found |
| `current_sequence` | aggregate_id | sequence number | Stream not found |

#### 3.1.4 AsyncEventStore Trait

```rust
#[async_trait]
pub trait AsyncEventStore {
    async fn append<E: Serialize + Clone + Send>(
        &self,
        aggregate_id: &str,
        event: E,
    ) -> Result<u64, EventSourcingError>;

    async fn read<E: for<'de> Deserialize<'de> + Send>(
        &self,
        aggregate_id: &str,
        from_sequence: u64,
    ) -> Result<Vec<EventEnvelope<E>>, EventSourcingError>;

    async fn stream<E: for<'de> Deserialize<'de> + Send>(
        &self,
        aggregate_id: &str,
        from_sequence: u64,
    ) -> Result<Pin<Box<dyn Stream<Item = EventEnvelope<E>> + Send>>, EventSourcingError>;
}
```

#### 3.1.5 Chain Verification

The `verify_chain` function validates the integrity of an event chain:

```rust
pub fn verify_chain<T: Serialize>(
    events: &[EventEnvelope<T>],
) -> Result<(), ChainVerificationError>;
```

**Verification Steps:**

1. Empty chain is valid (returns Ok)
2. First event must have `previous_hash == ZERO_HASH`
3. Each event's hash must match recomputed hash
4. Each event's `previous_hash` must match the previous event's `hash`
5. Sequence numbers must be consecutive (0, 1, 2, ...)

**Error Types:**

| Error | Condition |
|-------|-----------|
| `InvalidFirstEvent` | First event's `previous_hash` is not `ZERO_HASH` |
| `InvalidHash { index }` | Event hash does not match recomputed hash |
| `BrokenChain { index, expected, actual }` | Chain linkage broken |
| `SequenceGap { index, expected, actual }` | Non-consecutive sequence numbers |

#### 3.1.6 Snapshot Specification

Snapshots optimize aggregate reconstruction for long event streams:

| Field | Type | Description |
|-------|------|-------------|
| `state` | `A` | Serialized aggregate state |
| `version` | `u64` | Last event sequence included |
| `timestamp` | `DateTime<Utc>` | Snapshot creation time |

**SnapshotConfig:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `events_interval` | `u64` | 100 | Events between snapshots |
| `max_age` | `Duration` | 1 hour | Maximum age before re-snapshot |

**Snapshot Strategy:**

```
+--------------------------------------------------------------+
|                  Snapshot Decision Logic                     |
+--------------------------------------------------------------+
|                                                              |
|  Should snapshot?                                            |
|  ├── events_since_last_snapshot >= events_interval           |
|  │   └── YES: Create snapshot                                |
|  │                                                           |
|  └── current_time - last_snapshot_time >= max_age            |
|      └── YES: Create snapshot                                |
|                                                              |
|  Aggregate Reconstruction:                                   |
|  1. Load latest snapshot (if exists)                         |
|  2. Read events from snapshot.version + 1                    |
|  3. Apply events to snapshot state                           |
|  4. Return reconstructed aggregate                           |
|                                                              |
+--------------------------------------------------------------+
```

### 3.2 Event Bus

#### 3.2.1 Core Concepts

The event bus provides async publish/subscribe messaging for decoupled service communication. It supports both in-process (tokio channels) and distributed (NATS JetStream) communication.

#### 3.2.2 Event Trait

```rust
pub trait Event: Send + Sync + Serialize + 'static {
    fn event_type(&self) -> &'static str;
    fn event_id(&self) -> Uuid;
    fn timestamp(&self) -> DateTime<Utc>;
    fn as_any(&self) -> &dyn Any;
}
```

#### 3.2.3 EventBus Trait

```rust
#[async_trait]
pub trait EventBus: Send + Sync + 'static {
    async fn publish<E: Event>(
        &self,
        event: E,
    ) -> Result<(), EventBusError>;

    async fn subscribe<E: Event + for<'de> Deserialize<'de>>(
        &self,
    ) -> Result<mpsc::Receiver<E>, EventBusError>;

    fn subscribe_all(
        &self,
    ) -> Result<broadcast::Receiver<EventEnvelope>, EventBusError>;
}
```

**Behavioral Requirements:**

| Operation | Description | Guarantees |
|-----------|-------------|------------|
| `publish` | Send event to all subscribers | At-least-once for typed, best-effort for broadcast |
| `subscribe` | Get typed event receiver | Bounded channel (capacity: 100) |
| `subscribe_all` | Get all events receiver | Broadcast channel (may drop slow consumers) |

#### 3.2.4 EventEnvelope (Transport)

```rust
pub struct EventEnvelope {
    pub id: Uuid,
    pub event_type: String,
    pub payload: serde_json::Value,
    pub metadata: HashMap<String, String>,
    pub timestamp: DateTime<Utc>,
}
```

#### 3.2.5 EventHandler Trait

```rust
#[async_trait]
pub trait EventHandler<E: Event>: Send + Sync {
    async fn handle(&self, event: E) -> Result<(), EventBusError>;
}
```

#### 3.2.6 EventStream and FilteredStream

```rust
pub struct EventStream {
    receiver: broadcast::Receiver<EventEnvelope>,
}

impl EventStream {
    pub async fn next(&mut self) -> Option<EventEnvelope>;
    pub fn filter<F>(self, predicate: F) -> FilteredStream<F>;
}
```

#### 3.2.7 Python EventBus

```python
class EventBus:
    """In-memory event bus with pub/sub pattern."""

    def on(self, event_name: str):
        """Decorator to register event handler (supports wildcards)."""

    def subscribe(self, event_name: str, handler: Callable):
        """Subscribe to events."""

    def unsubscribe(self, event_name: str, handler: Callable | None = None):
        """Unsubscribe from events."""

    async def publish(
        self,
        event_name: str,
        data: Any = None,
        source: str | None = None,
        correlation_id: str | None = None,
    ) -> Event:
        """Publish event to all subscribers."""
```

**Wildcard Pattern Matching:**

| Pattern | Matches |
|---------|---------|
| `*` | All events |
| `user.*` | `user.created`, `user.deleted`, `user.updated` |
| `user.created` | Only `user.created` |
| `order.*.placed` | `order.new.placed`, `order.retry.placed` |

#### 3.2.8 NATS JetStream Integration

```python
class NatsEventBus:
    """NATS-backed event bus with JetStream persistence."""

    async def connect(self):
        """Connect to NATS server."""

    async def publish(self, subject: str, data: dict):
        """Publish event to JetStream."""

    async def subscribe(self, subject: str, handler):
        """Subscribe with durable consumer."""
```

### 3.3 Caching

#### 3.3.1 Two-Tier Cache (Rust)

```rust
pub struct TwoTierCache<K, V> {
    l1: Arc<DashMap<K, CacheEntry<V>>>,  // Hot cache
    l2: Arc<DashMap<K, CacheEntry<V>>>,  // Warm cache
    l1_capacity: usize,
    metrics: Arc<dyn MetricsHook>,
}
```

**Operations:**

| Operation | Behavior | Complexity |
|-----------|----------|------------|
| `get(key)` | Check L1, then L2 (promote if found) | O(1) average |
| `put(key, value)` | Insert into both tiers, evict L1 if full | O(1) average |
| `remove(key)` | Remove from both tiers | O(1) average |
| `clear()` | Clear both tiers | O(n) |
| `l1_len()` | Return L1 size | O(1) |
| `l2_len()` | Return L2 size | O(1) |

**Cache Flow:**

```
+--------------------------------------------------------------+
|                  Two-Tier Cache Flow                         |
+--------------------------------------------------------------+
|                                                              |
|  GET:                                                        |
|  ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐           |
|  │ get(k)│───>│ L1    │───>│ L2    │───>│ None  │           |
|  │       │    │ Hit?  │    │ Hit?  │    │ (miss)│           |
|  └───────┘    └───┬───┘    └───┬───┘    └───────┘           |
|                   │            │                             |
|              +----v----+  +----v----+                        |
|              | Return  |  | Promote |                        |
|              | value   |  | to L1   |                        |
|              +---------+  +----+----+                        |
|                            |                                 |
|                       +----v----+                            |
|                       | Return  |                            |
|                       | value   |                            |
|                       +---------+                            |
|                                                              |
|  PUT:                                                        |
|  ┌───────┐    ┌───────────┐    ┌───────────┐               |
|  │ put(k)│───>│ L1 full?  │───>│ Evict L1  │               |
|  │       │    │           │    │ (FIFO)    │               |
|  └───────┘    └─────┬─────┘    └─────┬─────┘               |
|                     │                │                      |
|              +------v----------------v------+               |
|              | Insert into L1 and L2        |               |
|              +------------------------------+               |
|                                                              |
+--------------------------------------------------------------+
```

#### 3.3.2 QueryCache (Python)

```python
class QueryCache:
    """In-memory cache with TTL and automatic invalidation."""

    def __init__(self, ttl: float = 30.0, max_size: int = 1000):
        """Initialize with TTL and max size."""

    def generate_key(self, operation: str, params: dict) -> str:
        """Generate MD5 cache key from operation + params."""

    def get(self, key: str) -> Any | None:
        """Get cached value if not expired."""

    def set(self, key: str, value: Any, metadata: dict | None = None):
        """Set cached value with metadata."""

    def invalidate(self, key: str):
        """Invalidate specific entry."""

    def invalidate_by_table(self, table: str):
        """Invalidate all entries for a table."""

    def invalidate_by_pattern(self, pattern: str):
        """Invalidate entries matching pattern."""

    def get_stats(self) -> dict:
        """Return cache statistics."""

    def cleanup_expired(self) -> int:
        """Remove expired entries, return count removed."""
```

**Statistics:**

| Metric | Description |
|--------|-------------|
| `hits` | Number of cache hits |
| `misses` | Number of cache misses |
| `hit_rate` | hits / (hits + misses) |
| `evictions` | Number of LRU evictions |
| `invalidations` | Number of explicit invalidations |
| `size` | Current cache size |
| `max_size` | Maximum cache size |
| `ttl` | Time-to-live in seconds |

#### 3.3.3 CachedQueryMixin

```python
class CachedQueryMixin:
    """Mixin to add caching capabilities to database adapters."""

    def _init_cache(self, ttl: float = 30.0, max_size: int = 1000, enabled: bool = True):
        """Initialize query cache."""

    def cached_query(self, operation: str, params: dict, table: str | None = None):
        """Decorator for cached query operations."""
```

### 3.4 In-Memory Store

#### 3.4.1 Store Trait

```rust
#[async_trait]
pub trait Store<K, V>: Send + Sync {
    async fn get(&self, key: &K) -> StoreResult<Option<V>>;
    async fn set(&self, key: K, value: V) -> StoreResult<()>;
    async fn delete(&self, key: &K) -> StoreResult<()>;
    async fn exists(&self, key: &K) -> StoreResult<bool>;
    async fn keys(&self) -> StoreResult<Vec<K>>;
    async fn entries(&self) -> StoreResult<Vec<(K, V)>>;
    async fn clear(&self) -> StoreResult<()>;
    async fn len(&self) -> StoreResult<usize>;
    async fn is_empty(&self) -> StoreResult<bool>;
}
```

#### 3.4.2 InMemoryStore

Thread-safe, async-compatible key-value store using `RwLock<HashMap>`:

| Feature | Description |
|---------|-------------|
| Concurrency | Read-write lock (multiple readers, single writer) |
| Capacity | Optional initial capacity |
| Thread Safety | `Arc<RwLock<HashMap>>` |
| Async | All operations are async |

#### 3.4.3 InMemoryStoreWithTTL

Extends `InMemoryStore` with time-to-live expiration:

| Feature | Description |
|---------|-------------|
| TTL | Configurable expiration time (seconds) |
| Expiration Check | On every read operation |
| Expired Entry Handling | Treated as non-existent |

#### 3.4.4 StoreBuilder

```rust
pub struct StoreBuilder<K, V> {
    capacity: Option<usize>,
    ttl_seconds: Option<i64>,
}

impl StoreBuilder {
    pub fn capacity(self, capacity: usize) -> Self;
    pub fn ttl(self, seconds: i64) -> Self;
    pub fn build(self) -> InMemoryStore<K, V>;
    pub fn build_with_ttl(self) -> InMemoryStoreWithTTL<K, V>;
}
```

### 3.5 Storage Backends

#### 3.5.1 StorageBackend Trait

```python
class StorageBackend(ABC):
    async def upload(
        self, bucket: str, path: str, data: bytes,
        *, content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str: ...

    async def download(self, bucket: str, path: str) -> bytes: ...
    async def delete(self, bucket: str, path: str) -> bool: ...
    async def exists(self, bucket: str, path: str) -> bool: ...
    async def list_files(
        self, bucket: str,
        prefix: str | None = None,
        limit: int | None = None,
    ) -> list[dict]: ...
    def get_public_url(self, bucket: str, path: str) -> str: ...
    async def get_signed_url(
        self, bucket: str, path: str, expires_in: int = 3600,
    ) -> str: ...
    async def stream_upload(
        self, bucket: str, path: str,
        chunk_iterator: AsyncIterator[bytes],
    ) -> str: ...
    async def stream_download(
        self, bucket: str, path: str, chunk_size: int = 8192,
    ) -> AsyncIterator[bytes]: ...
```

#### 3.5.2 Backend Implementations

| Backend | Type | Upload | Download | Streaming | Auth |
|---------|------|--------|----------|-----------|------|
| S3Backend | Object storage | Yes | Yes | Yes | AWS credentials |
| SupabaseBackend | Object storage | Yes | Yes | Yes | API key |
| LocalBackend | File system | Yes | Yes | Yes | File permissions |
| MemoryBackend | In-memory | Yes | Yes | No | None |
| SQLAlchemyBackend | Relational | Yes | Yes | No | DB credentials |

#### 3.5.3 Repository Pattern

```python
class Repository(ABC, Generic[T]):
    async def get(self, id: str) -> T | None: ...
    async def save(self, entity: T) -> T: ...
    async def delete(self, id: str) -> bool: ...
    async def list(self, **filters) -> list[T]: ...
```

### 3.6 Database Management

#### 3.6.1 Database Engine

```python
class Database:
    def __init__(self, adapter):
        self.adapter = adapter

    def from_(self, table: str):
        return self.adapter.from_(table)

    async def auth_context(self, jwt: str):
        if hasattr(self.adapter, "with_auth"):
            return await self.adapter.with_auth(jwt)
        return self
```

#### 3.6.2 Database Adapters

| Adapter | Platform | Features |
|---------|----------|----------|
| PostgresAdapter | PostgreSQL | Standard SQL, connection pooling |
| SupabaseAdapter | Supabase | REST API, real-time, auth context |
| NeonAdapter | Neon | Serverless PostgreSQL, branching |

#### 3.6.3 Connection Pooling

```python
class ConnectionPool:
    """Manage database connection pool."""

class PoolManager:
    """Manage multiple connection pools."""
```

#### 3.6.4 Real-Time Subscriptions

```python
class RealtimeClient:
    """Subscribe to database changes via WebSocket."""

    async def subscribe(self, table: str, filter: str, handler):
        """Subscribe to table changes."""

    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe from changes."""
```

#### 3.6.5 Migrations

```python
class MigrationEngine:
    """Manage database schema migrations."""

    async def migrate(self, direction: str = "up"):
        """Run migrations."""

    async def rollback(self, steps: int = 1):
        """Rollback migrations."""
```

### 3.7 Webhook Delivery

#### 3.7.1 WebhookManager

```python
class WebhookManager:
    """Manage webhook subscriptions and delivery."""

    async def register(self, url: str, events: list[str], secret: str):
        """Register a webhook endpoint."""

    async def deliver(self, event: dict, webhook: WebhookConfig):
        """Deliver event to webhook with retry."""
```

#### 3.7.2 Signature Verification

```python
class WebhookSignature:
    @staticmethod
    def generate_signature(payload: bytes, secret: str, timestamp: int) -> str:
        """Generate HMAC-SHA256 signature."""

    @staticmethod
    def verify_signature(
        payload: bytes, signature: str, secret: str,
        timestamp: int, max_age: int = 300,
    ) -> bool:
        """Verify webhook signature and timestamp."""
```

#### 3.7.3 Retry Policy

```python
class RetryPolicy:
    max_retries: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
```

---

## 4. Technical Architecture

### 4.1 Concurrency Model

```
+----------------------------------------------------------------+
|                    Concurrency Architecture                    |
+----------------------------------------------------------------+
|                                                                |
|  Rust:                                                         |
|  +----------------------------------------------------------+  |
|  | tokio runtime (multi-threaded)                           |  |
|  |                                                          |  |
|  | Event Bus:                                               |  |
|  |   - broadcast::Sender<EventEnvelope> (all events)        |  |
|  |   - mpsc::Sender<E> per type (typed events)              |  |
|  |   - Bounded channels (capacity: 100)                     |  |
|  |                                                          |  |
|  | Cache:                                                   |  |
|  |   - DashMap (concurrent hash map, lock-free reads)       |  |
|  |   - Arc<DashMap> for shared ownership                    |  |
|  |                                                          |  |
|  | Store:                                                   |  |
|  |   - RwLock<HashMap> (multiple readers, single writer)    |  |
|  |   - Arc<RwLock<>> for shared ownership                   |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python:                                                       |
|  +----------------------------------------------------------+  |
|  | asyncio event loop                                       |  |
|  |                                                          |  |
|  | Event Bus:                                               |  |
|  |   - dict[str, list[Callable]] (handlers)                 |  |
|  |   - asyncio.gather for concurrent handler execution      |  |
|  |   - threading.RLock for QueryCache                       |  |
|  |                                                          |  |
|  | NATS:                                                    |  |
|  |   - async nats-py client                                 |  |
|  |   - JetStream durable consumers                          |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Go:                                                           |
|  +----------------------------------------------------------+  |
|  | goroutines + channels                                      |  |
|  |                                                          |  |
|  | Storage:                                                 |  |
|  |   - sync.Mutex for concurrent access                     |  |
|  |   - context.Context for cancellation                     |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 4.2 Error Hierarchy

```
+----------------------------------------------------------------+
|                      Error Hierarchy                           |
+----------------------------------------------------------------+
|                                                                |
|  Rust:                                                         |
|  +----------------------------------------------------------+  |
|  | EventSourcingError                                       |  |
|  |   +-- StreamNotFound(String)                             |  |
|  |   +-- Serialization(String)                              |  |
|  |   +-- Deserialization(String)                            |  |
|  |   +-- HashVerificationFailed { sequence }                |  |
|  |   +-- ChainBroken { sequence }                           |  |
|  |                                                          |  |
|  | EventBusError                                            |  |
|  |   +-- PublishFailed(String)                              |  |
|  |   +-- SubscribeFailed(String)                            |  |
|  |   +-- UnknownEventType(String)                           |  |
|  |   +-- BusClosed                                          |  |
|  |                                                          |  |
|  | StoreError                                               |  |
|  |   +-- NotFound(String)                                   |  |
|  |   +-- AlreadyExists(String)                              |  |
|  |   +-- Serialization(String)                              |  |
|  |   +-- Internal(String)                                   |  |
|  |                                                          |  |
|  | HashError                                                |  |
|  |   +-- InvalidFirstEvent                                  |  |
|  |   +-- InvalidHash { index }                              |  |
|  |   +-- BrokenChain { index }                              |  |
|  |   +-- SequenceGap { index }                              |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python:                                                       |
|  +----------------------------------------------------------+  |
|  | StorageError (base)                                      |  |
|  |   +-- UploadError                                        |  |
|  |   +-- DownloadError                                      |  |
|  |   +-- DeleteError                                        |  |
|  |   +-- AuthenticationError                                |  |
|  |                                                          |  |
|  | RepositoryError (base)                                   |  |
|  |   +-- NotFoundError                                      |  |
|  |   +-- DuplicateError                                     |  |
|  |   +-- ValidationError                                    |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 4.3 Metrics Integration

```
+----------------------------------------------------------------+
|                      Metrics Architecture                      |
+----------------------------------------------------------------+
|                                                                |
|  Rust: phenotype_observability integration                     |
|  +----------------------------------------------------------+  |
|  | Counters:                                                |  |
|  |   - event_store.append_batch (every 100 events)          |  |
|  |   - cache.hits (by tier: L1, L2)                         |  |
|  |   - cache.misses (by tier: L1, L2)                       |  |
|  |                                                          |  |
|  | Gauges:                                                  |  |
|  |   - cache.l1_size                                        |  |
|  |   - cache.l2_size                                        |  |
|  |                                                          |  |
|  | Histograms:                                              |  |
|  |   - event_store.append_latency                           |  |
|  |   - cache.get_latency                                    |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python: Standard logging + custom stats                      |
|  +----------------------------------------------------------+  |
|  | QueryCache.get_stats():                                    |  |
|  |   - hits, misses, hit_rate                                 |  |
|  |   - evictions, invalidations                               |  |
|  |   - size, max_size, ttl                                    |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 4.4 Observability

```
+----------------------------------------------------------------+
|                    Observability Stack                         |
+----------------------------------------------------------------+
|                                                                |
|  Logging:                                                      |
|  +----------------------------------------------------------+  |
|  | Rust: tracing (structured, async)                        |  |
|  |   - debug!("Published event: {}", event_type)            |  |
|  |   - error!("Handler error: {}", e)                       |  |
|  |                                                          |  |
|  | Python: logging module                                   |  |
|  |   - print(f"Error in event handler: {e}")                |  |
|  |   - Convert Python logging to structlog in a follow-up   |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Tracing:                                                      |
|  +----------------------------------------------------------+  |
|  | Rust: phenotype_infrakit::phenotype_observability        |  |
|  |   - init_tracer(service_name)                            |  |
|  |   - Span per event append                                |  |
|  |   - Span per cache operation                             |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Correlation:                                                  |
|  +----------------------------------------------------------+  |
|  | Event correlation_id propagates through:                   |  |
|  |   API Request -> Event Bus -> Handler -> Event Store      |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

---

## 5. API Reference

### 5.1 Rust API

#### 5.1.1 Event Sourcing

```rust
// Create event store
let mut store = InMemoryEventStore::new();

// Append event
let seq = store.append("aggregate-id", event)?;

// Read events
let events: Vec<EventEnvelope<MyEvent>> = store.read("aggregate-id", 0)?;

// Verify chain
verify_chain(&events)?;

// Get current sequence
let current = store.current_sequence("aggregate-id")?;
```

#### 5.1.2 Event Bus

```rust
// Create event bus
let bus = Arc::new(InMemoryEventBus::default());

// Subscribe
let mut rx = bus.subscribe::<MyEvent>().await?;

// Publish
bus.publish(MyEvent::new("data")).await?;

// Subscribe to all
let mut all_rx = bus.subscribe_all()?;
```

#### 5.1.3 Cache

```rust
// Create cache
let cache = TwoTierCache::<String, String>::new(100, 1000);

// Put
cache.put("key".to_string(), "value".to_string());

// Get
let value = cache.get(&"key".to_string());

// Remove
cache.remove(&"key".to_string());

// Clear
cache.clear();
```

#### 5.1.4 In-Memory Store

```rust
// Create store
let store = InMemoryStore::<String, String>::new();

// Set
store.set("key".to_string(), "value".to_string()).await?;

// Get
let value = store.get(&"key".to_string()).await?;

// Delete
store.delete(&"key".to_string()).await?;

// With TTL
let ttl_store = InMemoryStoreWithTTL::<String, String>::new(300); // 5 min
```

### 5.2 Python API

#### 5.2.1 Event Bus

```python
# Create event bus
bus = EventBus()

# Register handler
@bus.on("user.created")
async def handle_user_created(event):
    print(f"User created: {event.data}")

# Register wildcard handler
@bus.on("user.*")
async def handle_all_user_events(event):
    print(f"User event: {event.name}")

# Publish
await bus.publish("user.created", data={"user_id": "123"})
```

#### 5.2.2 Event Store

```python
# Create event store
store = EventStore(storage_path=Path("/tmp/events"))

# Append event
event = await store.append(
    event_type="UserCreated",
    aggregate_id="user-123",
    aggregate_type="User",
    data={"email": "user@example.com"},
)

# Get stream
events = await store.get_stream("user-123")

# Replay
state = await store.replay("user-123", reducer_fn)
```

#### 5.2.3 Query Cache

```python
# Create cache
cache = QueryCache(ttl=30.0, max_size=1000)

# Generate key
key = cache.generate_key("select", {"table": "users", "id": 123})

# Set
cache.set(key, {"name": "Alice"}, metadata={"table": "users"})

# Get
result = cache.get(key)

# Invalidate
cache.invalidate_by_table("users")

# Stats
stats = cache.get_stats()
```

#### 5.2.4 Storage

```python
# Create backend
backend = S3Backend(bucket="my-bucket", region="us-east-1")

# Upload
url = await backend.upload("bucket", "path/file.txt", b"content")

# Download
data = await backend.download("bucket", "path/file.txt")

# Delete
deleted = await backend.delete("bucket", "path/file.txt")

# List
files = await backend.list_files("bucket", prefix="path/")
```

#### 5.2.5 Database

```python
# Create database
db = Database(SupabaseAdapter(url, key))

# Query
query = db.from_("users").select("*").eq("id", "123")

# Auth context
auth_db = await db.auth_context(jwt_token)
```

### 5.3 Go API

#### 5.3.1 Storage

```go
// Create backend
backend := NewS3Backend(region, bucket)

// Upload
url, err := backend.Upload(ctx, bucket, path, data, opts)

// Download
reader, err := backend.Download(ctx, bucket, path)

// Delete
err := backend.Delete(ctx, bucket, path)
```

---

## 6. Error Handling

### 6.1 Error Handling Strategy

```
+----------------------------------------------------------------+
|                    Error Handling Strategy                     |
+----------------------------------------------------------------+
|                                                                |
|  Rust: thiserror derive macros                                |
|  +----------------------------------------------------------+  |
|  | - All errors implement std::error::Error                 |  |
|  | - Display formatting via #[error("...")]                 |  |
|  | - Source chaining via #[from]                            |  |
|  | - Result type aliases (Result<T, EventSourcingError>)    |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python: Exception hierarchy                                  |
|  +----------------------------------------------------------+  |
|  | - Custom exception classes per domain                    |  |
|  | - Inherit from base exception                            |  |
|  | - Include context in exception message                   |  |
|  | - Add exception-group support for Python 3.11+           |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Go: error interface + fmt.Errorf with %w                     |
|  +----------------------------------------------------------+  |
|  | - Wrap errors with context: fmt.Errorf("context: %w", e) |  |
|  | - Type assertions for error checking                     |  |
|  | - errors.Is / errors.As for error chain inspection       |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 6.2 Error Recovery Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Retry | Retry failed operation with backoff | Network failures, temporary unavailability |
| Circuit Breaker | Stop calling failing service after threshold | Cascading failure prevention |
| Fallback | Use alternative implementation | Cache miss, degraded mode |
| Dead Letter | Send failed events to separate queue | Unprocessable events |
| Idempotency | Safe to retry without side effects | Event replay, duplicate delivery |

### 6.3 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `STORE_NOT_FOUND` | Storage | Resource does not exist |
| `STORE_ALREADY_EXISTS` | Storage | Resource already exists |
| `STORE_SERIALIZATION` | Storage | Serialization/deserialization failed |
| `EVENT_STREAM_NOT_FOUND` | Event Sourcing | Aggregate stream not found |
| `EVENT_HASH_VERIFICATION` | Event Sourcing | Hash chain verification failed |
| `EVENT_CHAIN_BROKEN` | Event Sourcing | Chain linkage broken |
| `EVENT_SEQUENCE_GAP` | Event Sourcing | Non-consecutive sequence numbers |
| `BUS_PUBLISH_FAILED` | Event Bus | Failed to publish event |
| `BUS_SUBSCRIBE_FAILED` | Event Bus | Failed to subscribe |
| `BUS_CHANNEL_CLOSED` | Event Bus | Channel closed unexpectedly |
| `CACHE_MISS` | Cache | Key not found in cache |
| `CACHE_EXPIRED` | Cache | Entry has expired |
| `AUTH_FAILED` | Security | Authentication failed |
| `SIGNATURE_INVALID` | Security | Webhook signature verification failed |

---

## 7. Security

### 7.1 Security Architecture

```
+----------------------------------------------------------------+
|                    Security Architecture                       |
+----------------------------------------------------------------+
|                                                                |
|  Layer 1: Transport Security                                  |
|  +----------------------------------------------------------+  |
|  | - TLS for all network communication                      |  |
|  | - NATS TLS authentication                                |  |
|  | - Supabase JWT authentication                            |  |
|  | - S3 IAM roles / access keys                             |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Layer 2: Data Integrity                                      |
|  +----------------------------------------------------------+  |
|  | - Blake3 hash chains (event sourcing)                    |  |
|  | - Chain verification on read                             |  |
|  | - Tamper-evident audit trail                             |  |
|  | - HMAC-SHA256 webhook signatures                         |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Layer 3: Access Control                                      |
|  +----------------------------------------------------------+  |
|  | - Row-Level Security (PostgreSQL)                        |  |
|  | - JWT-based auth context                                 |  |
|  | - Tenant isolation                                       |  |
|  | - Signed URLs for temporary access                       |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Layer 4: Audit & Compliance                                  |
|  +----------------------------------------------------------+  |
|  | - Immutable event log                                    |  |
|  | - Cryptographic verification                             |  |
|  | - Complete replay capability                             |  |
|  | - Webhook delivery with retry and logging                |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 7.2 Hash Chain Security

| Property | Description | Importance |
|----------|-------------|------------|
| Tamper Evidence | Any modification breaks the chain | Critical for audit |
| Ordering Guarantee | Sequence + previous hash ensures order | Event ordering |
| Cryptographic Security | 256-bit Blake3 output | Collision resistant |
| Performance | 1.4+ GB/s single-threaded | Real-time verification |

### 7.3 Webhook Security

```python
# Signature verification
class WebhookSignature:
    @staticmethod
    def verify_signature(
        payload: bytes,
        signature: str,
        secret: str,
        timestamp: int,
        max_age: int = 300,  # 5 minutes
    ) -> bool:
        # Check timestamp freshness
        if time.time() - timestamp > max_age:
            return False

        # Constant-time comparison
        expected = hmac.new(
            secret.encode(),
            f"{timestamp}.{payload.decode()}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
```

### 7.4 Data Protection

| Data Type | Protection | Method |
|-----------|-----------|--------|
| Event payloads | Integrity | Blake3 hash chain |
| Webhook payloads | Authenticity | HMAC-SHA256 signature |
| Database queries | Access control | JWT auth context |
| Storage uploads | Access control | IAM roles / API keys |
| Cache entries | Isolation | Process memory |

---

## 8. Performance

### 8.1 Performance Targets

| Operation | Target Latency | Target Throughput | Notes |
|-----------|---------------|-------------------|-------|
| Event Append (in-memory) | < 1us | 1M+/sec | Rust, no I/O |
| Event Read (sequential) | < 1us | 1M+/sec | In-memory |
| Hash Computation (Blake3) | < 100ns | 10M+/sec | Per event |
| Chain Verification | 1-5us | 200K+/sec | Per event |
| Cache L1 Hit | ~100ns | 10M+/sec | DashMap |
| Cache L2 Hit | ~200ns | 5M+/sec | + promotion |
| Event Publish (tokio) | 1-10us | 100K+/sec | In-process |
| Event Publish (NATS) | 100-500us | 10K+/sec | Network |
| Storage Upload (local) | 100us-1ms | 1K+/sec | Disk I/O |
| Storage Upload (S3) | 50-500ms | 100+/sec | Network |

### 8.2 Memory Usage

| Component | Memory Profile | Notes |
|-----------|---------------|-------|
| InMemoryEventStore | O(events) | All events in memory |
| InMemoryStore | O(entries) | All entries in memory |
| TwoTierCache | O(l1_capacity + l2_capacity) | Bounded by config |
| QueryCache | O(max_size) | Bounded by config |
| EventEnvelope<T> | sizeof(T) + 80 bytes | Hash + metadata overhead |

### 8.3 Optimization Guidelines

1. **Use L1 cache for hot data**: Keep frequently accessed items in L1 (small, fast)
2. **Batch event appends**: Group multiple events before appending
3. **Use snapshots for long streams**: Avoid replaying thousands of events
4. **Pre-allocate store capacity**: Use `with_capacity()` to avoid reallocations
5. **Monitor cache hit rates**: Aim for > 80% L1 hit rate
6. **Use bounded channels**: Prevent memory exhaustion under load

---

## 9. Testing

### 9.1 Testing Strategy

```
+----------------------------------------------------------------+
|                      Testing Pyramid                           |
+----------------------------------------------------------------+
|                                                                |
|                         /\                                     |
|                        /  \    Integration Tests               |
|                       /----\   Cross-component, NATS, DB       |
|                      /      \                                  |
|                     /--------\  Component Tests                 |
|                    /          \ Event bus, cache, store         |
|                   /------------\                                |
|                  /              \ Unit Tests                    |
|                 /________________\ Hash chains, serialization   |
|                                                                |
+----------------------------------------------------------------+
```

### 9.2 Unit Tests

| Component | Test Coverage | Key Tests |
|-----------|--------------|-----------|
| Event Sourcing | Hash computation, chain verification, append/read | `verify_chain`, `compute_hash` |
| Event Bus | Publish/subscribe, filtering, broadcast | Type-specific channels, wildcard matching |
| Cache | Get/put/remove, eviction, promotion, TTL | L1/L2 interaction, expiration |
| In-Memory Store | CRUD operations, TTL expiration | Concurrent access, time-based tests |

### 9.3 Test Examples

```rust
// Rust: Two-tier cache tests
#[test]
fn test_two_tier_cache_basic() {
    let cache: TwoTierCache<String, String> = TwoTierCache::new(10, 100);
    cache.put("key1".to_string(), "value1".to_string());
    assert_eq!(cache.get(&"key1".to_string()), Some("value1".to_string()));
}

#[test]
fn test_two_tier_cache_eviction() {
    let cache: TwoTierCache<String, String> = TwoTierCache::new(2, 100);
    cache.put("k1".to_string(), "v1".to_string());
    cache.put("k2".to_string(), "v2".to_string());
    cache.put("k3".to_string(), "v3".to_string());
    assert_eq!(cache.l1_len(), 2);
    assert!(cache.l2_len() >= 3);
}
```

```python
# Python: Query cache tests
def test_query_cache_ttl():
    cache = QueryCache(ttl=0.1, max_size=100)
    key = cache.generate_key("test", {"id": 1})
    cache.set(key, "value")
    assert cache.get(key) == "value"
    time.sleep(0.2)
    assert cache.get(key) is None  # Expired
```

```rust
// Rust: TTL store tests
#[tokio::test]
async fn test_ttl_store() {
    let store = InMemoryStoreWithTTL::<String, String>::new(1);
    store.set("key1".to_string(), "value1".to_string()).await.unwrap();
    assert!(store.exists(&"key1".to_string()).await.unwrap());
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    assert!(!store.exists(&"key1".to_string()).await.unwrap());
}
```

### 9.4 Integration Tests

| Test | Components | Description |
|------|-----------|-------------|
| Event roundtrip | Event Bus + Event Store | Publish event, verify stored with hash chain |
| Cache coherence | Cache + Event Bus | Event invalidates cache entry |
| NATS delivery | NATS + Event Handlers | Event delivered to all subscribers |
| Storage backend | Storage + File system | Upload, download, delete cycle |

---

## 10. Deployment

### 10.1 Deployment Architecture

```
+----------------------------------------------------------------+
|                    Deployment Architecture                     |
+----------------------------------------------------------------+
|                                                                |
|  Rust Services:                                                |
|  +----------------------------------------------------------+  |
|  | - Compiled binary (static linking)                       |  |
|  | - Container image (distroless or alpine)                 |  |
|  | - Health check endpoint                                  |  |
|  | - Graceful shutdown (tokio signal handling)              |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Python Services:                                              |
|  +----------------------------------------------------------+  |
|  | - uv/pip installable packages                            |  |
|  | - Container image (python slim)                          |  |
|  | - ASGI server (FastAPI) or asyncio runner                |  |
|  | - Health check endpoint                                  |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Go Services:                                                  |
|  +----------------------------------------------------------+  |
|  | - Compiled binary (static linking)                       |  |
|  | - Container image (scratch or distroless)                |  |
|  | - Health check endpoint                                  |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Infrastructure:                                               |
|  +----------------------------------------------------------+  |
|  | - NATS JetStream cluster (persistent messaging)          |  |
|  | - PostgreSQL / Supabase (event persistence)              |  |
|  | - S3 / Supabase Storage (file storage)                   |  |
|  | - Redis (future: L3 cache)                               |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 10.2 Configuration

| Component | Configuration | Method |
|-----------|--------------|--------|
| Rust | Environment variables, config files | `config` crate |
| Python | Environment variables, pydantic settings | `pydantic-settings` |
| Go | Environment variables, config structs | `viper` or custom |

### 10.3 Environment Variables

| Variable | Component | Description |
|----------|-----------|-------------|
| `NATS_URL` | Event Bus | NATS server URL |
| `SUPABASE_URL` | Database | Supabase project URL |
| `SUPABASE_KEY` | Database | Supabase API key |
| `S3_BUCKET` | Storage | S3 bucket name |
| `S3_REGION` | Storage | S3 region |
| `CACHE_L1_CAPACITY` | Cache | L1 cache size |
| `CACHE_L2_CAPACITY` | Cache | L2 cache size |
| `CACHE_TTL` | Cache | Default TTL in seconds |

---

## 11. Migration Guide

### 11.1 From In-Memory to Persistent

```
+----------------------------------------------------------------+
|              Migration: In-Memory to Persistent                |
+----------------------------------------------------------------+
|                                                                |
|  Step 1: Add persistent backend                                |
|  +----------------------------------------------------------+  |
|  | - Implement EventStore for PostgreSQL                    |  |
|  | - Implement EventStore for S3                            |  |
|  | - Keep InMemoryEventStore for testing                    |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Step 2: Dual-write during migration                           |
|  +----------------------------------------------------------+  |
|  | - Write to both in-memory and persistent store           |  |
|  | - Read from persistent store                             |  |
|  | - Verify consistency between stores                      |  |
|  +----------------------------------------------------------+  |
|                                                                |
|  Step 3: Cutover                                               |
|  +----------------------------------------------------------+  |
|  | - Switch reads to persistent store                       |  |
|  | - Remove in-memory store from production                 |  |
|  | - Keep in-memory store for testing                       |  |
|  +----------------------------------------------------------+  |
|                                                                |
+----------------------------------------------------------------+
```

### 11.2 Schema Migration

See [ADR-003: Schema Evolution Strategy](docs/adr/ADR-003-schema-evolution.md) for detailed migration procedures.

### 11.3 Breaking Changes

| Change | Migration Path |
|--------|---------------|
| Event envelope field addition | Add `#[serde(default)]` for backward compatibility |
| Event type rename | Use `#[serde(alias = "old_name")]` for transition period |
| Cache API change | Deprecate old methods, add new methods with migration guide |
| Storage backend interface | Implement both old and new interfaces during transition |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Aggregate** | A domain object reconstructed from its event stream |
| **Append-Only** | Data can only be added, never modified or deleted |
| **Backpressure** | Mechanism to slow producers when consumers are overwhelmed |
| **Blake3** | Fast cryptographic hash function (1.4+ GB/s) |
| **Broadcast Channel** | Tokio channel that sends to all subscribers (may drop slow consumers) |
| **CQRS** | Command Query Responsibility Segregation pattern |
| **DashMap** | Concurrent hash map for Rust (lock-free reads) |
| **Event** | Immutable record of something that happened |
| **Event Bus** | Publish/subscribe messaging system |
| **Event Sourcing** | Storing state as a sequence of events |
| **Event Store** | Storage system for event streams |
| **Hash Chain** | Sequence of hashes where each links to the previous |
| **JetStream** | NATS persistent streaming layer |
| **L1 Cache** | Hot cache tier (small, fast) |
| **L2 Cache** | Warm cache tier (larger, slightly slower) |
| **MPSC Channel** | Multi-producer, single-consumer channel |
| **Projection** | Read model derived from event stream |
| **Snapshot** | Serialized aggregate state for performance optimization |
| **Stream** | Ordered sequence of events for a single aggregate |
| **TTL** | Time-To-Live, expiration time for cache entries |
| **ZERO_HASH** | 32-byte zero array, used as first event's previous_hash |

---

## 13. Change Log

### Version 2.0 (2026-04-03)

**Major Changes:**
- Comprehensive specification covering all DataKit components
- Added Go module documentation
- Expanded Python API reference
- Added security architecture section
- Added performance targets and optimization guidelines
- Added testing strategy and examples
- Added deployment architecture
- Added migration guide

### Version 1.0 (2025-12-01)

**Initial Specification:**
- Rust event sourcing with Blake3 hash chains
- Rust event bus with tokio channels
- Rust two-tier cache adapter
- Rust in-memory store
- Basic Python event bus
- Basic Python query cache

---

## 14. Compliance Requirements

### 14.1 Audit Requirements

For audit-heavy domains, DataKit provides:

| Requirement | Implementation | Verification |
|-------------|---------------|--------------|
| Immutable event log | Append-only event store | Hash chain verification |
| Tamper evidence | Blake3 hash chains | `verify_chain()` function |
| Complete history | Event stream per aggregate | `read(from_sequence=0)` |
| Timestamp accuracy | UTC timestamps | `chrono::DateTime<Utc>` |
| Sequence integrity | Monotonically increasing | Sequence gap detection |
| Event ordering | Per-stream ordering | Chain linkage verification |

### 14.2 Data Retention

| Data Type | Retention Policy | Implementation |
|-----------|-----------------|----------------|
| Events | Indefinite (append-only) | Event store with no delete |
| Snapshots | Configurable TTL | `SnapshotConfig.max_age` |
| Cache entries | TTL-based expiration | `QueryCache.ttl`, `InMemoryStoreWithTTL` |
| Webhook deliveries | Retry period + log | `RetryPolicy` configuration |

### 14.3 Regulatory Considerations

| Regulation | Relevance | DataKit Support |
|------------|-----------|-----------------|
| GDPR | Data subject rights | Event deletion requires careful design (append-only) |
| HIPAA | Healthcare data | Encryption at rest, audit trail |
| SOC 2 | Security controls | Hash chain integrity, access logging |
| PCI DSS | Payment data | Tokenization, audit trail |

---

## 15. Future Roadmap

### 15.1 Near-Term (Q2 2026)

| Feature | Priority | Description |
|---------|----------|-------------|
| PostgreSQL Event Store | High | Persistent backend for `phenotype-event-sourcing` |
| S3 Event Store | High | Object storage backend for event persistence |
| Schema Registry | High | JSON schema files with cross-language validation |
| Redis L3 Cache | Medium | Distributed cache tier for multi-instance deployments |
| NATS Go Client | Medium | Go integration with NATS JetStream |

### 15.2 Mid-Term (Q3-Q4 2026)

| Feature | Priority | Description |
|---------|----------|-------------|
| Apache Arrow Integration | Medium | Cross-language data exchange format |
| WebAssembly Plugins | Low | Custom transformation plugins |
| Kubernetes Operator | Low | Automated DataKit deployment |
| Grafana Dashboards | Low | Pre-built observability dashboards |
| OpenTelemetry Export | Medium | Standard tracing integration |

### 15.3 Long-Term (2027+)

| Feature | Priority | Description |
|---------|----------|-------------|
| Distributed Event Store | Low | Multi-node event sourcing |
| CRDT Replication | Low | Conflict-free replicated data types |
| ML Pipeline Integration | Low | Real-time feature store |
| Auto-Scaling | Low | Dynamic resource management |

---

## 16. Contributing

### 16.1 Development Setup

```bash
# Rust
cd rust && cargo build && cargo test

# Python
cd python/pheno-events && uv sync && uv run pytest
cd python/pheno-caching && uv sync && uv run pytest
cd python/pheno-database && uv sync && uv run pytest
cd python/pheno-storage && uv sync && uv run pytest

# Go
cd go && go build ./...
```

### 16.2 Code Style

| Language | Formatter | Linter |
|----------|-----------|--------|
| Rust | `cargo fmt` | `cargo clippy` |
| Python | `ruff format` | `ruff check` |
| Go | `gofmt` | `golangci-lint` |

### 16.3 Pull Request Requirements

1. All tests pass (`cargo test`, `pytest`, `go test`)
2. No clippy warnings (`cargo clippy -- -D warnings`)
3. No ruff violations (`ruff check`)
4. Documentation updated for API changes
5. ADR updated if architectural decision changed

---

## 17. Support

### 17.1 Resources

| Resource | Location |
|----------|----------|
| Specifications | `docs/` directory |
| ADRs | `docs/adr/` directory |
| Research | `docs/research/` directory |
| Examples | `rust/*/examples/` directory |
| PhenoSpecs | https://github.com/KooshaPari/PhenoSpecs |
| PhenoHandbook | https://github.com/KooshaPari/PhenoHandbook |
| HexaKit | https://github.com/KooshaPari/HexaKit |

### 17.2 Issue Reporting

Report issues through the AgilePlus workflow:
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify --title "DataKit: <issue>" --description "<description>"
```

---

*Specification Version: 2.0*  
*Last Updated: 2026-04-03*  
*Next Review: 2026-07-03*
