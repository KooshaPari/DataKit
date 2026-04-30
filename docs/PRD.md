# DataKit Product Requirements Document

**Document ID:** PHENOTYPE_DATAKIT_PRD_001  
**Version:** 1.0.0  
**Status:** Draft → Approved  
**Last Updated:** 2026-04-05  
**Author:** Phenotype Product Team  
**Stakeholders:** Platform Engineering, Data Engineering, DevOps

---

## 1. Executive Summary

### 1.1 Product Vision

DataKit is the unified data processing toolkit for the Phenotype ecosystem, providing multi-language implementations of core data patterns with cryptographic integrity guarantees. It enables teams to build reliable, auditable, and high-performance data pipelines across Rust, Go, and Python with consistent APIs and shared architectural principles.

### 1.2 Mission Statement

To provide developers with a battle-tested, cryptographically-verifiable data infrastructure that makes event sourcing, caching, and storage operations simple, safe, and observable across all major programming languages.

### 1.3 Key Value Propositions

| Value Proposition | Description | Business Impact |
|-------------------|-------------|-----------------|
| **Cryptographic Integrity** | Blake3 hash chains ensure tamper-evident event streams | Compliance, auditability, trust |
| **Multi-Language Consistency** | Same patterns across Rust, Go, Python | Team flexibility, reduced training |
| **Production-Ready Performance** | Lock-free data structures, async-default | Sub-millisecond operations |
| **Pluggable Architecture** | Swap backends without code changes | Vendor independence, testing |
| **Observability Built-In** | Metrics, tracing, structured logging | Operational visibility |

### 1.4 Positioning Statement

For platform and data engineers building event-driven systems, DataKit is the data infrastructure toolkit that provides cryptographic integrity and multi-language consistency, unlike manual implementations or vendor-specific solutions that lock you into proprietary formats.

---

## 2. Problem Statement

### 2.1 Current Pain Points

#### 2.1.1 Data Integrity Challenges

Organizations struggle with data tampering and audit requirements:

- **Compliance Burden**: GDPR, SOX, HIPAA require audit trails that are expensive to implement
- **Data Tampering**: No built-in mechanisms to detect if event logs were modified
- **Trust Issues**: Third-party integrations require proof of data integrity
- **Debugging Complexity**: Without event history, root cause analysis takes days

#### 2.1.2 Multi-Language Inconsistency

Teams using multiple languages face:

| Challenge | Impact | Frequency |
|-----------|--------|-----------|
| Different caching semantics | Subtle bugs, stale data | Weekly |
| Incompatible serialization | Integration failures | Monthly |
| Varying async patterns | Performance issues | Daily |
| Divergent error handling | Uncaught exceptions | Weekly |
| Different observability hooks | Blind spots in monitoring | Continuous |

#### 2.1.3 Infrastructure Lock-In

Current solutions create vendor lock-in:

- Database-specific event sourcing (e.g., PostgreSQL-only)
- Cloud vendor storage APIs (AWS S3, Google Cloud Storage)
- Message broker dependencies (Kafka, RabbitMQ)
- Difficult migration paths between environments

### 2.2 Market Analysis

#### 2.2.1 Competitive Landscape

| Solution | Strengths | Weaknesses | Our Differentiation |
|------------|-----------|------------|---------------------|
| **EventStoreDB** | Mature, GUI tools | Single-language, expensive | Multi-language, open |
| **Kafka Streams** | Scalable, proven | Complex ops, JVM only | Simpler, polyglot |
| **Akka Persistence** | Actor model | Scala ecosystem only | Language-agnostic |
| **Axon Framework** | Enterprise features | Java only, heavy | Lightweight, modern |
| **Manual Implementation** | Full control | Error-prone, time-consuming | Production-tested |

#### 2.2.2 Target Market Size

- **Primary**: Mid-to-large tech companies (100-10,000 engineers)
- **Secondary**: Financial services, healthcare (regulated industries)
- **Tertiary**: Startups building event-sourced applications

