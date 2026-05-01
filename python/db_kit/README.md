# pheno-db-kit 🗄️

Universal database abstraction layer with RLS support, multi-tenancy, connection pooling, and a clean async API.

## Features

### Core Database Abstractions
- **🔌 Pluggable Adapters**: Supabase, PostgreSQL, Neon (serverless), Turso (edge SQLite)
- **🔐 Row-Level Security (RLS)**: Automatic JWT context for secure queries
- **🏢 Multi-Tenancy**: Built-in tenant context manager with automatic filtering
- **⚡ Connection Pooling**: Async and sync connection pools with health monitoring
- **📊 Query Building**: Rich filtering with operators (eq, gt, like, in, etc.)
- **🎯 Type-Safe**: Full type hints with mypy support
- **🚀 Async-First**: Built on async/await for high performance

### Advanced Features
- **Migration Engine**: Schema migration management with Alembic integration
- **Realtime Subscriptions**: Live query updates via Supabase Realtime
- **Storage Abstractions**: Unified file storage interface
- **Vector/Embeddings Support**: pgvector integration for AI workloads
- **Tenant Isolation**: Row-level and schema-level tenancy patterns

## Platform Support

| Platform | Adapter | Features |
|----------|---------|----------|
| Supabase | `SupabaseAdapter` | Auth, RLS, Realtime, Storage |
| PostgreSQL | `PostgreSQLAdapter` | Direct async/sync connections |
| Neon | `NeonAdapter` | Serverless PostgreSQL, branching |
| Turso | `TursoAdapter` | Edge SQLite with replicas |

## Installation

```bash
# Basic installation (PostgreSQL adapters)
pip install pheno-db-kit

# With Supabase support
pip install "pheno-db-kit[supabase]"

# With Neon serverless support
pip install "pheno-db-kit[neon]"

# With Turso edge support
pip install "pheno-db-kit[turso]"

# All platforms
pip install "pheno-db-kit[all]"

# Development dependencies
pip install "pheno-db-kit[dev]"
```

## Quick Start

### Supabase

```python
from db_kit import Database

# Auto-configure from environment variables
# Requires: SUPABASE_URL, SUPABASE_KEY
db = Database.supabase()

# Set user token for RLS
db.set_access_token(user_jwt_token)

# Query with filters
users = await db.query(
    "users",
    filters={"active": True},
    order_by="created_at:desc",
    limit=10
)

# Insert
new_user = await db.insert("users", {
    "username": "johndoe",
    "email": "john@example.com"
})
```

### PostgreSQL Direct

```python
from db_kit import Database, PostgreSQLAdapter

# Create adapter
adapter = PostgreSQLAdapter(
    host="localhost",
    port=5432,
    database="myapp",
    user="postgres",
    password="secret"
)

# Or use connection string
adapter = PostgreSQLAdapter.from_dsn(
    "postgresql://postgres:secret@localhost:5432/myapp"
)

db = Database(adapter=adapter)

# Use the database
users = await db.query("users", filters={"active": True})
```

## Usage Examples

### 1. Connection Pooling

```python
from db_kit import ConnectionPoolManager, ConnectionPoolConfig

# Configure pool
config = ConnectionPoolConfig(
    min_connections=5,
    max_connections=20,
    max_idle_time=300,
    health_check_interval=30
)

# Get pool manager
manager = ConnectionPoolManager()

# Create provider-specific pool
pool = await manager.create_pool(
    provider="postgresql",
    host="localhost",
    database="myapp",
    config=config
)

# Use pooled connection
async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")

# Cleanup all pools on shutdown
from db_kit import cleanup_all_pools
await cleanup_all_pools()
```

### 2. Multi-Tenancy

