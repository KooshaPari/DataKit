# ADR-003: Schema Evolution Strategy

**Document ID:** PHENOTYPE_DATAKIT_ADR_003  
**Status:** Proposed  
**Last Updated:** 2026-04-03  
**Author:** Phenotype Architecture Team  
**Deciders:** Phenotype Architecture Team  
**Technical Story:** DataKit cross-language schema management

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

DataKit operates across three programming languages (Rust, Go, Python) with data flowing between them through event buses, storage backends, and database adapters. Schema evolution -- the ability to change data structures over time without breaking consumers -- is critical for:

- **Event Sourcing**: Events persisted with Blake3 hash chains must remain readable as schemas evolve
- **Event Bus**: Producers and consumers may run different versions simultaneously
- **Storage Backends**: Data stored in S3, Supabase, or local files must remain accessible
- **Database Adapters**: Schema changes in PostgreSQL/Supabase must be managed safely

### Schema Evolution Challenges

```
+--------------------------------------------------------------+
|              Schema Evolution Challenges                     |
+--------------------------------------------------------------+
|                                                              |
|  1. Cross-Language Consistency                               |
|     +---------+    +---------+    +---------+                |
|     |  Rust   |    |   Go    |    | Python  |                |
|     | struct  |    | struct  |    | class   |                |
|     | User {  |    | User {  |    | User:   |                |
|     |  id:    |    |  ID     |    |  id     |                |
|     |  String |    |  string |    |  id: str|                |
|     |  email: |    |  Email  |    |  email  |                |
|     |  String |    |  string |    |  email  |                |
|     | }       |    | }       |    | }       |                |
|     +---------+    +---------+    +---------+                |
|     All must serialize/deserialize identically               |
|                                                              |
|  2. Backward Compatibility                                   |
|     v1 Event: {user_id, name}                                |
|     v2 Event: {user_id, name, email}                         |
|     Old consumers must still read v2 events                  |
|                                                              |
|  3. Forward Compatibility                                    |
|     v2 Producer sends {user_id, name, email}                 |
|     v1 Consumer only knows {user_id, name}                   |
|     v1 Consumer must not crash                               |
|                                                              |
|  4. Event Store Immutability                                 |
|     Events in Blake3 hash chain cannot be modified           |
|     Schema changes must handle historical events             |
|                                                              |
|  5. Breaking Changes                                         |
|     Renaming fields, changing types, removing fields         |
|     Require migration strategy                               |
|                                                              |
+--------------------------------------------------------------+
```

### Current Schema Approach

DataKit currently uses language-native serialization without explicit schema management:

| Language | Serialization | Schema Enforcement |
|----------|--------------|-------------------|
| Rust | serde (derive) | Compile-time types |
| Go | encoding/json | Struct tags |
| Python | json, dataclass | Runtime (minimal) |

**Problems with Current Approach:**

1. No cross-language schema validation
2. No schema versioning in event envelopes
3. No migration strategy for breaking changes
4. No schema registry for discovery
5. Inconsistent error handling for schema mismatches

### Options Considered

#### Option 1: Protocol Buffers (Protobuf)

```
+--------------------------------------------------------------+
|                    Protobuf Schema                           |
+--------------------------------------------------------------+
|                                                              |
|  syntax = "proto3";                                          |
|                                                              |
|  message UserEvent {                                         |
|    string user_id = 1;                                       |
|    string name = 2;                                          |
|    string email = 3;                                         |
|    int64 timestamp = 4;                                      |
|    uint32 schema_version = 5;                                |
|  }                                                           |
|                                                              |
|  Generated code for:                                         |
|  - Rust: prost-build                                         |
|  - Go: protoc-gen-go                                         |
|  - Python: protobuf / grpcio                                 |
|                                                              |
|  Compatibility:                                              |
|  - Adding fields: Safe (new fields get defaults)             |
|  - Removing fields: Safe (old fields ignored)                |
|  - Renaming fields: Breaking (field number must stay)        |
|  - Changing types: Breaking                                  |
|                                                              |
+--------------------------------------------------------------+
```

**Pros:**
- Explicit schema definition in .proto files
- Cross-language code generation
- Built-in forward/backward compatibility
- Compact binary encoding
- Schema evolution rules are clear