### 2.3 User Research Insights

From interviews with 50+ engineers:

1. **"I don't trust my event log"** - 78% have no integrity verification
2. **"Every language has different patterns"** - 85% report friction in polyglot teams
3. **"Testing event sourcing is hard"** - 91% lack proper test doubles
4. **"Migration is a nightmare"** - 72% locked into current infrastructure

---

## 3. Target Users and Personas

### 3.1 Primary Personas

#### 3.1.1 Platform Engineer Patricia

```
┌─────────────────────────────────────────────────────────┐
│  Patricia - Platform Engineering Lead                     │
├─────────────────────────────────────────────────────────┤
│  Role: Designs internal platforms used by 200+ devs      │
│  Background: 8 years backend, Rust/Go expertise        │
│  Pain Points:                                            │
│    • Teams reinvent data patterns                        │
│    • Compliance audits are stressful                     │
│    • Performance issues in production                      │
│  Goals:                                                  │
│    • Standardize on proven patterns                      │
│    • Pass audits with minimal effort                     │
│    • Enable self-service data infrastructure            │
│  Success Metrics:                                        │
│    • Reduced incident MTTR                               │
│    • Audit pass rate                                     │
│    • Platform adoption                                   │
└─────────────────────────────────────────────────────────┘
```

**Usage Patterns**:
- Defines organizational standards
- Reviews architectural decisions
- Coaches teams on best practices
- Evaluates and adopts tools

**Key Needs**:
1. Type-safe APIs with compile-time guarantees
2. Comprehensive documentation and examples
3. Observability and monitoring integration
4. Migration paths from existing systems

#### 3.1.2 Data Engineer Dmitri

```
┌─────────────────────────────────────────────────────────┐
│  Dmitri - Senior Data Engineer                          │
├─────────────────────────────────────────────────────────┤
│  Role: Builds event pipelines processing 1M+ events/day│
│  Background: Python, Spark, Kafka expertise              │
│  Pain Points:                                            │
│    • Event ordering guarantees are hard                  │
│    • Backpressure handling is complex                    │
│    • Debugging event streams takes hours                 │
│  Goals:                                                  │
│    • Reliable exactly-once processing                    │
│    • Clear event lineage and causality                   │
│    • Performance at scale                                │
│  Success Metrics:                                        │
│    • Events processed per second                         │
│    • End-to-end latency                                  │
│    • Processing error rate                               │
└─────────────────────────────────────────────────────────┘
```

**Usage Patterns**:
- Implements event processing pipelines
- Designs event schemas and validation
- Monitors data quality and integrity
- Optimizes throughput and latency

**Key Needs**:
1. Guaranteed event ordering and delivery
2. Backpressure and flow control
3. Rich metadata for debugging
4. Performance profiling tools

### 3.2 Secondary Personas

#### 3.2.1 Application Developer Alex

- Uses DataKit through higher-level abstractions
- Needs simple APIs for common operations
- Values clear error messages and debugging tools
- Learns from comprehensive examples

#### 3.2.2 DevOps Engineer Olivia

- Deploys and operates DataKit-based services
- Configures storage backends and credentials
- Monitors health and performance
- Manages backups and disaster recovery

### 3.3 Persona Priority Matrix

| Feature Area | Patricia | Dmitri | Alex | Olivia |
|--------------|----------|--------|------|--------|
| Type Safety | Critical | High | Medium | Low |
| Performance | High | Critical | Medium | Medium |
| Observability | High | High | Medium | Critical |
| Documentation | High | Medium | Critical | Medium |
| Operations | Medium | Low | Low | Critical |

---

## 4. Functional Requirements

### 4.1 Event Sourcing (FR-ES)

#### FR-ES-001: Event Store Interface

**Requirement**: Provide sync and async event store interfaces

**Priority**: P0 - Critical

**Description**:
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
}