```python
from db_kit import Database

db = Database.supabase()
db.set_access_token(jwt_token)

# Automatic tenant_id filtering
async with db.tenant_context("org_abc123") as tenant_db:
    # All queries automatically filter by tenant_id="org_abc123"
    users = await tenant_db.query("users", filters={"active": True})

    # Inserts automatically add tenant_id
    new_user = await tenant_db.insert("users", {
        "username": "bob",
        "email": "bob@example.com"
    })  # tenant_id is auto-added

    # Updates/deletes are scoped to tenant
    await tenant_db.update(
        "users",
        data={"role": "admin"},
        filters={"username": "bob"}
    )
```

### 3. Migrations

```python
from db_kit import MigrationEngine, Migration

# Initialize migration engine
engine = MigrationEngine(
    adapter=adapter,
    migration_directory="./migrations"
)

# Create a new migration
migration = await engine.create_migration(
    name="add_users_table",
    up="""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """,
    down="DROP TABLE users;"
)

# Run pending migrations
await engine.migrate()

# Get migration status
status = await engine.status()
for migration in status:
    print(f"{migration.name}: {migration.status}")

# Rollback last migration
await engine.rollback(steps=1)
```

### 4. Realtime Subscriptions

```python
from db_kit import Database, SupabaseRealtimeAdapter

db = Database.supabase()

# Subscribe to table changes
async def on_users_change(payload):
    print(f"Change type: {payload.event_type}")
    print(f"Record: {payload.record}")

# Start realtime subscription
realtime = SupabaseRealtimeAdapter(db.client)
await realtime.subscribe("users", on_users_change)

# Subscribe with filters
await realtime.subscribe(
    "users",
    on_users_change,
    filters={"event": "INSERT", "schema": "public"}
)

# Unsubscribe when done
await realtime.unsubscribe("users")
```

### 5. Storage Operations

```python
from db_kit import Database, SupabaseStorageAdapter

db = Database.supabase()

# Initialize storage adapter
storage = SupabaseStorageAdapter(db.client)

# Upload file
with open("document.pdf", "rb") as f:
    result = await storage.upload(
        bucket="documents",
        path="user123/document.pdf",
        file=f,
        content_type="application/pdf"
    )

# Download file
data = await storage.download(
    bucket="documents",
    path="user123/document.pdf"
)

# List files
files = await storage.list(
    bucket="documents",
    path="user123"
)

# Delete file
await storage.delete(
    bucket="documents",
    path="user123/document.pdf"
)
```

### 6. Advanced Filtering

```python
from db_kit import Database

db = Database.supabase()

# Simple equality
users = await db.query("users", filters={"active": True})

# Comparison operators
users = await db.query("users", filters={
    "age": {"gte": 18},           # age >= 18
    "score": {"gt": 100},         # score > 100
    "created_at": {"lt": "2024-01-01"}
})

# Pattern matching
users = await db.query("users", filters={
    "username": {"like": "%john%"},      # SQL LIKE
    "email": {"ilike": "%@GMAIL.COM"}  # Case-insensitive LIKE
})

# List operators
users = await db.query("users", filters={
    "role": {"in": ["admin", "moderator"]},
    "status": {"not_in": ["banned", "suspended"]}
})

# Null checks
users = await db.query("users", filters={
    "deleted_at": None,           # IS NULL
    "confirmed_at": {"not": None}  # IS NOT NULL
})

# Combined filters
users = await db.query("users", filters={
    "active": True,
    "age": {"gte": 18, "lte": 65},
    "role": {"in": ["admin", "user"]},
    "email": {"like": "%@company.com"}
})
```

### 7. Vector Search (pgvector)

```python
from db_kit import Database, VectorAdapter

db = Database.supabase()

# Initialize vector adapter
vectors = VectorAdapter(db.client)

# Store embedding
await vectors.insert(
    table="documents",
    id="doc-123",
    embedding=[0.1, 0.2, 0.3, ...],  # 1536-dim vector
    metadata={"title": "Document Title"}
)

# Similarity search
results = await vectors.similarity_search(
    table="documents",
    query_embedding=[0.1, 0.2, 0.3, ...],
    limit=10,
    threshold=0.8  # cosine similarity threshold
)

# Hybrid search (vector + keyword)
results = await vectors.hybrid_search(
    table="documents",
    query="machine learning",
    query_embedding=[0.1, 0.2, ...],
    keyword_weight=0.3,
    semantic_weight=0.7
)
```

