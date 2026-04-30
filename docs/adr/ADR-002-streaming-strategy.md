# ADR-002: Streaming vs Batch Processing Strategy

**Document ID:** PHENOTYPE_DATAKIT_ADR_002  
**Status:** Accepted  
**Last Updated:** 2026-04-03  
**Author:** Phenotype Architecture Team  
**Deciders:** Phenotype Architecture Team  
**Technical Story:** DataKit processing model selection

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

DataKit must support both streaming (real-time) and batch (bulk) data processing patterns. The Phenotype ecosystem generates data through multiple channels:

- **Real-Time Events**: User actions, system events, webhook deliveries, database changes
- **Batch Operations**: Data imports, report generation, analytics aggregation, periodic syncs
- **Mixed Workloads**: Event-driven processing with periodic batch reconciliation

### Processing Requirements

| Requirement | Streaming | Batch |
|-------------|-----------|-------|
| Latency | < 100ms | Minutes to hours |
| Throughput | Continuous | Periodic bursts |
| Ordering | Strict per-subject | Flexible |
| Fault Tolerance | At-least-once delivery | Retry with idempotency |
| State Management | In-memory, checkpoints | Full dataset scans |
| Resource Usage | Constant, predictable | Spiky, scalable |

### Current DataKit Processing Patterns

```
┌──────────────────────────────────────────────────────────────┐
│              DataKit Processing Patterns                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Streaming (Real-Time):                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Event Bus   │───>│ Event        │───>│ Projections    │  │
│  │ (tokio/NATS)│    │ Handlers     │    │ (Read Models)  │  │
│  └─────────────┘    └──────────────┘    └────────────────┘  │
│                                                              │
│  Batch (Bulk):                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Data Source │───>│ Transform    │───>│ Load           │  │
│  │ (File/DB)   │    │ (Map/Reduce) │    │ (Storage)      │  │
│  └─────────────┘    └──────────────┘    └────────────────┘  │
│                                                              │
│  Hybrid (Stream + Batch):                                    │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Event Stream│───>│ Micro-Batch  │───>│ Aggregated     │  │
│  │ (Continuous)│    │ (Windowed)   │    │ Results        │  │
│  └─────────────┘    └──────────────┘    └────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Options Considered

#### Option 1: Streaming-Only (Kappa Architecture)

```
┌──────────────────────────────────────────────────────────────┐
│                    Kappa Architecture                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ All Data │───>│  Stream      │───>│  Stream          │   │
│  │ as Events│    │  Processor   │    │  Processors      │   │
│  │          │    │              │    │                  │   │
│  └──────────┘    └──────────────┘    └──────────────────┘   │
│                            │                                 │
│                     ┌──────┴──────┐                         │
│                     │  Replay     │                         │
│                     │  for Batch  │                         │
│                     └─────────────┘                         │
│                                                              │
│  Batch = Replaying stream from beginning                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Single processing model to maintain
- Natural fit for event sourcing
- Replay capability for any computation
- Consistent ordering guarantees

**Cons:**
- Replay can be slow for large datasets
- Not all workloads fit streaming model
- Complex windowing for aggregations
- Overhead for simple batch operations

#### Option 2: Lambda Architecture (Stream + Batch)

```
┌──────────────────────────────────────────────────────────────┐
│                   Lambda Architecture                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐                                                │
│  │ Data     │                                               │
│  │ Source   │                                               │
│  └────┬─────┘                                               │
│       │                                                      │
│  ┌────┴─────────────────────────────────────┐               │
│  │                                          │               │
│  ▼                                          ▼               │
│  ┌──────────────┐                    ┌──────────────┐       │
│  │ Speed Layer  │                    │ Batch Layer  │       │
│  │ (Streaming)  │                    │ (Batch)      │       │
│  │              │                    │              │       │
│  │ Low latency  │                    │ High accuracy│       │
│  │ Approximate  │                    │ Complete     │       │
│  └──────┬───────┘                    └──────┬───────┘       │
│         │                                   │               │
│         ▼                                   ▼               │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Serving Layer                       │       │
│  │  Merge speed + batch results                     │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Handles both real-time and historical analysis
- Fault-tolerant through batch reconciliation
- Proven at massive scale (Twitter, Netflix)

**Cons:**
- Two codebases to maintain (stream + batch logic)
- Complex serving layer for result merging
- Significant operational overhead
- Overkill for Phenotype's scale

#### Option 3: Streaming-First with Batch Fallback (Selected)

```
┌──────────────────────────────────────────────────────────────┐
│              Streaming-First with Batch Fallback             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Primary Path (Streaming):                                   │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Events   │───>│  Event Bus   │───>│  Handlers        │   │
│  │ (Real)   │    │  (NATS/Rust) │    │  (Projections)   │   │
│  └──────────┘    └──────────────┘    └──────────────────┘   │
│                                                              │
│  Fallback Path (Batch):                                      │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Backfill │───>│  In-Memory   │───>│  Bulk Load       │   │
│  │ / Import │    │  Store       │    │  (Storage)       │   │
│  └──────────┘    └──────────────┘    └──────────────────┘   │
│                                                              │
│  Reconciliation:                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Periodic batch jobs verify stream processing        │   │
│  │  Event sourcing enables exact replay for correction  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Streaming as the default, natural fit for event-driven architecture
- Batch for exceptional cases (backfill, import, analytics)
- Event sourcing enables replay for batch reconciliation
- Single primary processing model
- Simpler than Lambda Architecture