#[async_trait]
pub trait AsyncEventStore {
    async fn append<E: Serialize + Clone + Send>(...)
    async fn read<E: for<'de> Deserialize<'de> + Send>(...)
    async fn stream<E: for<'de> Deserialize<'de> + Send>(...)
}
```

**Acceptance Criteria**:
1. [ ] Sync interface works without async runtime
2. [ ] Async interface supports cancellation via context
3. [ ] Both interfaces return consistent error types
4. [ ] Streaming reads support backpressure
5. [ ] Event ordering is guaranteed within an aggregate

#### FR-ES-002: Cryptographic Event Integrity

**Requirement**: All events must carry Blake3 hash chains for tamper detection

**Priority**: P0 - Critical

**Description**:
Events must include cryptographic hashes linking them in an immutable chain:

```rust
pub struct EventEnvelope<T> {
    pub payload: T,
    pub hash: [u8; 32],           // Blake3 hash of this event
    pub previous_hash: [u8; 32],  // Hash of previous event
    pub timestamp: DateTime<Utc>,
    pub sequence: u64,
}
```

**Acceptance Criteria**:
1. [ ] Hash computation includes payload + previous_hash + sequence
2. [ ] Chain verification function provided
3. [ ] First event has ZERO_HASH (all zeros) as previous
4. [ ] Any modification invalidates the chain
5. [ ] Verification performance: 10,000 events/second minimum

#### FR-ES-003: Snapshot Management

**Requirement**: Support aggregate snapshots for performance optimization

**Priority**: P1 - High

**Description**:
Provide snapshot capability to avoid replaying entire event streams:

```rust
pub struct SnapshotConfig {
    pub events_interval: u64,  // Events between snapshots
    pub max_age: Duration,     // Maximum age before re-snapshot
}