**Cons:**
- Additional build step (protoc compilation)
- Less idiomatic in each language
- JSON interoperability requires special handling
- Learning curve for team
- Binary format less debuggable

#### Option 2: JSON Schema + Validation

```
+--------------------------------------------------------------+
|                  JSON Schema Approach                        |
+--------------------------------------------------------------+
|                                                              |
|  Schema Definition:                                          |
|  {                                                           |
|    "$schema": "https://json-schema.org/draft/2020-12/schema",|
|    "title": "UserEvent",                                     |
|    "type": "object",                                         |
|    "properties": {                                           |
|      "user_id": { "type": "string" },                        |
|      "name": { "type": "string" },                           |
|      "email": { "type": "string", "format": "email" },       |
|      "schema_version": { "type": "integer", "minimum": 1 }   |
|    },                                                        |
|    "required": ["user_id", "name", "schema_version"]         |
|  }                                                           |
|                                                              |
|  Validation Libraries:                                       |
|  - Rust: jsonschema crate                                    |
|  - Go: go-jsonschema                                         |
|  - Python: jsonschema / pydantic                             |
|                                                              |
+--------------------------------------------------------------+
```

**Pros:**
- Human-readable schema definitions
- Native JSON compatibility
- Rich validation rules
- Widely supported
- Easy to debug

**Cons:**
- Runtime validation overhead
- No compile-time guarantees
- Schema files separate from code
- Version management still manual
- Performance impact on hot paths

#### Option 3: Language-Native Types + Schema Registry (Selected)

```
+--------------------------------------------------------------+
|           Language-Native + Schema Registry                  |
+--------------------------------------------------------------+
|                                                              |
|  Rust:                                                       |
|  #[derive(Serialize, Deserialize)]                           |
|  #[serde(tag = "type", content = "data")]                    |
|  enum DomainEvent {                                          |
|      #[serde(rename = "user_created_v1")]                    |
|      UserCreatedV1(UserCreatedV1),                           |
|      #[serde(rename = "user_created_v2")]                    |
|      UserCreatedV2(UserCreatedV2),                           |
|  }                                                           |
|                                                              |
|  Go:                                                         |
|  type DomainEvent struct {                                   |
|      Type    string          `json:"type"`                   |
|      Version int             `json:"schema_version"`         |
|      Data    json.RawMessage `json:"data"`                   |
|  }                                                           |
|                                                              |
|  Python:                                                     |
|  @dataclass                                                  |
|  class DomainEvent:                                          |
|      type: str                                               |
|      schema_version: int                                     |
|      data: dict[str, Any]                                    |
|                                                              |
|  Schema Registry:                                            |
|  - JSON files defining each schema version                   |
|  - Validation on deserialization                             |
|  - Migration functions between versions                      |
|                                                              |
+--------------------------------------------------------------+
```

**Pros:**
- Idiomatic in each language
- Compile-time type safety (Rust, Go)
- JSON native (easy debugging)
- Flexible evolution through type-tagged unions
- No external tooling required

**Cons:**
- Manual schema version management
- Cross-language consistency requires discipline
- No automatic code generation
- Migration logic must be written manually

---

## Decision

We adopt **Option 3: Language-Native Types + Schema Registry** with the following implementation:

### Schema Versioning in Event Envelope

Add `schema_version` to the event envelope across all languages:

```rust
// Rust: EventEnvelope with schema version
#[derive(Serialize, Deserialize)]
pub struct EventEnvelope<T> {
    pub payload: T,
    pub hash: [u8; 32],
    pub previous_hash: [u8; 32],
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub sequence: u64,
    pub schema_version: u32,  // NEW: Schema version
}
```

```python
# Python: StoredEvent with schema version
@dataclass
class StoredEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1
    schema_version: int = 1  # NEW: Schema version
```

```go
// Go: EventEnvelope with schema version
type EventEnvelope struct {
    Payload       json.RawMessage `json:"payload"`
    Hash          string          `json:"hash"`
    PreviousHash  string          `json:"previous_hash"`
    Timestamp     time.Time       `json:"timestamp"`
    Sequence      uint64          `json:"sequence"`
    SchemaVersion uint32          `json:"schema_version"` // NEW
}
```

### Schema Registry Structure

