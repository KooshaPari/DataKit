# DataKit ADRs

## ADR 001: Blake3 Hash Chains for Event Sourcing

### Status: Accepted

### Context

Event sourcing requires tamper-evident storage for audit-heavy domains. Traditional event stores provide ordering but not cryptographic verification. We need integrity guarantees without blockchain complexity.

Options considered:
- SHA-256: Slower, no parallelism
- SHA3-256: Slower, different design
- Blake2b: Fast but single-threaded
- Blake3: Fast, parallelizable, modern

### Decision

Use Blake3 for cryptographic hash chains in event sourcing:

```rust
pub fn compute_hash(data: &[u8], previous_hash: &[u8; 32], sequence: u64) -> [u8; 32] {
    let mut hasher = blake3::Hasher::new();
    hasher.update(data);
    hasher.update(previous_hash);
    hasher.update(&sequence.to_le_bytes());
    hasher.finalize().into()
}
```

### Consequences

#### Positive

1. **Performance**: 1.4 GB/s on modern CPUs
2. **Integrity**: Cryptographic tamper detection
3. **Parallelism**: SIMD-optimized
4. **Merkle trees**: Built-in support for batch verification

#### Negative

1. **Dependency**: Additional crate (blake3)
2. **Newer**: Less battle-tested than SHA-256
3. **Hardware**: Best performance on AVX-512 systems

---

## ADR 002: Two-Tier In-Memory Cache Architecture

### Status: Accepted

### Context

Caching needs to balance speed and capacity. Single-tier caches either sacrifice speed (large) or capacity (small). We need hot data immediately available and warm data nearby.

### Decision

Implement L1 (hot, small) and L2 (warm, larger) tiers:

```rust
pub struct TwoTierCache<K, V> {
    l1: Arc<DashMap<K, CacheEntry<V>>>,  // Hot cache
    l2: Arc<DashMap<K, CacheEntry<V>>>,  // Warm cache
    l1_capacity: usize,
}

impl<K, V> TwoTierCache<K, V> {
    pub fn get(&self, key: &K) -> Option<V> {
        // L1 check (fastest)
        if let Some(entry) = self.l1.get(key) {
            return Some(entry.value.clone());
        }
        
        // L2 check with promotion
        if let Some(entry) = self.l2.get(key) {
            if self.l1.len() < self.l1_capacity {
                self.l1.insert(key.clone(), entry.clone());
            }
            return Some(entry.value.clone());
        }
        
        None
    }
}
```

### Consequences

#### Positive

1. **Speed**: Hot data in L1
2. **Capacity**: Warm data in L2
3. **Automatic promotion**: Frequently accessed items move to L1
4. **No eviction complexity**: Simple FIFO in L1

#### Negative

1. **Memory overhead**: Two copies possible
2. **Promotion cost**: L2 hit requires L1 insert
3. **Tuning required**: L1/L2 ratio depends on workload

---

## ADR 003: Async-First Event Bus with Backpressure

### Status: Accepted

### Context

Event bus systems must handle varying producer/consumer rates. Synchronous event buses can cause cascading failures under load. We need bounded queues and backpressure.

### Decision

Implement async event bus with bounded channels and concurrent dispatch:

```rust
pub struct InMemoryEventBus {
    broadcast_tx: broadcast::Sender<EventEnvelope>,
    channels: DashMap<TypeId, Box<dyn Any + Send + Sync>>,
}

#[async_trait]
impl EventBus for InMemoryEventBus {
    async fn publish<E: Event>(&self, event: E) -> Result<(), EventBusError> {
        let envelope = EventEnvelope {
            id: event.event_id(),
            event_type: event.event_type().to_string(),
            payload: serde_json::to_value(&event)?,
            metadata: HashMap::new(),
            timestamp: event.timestamp(),
        };
        
        // Broadcast (may drop slow consumers)
        self.broadcast_tx.send(envelope).ok();
        
        Ok(())
    }
    
    async fn subscribe<E: Event>(&self) -> Result<mpsc::Receiver<E>, EventBusError> {
        let (tx, rx) = mpsc::channel(100);  // Bounded channel
        // Store sender for type
        self.channels.insert(TypeId::of::<E>(), Box::new(tx));
        Ok(rx)
    }
}
```

### Consequences

#### Positive

1. **Backpressure**: Bounded channels prevent memory exhaustion
2. **Concurrency**: Parallel event processing
3. **Type safety**: Type-specific channels
4. **Broadcast**: All consumers receive all events

#### Negative

1. **Complexity**: Async runtime required
2. **Ordering**: Broadcast channel may drop events for slow consumers
3. **Memory**: Each subscriber has its own queue

---

*ADRs DataKit - Version 1.0*