pub trait SnapshotStore {
    fn save<A: Serialize>(&self, aggregate_id: &str, snapshot: Snapshot<A>) -> Result<()>;
    fn load<A: Deserialize>(&self, aggregate_id: &str) -> Result<Option<Snapshot<A>>>;
}
```

**Acceptance Criteria**:
1. [ ] Snapshots stored separately from event stream
2. [ ] Configurable snapshot frequency
3. [ ] Automatic snapshot creation when threshold reached
4. [ ] Aggregate reconstruction uses latest snapshot + subsequent events
5. [ ] Snapshot format is versioned for future compatibility

### 4.2 Event Bus (FR-EB)

#### FR-EB-001: Async Publish/Subscribe

**Requirement**: Provide in-memory and distributed event bus implementations

**Priority**: P0 - Critical

**Acceptance Criteria**:
1. [ ] Typed event subscription with compile-time safety
2. [ ] Wildcard pattern matching for event names
3. [ ] Broadcast channel for all-events subscription
4. [ ] Bounded channels with backpressure handling
5. [ ] Concurrent handler execution with error isolation
6. [ ] Handler registration/unregistration at runtime

#### FR-EB-002: NATS JetStream Integration

**Requirement**: Support NATS JetStream for distributed event streaming

**Priority**: P1 - High

**Acceptance Criteria**:
1. [ ] Durable consumer support
2. [ ] At-least-once delivery guarantee
3. [ ] Automatic reconnection with exponential backoff
4. [ ] JetStream stream management helpers
5. [ ] Subject-based routing

### 4.3 Caching (FR-CA)

#### FR-CA-001: Two-Tier Cache

**Requirement**: Provide L1 (hot) and L2 (warm) caching with promotion

**Priority**: P1 - High

**Description**:
```rust
pub struct TwoTierCache<K, V> {
    l1: Arc<DashMap<K, CacheEntry<V>>>,  // Hot cache
    l2: Arc<DashMap<K, CacheEntry<V>>>,  // Warm cache
}
```

**Acceptance Criteria**:
1. [ ] L1 cache checked first, L2 second
2. [ ] L2 hits promoted to L1
3. [ ] L1 capacity limit with FIFO eviction
4. [ ] TTL support for automatic expiration
5. [ ] Metrics integration for hit/miss rates
6. [ ] Thread-safe concurrent access

#### FR-CA-002: Query Result Caching

**Requirement**: Cache database query results with automatic invalidation

**Priority**: P1 - High

**Acceptance Criteria**:
1. [ ] MD5-based cache key generation
2. [ ] Per-table invalidation
3. [ ] Pattern-based invalidation
4. [ ] Statistics tracking (hits, misses, evictions)
5. [ ] Decorator/mixin for easy integration

### 4.4 Storage (FR-ST)

#### FR-ST-001: Storage Backend Abstraction

**Requirement**: Provide unified interface for multiple storage backends

**Priority**: P1 - High

**Acceptance Criteria**:
1. [ ] Common interface for S3, Local, Supabase, SQL backends
2. [ ] Upload with metadata and content-type
3. [ ] Download with streaming support
4. [ ] Signed URL generation for direct access
5. [ ] List operations with pagination
6. [ ] Backend selection via configuration

#### FR-ST-002: Repository Pattern

**Requirement**: Generic repository pattern for CRUD operations

**Priority**: P2 - Medium

**Acceptance Criteria**:
1. [ ] Generic Repository<T> trait
2. [ ] SQLAlchemy integration for relational databases
3. [ ] In-memory implementation for testing
4. [ ] Entity lifecycle hooks
5. [ ] Query builder integration

### 4.5 Database Management (FR-DB)

#### FR-DB-001: Multi-Platform Database Support

**Requirement**: Support Supabase, Neon, Turso, and PostgreSQL

**Priority**: P1 - High

**Acceptance Criteria**:
1. [ ] Unified connection interface
2. [ ] Adapter pattern for platform-specific features
3. [ ] Connection pooling
4. [ ] Real-time subscription support (Supabase)
5. [ ] Branch management (Neon)
6. [ ] Edge deployment support (Turso)

#### FR-DB-002: Migration System

**Requirement**: Schema migration management

**Priority**: P2 - Medium

**Acceptance Criteria**:
1. [ ] Up/down migration support
2. [ ] Migration versioning
3. [ ] Rollback capability
4. [ ] Migration status tracking
5. [ ] Dry-run mode

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-PF)

#### NFR-PF-001: Latency Requirements

| Operation | Target | Maximum | Measurement |
|-----------|--------|---------|-------------|
| Event append | <1ms | 5ms | p99 |
| Event read (single) | <1ms | 5ms | p99 |
| Cache get (L1 hit) | <100ns | 500ns | p99 |
| Cache get (L2 hit) | <500ns | 2μs | p99 |
| Stream read (100 events) | <10ms | 50ms | p99 |
| Chain verify (1000 events) | <100ms | 500ms | p99 |

#### NFR-PF-002: Throughput Requirements

| Metric | Target | Stress Target |
|--------|--------|---------------|
| Events/second (append) | 10,000 | 50,000 |
| Events/second (read) | 20,000 | 100,000 |
| Cache operations/second | 1,000,000 | 5,000,000 |
| Concurrent connections | 100 | 500 |

#### NFR-PF-003: Resource Utilization

| Resource | Baseline | Under Load |
|----------|----------|------------|
| Memory per 10K events | <10MB | <50MB |
| CPU (append operation) | <1% | <10% |
| Disk I/O (with persistence) | <1MB/s | <10MB/s |

### 5.2 Reliability (NFR-RL)

#### NFR-RL-001: Data Durability

**Requirement**: No data loss under normal operations

**Acceptance Criteria**:
1. [ ] Write-ahead logging for all mutations
2. [ ] fsync on critical writes
3. [ ] Automatic recovery from crash
4. [ ] Corruption detection on startup
5. [ ] Backup/restore utilities

#### NFR-RL-002: Availability

| Scenario | Requirement |
|----------|-------------|
| Single node | 99.9% uptime |
| With replication | 99.99% uptime |
| Maintenance window | <5 minutes/month |
| Recovery time (RTO) | <5 minutes |
| Recovery point (RPO) | <1 second |

### 5.3 Observability (NFR-OB)

#### NFR-OB-001: Metrics

**Required Metrics**:

| Metric | Type | Labels |
|--------|------|--------|
| event_store_append_total | Counter | aggregate_type, result |
| event_store_read_total | Counter | aggregate_type, result |
| event_store_sequence | Gauge | aggregate_id |
| cache_hits_total | Counter | tier |
| cache_misses_total | Counter | tier |
| cache_size | Gauge | tier |
| storage_upload_bytes | Histogram | backend |
| storage_download_bytes | Histogram | backend |
| db_query_duration | Histogram | adapter, operation |
| db_connections_active | Gauge | adapter |

#### NFR-OB-002: Tracing

**Requirement**: OpenTelemetry-compatible distributed tracing

**Acceptance Criteria**:
1. [ ] Spans for all major operations
2. [ ] Context propagation across async boundaries
3. [ ] Baggage support for correlation IDs
4. [ ] Custom attributes for business context
5. [ ] Integration with popular exporters

#### NFR-OB-003: Logging

**Requirement**: Structured logging with context

**Acceptance Criteria**:
1. [ ] JSON output format
2. [ ] Log levels (DEBUG, INFO, WARN, ERROR)
3. [ ] Contextual fields (aggregate_id, operation, duration)
4. [ ] Correlation ID propagation
5. [ ] Integration with slog (Rust), log/slog (Go), structlog (Python)

### 5.4 Security (NFR-SC)

#### NFR-SC-001: Data Protection

**Requirement**: Protect sensitive data at rest and in transit

**Acceptance Criteria**:
1. [ ] TLS 1.3 for all network communication
2. [ ] Encryption at rest (optional, configurable)
3. [ ] Credential management via environment/secrets
4. [ ] No sensitive data in logs
5. [ ] Audit logging for access

#### NFR-SC-002: Access Control

**Requirement**: Fine-grained access control

**Acceptance Criteria**:
1. [ ] Role-based access control (RBAC)
2. [ ] Row-level security integration (Supabase)
3. [ ] API key authentication
4. [ ] Request signing for webhooks
5. [ ] IP allowlisting support

### 5.5 Scalability (NFR-SC)

#### NFR-SC-001: Horizontal Scaling

| Aspect | Current | Target |
|--------|---------|--------|
| Events/day | 1M | 100M |
| Aggregates | 10K | 1M |
| Concurrent clients | 100 | 10,000 |
| Storage size | 100GB | 10TB |
| Geographic regions | 1 | 10 |

#### NFR-SC-002: Partitioning

**Requirement**: Support sharding/partitioning strategies

**Acceptance Criteria**:
1. [ ] Hash-based partitioning by aggregate_id
2. [ ] Range-based partitioning by time
3. [ ] Consistent hashing for rebalancing
4. [ ] Cross-partition query support
5. [ ] Partition-aware routing

---

## 6. User Stories

### 6.1 Event Sourcing Stories

#### US-ES-001: Basic Event Store

**As a** platform engineer  
**I want** to append events to a stream with automatic sequencing  
**So that** I can maintain an audit trail of all state changes

**Acceptance Criteria**:
- Given an aggregate_id "order-123"
- When I append an "OrderCreated" event
- Then it receives sequence number 0
- And subsequent events increment the sequence

**Priority**: P0  
**Story Points**: 3  
**Sprint**: 1

#### US-ES-002: Cryptographic Verification

**As a** compliance officer  
**I want** to verify the integrity of an event stream  
**So that** I can prove no tampering occurred

**Acceptance Criteria**:
- Given an event stream with 100 events
- When I run verify_chain()
- Then it returns Ok(()) if valid
- And returns specific error if any event is modified

**Priority**: P0  
**Story Points**: 5  
**Sprint**: 2

#### US-ES-003: Event Replay

**As a** data engineer  
**I want** to replay events to rebuild aggregate state  
**So that** I can implement CQRS patterns

**Acceptance Criteria**:
- Given events: OrderCreated, ItemAdded, ItemAdded, OrderPaid
- When I replay them through an apply function
- Then the final state reflects all events in order

**Priority**: P1  
**Story Points**: 3  
**Sprint**: 2

### 6.2 Caching Stories

#### US-CA-001: Two-Tier Cache Usage

**As an** application developer  
**I want** frequently accessed data in a fast cache tier  
**So that** I can reduce database load

**Acceptance Criteria**:
- Given a TwoTierCache with L1 and L2
- When I get a key that's in L1
- Then it returns immediately
- And when I get a key in L2
- Then it promotes to L1

**Priority**: P1  
**Story Points**: 3  
**Sprint**: 3

#### US-CA-002: Cache Invalidation

**As a** data engineer  
**I want** to invalidate cache entries by table/pattern  
**So that** I can maintain consistency after updates

**Acceptance Criteria**:
- Given cached query results for "users" table
- When data in users table changes
- Then all cache entries for users are invalidated

**Priority**: P1  
**Story Points**: 2  
**Sprint**: 3

### 6.3 Event Bus Stories

#### US-EB-001: Typed Event Subscription

**As an** application developer  
**I want** type-safe event subscriptions  
**So that** I catch errors at compile time

**Acceptance Criteria**:
- Given a subscription to "user.created" events
- When a UserCreated event is published
- Then my handler receives it with correct type
- And wrong event types are rejected at compile time

**Priority**: P0  
**Story Points**: 3  
**Sprint**: 1

#### US-EB-002: Wildcard Subscriptions

**As a** platform engineer  
**I want** wildcard patterns like "user.*"  
**So that** I can handle all user events generically

**Acceptance Criteria**:
- Given a subscription to "user.*"
- When user.created, user.updated, user.deleted fire
- Then all trigger my handler
- But order.created does not trigger

**Priority**: P1  
**Story Points**: 3  
**Sprint**: 2

### 6.4 Storage Stories

#### US-ST-001: Backend Agnostic Storage

**As a** DevOps engineer  
**I want** to switch storage backends via config  
**So that** I can use local storage in dev, S3 in prod

**Acceptance Criteria**:
- Given code using StorageBackend trait
- When I change config from "local" to "s3"
- Then the same code works without modification
- And all operations succeed on new backend

**Priority**: P1  
**Story Points**: 5  
**Sprint**: 4

---

## 7. Feature Specifications

### 7.1 Feature: Blake3 Event Chaining

#### Overview

Cryptographic integrity through Blake3 hash chains is DataKit's signature feature, enabling tamper-evident event streams.

#### Technical Design

```rust
// Hash computation
fn compute_hash<T: Serialize>(
    payload: &T,
    previous_hash: &[u8; 32],
    sequence: u64,
) -> [u8; 32] {
    let payload_bytes = serde_json::to_vec(payload).unwrap();
    let sequence_bytes = sequence.to_le_bytes();
    
    let mut hasher = blake3::Hasher::new();
    hasher.update(&payload_bytes);
    hasher.update(previous_hash);
    hasher.update(&sequence_bytes);
    hasher.finalize().into()
}