```
docs/schemas/
├── registry.json              # Schema registry index
├── events/
│   ├── user_created_v1.json   # Schema definition v1
│   ├── user_created_v2.json   # Schema definition v2
│   └── migrations/
│       └── user_created_v1_to_v2.json  # Migration spec
├── commands/
│   └── ...
└── projections/
    └── ...
```

```json
{
  "schema_id": "user_created",
  "version": 2,
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "email": { "type": "string", "format": "email" },
    "name": { "type": "string" },
    "metadata": {
      "type": "object",
      "properties": {
        "source": { "type": "string" },
        "ip_address": { "type": "string" }
      }
    }
  },
  "required": ["user_id", "email", "name"],
  "additionalProperties": false,
  "migrations": {
    "from_v1": {
      "add_fields": ["metadata"],
      "rename_fields": {},
      "remove_fields": [],
      "transform": "metadata = {source: 'unknown'}"
    }
  }
}
```

### Compatibility Rules

```
+--------------------------------------------------------------+
|              Schema Compatibility Rules                      |
+--------------------------------------------------------------+
|                                                              |
|  BACKWARD COMPATIBLE (old consumer reads new data):          |
|  + Adding optional fields (with defaults)                    |
|  + Adding new event types to tagged enum                     |
|  + Adding new enum variants                                  |
|                                                              |
|  FORWARD COMPATIBLE (new consumer reads old data):           |
|  + Removing optional fields                                  |
|  + Adding #[serde(default)] to new required fields           |
|  + Using Option<T> for fields that may be absent             |
|                                                              |
|  BREAKING CHANGES (require migration):                       |
|  - Renaming fields (use #[serde(alias)] for transition)      |
|  - Changing field types (use custom deserializer)            |
|  - Removing required fields without default                  |
|  - Changing event type names in tagged enums                 |
|                                                              |
|  RULE: All schema changes must be backward compatible.       |
|  Breaking changes require new schema version + migration.    |
|                                                              |
+--------------------------------------------------------------+
```

### Migration Strategy

```
+--------------------------------------------------------------+
|              Schema Migration Flow                           |
+--------------------------------------------------------------+
|                                                              |
|  Step 1: Define new schema version                           |
|  ┌──────────────────────────────────────────────────────┐   |
|  │  Create user_created_v2.json in schema registry      │   |
|  │  Define migration spec (v1 -> v2)                    │   |
|  └──────────────────────────────────────────────────────┘   |
|                                                              |
|  Step 2: Update producers first                              |
|  ┌──────────────────────────────────────────────────────┐   |
|  │  Producers emit v2 events with schema_version: 2     │   |
|  │  Old consumers still work (backward compatible)      │   |
|  └──────────────────────────────────────────────────────┘   |
|                                                              |
|  Step 3: Update consumers                                    |
|  ┌──────────────────────────────────────────────────────┐   |
|  │  Consumers handle both v1 and v2 events              │   |
|  │  Use migration functions for v1 -> v2 conversion     │   |
|  └──────────────────────────────────────────────────────┘   |
|                                                              |
|  Step 4: Verify and cleanup                                  |
|  ┌──────────────────────────────────────────────────────┐   |
|  │  Monitor for v1 events in event store                │   |
|  │  When all events are v2, remove v1 handling code     │   |
|  └──────────────────────────────────────────────────────┘   |
|                                                              |
+--------------------------------------------------------------+
```

---

## Consequences

### Positive Consequences

1. **Idiomatic Code**: Each language uses its native type system. Rust gets compile-time safety through serde derive macros. Go gets struct tags for JSON mapping. Python gets dataclasses with type hints. No foreign schema language to learn.

2. **Zero Build Step**: No protoc compilation or code generation phase. Schema changes are reflected immediately in the type definitions. Faster iteration and simpler CI/CD pipeline.

3. **JSON Native**: All data is JSON, making debugging trivial. Developers can inspect event store files directly, use jq for analysis, and test with curl. No binary decoding required.

4. **Explicit Versioning**: The `schema_version` field in every event envelope makes version identification O(1). Consumers can route to the correct deserializer or migration function based on version number alone.

5. **Migration Functions**: Explicit migration code between versions is easier to test and reason about than implicit Protobuf field number mapping. Each migration is a documented, testable function.

6. **Serde Flexibility**: Rust's serde provides powerful evolution tools: `#[serde(default)]` for new optional fields, `#[serde(alias)]` for field renames, `#[serde(skip_serializing_if)]` for optional omission, and `#[serde(tag = "type")]` for versioned enums.

