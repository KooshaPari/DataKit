# Agent Rules - DataKit

**This project is managed through AgilePlus.**

## Project Overview

### Name
DataKit (Phenotype Data Processing Toolkit)

### Description
DataKit is the data processing toolkit for the Phenotype ecosystem. It provides multi-language implementations of core data patterns: event sourcing with cryptographic integrity (Blake3 hash chains), async event communication, hierarchical caching, storage abstraction, and database management. It spans Rust, Go, and Python with 131+ files across multiple domains.

### Location
`/Users/kooshapari/CodeProjects/Phenotype/repos/DataKit`

### Language Stack
- **Rust**: Event sourcing, event bus, cache adapter, in-memory store
- **Go**: Storage abstraction, caching, event handling, persistence
- **Python**: Event system (NATS JetStream), caching, database management, storage backends

### Purpose & Goals
- **Mission**: Provide robust, cryptographically-verified data processing primitives
- **Primary Goal**: Enable event sourcing with tamper-evident audit trails
- **Secondary Goals**:
  - Implement async-first event communication across services
  - Provide multi-tier caching with hot/warm separation
  - Deliver unified storage backend abstraction
  - Support multiple database platforms (PostgreSQL, Supabase, Neon)

### Key Responsibilities
1. **Event Sourcing**: Append-only storage with Blake3 hash chain verification
2. **Event Bus**: Async pub/sub messaging with NATS JetStream
3. **Caching**: L1/L2 tiered cache with automatic invalidation
4. **Storage**: Unified abstraction over S3, Supabase, local filesystem
5. **Database Management**: Multi-platform adapters with connection pooling

---

## Quick Start Commands

### Prerequisites

```bash
# Rust 1.75+
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Go 1.24+
brew install go@1.24

# Python 3.12+
brew install python@3.12

# NATS Server (for event bus)
brew install nats-server
brew services start nats-server
```

### Installation

```bash
# Navigate to DataKit
cd /Users/kooshapari/CodeProjects/Phenotype/repos/DataKit

# Build Rust components
cd rust && cargo build --workspace

# Install Go dependencies
cd go && go mod download

# Install Python components
pip install -e python/pheno-events/
pip install -e python/pheno-caching/
pip install -e python/pheno-database/
pip install -e python/pheno-storage/
pip install -e python/db-kit/
```

### Development Environment Setup

```bash
# Copy environment configuration
cp .env.example .env

# Start NATS (if not running)
nats-server -js

# Initialize test database
python -m pheno_database init --dev
```

### Running Examples

```bash
# Rust event sourcing example
cd rust/phenotype-event-sourcing && cargo run --example usage

# Go storage example
cd go/pheno-storage && go run examples/basic.go

# Python event bus example
python python/pheno-events/examples/nats_pubsub.py

# Database connection test
python -m pheno_database test-connection
```

### Verification