### 8. Custom Adapter

```python
from db_kit import DatabaseAdapter
from typing import Any, Dict, List, Optional, Union

class CustomAdapter(DatabaseAdapter):
    """Custom database adapter implementation."""

    def __init__(self, config: dict):
        self.config = config
        self._pool = None

    async def connect(self):
        """Establish connection."""
        pass

    async def disconnect(self):
        """Close connection."""
        pass

    async def query(
        self,
        table: str,
        *,
        select: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Execute query."""
        # Implementation
        pass

    async def insert(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        *,
        returning: Optional[str] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Insert records."""
        pass

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
        *,
        returning: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Update records."""
        pass

    async def delete(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete records."""
        pass

    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records."""
        pass

    def set_access_token(self, token: str) -> None:
        """Set access token for RLS."""
        self.access_token = token

# Use custom adapter
from db_kit import Database
db = Database(adapter=CustomAdapter(config={"host": "localhost"}))
```

## API Reference

### Database Class

#### Factory Methods

| Method | Description |
|--------|-------------|
| `Database.supabase()` | Create Supabase client from env vars |
| `Database.postgresql()` | Create PostgreSQL direct connection |
| `Database.neon()` | Create Neon serverless connection |
| `Database(adapter=...)` | Use custom adapter |

#### Core Methods

| Method | Description |
|--------|-------------|
| `set_access_token(token)` | Set JWT for RLS context |
| `query(table, ...)` | Query records with filters |
| `get_single(table, ...)` | Get single record |
| `insert(table, data, ...)` | Insert record(s) |
| `update(table, data, ...)` | Update records |
| `delete(table, ...)` | Delete records |
| `count(table, ...)` | Count records |
| `transaction()` | Transaction context manager |
| `tenant_context(tenant_id)` | Multi-tenancy context |

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| Direct value | Equality | `{"age": 25}` |
| `{"eq": val}` | Equals | `{"age": {"eq": 25}}` |
| `{"neq": val}` | Not equals | `{"status": {"neq": "deleted"}}` |
| `{"gt": val}` | Greater than | `{"age": {"gt": 18}}` |
| `{"gte": val}` | Greater than or equal | `{"age": {"gte": 18}}` |
| `{"lt": val}` | Less than | `{"age": {"lt": 65}}` |
| `{"lte": val}` | Less than or equal | `{"age": {"lte": 65}}` |
| `{"like": val}` | LIKE pattern | `{"name": {"like": "%john%"}}` |
| `{"ilike": val}` | Case-insensitive LIKE | `{"email": {"ilike": "%@GMAIL.COM"}}` |
| `{"in": list}` | IN list | `{"role": {"in": ["admin", "mod"]}}` |
| `{"not_in": list}` | NOT IN list | `{"status": {"not_in": ["banned"]}}` |
| `{"not": None}` | IS NOT NULL | `{"deleted_at": {"not": None}}` |
| `None` | IS NULL | `{"deleted_at": None}` |

## Configuration

### Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `SUPABASE_URL` | Supabase | Project URL |
| `SUPABASE_KEY` | Supabase | Anon/service key |
| `DATABASE_URL` | PostgreSQL | Connection string |
| `NEON_CONNECTION_STRING` | Neon | Serverless connection |
| `TURSO_DATABASE_URL` | Turso | LibSQL connection |

### Connection Pool Configuration