7. **Schema Registry as Documentation**: JSON schema files serve as living documentation. Developers can browse the registry to understand available event types, their versions, and migration paths without reading source code.

8. **Gradual Adoption**: Existing events without `schema_version` default to version 1. New events include the version. This allows incremental migration without a big-bang cutover.

### Negative Consequences

1. **Manual Consistency**: Cross-language schema consistency relies on developer discipline. A field added to the Rust struct must be manually added to the Go struct and Python dataclass. No automatic code generation catches omissions.

2. **No Compile-Time Cross-Language Validation**: The compiler cannot verify that Rust, Go, and Python types produce identical JSON. A mismatch is only caught at runtime when deserialization fails or data is silently lost.

3. **Migration Code Overhead**: Each schema version transition requires writing and testing migration functions. For N versions, there are potentially N*(N-1)/2 migration paths. In practice, only adjacent version migrations are needed.

4. **Schema Drift Risk**: Without automated validation, schemas can drift between languages over time. A field renamed in Rust but not in Python causes silent data loss for Python consumers.

5. **No Schema Evolution Enforcement**: Nothing prevents a developer from making a breaking change without incrementing the version number. This requires code review discipline and potentially CI checks.

6. **Larger Payloads**: JSON is more verbose than Protobuf binary encoding. For high-throughput event streams, the serialization overhead may become significant compared to binary formats.

7. **Version Proliferation**: Without strict governance, schema versions can proliferate. Consumers must handle multiple versions simultaneously, increasing code complexity.

---

## Architecture

### Schema Registry Architecture

```
+-------------------------------------------------------------------------+
|                        Schema Registry                                  |
+-------------------------------------------------------------------------+
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |  Schema Definitions (JSON)                                         |  |
|  |  +-------------------------------------------------------------+  |  |
|  |  |  events/user_created_v1.json                                |  |  |
|  |  |  events/user_created_v2.json                                |  |  |
|  |  |  events/order_placed_v1.json                                |  |  |
|  |  |  commands/create_user_v1.json                               |  |  |
|  |  |  projections/user_profile_v1.json                           |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |  Validation Layer                                                   |  |
|  |  +-------------------------------------------------------------+  |  |
|  |  |  Rust: jsonschema crate (optional, for validation)          |  |  |
|  |  |  Go: go-jsonschema (optional, for validation)               |  |  |
|  |  |  Python: pydantic (built-in validation)                     |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |  Migration Layer                                                    |  |
|  |  +-------------------------------------------------------------+  |  |
|  |  |  Rust: migrate_v1_to_v2(event: EventV1) -> EventV2          |  |  |
|  |  |  Go: MigrateV1ToV2(event EventV1) EventV2                   |  |  |
|  |  |  Python: migrate_v1_to_v2(event: EventV1) -> EventV2        |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|  +-------------------------------------------------------------------+  |
|  |  Runtime Schema Resolution                                          |  |
|  |  +-------------------------------------------------------------+  |  |
|  |  |  1. Read schema_version from event envelope                 |  |  |
|  |  |  2. If version matches current, deserialize directly        |  |  |
|  |  |  3. If version is older, apply migration chain              |  |  |
|  |  |  4. If version is newer, reject or store raw for later      |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Event Versioning Flow

```
+--------------------------------------------------------------+
|              Event Version Resolution                        |
+--------------------------------------------------------------+
|                                                              |
|  Producer (v2)                    Consumer (v1)              |
|  ┌────────────────────┐           ┌────────────────────┐    |
|  │ Create v2 event    │           │ Receive event      │    |
|  │ schema_version: 2  │──JSON────>│ schema_version: 2  │    |
|  │ {user, email, meta}│           │                    │    |
|  └────────────────────┘           │ Version mismatch   │    |
|                                   │                    │    |
|                                   │ Option A: Reject   │    |
|                                   │ Option B: Migrate  │    |
|                                   │ Option C: Ignore   │    |
|                                   │   unknown fields   │    |
|                                   └────────────────────┘    |
|                                                              |
|  Recommended: Option C (ignore unknown fields)               |
|  - Forward compatible by default                             |
|  - No migration needed for additive changes                  |
|  - Breaking changes still require version bump               |
|                                                              |
+--------------------------------------------------------------+
```

### Cross-Language Schema Validation

```
+--------------------------------------------------------------+
|              Cross-Language Validation Pipeline              |
+--------------------------------------------------------------+
|                                                              |
|  CI Pipeline:                                                |
|  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐   |
|  │ Schema   │───>│ Cross-Lang   │───>│ Compatibility    │   |
|  │ Files    │    │ Validation   │    │ Check            │   |
|  │ (JSON)   │    │              │    │                  │   |
|  └──────────┘    └──────────────┘    └──────────────────┘   |
|                           │                                  |
|                    ┌──────▼──────┐                          |
|                    │  Generate   │                          |
|                    │  Test Cases │                          |
|                    │  (Roundtrip)│                          |
|                    └─────────────┘                          |
|                                                              |
|  Roundtrip Test:                                             |
|  1. Serialize Rust struct to JSON                            |
|  2. Deserialize JSON in Go                                   |
|  3. Re-serialize in Go                                       |
|  4. Deserialize in Python                                    |
|  5. Verify all three produce identical JSON                  |
|                                                              |
+--------------------------------------------------------------+
```

---

## Code Examples

### Rust: Versioned Event Types

```rust
use serde::{Deserialize, Serialize};