**Cons:**
- Batch operations less optimized than dedicated batch systems
- Requires careful design for batch-stream boundary
- May need dedicated batch tooling as scale grows

---

## Decision

We adopt **Option 3: Streaming-First with Batch Fallback** with the following implementation strategy:

### Streaming as Primary

All real-time data processing flows through the event bus:

```
┌──────────────────────────────────────────────────────────────┐
│                  Streaming Pipeline                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │ Source  │───>│  Event Bus   │───>│  Handlers        │    │
│  │         │    │              │    │                  │    │
│  │ API     │    │ Rust: tokio  │    │ - Projections    │    │
│  │ Webhook │    │ Python: NATS │    │ - Notifications  │    │
│  │ DB Change│   │              │    │ - Cache Updates  │    │
│  │ Timer   │    │              │    │ - Audit Log      │    │
│  └─────────┘    └──────────────┘    └──────────────────┘    │
│                                                              │
│  Guarantees:                                                 │
│  - At-least-once delivery (NATS JetStream)                   │
│  - Ordered per-subject (NATS) / per-type (tokio channels)    │
│  - Bounded channels for backpressure                         │
│  - Hash chain verification for integrity                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Batch for Exceptional Cases

Batch processing handles scenarios where streaming is impractical:

| Scenario | Batch Approach | Tool |
|----------|---------------|------|
| Initial data import | Bulk load from file | InMemoryStore + Storage |
| Historical backfill | Replay events from store | EventStore.read() |
| Analytics aggregation | Periodic scan | InMemoryStore.entries() |
| Data migration | Transform + reload | ETL Pipeline |
| Report generation | Snapshot + query | Database adapter |

### Reconciliation Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                  Reconciliation Flow                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Stream State (Real-Time)          Batch State (Periodic)    │
│  ┌────────────────────┐            ┌────────────────────┐   │
│  │ Current projection │            │ Full scan result   │   │
│  │ from event stream  │            │ from raw data      │   │
│  └─────────┬──────────┘            └─────────┬──────────┘   │
│            │                                 │              │
│            └─────────────┬───────────────────┘              │
│                          │                                  │
│                   ┌──────▼──────┐                          │
│                   │  Compare    │                          │
│                   │  & Reconcile│                          │
│                   └──────┬──────┘                          │
│                          │                                  │
│                   ┌──────▼──────┐                          │
│                   │  Correct    │                          │
│                   │  Divergence │                          │
│                   │  via Replay │                          │
│                   └─────────────┘                          │
│                                                              │
│  Blake3 hash chains enable verification at every step        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Processing Model Selection Guide

```
┌──────────────────────────────────────────────────────────────┐
│              Processing Model Decision Guide                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Is the data event-driven?                                   │
│  ├── Yes → Use Event Bus (streaming)                        │
│  │   ├── Rust services → tokio channels                     │
│  │   ├── Python services → NATS JetStream                   │
│  │   └── Cross-service → NATS JetStream                     │
│  │                                                           │
│  └── No → Is it a one-time bulk operation?                  │
│      ├── Yes → Use Batch Processing                         │
│      │   ├── Small data → InMemoryStore                     │
│      │   ├── Large data → Storage backend (S3)              │
│      │   └── Database data → Direct query                   │
│      │                                                       │
│      └── No → Is it periodic aggregation?                   │
│          ├── Yes → Use Stream + Windowing                   │
│          │   └── Aggregate events in time windows           │
│          │                                                   │
│          └── No → Use direct database query                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Consequences