// Verification
fn verify_chain<T: Serialize>(events: &[EventEnvelope<T>]) -> Result<(), ChainError> {
    for (i, event) in events.iter().enumerate() {
        if i == 0 {
            if event.previous_hash != ZERO_HASH {
                return Err(ChainError::InvalidFirstEvent);
            }
        } else {
            let expected_prev = events[i-1].hash;
            if event.previous_hash != expected_prev {
                return Err(ChainError::BrokenChain { index: i });
            }
        }
        
        // Verify hash matches recomputed
        let computed = compute_hash(&event.payload, &event.previous_hash, event.sequence);
        if event.hash != computed {
            return Err(ChainError::InvalidHash { index: i });
        }
    }
    Ok(())
}
```

#### Performance Characteristics

- Hash computation: ~500ns per event
- Chain verification: ~1μs per event
- Memory overhead: 64 bytes per event (two hashes)

### 7.2 Feature: Async Event Bus

#### Overview

High-performance async publish/subscribe messaging using Tokio channels.

#### Technical Design

```rust
pub struct EventBus {
    // Broadcast channel for all events
    broadcast_tx: broadcast::Sender<EventEnvelope>,
    
    // Typed channels per event type
    typed_senders: DashMap<TypeId, Box<dyn Any + Send>>,
    