// Version 1 of the event
#[derive(Clone, Serialize, Deserialize)]
pub struct UserCreatedV1 {
    pub user_id: String,
    pub name: String,
}

// Version 2 adds email and metadata
#[derive(Clone, Serialize, Deserialize)]
pub struct UserCreatedV2 {
    pub user_id: String,
    pub name: String,
    pub email: String,
    #[serde(default)]
    pub metadata: UserMetadata,
}

#[derive(Clone, Serialize, Deserialize, Default)]
pub struct UserMetadata {
    pub source: String,
    pub ip_address: Option<String>,
}

// Tagged enum for versioned events
#[derive(Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "data")]
pub enum UserCreatedEvent {
    #[serde(rename = "user_created_v1")]
    V1(UserCreatedV1),
    #[serde(rename = "user_created_v2")]
    V2(UserCreatedV2),
}

impl UserCreatedEvent {
    pub fn schema_version(&self) -> u32 {
        match self {
            UserCreatedEvent::V1(_) => 1,
            UserCreatedEvent::V2(_) => 2,
        }
    }

    // Normalize to latest version
    pub fn into_latest(self) -> UserCreatedV2 {
        match self {
            UserCreatedEvent::V1(v1) => UserCreatedV2 {
                user_id: v1.user_id,
                name: v1.name,
                email: String::new(), // Migration fills this
                metadata: UserMetadata::default(),
            },
            UserCreatedEvent::V2(v2) => v2,
        }
    }
}
```

### Python: Schema-Aware Event Processing

```python
"""
Schema-aware event processing with version migration.
"""
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime


@dataclass
class UserCreatedV1:
    user_id: str
    name: str


@dataclass
class UserCreatedV2:
    user_id: str
    name: str
    email: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def migrate_v1_to_v2(event_v1: dict) -> UserCreatedV2:
    """Migrate v1 event data to v2 schema."""
    return UserCreatedV2(
        user_id=event_v1["user_id"],
        name=event_v1["name"],
        email="",  # v1 did not have email
        metadata={"source": "migration", "migrated_from": "v1"},
    )


def deserialize_event(data: dict) -> Any:
    """Deserialize event with schema version awareness."""
    schema_version = data.get("schema_version", 1)
    event_data = data.get("data", data)

    if schema_version == 1:
        return migrate_v1_to_v2(event_data)
    elif schema_version == 2:
        return UserCreatedV2(**event_data)
    else:
        raise ValueError(f"Unknown schema version: {schema_version}")


# Usage
event_data = {
    "schema_version": 1,
    "data": {"user_id": "user-123", "name": "Alice"},
}
event = deserialize_event(event_data)
print(f"Migrated to v2: email='{event.email}', metadata={event.metadata}")
```

### Go: Schema Version Handling

```go
package schema

import (
    "encoding/json"
    "fmt"
    "time"
)

// EventEnvelope with schema version
type EventEnvelope struct {
    Payload       json.RawMessage `json:"payload"`
    Hash          string          `json:"hash"`
    PreviousHash  string          `json:"previous_hash"`
    Timestamp     time.Time       `json:"timestamp"`
    Sequence      uint64          `json:"sequence"`
    SchemaVersion uint32          `json:"schema_version"`
}