```bash
# Run Rust tests
cd rust && cargo test --workspace

# Run Go tests
cd go && go test ./...

# Run Python tests
pytest python/ -v

# Check event sourcing chain verification
cd rust/phenotype-event-sourcing && cargo test verify_chain -- --nocapture
```

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Service A  │  │   Service B  │  │   Service C  │       │
│  │              │  │              │  │              │       │
│  │ • Events     │  │ • Cache      │  │ • Storage    │       │
│  │ • Queries    │  │ • Queries    │  │ • Files      │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DataKit Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Rust Core Layer                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ Event        │  │ Event        │  │ Cache        │ │  │
│  │  │ Sourcing     │  │ Bus          │  │ Adapter      │ │  │
│  │  │              │  │              │  │              │ │  │
│  │  │ • Blake3     │  │ • tokio      │  │ • L1/L2      │ │  │
│  │  │ • Hash chain │  │ • DashMap   │  │ • Metrics    │ │  │
│  │  │ • Snapshots  │  │ • Channels  │  │ • TTL        │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  │  ┌───────────────────────────────────────────────────┐  │
│  │  │         In-Memory Store (Store<K, V>)             │  │
│  │  │         • RwLock<HashMap> • TTL support         │  │
│  │  └───────────────────────────────────────────────────┘  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Go Layer                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ pheno-       │  │ pheno-       │  │ pheno-       │ │  │
│  │  │ storage      │  │ cache        │  │ persistence  │ │  │
│  │  │              │  │              │  │              │ │  │
│  │  │ • Interfaces │  │ • Strategies │  │ • Layer      │ │  │
│  │  │ • Backends   │  │ • Context    │  │ • Migrations │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  Python Layer                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ pheno-       │  │ pheno-       │  │ pheno-       │ │  │
│  │  │ events       │  │ caching      │  │ database     │ │  │
│  │  │              │  │              │  │              │ │  │
│  │  │ • NATS Bus   │  │ • QueryCache │  │ • Adapters   │ │  │
│  │  │ • EventStore │  │ • DiskCache  │  │ • Pooling    │ │  │
│  │  │ • Webhooks   │  │ • Decorators │  │ • Realtime   │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  │  ┌───────────────────────────────────────────────────┐  │
│  │  │              db-kit (Unified)                   │  │
│  │  │   Migrations • Tenancy • Vector • RLS           │  │
│  │  └───────────────────────────────────────────────────┘  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│    NATS      │   │  PostgreSQL  │   │     S3       │
│  JetStream   │   │  Supabase    │   │   MinIO      │
│              │   │   Neon       │   │   Local      │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Event Sourcing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Event Stream Structure                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Stream: "order-123"                                            │
│                                                                 │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐             │
│  │  Event 0  │────▶│  Event 1  │────▶│  Event 2  │────▶ ...    │
│  │           │     │           │     │           │             │
│  │prev_hash:│     │prev_hash: │     │prev_hash: │             │
│  │0x0000...  │     │0xABCD...  │     │0x1234...  │             │
│  │hash:      │     │hash:      │     │hash:      │             │
│  │0xABCD...  │     │0x1234...  │     │0x5678...  │             │
│  │seq: 0     │     │seq: 1     │     │seq: 2     │             │
│  │payload:   │     │payload:   │     │payload:   │             │
│  │{...}      │     │{...}      │     │{...}      │             │
│  └───────────┘     └───────────┘     └───────────┘             │
│                                                                 │
│  Hash Computation:                                              │
│  hash = blake3(serialize(payload) || previous_hash ||          │
│               sequence_le_bytes)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Cache Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Two-Tier Cache Flow                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GET Operation:                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │  get(k)  │──▶│   L1     │──▶│   L2     │──▶│  None    │      │
│  │          │   │  Hit?    │   │  Hit?    │   │ (miss)   │      │
│  └──────────┘   └────┬─────┘   └────┬─────┘   └──────────┘      │
│                      │              │                           │
│              ┌───────┴──────┐ ┌──────┴──────┐                  │
│              │   Return     │ │  Promote    │                  │
│              │   Value      │ │  to L1      │                  │
│              │   (fast)     │ │             │                  │
│              └──────────────┘ └──────┬──────┘                  │
│                                      │                          │
│                              ┌───────┴──────┐                  │
│                              │   Return     │                  │
│                              │   Value      │                  │
│                              └──────────────┘                  │
│                                                                 │
│  PUT Operation:                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│  │  put(k)  │──▶│ L1 Full? │──▶│ Evict L1 │                  │
│  │          │   │          │   │ (FIFO)   │                  │
│  └──────────┘   └────┬─────┘   └────┬─────┘                  │
│                      │              │                           │
│              ┌───────┴──────────────┴───────┐                  │
│              │  Insert into L1 and L2       │                  │
│              └───────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Flow Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WRITE PATH:                                                    │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐             │
│  │ Client │──▶│ Event  │──▶│ Event  │──▶│Storage │             │
│  │ Request│   │ Bus    │   │ Store  │   │ (S3)   │             │
│  └────────┘   │Publish │   │Blake3  │   └────────┘             │
│               └────────┘   └────────┘                         │
│                                                                 │
│  READ PATH:                                                     │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐          │
│  │ Client │──▶│ Cache  │──▶│ Event  │──▶│Storage │          │
│  │ Query  │   │L1→L2  │   │ Store  │   │        │          │
│  └────────┘   └────────┘   │Read    │   └────────┘          │
│                            └────────┘                         │
│                                                                 │
│  CACHE INVALIDATION:                                            │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐          │
│  │ Data   │──▶│ Event  │──▶│ Cache  │──▶│Invalid-│          │
│  │ Change │   │ Bus    │   │ Listener│   │ate     │          │
│  └────────┘   └────────┘   └────────┘   └────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Standards