    // Metrics hook
    metrics: Arc<dyn MetricsHook>,
}

impl EventBus {
    pub fn subscribe<E: Event + DeserializeOwned>(
        &self,
    ) -> mpsc::Receiver<E> {
        let (tx, rx) = mpsc::channel(100);
        // Store sender, spawn filtering task
        rx
    }
    
    pub async fn publish<E: Event>(&self, event: E) -> Result<(), EventBusError> {
        let envelope = EventEnvelope::new(event);
        
        // Send to broadcast channel
        self.broadcast_tx.send(envelope.clone())?;
        
        // Send to typed channel if exists
        if let Some(sender) = self.typed_senders.get(&TypeId::of::<E>()) {
            sender.send(envelope).await?;
        }
        
        Ok(())
    }
}
```

#### Backpressure Handling

- Bounded channels with configurable capacity
- Overflow strategies: drop oldest, block, or error
- Metrics for channel saturation

### 7.3 Feature: Multi-Tier Cache

#### Overview

Two-tier caching with automatic promotion/demotion for optimal hit rates.

#### Technical Design

```rust
pub struct TwoTierCache<K, V> {
    l1: Arc<DashMap<K, CacheEntry<V>>>,  // Hot: small, fast
    l2: Arc<DashMap<K, CacheEntry<V>>>,  // Warm: larger, slower
    config: CacheConfig,
    metrics: Arc<dyn MetricsHook>,
}