// UserCreatedV1 represents the original event schema
type UserCreatedV1 struct {
    UserID string `json:"user_id"`
    Name   string `json:"name"`
}

// UserCreatedV2 represents the current event schema
type UserCreatedV2 struct {
    UserID   string            `json:"user_id"`
    Name     string            `json:"name"`
    Email    string            `json:"email"`
    Metadata map[string]string `json:"metadata,omitempty"`
}

// MigrateV1ToV2 converts a v1 event to v2
func MigrateV1ToV2(v1 UserCreatedV1) UserCreatedV2 {
    return UserCreatedV2{
        UserID: v1.UserID,
        Name:   v1.Name,
        Email:  "", // v1 had no email
        Metadata: map[string]string{
            "source":         "migration",
            "migrated_from":  "v1",
        },
    }
}

// DeserializeEvent handles schema version resolution
func DeserializeEvent(envelope EventEnvelope) (interface{}, error) {
    switch envelope.SchemaVersion {
    case 1:
        var v1 UserCreatedV1
        if err := json.Unmarshal(envelope.Payload, &v1); err != nil {
            return nil, fmt.Errorf("unmarshal v1: %w", err)
        }
        return MigrateV1ToV2(v1), nil
    case 2:
        var v2 UserCreatedV2
        if err := json.Unmarshal(envelope.Payload, &v2); err != nil {
            return nil, fmt.Errorf("unmarshal v2: %w", err)
        }
        return v2, nil
    default:
        return nil, fmt.Errorf("unknown schema version: %d", envelope.SchemaVersion)
    }
}
```

### Schema Registry Index

```json
{
  "registry_version": 1,
  "schemas": {
    "user_created": {
      "latest_version": 2,
      "versions": [1, 2],
      "compatibility": "backward",
      "description": "User account creation event"
    },
    "email_verified": {
      "latest_version": 1,
      "versions": [1],
      "compatibility": "backward",
      "description": "Email address verification event"
    },
    "order_placed": {
      "latest_version": 3,
      "versions": [1, 2, 3],
      "compatibility": "backward",
      "description": "Order placement event"
    }
  },
  "migrations": {
    "user_created": {
      "1->2": {
        "added_fields": ["email", "metadata"],
        "removed_fields": [],
        "renamed_fields": {},
        "default_values": {
          "email": "",
          "metadata": {}
        }
      }
    },
    "order_placed": {
      "1->2": {
        "added_fields": ["currency"],
        "removed_fields": [],
        "renamed_fields": {},
        "default_values": {
          "currency": "USD"
        }
      },
      "2->3": {
        "added_fields": ["metadata"],
        "removed_fields": [],
        "renamed_fields": {
          "total": "amount_cents"
        },
        "default_values": {
          "metadata": {}
        }
      }
    }
  }
}
```

---

## Cross-References

### Related ADRs

- [ADR-001: Data Processing Engine Architecture](ADR-001-processing-engine.md) -- Foundation for the processing engine
- [ADR-002: Streaming vs Batch Processing Strategy](ADR-002-streaming-strategy.md) -- Processing model selection

### Related Research

- [Data Processing SOTA](../research/DATA_PROCESSING_SOTA.md) -- Schema evolution technology analysis
- [DataKit Specification](../SPEC.md) -- Complete system specification

### External References

- [Schema Evolution in Avro, Protocol Buffers and Thrift](https://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html) -- Martin Kleppmann
- [Semantic Versioning](https://semver.org/) -- Version numbering standard
- [JSON Schema](https://json-schema.org/) -- Schema definition standard
- [Serde Attributes](https://serde.rs/attributes.html) -- Rust serialization customization
- [Designing Data-Intensive Applications](https://dataintensive.net/) -- Chapter 4: Encoding and Evolution

### Phenotype Ecosystem

- [PhenoSpecs](https://github.com/KooshaPari/PhenoSpecs) -- Specifications and ADRs
- [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) -- Patterns and guidelines
- [HexaKit](https://github.com/KooshaPari/HexaKit) -- Templates and scaffolding

---

*This ADR was proposed on 2026-04-03 by the Phenotype Architecture Team. Awaiting review and acceptance.*