### Testing Requirements

#### Test Coverage
- **Minimum Coverage**: 80% for event sourcing, 75% for cache
- **Critical Paths**: 95% for hash chain verification
- **Integration Tests**: Required for all storage backends

#### Test Categories
```bash
# Rust tests
cd rust && cargo test --workspace
cd rust && cargo test --workspace --features integration

# Go tests
cd go && go test ./...
cd go && go test ./... -race

# Python tests
pytest python/ -v
pytest python/ --integration
```

### Code Quality

#### Rust Standards
```bash
# Linting
cargo clippy --workspace --all-targets --all-features -- -D warnings

# Formatting
cargo fmt --all

# Documentation
cargo doc --workspace --no-deps

# Check dependencies
cargo tree -d  # Check for duplicates
cargo audit    # Security audit
```

#### Go Standards
```bash
# Linting
golangci-lint run

# Formatting
gofmt -l -w .

# Testing with race detection
go test -race ./...

# Coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

#### Python Standards
```bash
# Linting
ruff check python/
mypy python/pheno-events/
mypy python/pheno-caching/
mypy python/pheno-database/

# Formatting
black python/
ruff format python/

# Testing
pytest python/ -v --cov=src
```

### Performance Standards

| Component | Target | Measurement |
|-----------|--------|-------------|
| Event append | < 1ms | Single event |
| Event read | < 5ms | 100 events |
| Chain verify | < 10ms | 1000 events |
| Cache hit (L1) | < 100μs | Single key |
| Cache miss | < 1ms | L2 + promote |

---

## Git Workflow

### Branch Strategy

```
main
  │
  ├── feature/event-sourcing-blake3
  │   └── PR #45 → squash merge ──┐
  │                               │
  ├── feature/cache-metrics        │
  │   └── PR #46 → squash merge ──┤
  │                               │
  ├── fix/hash-verification        │
  │   └── PR #47 → squash merge ──┤
  │                               │
  └── hotfix/data-corruption ───────┘
      └── PR #48 → merge commit
```

### Branch Naming

```
feature/<language>/<description>
fix/<component>/<issue>
perf/<scope>/<optimization>
refactor/<language>/<scope>
docs/<topic>
chore/<maintenance>
```

### Commit Conventions

```
feat(rust/event-sourcing): add Blake3 hash chain verification

Implements cryptographic verification for event streams.
Each event includes Blake3 hash of payload + previous hash.

- EventEnvelope with hash field
- verify_chain() function
- HashError types for validation failures

Closes #123

fix(python/cache): resolve TTL expiration race

