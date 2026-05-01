"""
Tests for db_kit (pheno-database) package.
"""

import pytest
from db_kit.adapters.base import DatabaseAdapter


class MockDatabaseAdapter(DatabaseAdapter):
    """Mock database adapter for testing."""

    def __init__(self):
        self._data = {}

    async def query(
        self,
        table: str,
        *,
        select: str | None = None,
        filters: dict | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict]:
        """Execute SELECT query."""
        results = self._data.get(table, [])
        if filters:
            results = [r for r in results if all(r.get(k) == v for k, v in filters.items())]
        if order_by:
            field, direction = order_by.split(":") if ":" in order_by else (order_by, "asc")
            results = sorted(results, key=lambda x: x.get(field, ""), reverse=(direction == "desc"))
        if offset:
            results = results[offset:]
        if limit:
            results = results[:limit]
        return results

    async def get_single(
        self, table: str, filters: dict, *, select: str | None = None,
    ) -> dict | None:
        """Get single row."""
        results = await self.query(table, filters=filters, limit=1)
        return results[0] if results else None

    async def insert(
        self,
        table: str,
        data: dict | list[dict],
        *,
        returning: str | None = None,
    ) -> dict | list[dict]:
        """Insert row(s)."""
        if not isinstance(data, list):
            data = [data]

        ids = []
        for row in data:
            row_id = len(self._data.get(table, [])) + 1
            row_with_id = {"id": row_id, **row}
            if table not in self._data:
                self._data[table] = []
            self._data[table].append(row_with_id)
            ids.append(row_with_id)

        if returning:
            return ids
        return ids[0] if len(ids) == 1 else ids

    async def update(
        self,
        table: str,
        filters: dict,
        data: dict,
        *,
        returning: str | None = None,
    ) -> list[dict]:
        """Update rows."""
        updated = []
        for row in self._data.get(table, []):
            if all(row.get(k) == v for k, v in filters.items()):
                row.update(data)
                updated.append(row)
        return updated

    async def delete(
        self, table: str, filters: dict, *, returning: str | None = None,
    ) -> list[dict]:
        """Delete rows."""
        deleted = []
        if table in self._data:
            to_delete = [i for i, row in enumerate(self._data[table])
                        if all(row.get(k) == v for k, v in filters.items())]
            for i in reversed(to_delete):
                deleted.append(self._data[table].pop(i))
        return deleted

    async def upsert(
        self,
        table: str,
        data: dict | list[dict],
        *,
        conflict_columns: list[str] | None = None,
        returning: str | None = None,
    ) -> dict | list[dict]:
        """Insert or update rows."""
        if not isinstance(data, list):
            data = [data]

        results = []
        for row in data:
            existing = await self.get_single(table, {c: row[c] for c in (conflict_columns or ["id"])})
            if existing:
                updated = await self.update(table, {"id": existing["id"]}, row, returning=returning)
                results.extend(updated)
            else:
                inserted = await self.insert(table, row, returning=returning)
                results.append(inserted if isinstance(inserted, dict) else inserted[0])

        return results[0] if len(results) == 1 else results

    async def execute(self, sql: str, params: list | dict | None = None) -> any:
        """Execute raw SQL."""
        return {"sql": sql, "params": params}

    async def count(self, table: str, filters: dict | None = None) -> int:
        """Count rows."""
        results = await self.query(table, filters=filters)
        return len(results)