### Positive Consequences

1. **Natural Event-Driven Fit**: Streaming aligns perfectly with DataKit's event sourcing foundation. Every state change is an event, making streaming the natural processing model. Event handlers process changes as they occur, maintaining real-time projections.

2. **Backpressure Through Bounded Channels**: Rust event bus uses bounded tokio channels (default: 100 capacity). When consumers are slow, producers naturally slow down, preventing memory exhaustion. NATS JetStream provides persistent backpressure for distributed scenarios.

3. **Replay Capability for Recovery**: Blake3 hash chains enable complete event replay with integrity verification. If a projection diverges, replay from the event store restores correctness. This eliminates the need for separate batch reconciliation in most cases.

4. **Simplified Mental Model**: Developers reason about one primary processing model (streaming) rather than maintaining separate stream and batch logic. Batch operations are clearly delineated as exceptional cases.

5. **Incremental Processing**: Events are processed incrementally as they arrive, avoiding the need to scan entire datasets for each update. This scales better than batch processing for growing datasets.

6. **Cache Coherence**: Event-driven cache invalidation ensures caches stay consistent with the source of truth. When an event modifies data, the cache invalidation event flows through the same bus as the data event.

7. **Audit Trail**: Every processed event is recorded in the event store with Blake3 hash chain verification. This provides a complete, tamper-evident audit trail of all data processing.

8. **Graceful Degradation**: When streaming infrastructure is unavailable, events can be queued locally and processed when connectivity is restored. NATS JetStream's persistent storage provides this guarantee natively.

### Negative Consequences

1. **Batch Inefficiency**: Bulk operations (e.g., importing 1M records) are inefficient through the streaming model. Each event incurs overhead (serialization, channel send, handler dispatch) that batch processing avoids.

2. **Windowing Complexity**: Time-based aggregations (e.g., "events per hour") require explicit windowing logic in the streaming model, whereas batch processing can simply GROUP BY time period.

3. **Late Event Handling**: Events arriving out of order (late events) require special handling. NATS JetStream provides some ordering guarantees, but cross-service events may arrive out of order.

4. **State Management**: Streaming processors must maintain state in memory or external stores. For complex aggregations, this state management adds complexity compared to batch's full-dataset approach.

5. **Debugging Difficulty**: Streaming systems are harder to debug than batch systems. You cannot simply "look at the data" — you must understand the flow of events through time.

6. **Resource Estimation**: Streaming resource usage is constant but harder to estimate. Batch resource usage is predictable (proportional to data size) but spiky.

7. **Migration Complexity**: Migrating from streaming to batch (or vice versa) requires careful coordination. The event sourcing foundation helps but doesn't eliminate the challenge.

---

## Architecture