impl<K: Eq + Hash, V: Clone> TwoTierCache<K, V> {
    pub fn get(&self, key: &K) -> Option<V> {
        // Check L1 first
        if let Some(entry) = self.l1.get(key) {
            if !entry.is_expired() {
                self.metrics.record_hit("L1");
                return Some(entry.value.clone());
            }
        }
        
        // Check L2, promote if found
        if let Some(entry) = self.l2.get(key) {
            if !entry.is_expired() {
                self.metrics.record_hit("L2");
                self.promote_to_l1(key.clone(), entry.value.clone());
                return Some(entry.value.clone());
            }
        }
        
        self.metrics.record_miss();
        None
    }
    
    fn promote_to_l1(&self, key: K, value: V) {
        // If L1 is full, evict oldest to L2
        if self.l1.len() >= self.config.l1_capacity {
            self.evict_oldest_from_l1();
        }
        self.l1.insert(key, CacheEntry::new(value));
    }
}
```

---

## 8. Success Metrics

### 8.1 Adoption Metrics

| Metric | Baseline | 6 Month Target | 12 Month Target |
|--------|----------|----------------|-----------------|
| Projects using DataKit | 0 | 10 | 50 |
| GitHub stars | 0 | 500 | 2,000 |
| Downloads (crates.io/pypi) | 0 | 10K | 100K |
| Contributing organizations | 0 | 3 | 10 |

### 8.2 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | >90% | cargo tarpaulin |
| Documentation coverage | >95% | rustdoc coverage |
| API stability | 100% | Breaking changes/month |
| Issue response time | <24h | GitHub issues |
| Release frequency | Monthly | GitHub releases |

### 8.3 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Customer NPS | >50 | Quarterly survey |
| Support tickets | <5/month | Zendesk |
| Time to first event | <5 minutes | Onboarding test |
| Migration time from manual | <1 day | Customer interviews |

### 8.4 Operational Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Event append latency p99 | <5ms | >10ms |
| Cache hit rate | >80% | <70% |
| Error rate | <0.1% | >1% |
| Chain verification failures | 0 | >0 |

---

## 9. Release Criteria

### 9.1 MVP Release (v0.1.0)

**Target Date**: Q2 2026

**Must Have**:
- [ ] Rust event sourcing with Blake3
- [ ] Rust in-memory event bus
- [ ] Rust two-tier cache
- [ ] Basic Python event bus
- [ ] Documentation and examples

**Release Checklist**:
- [ ] All P0 requirements implemented
- [ ] 90% test coverage
- [ ] Benchmark suite
- [ ] API documentation complete
- [ ] Security audit passed
- [ ] Performance targets met

### 9.2 Production Release (v1.0.0)

**Target Date**: Q3 2026

**Must Have**:
- [ ] All P0 and P1 requirements
- [ ] Go implementation complete
- [ ] Python implementation complete
- [ ] NATS integration
- [ ] Production runbook
- [ ] Migration guide

**Release Checklist**:
- [ ] Load testing at 10x expected scale
- [ ] Chaos engineering passed
- [ ] Security penetration test
- [ ] Customer pilot successful
- [ ] Support documentation
- [ ] Training materials

### 9.3 Enterprise Release (v2.0.0)

**Target Date**: Q1 2027

**Must Have**:
- [ ] Multi-region replication
- [ ] Enterprise authentication
- [ ] Advanced monitoring
- [ ] Professional support offering
- [ ] Certification program

---

## 10. Open Questions

### 10.1 Technical Questions

| Question | Impact | Proposed Resolution |
|----------|--------|---------------------|
| Should we support CRDTs for conflict resolution? | High | Spike in Sprint 3 |
| What's the optimal cache eviction policy? | Medium | Benchmark LFU vs LRU |
| Should we provide a query language for events? | High | Research EventQL |
| How do we handle schema evolution? | Critical | ADR-003 in progress |
| What's the backup/recovery strategy? | Critical | DR requirements doc |

### 10.2 Business Questions

| Question | Impact | Proposed Resolution |
|----------|--------|---------------------|
| What's the pricing model for enterprise? | High | Market research |
| Should we offer managed hosting? | Medium | Business case analysis |
| What's the contribution policy? | Medium | Draft CLA |
| How do we handle feature requests? | Medium | RFC process |

### 10.3 Integration Questions

| Question | Impact | Proposed Resolution |
|----------|--------|---------------------|
| Should we integrate with vector databases? | Medium | Partner discussions |
| What's the Kafka integration approach? | High | Prototype in Sprint 4 |
| Should we support GraphQL subscriptions? | Low | Community feedback |

---

## 11. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Aggregate** | A cluster of domain objects that can be treated as a single unit |
| **Blake3** | Cryptographic hash function, faster than SHA-256 |
| **CQRS** | Command Query Responsibility Segregation pattern |
| **DashMap** | Concurrent hash map with lock-free reads |
| **Event Sourcing** | Storing state changes as a sequence of events |
| **L1/L2 Cache** | Tiered caching (L1=hot/smaller, L2=warm/larger) |
| **PromQL** | Prometheus Query Language |
| **Snapshot** | Point-in-time capture of aggregate state |
| **WAL** | Write-Ahead Log for durability |

### Appendix B: References

1. [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
2. [Blake3 Specification](https://github.com/BLAKE3-team/BLAKE3-specs)
3. [Prometheus Best Practices](https://prometheus.io/docs/practices/)
4. [Rust Async Patterns](https://rust-lang.github.io/async-book/)

### Appendix C: Decision Log

| Date | Decision | Context | Status |
|------|----------|---------|--------|
| 2026-04-01 | Use Blake3 over SHA-256 | Performance, security | Approved |
| 2026-04-02 | Support Rust, Go, Python | Market coverage | Approved |
| 2026-04-03 | DashMap for concurrent cache | Performance | Approved |

---

*End of DataKit PRD v1.0.0*