Expired entries could be returned if cleanup hadn't run.
Now checks TTL on every read operation.
```

---

## File Structure

```
DataKit/
├── docs/                       # Documentation
│   ├── SPEC.md                 # This specification
│   ├── adr/                    # Architecture decisions
│   │   ├── ADR-001-processing-engine.md
│   │   ├── ADR-002-streaming-strategy.md
│   │   └── ADR-003-schema-evolution.md
│   └── research/
│       └── DATA_PROCESSING_SOTA.md
│
├── rust/                       # Rust implementation
│   ├── Cargo.toml              # Workspace definition
│   ├── phenotype-event-sourcing/
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── event.rs          # EventEnvelope<T>
│   │   │   ├── hash.rs           # Blake3 operations
│   │   │   ├── store.rs          # EventStore trait
│   │   │   ├── async_store.rs    # AsyncEventStore
│   │   │   ├── memory.rs         # InMemoryEventStore
│   │   │   ├── snapshot.rs       # Snapshot management
│   │   │   └── error.rs          # Error types
│   │   └── examples/
│   │       └── usage.rs
│   ├── phenotype-event-bus/
│   │   ├── src/lib.rs            # EventBus trait + impl
│   │   └── Cargo.toml
│   ├── phenotype-cache-adapter/
│   │   ├── src/lib.rs            # TwoTierCache<K, V>
│   │   └── Cargo.toml
│   └── phenotype-in-memory-store/
│       ├── src/lib.rs            # Store<K, V> + TTL
│       └── Cargo.toml
│
├── go/                         # Go implementation
│   ├── go.work                 # Go workspace
│   ├── pheno-storage/          # Storage abstraction
│   │   ├── storage.go
│   │   └── backends/
│   ├── pheno-cache/            # Caching utilities
│   │   └── cache.go
│   ├── pheno-events/             # Event handling
│   │   └── events.go
│   └── pheno-persistence/        # Persistence layer
│       └── persistence.go
│
├── python/                     # Python implementation
│   ├── pheno-events/             # Event system
│   │   └── src/pheno_events/
│   │       ├── __init__.py
│   │       ├── bus.py
│   │       ├── nats_bus.py
│   │       ├── nats_factory.py
│   │       ├── jetstream_utils.py
│   │       ├── core/
│   │       │   ├── event_store.py
│   │       │   └── event_bus.py
│   │       └── webhooks/
│   │           ├── signature.py
│   │           └── webhook_manager.py
│   ├── pheno-caching/          # Multi-tier caching
│   │   └── src/pheno_caching/
│   │       ├── __init__.py
│   │       ├── hot/query_cache.py
│   │       ├── cold/disk_cache.py
│   │       └── dry/decorators.py
│   ├── pheno-database/         # Database abstraction
│   │   └── src/pheno_database/
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── adapters/
│   │       │   ├── postgres.py
│   │       │   ├── supabase.py
│   │       │   └── neon.py
│   │       ├── pooling/
│   │       ├── storage/
│   │       ├── realtime/
│   │       └── platforms/
│   ├── pheno-storage/          # Storage backends
│   │   └── src/pheno_storage/
│   │       ├── client.py
│   │       ├── backends/
│   │       │   ├── s3.py
│   │       │   ├── supabase.py
│   │       │   ├── local.py
│   │       │   └── memory.py
│   │       └── repositories/
│   └── db-kit/                 # Unified database toolkit
│       ├── __init__.py
│       ├── client.py
│       ├── core/engine.py
│       ├── adapters/
│       ├── migrations/
│       ├── tenancy/
│       └── vector/
│
├── README.md
└── AGENTS.md                   # This file
```

---

## CLI Commands

### Rust Commands

```bash
# Build all crates
cd rust && cargo build --workspace

# Run tests
cd rust && cargo test --workspace

# Run specific crate
cargo test -p phenotype-event-sourcing
cargo test -p phenotype-cache-adapter

# Documentation
cargo doc --workspace --open

# Benchmarks
cargo bench -p phenotype-event-sourcing
```

### Go Commands

```bash
# Build all modules
cd go && go build ./...

# Run tests
cd go && go test ./...

# Run specific module
go test ./pheno-storage/...
go test ./pheno-cache/...

# Workspace commands
cd go/pheno-storage && go run .
```

### Python Commands

```bash
# Install all packages
pip install -e python/pheno-events/
pip install -e python/pheno-caching/
pip install -e python/pheno-database/
pip install -e python/pheno-storage/
pip install -e python/db-kit/

# Run tests
pytest python/pheno-events/ -v
pytest python/pheno-caching/ -v
pytest python/pheno-database/ -v

# Database operations
python -m pheno_database init
python -m pheno_database migrate
python -m pheno_database test-connection

# Storage operations
python -m pheno_storage list-buckets
python -m pheno_storage upload <file>
```

---

## Troubleshooting

### Common Issues

#### Issue: Event chain verification fails

**Symptoms:**
```
ChainVerificationError: InvalidHash { index: 5 }
```

**Diagnosis:**
```bash
# Verify specific stream
cd rust/phenotype-event-sourcing
cargo test verify_chain -- --nocapture