### Streaming Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Streaming Pipeline                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Event Sources                                                     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │ API      │ │ Webhook  │ │ DB Change│ │ Timer    │             │  │
│  │  │ Requests │ │ Delivery │ │ Capture  │ │ Events   │             │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘             │  │
│  └───────┼────────────┼────────────┼─────────────┼───────────────────┘  │
│          │            │            │             │                       │
│  ┌───────▼────────────▼────────────▼─────────────▼───────────────────┐  │
│  │  Event Bus (Publish)                                              │  │
│  │  ┌─────────────────────────┐  ┌───────────────────────────────┐  │  │
│  │  │ Rust: tokio channels    │  │ Python: NATS JetStream        │  │  │
│  │  │ - Bounded (capacity:100)│  │ - Persistent stream           │  │  │
│  │  │ - Type-specific         │  │ - Durable consumers           │  │  │
│  │  │ - Broadcast (all events)│  │ - Ack-based delivery          │  │  │
│  │  └────────────┬────────────┘  └───────────────┬───────────────┘  │  │
│  └───────────────┼───────────────────────────────┼──────────────────┘  │
│                  │                               │                      │
│  ┌───────────────▼───────────────────────────────▼──────────────────┐  │
│  │  Event Handlers (Subscribe)                                      │  │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────────┐   │  │
│  │  │ Projections     │ │ Notifications   │ │ Cache Updates    │   │  │
│  │  │ (Read Models)   │ │ (Email, Push)   │ │ (Invalidate)     │   │  │
│  │  └────────┬────────┘ └────────┬────────┘ └────────┬─────────┘   │  │
│  │           │                   │                   │             │  │
│  │  ┌────────▼───────────────────▼───────────────────▼─────────┐   │  │
│  │  │  Event Store (Append with Blake3 Hash Chain)             │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐    │   │  │
│  │  │  │ E1:Hash0xABCD ──> E2:Hash0x1234 ──> E3:Hash...  │    │   │  │
│  │  │  └──────────────────────────────────────────────────┘    │   │  │
│  │  └──────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Batch Processing Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Batch Processing                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Extract Phase                                                     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │ File     │ │ Database │ │ API      │ │ Event    │             │  │
│  │  │ (CSV/JSON│ │ (Query)  │ │ (Fetch)  │ │ Store    │             │  │
│  │  │  /Parquet)│ │          │ │          │ │ (Replay) │             │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘             │  │
│  └───────┼────────────┼────────────┼─────────────┼───────────────────┘  │
│          │            │            │             │                       │
│  ┌───────▼────────────▼────────────▼─────────────▼───────────────────┐  │
│  │  Transform Phase                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │  InMemoryStore<K, V>                                         │  │  │
│  │  │  - Load all records                                          │  │  │
│  │  │  - Apply transformations                                     │  │  │
│  │  │  - Validate results                                          │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│  ┌─────────────────────────────────▼─────────────────────────────────┐  │
│  │  Load Phase                                                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │ Database │ │ Storage  │ │ Event    │ │ Cache    │             │  │
│  │  │ (Bulk    │ │ (Upload) │ │ Store    │ │ (Refresh)│             │  │
│  │  │  Insert) │ │          │ │ (Append) │ │          │             │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Windowed Stream Processing

```
┌──────────────────────────────────────────────────────────────┐
│                  Windowed Aggregation                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Events:                                                     │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐         │
│  │ E1 │ │ E2 │ │ E3 │ │ E4 │ │ E5 │ │ E6 │ │ E7 │ ...     │
│  │ t=1│ │ t=2│ │ t=3│ │ t=4│ │ t=5│ │ t=6│ │ t=7│         │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘         │
│  ◄──────── Window 1 ────────► ◄──── Window 2 ──────►       │
│                                                              │
│  Window 1 Result: aggregate(E1, E2, E3, E4)                 │
│  Window 2 Result: aggregate(E4, E5, E6, E7)                 │
│  (Overlapping windows for tumbling)                         │
│                                                              │
│  Implementation:                                             │
│  - Collect events in time-ordered buffer                     │
│  - When window closes, compute aggregate                     │
│  - Emit result as new event                                  │
│  - Store aggregate in event store                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Code Examples

### Rust: Streaming Event Handler

```rust
use phenotype_event_bus::{EventBus, Event, EventHandler, InMemoryEventBus};
use std::sync::Arc;

#[derive(Debug, Clone, serde::Serialize)]
struct UserEvent {
    id: uuid::Uuid,
    event_type: String,
    user_id: String,
    timestamp: chrono::DateTime<chrono::Utc>,
}

impl Event for UserEvent {
    fn event_type(&self) -> &'static str {
        &self.event_type
    }
    fn event_id(&self) -> uuid::Uuid {
        self.id
    }
    fn timestamp(&self) -> chrono::DateTime<chrono::Utc> {
        self.timestamp
    }
    fn as_any(&self) -> &dyn std::any::Any {
        self
    }
}

struct UserProjectionHandler;

#[async_trait::async_trait]
impl EventHandler<UserEvent> for UserProjectionHandler {
    async fn handle(&self, event: UserEvent) -> Result<(), phenotype_event_bus::EventBusError> {
        // Update read model
        println!("Processing user event: {:?}", event);
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let bus = Arc::new(InMemoryEventBus::default());

    // Subscribe and process
    let mut rx = bus.subscribe::<UserEvent>().await?;
    tokio::spawn(async move {
        while let Some(event) = rx.recv().await {
            let handler = UserProjectionHandler;
            if let Err(e) = handler.handle(event).await {
                eprintln!("Handler error: {}", e);
            }
        }
    });

    // Publish events (streaming)
    for i in 0..10 {
        let event = UserEvent {
            id: uuid::Uuid::new_v4(),
            event_type: "user.created".to_string(),
            user_id: format!("user-{}", i),
            timestamp: chrono::Utc::now(),
        };
        bus.publish(event).await?;
    }

    Ok(())
}
```

### Python: Batch Processing with Event Replay

```python
"""
Batch processing via event replay.
"""
import asyncio
from pheno_events.core.event_store import EventStore
from pheno_events.core.event_bus import EventBus


async def batch_rebuild_projections(event_store: EventStore):
    """Rebuild all projections from event store (batch operation)."""
    # Get all aggregates
    events = await event_store.get_events()
    aggregates = set(e.aggregate_id for e in events)