```python
from db_kit import ConnectionPoolConfig

config = ConnectionPoolConfig(
    min_connections=5,          # Minimum connections in pool
    max_connections=20,         # Maximum connections
    connection_timeout=30,      # Connection timeout (seconds)
    max_idle_time=300,         # Max idle time before cleanup
    health_check_interval=30,  # Health check frequency
    retry_attempts=3,          # Retry failed connections
    retry_delay=1.0           # Delay between retries
)
```

## Architecture

```
pheno-db-kit/
├── adapters/           # Database adapters
│   ├── base.py        # Abstract adapter interface
│   ├── supabase.py    # Supabase adapter
│   ├── postgres.py    # PostgreSQL adapter
│   └── neon.py        # Neon adapter
├── core/              # Core engine and client
│   ├── engine.py      # Query execution engine
│   └── __init__.py
├── pooling/           # Connection pooling
│   ├── pool_manager.py    # Pool lifecycle management
│   └── connection_pool.py # Async/sync pools
├── migrations/        # Schema migrations
│   ├── engine.py     # Migration runner
│   └── migration.py  # Migration models
├── tenancy/          # Multi-tenancy
│   └── __init__.py   # Tenant context managers
├── realtime/         # Realtime subscriptions
│   ├── base.py       # Abstract realtime interface
│   └── supabase.py   # Supabase realtime
├── storage/          # File storage
│   ├── base.py       # Storage interface
│   └── supabase.py   # Supabase storage
├── vector/           # Vector embeddings
│   └── __init__.py   # Vector search adapters
├── rls/              # Row-level security
│   └── __init__.py   # RLS context managers
├── query/            # Query building (WIP)
│   └── __init__.py
├── platforms/        # Platform-specific clients
│   ├── supabase/
│   ├── neon/
│   └── turso/
├── client.py         # Main Database client
└── supabase_client.py # Supabase utilities
```

## Row-Level Security (RLS)

DB-Kit integrates seamlessly with PostgreSQL RLS policies:

```sql
-- Example RLS policy
CREATE POLICY "Users can only see their own data"
ON users
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can only update their own data"
ON users
FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

```python
# Set user JWT - RLS automatically enforces policies
db.set_access_token(user_jwt_token)

# This query respects RLS - only returns user's own records
my_data = await db.query("users")

# Inserts automatically use RLS
db.set_access_token(admin_jwt_token)
# Now queries run with admin privileges
```

## Performance Best Practices

1. **Use Connection Pooling**: Reduces connection overhead
2. **Enable RLS**: Automatic security without code changes
3. **Tenant Context**: Reduces code duplication and errors
4. **Batch Operations**: Insert multiple records at once
5. **Selective Columns**: Use `select="id,name"` instead of `"*"`
6. **Pagination**: Always paginate large result sets
7. **Caching**: Enable query caching for read-heavy workloads
8. **Proper Indexing**: Ensure database indexes match query patterns

## Error Handling

```python
from db_kit import Database, DatabaseError, ConnectionError, QueryError

db = Database.supabase()

try:
    users = await db.query("users")
except ConnectionError as e:
    # Handle connection failures
    logger.error(f"Database connection failed: {e}")
except QueryError as e:
    # Handle query errors
    logger.error(f"Query failed: {e}")
except DatabaseError as e:
    # Handle general database errors
    logger.error(f"Database error: {e}")
```

## Type Safety

```python
from db_kit import Database
from pydantic import BaseModel

class User(BaseModel):
    id: str
    email: str
    name: str

db = Database.supabase()

# Type-safe query results
users: list[User] = await db.query("users", model=User)

# Single record with type
user: User | None = await db.get_single("users", filters={"id": "123"}, model=User)
```

## Development

```bash
# Clone repository
git clone https://github.com/phenotype/db-kit.git
cd db-kit

# Install with dev dependencies
pip install -e ".[dev,all]"

# Run tests
pytest

# Run linting
ruff check .
mypy src/

# Format code
ruff format .
```

## License

MIT License - see LICENSE file for details

## Credits

Extracted from the Phenotype SDK project and generalized for standalone use.