# Check event sequence
redis-cli LRANGE "stream:order-123" 0 -1

# Inspect event hashes
python -c "
import blake3
import json
events = [...]  # Load events
for i, e in enumerate(events):
    computed = blake3(json.dumps(e.payload).encode() + e.previous_hash).hexdigest()
    print(f'{i}: stored={e.hash}, computed={computed}, match={e.hash == computed}')
"
```

**Resolution:**
- Check for concurrent modifications
- Verify serialization format consistency
- Rebuild from source events if needed
- Review snapshot integrity

---

#### Issue: NATS connection refused

**Symptoms:**
```
nats.errors.NoServersError: No servers available for connection
```

**Diagnosis:**
```bash
# Check NATS server
nats-server --version
brew services list | grep nats

# Test connection
nats-pub test "hello"
nats-sub test
```

**Resolution:**
```bash
# Start NATS with JetStream
nats-server -js

# Or with config
nats-server -c /usr/local/etc/nats-server.conf

# Verify JetStream enabled
nats stream list
```

---

#### Issue: Cache returning stale data

**Symptoms:**
Query returns old data after database update.

**Diagnosis:**
```bash
# Check cache stats
python -c "from pheno_caching import QueryCache; qc = QueryCache(); print(qc.get_stats())"

# List cache keys
python -c "from pheno_caching import QueryCache; qc = QueryCache(); print(list(qc.cache.keys()))"

# Verify invalidation events
nats-sub "cache.invalidate.*"
```

**Resolution:**
```bash
# Manual invalidation
python -c "from pheno_caching import QueryCache; qc = QueryCache(); qc.invalidate_by_table('users')"

# Clear all cache
python -c "from pheno_caching import QueryCache; qc = QueryCache(); qc.clear()"

# Reduce TTL
export CACHE_TTL=10  # seconds
```

---

#### Issue: Storage backend authentication failure

**Symptoms:**
```
AuthenticationError: Failed to authenticate with S3
```

**Diagnosis:**
```bash
# Check credentials
aws sts get-caller-identity

# Verify environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# Test S3 connection
aws s3 ls
```

**Resolution:**
- Update credentials in ~/.aws/credentials
- Check IAM permissions
- Verify bucket policy
- Use instance profile for EC2

---

### Debug Mode

```bash
# Rust debug logging
export RUST_LOG=debug
cargo run --example usage 2>&1 | tee debug.log

# Python debug logging
export PHENO_DEBUG=1
export PHENO_LOG_LEVEL=debug
python -m pheno_events 2>&1 | tee debug.log

# NATS debug
nats-server -DV  # Debug and trace

# Database query logging
export PHENO_DATABASE_QUERY_LOG=1
```

### Recovery Procedures

```bash
# Rebuild event stream from snapshots
cd rust/phenotype-event-sourcing
cargo run --bin rebuild-stream -- --aggregate order-123

# Clear corrupted cache
redis-cli FLUSHDB

# Reset database connections
python -c "from pheno_database import PoolManager; PoolManager().close_all()"

# Verify storage backends
python -m pheno_storage verify
```

---

## Agent Self-Correction & Verification Protocols

### Critical Rules

1. **Cryptographic Integrity**
   - Never skip hash verification in production
   - Use constant-time comparison for hashes
   - Validate chain before any state reconstruction
   - Log all verification failures

2. **Event Ordering**
   - Events must be processed in sequence order
   - No gaps allowed in event streams
   - Concurrent appends must be serialized
   - Use optimistic locking for conflicts

3. **Cache Consistency**
   - Invalidate before update (not after)
   - Use event-driven invalidation
   - TTL must be shorter than source freshness
   - Monitor cache hit rates

4. **Resource Cleanup**
   - Close all connections in finally blocks
   - Implement proper connection pooling
   - Handle context cancellation
   - Clean up temporary files

---

*This AGENTS.md is a living document. Update it as DataKit evolves.*