    # Rebuild each aggregate
    for aggregate_id in aggregates:
        stream = await event_store.get_stream(aggregate_id)

        # Replay events to rebuild state
        state = None
        for event in stream:
            state = apply_event(state, event)

        # Save rebuilt projection
        await save_projection(aggregate_id, state)

    print(f"Rebuilt projections for {len(aggregates)} aggregates")


async def batch_import_from_file(file_path: str, event_store: EventStore):
    """Batch import events from a file."""
    import json

    with open(file_path) as f:
        events = [json.loads(line) for line in f if line.strip()]

    for event_data in events:
        await event_store.append(
            event_type=event_data["event_type"],
            aggregate_id=event_data["aggregate_id"],
            aggregate_type=event_data["aggregate_type"],
            data=event_data["data"],
            version=event_data.get("version", 1),
        )

    print(f"Imported {len(events)} events from {file_path}")


def apply_event(state, event):
    """Apply a single event to rebuild state."""
    if state is None:
        state = {}

    if event.event_type == "UserCreated":
        state["user_id"] = event.data.get("user_id")
        state["email"] = event.data.get("email")
        state["created"] = True
    elif event.event_type == "EmailVerified":
        state["email_verified"] = True

    return state


async def save_projection(aggregate_id: str, state):
    """Save rebuilt projection to storage."""
    pass  # Implementation depends on storage backend
```

### Go: ETL Pipeline

```go
package etl

import (
    "context"
    "fmt"
)

// StreamingETL processes records through a streaming pipeline
type StreamingETL struct {
    source    EventSource
    processor EventProcessor
    sink      EventSink
}

type EventSource interface {
    Events(ctx context.Context) (<-chan Record, error)
}

type EventProcessor interface {
    Process(ctx context.Context, record Record) (Record, error)
}

type EventSink interface {
    Write(ctx context.Context, record Record) error
}

func (e *StreamingETL) Run(ctx context.Context) error {
    events, err := e.source.Events(ctx)
    if err != nil {
        return fmt.Errorf("failed to get events: %w", err)
    }

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case record, ok := <-events:
            if !ok {
                return nil // Stream closed
            }

            processed, err := e.processor.Process(ctx, record)
            if err != nil {
                return fmt.Errorf("processing failed: %w", err)
            }

            if err := e.sink.Write(ctx, processed); err != nil {
                return fmt.Errorf("write failed: %w", err)
            }
        }
    }
}
```

---

## Cross-References

### Related ADRs

- [ADR-001: Data Processing Engine Architecture](ADR-001-processing-engine.md) — Foundation for the processing engine
- [ADR-003: Schema Evolution Strategy](ADR-003-schema-evolution.md) — Schema handling for streaming and batch data

### Related Research

- [Data Processing SOTA](../research/DATA_PROCESSING_SOTA.md) — Stream processing technology analysis
- [DataKit Specification](../SPEC.md) — Complete system specification

### External References

- [Kappa Architecture](https://www.oreilly.com/radar/questioning-the-lambda-architecture/) — Jay Kreps
- [Lambda Architecture](https://lambda-architecture.net/) — Nathan Marz
- [Designing Data-Intensive Applications](https://dataintensive.net/) — Martin Kleppmann, Chapter 11
- [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream) — Persistent streaming
- [Apache Flink](https://flink.apache.org/) — Stream processing framework

### Phenotype Ecosystem

- [PhenoSpecs](https://github.com/KooshaPari/PhenoSpecs) — Specifications and ADRs
- [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) — Patterns and guidelines
- [HexaKit](https://github.com/KooshaPari/HexaKit) — Templates and scaffolding

---

*This ADR was accepted on 2026-04-03 by the Phenotype Architecture Team.*