class TestDatabaseAdapter:
    """Tests for DatabaseAdapter base class."""

    def test_adapter_is_abstract(self):
        """Test that DatabaseAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DatabaseAdapter()


class TestMockDatabaseAdapter:
    """Tests for MockDatabaseAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return MockDatabaseAdapter()

    @pytest.mark.asyncio
    async def test_insert_single(self, adapter):
        """Test inserting single row."""
        result = await adapter.insert("users", {"name": "Alice", "email": "alice@example.com"})

        assert result["name"] == "Alice"
        assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_insert_multiple(self, adapter):
        """Test inserting multiple rows."""
        result = await adapter.insert(
            "users",
            [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ],
        )

        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_query_all(self, adapter):
        """Test querying all rows."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Bob"})

        results = await adapter.query("users")

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_query_with_filters(self, adapter):
        """Test querying with filters."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Bob"})

        results = await adapter.query("users", filters={"name": "Alice"})

        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_query_with_limit(self, adapter):
        """Test querying with limit."""
        for i in range(10):
            await adapter.insert("users", {"name": f"User{i}"})

        results = await adapter.query("users", limit=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_offset(self, adapter):
        """Test querying with offset."""
        for i in range(10):
            await adapter.insert("users", {"name": f"User{i}"})

        results = await adapter.query("users", limit=5, offset=5)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_query_with_order_by(self, adapter):
        """Test querying with order_by."""
        await adapter.insert("users", {"name": "Charlie", "age": 30})
        await adapter.insert("users", {"name": "Alice", "age": 25})
        await adapter.insert("users", {"name": "Bob", "age": 35})

        results = await adapter.query("users", order_by="age:desc")

        assert results[0]["name"] == "Bob"
        assert results[1]["name"] == "Charlie"
        assert results[2]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_get_single(self, adapter):
        """Test getting single row."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Bob"})

        result = await adapter.get_single("users", {"name": "Alice"})

        assert result is not None
        assert result["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_get_single_not_found(self, adapter):
        """Test getting non-existent single row."""
        result = await adapter.get_single("users", {"name": "Nonexistent"})

        assert result is None

    @pytest.mark.asyncio
    async def test_update(self, adapter):
        """Test updating rows."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Alice"})

        updated = await adapter.update("users", {"name": "Alice"}, {"name": "Alicia"})

        assert len(updated) == 2
        assert all(row["name"] == "Alicia" for row in updated)

    @pytest.mark.asyncio
    async def test_delete(self, adapter):
        """Test deleting rows."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Bob"})

        deleted = await adapter.delete("users", {"name": "Alice"})

        assert len(deleted) == 1

        remaining = await adapter.query("users")
        assert len(remaining) == 1
        assert remaining[0]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_upsert_insert(self, adapter):
        """Test upsert when row doesn't exist (insert)."""
        result = await adapter.upsert(
            "users",
            {"id": 1, "name": "Alice"},
            conflict_columns=["id"],
        )

        assert result["name"] == "Alice"
        assert result["id"] == 1

    @pytest.mark.asyncio
    async def test_upsert_update(self, adapter):
        """Test upsert when row exists (update)."""
        await adapter.insert("users", {"id": 1, "name": "Alice"})

        result = await adapter.upsert(
            "users",
            {"id": 1, "name": "Alicia"},
            conflict_columns=["id"],
        )

        assert result["name"] == "Alicia"

        # Verify only one row exists
        all_rows = await adapter.query("users")
        assert len(all_rows) == 1

    @pytest.mark.asyncio
    async def test_count(self, adapter):
        """Test counting rows."""
        await adapter.insert("users", {"name": "Alice"})
        await adapter.insert("users", {"name": "Bob"})

        count = await adapter.count("users")

        assert count == 2

    @pytest.mark.asyncio
    async def test_count_with_filters(self, adapter):
        """Test counting with filters."""
        await adapter.insert("users", {"name": "Alice", "active": True})
        await adapter.insert("users", {"name": "Bob", "active": False})
        await adapter.insert("users", {"name": "Charlie", "active": True})

        count = await adapter.count("users", {"active": True})

        assert count == 2

    @pytest.mark.asyncio
    async def test_execute(self, adapter):
        """Test executing raw SQL."""
        result = await adapter.execute("SELECT * FROM users WHERE id = $1", [1])

        assert result["sql"] == "SELECT * FROM users WHERE id = $1"
        assert result["params"] == [1]
