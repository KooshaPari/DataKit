"""
Tests for pheno-caching package.
"""

import tempfile
import threading
import time
from pathlib import Path

import pytest
from pheno_caching import (
    CachedQueryMixin,
    DiskCache,
    DryRunContext,
    DryRunMixin,
    EmbeddingCache,
    QueryCache,
    dry_run_aware,
    dry_run_method,
    dry_run_skip,
    is_dry_run,
    set_dry_run,
)

try:
    from pheno_caching.cold.disk_cache import TestDataCache
except ImportError:
    TestDataCache = DiskCache  # type: ignore


class TestQueryCache:
    """Tests for QueryCache (hot cache)."""

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = QueryCache(ttl=30)

        cache.set("key1", {"data": "value"})
        result = cache.get("key1")

        assert result == {"data": "value"}

    def test_get_missing_key(self):
        """Test getting non-existent key."""
        cache = QueryCache()

        result = cache.get("nonexistent")

        assert result is None

    def test_generate_key_consistency(self):
        """Test that key generation is consistent regardless of param order."""
        cache = QueryCache()

        key1 = cache.generate_key("select", {"table": "users", "id": 123})
        key2 = cache.generate_key("select", {"id": 123, "table": "users"})

        assert key1 == key2

    def test_generate_key_different_params(self):
        """Test that different params generate different keys."""
        cache = QueryCache()

        key1 = cache.generate_key("select", {"table": "users", "id": 1})
        key2 = cache.generate_key("select", {"table": "users", "id": 2})

        assert key1 != key2

    def test_generate_key_different_operations(self):
        """Test that different operations generate different keys."""
        cache = QueryCache()

        key1 = cache.generate_key("select", {"table": "users"})
        key2 = cache.generate_key("insert", {"table": "users"})

        assert key1 != key2

    def test_expiration(self):
        """Test that entries expire after TTL."""
        cache = QueryCache(ttl=0.1)  # 100ms TTL

        cache.set("key", "value")
        result1 = cache.get("key")
        assert result1 == "value"

        time.sleep(0.15)  # Wait for expiration

        result2 = cache.get("key")
        assert result2 is None

    def test_lru_eviction(self):
        """Test LRU eviction when max size is reached."""
        cache = QueryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add new entry - key2 should be evicted (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_invalidate(self):
        """Test invalidating specific key."""
        cache = QueryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.invalidate("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_invalidate_by_table(self):
        """Test invalidating all entries for a table."""
        cache = QueryCache()

        cache.set("key1", "value1", metadata={"table": "users"})
        cache.set("key2", "value2", metadata={"table": "orders"})
        cache.set("key3", "value3", metadata={"table": "users"})

        cache.invalidate_by_table("users")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None

    def test_invalidate_by_pattern(self):
        """Test invalidating by pattern."""
        cache = QueryCache()

        cache.set("user_1", "value1")
        cache.set("user_2", "value2")
        cache.set("order_1", "value3")

        cache.invalidate_by_pattern("user_")

        assert cache.get("user_1") is None
        assert cache.get("user_2") is None
        assert cache.get("order_1") == "value3"

    def test_clear(self):
        """Test clearing entire cache."""
        cache = QueryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self):
        """Test cache statistics."""
        cache = QueryCache()

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        cache = QueryCache(ttl=0.05)

        cache.set("key1", "value1")
        time.sleep(0.1)
        cache.set("key2", "value2")

        removed = cache.cleanup_expired()

        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_thread_safety(self):
        """Test thread-safe operations."""
        cache = QueryCache()
        errors = []

        def writer():
            for i in range(100):
                try:
                    cache.set(f"key_{threading.current_thread().name}_{i}", i)
                except Exception as e:
                    errors.append(e)

        def reader():
            for i in range(100):
                try:
                    cache.get(f"key_{threading.current_thread().name}_{i}")
                except Exception as e:
                    errors.append(e)

        threads = []
        for i in range(5):
            t1 = threading.Thread(target=writer, name=f"writer_{i}")
            t2 = threading.Thread(target=reader, name=f"reader_{i}")
            threads.extend([t1, t2])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestDiskCache:
    """Tests for DiskCache (cold cache)."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_set_and_get(self, temp_cache_dir):
        """Test basic set and get operations."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))

        cache.set("key1", {"data": "value"})
        result = cache.get("key1")

        assert result == {"data": "value"}

    def test_get_missing(self, temp_cache_dir):
        """Test getting non-existent key."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))

        result = cache.get("nonexistent")

        assert result is None

    def test_persistence_across_instances(self, temp_cache_dir):
        """Test that cache persists across cache instances."""
        cache1 = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))
        cache1.set("key1", {"persistent": True})

        # Create new cache instance pointing to same directory
        cache2 = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))
        result = cache2.get("key1")

        assert result == {"persistent": True}

    def test_invalidate(self, temp_cache_dir):
        """Test invalidating specific key."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.invalidate("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_clear(self, temp_cache_dir):
        """Test clearing entire cache."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self, temp_cache_dir):
        """Test cache statistics."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir))

        cache.set("key1", {"data": "x" * 100})
        cache.set("key2", {"data": "y" * 100})

        stats = cache.get_stats()

        assert stats["entries"] == 2
        assert stats["namespace"] == "test"
        assert stats["max_size_mb"] == 1000

    def test_expiration(self, temp_cache_dir):
        """Test TTL-based expiration."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir), ttl=0.1)

        cache.set("key1", "value1")

        result1 = cache.get("key1")
        assert result1 == "value1"

        time.sleep(0.15)

        result2 = cache.get("key1")
        assert result2 is None

    def test_cleanup_expired(self, temp_cache_dir):
        """Test cleanup of expired entries."""
        cache = DiskCache(namespace="test", cache_dir=str(temp_cache_dir), ttl=0.05)

        cache.set("key1", "value1")
        time.sleep(0.1)
        cache.set("key2", "value2")

        removed = cache.cleanup_expired()

        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestEmbeddingCache:
    """Tests for EmbeddingCache."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_set_and_get_embedding(self, temp_cache_dir):
        """Test setting and getting embeddings."""
        cache = EmbeddingCache(cache_dir=str(temp_cache_dir))

        embedding = [0.1, 0.2, 0.3, 0.4]
        cache.set_embedding(
            entity_id="doc_123",
            embedding=embedding,
            model="text-embedding-3-small",
            dimensions=768,
        )

        result = cache.get_embedding("doc_123")

        assert result is not None
        assert result["embedding"] == embedding
        assert result["model"] == "text-embedding-3-small"
        assert result["dimensions"] == 768


class TestDataCacheWrapper:
    """Tests for TestDataCache."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_set_and_get_uuid(self, temp_cache_dir):
        """Test setting and getting UUIDs."""
        cache = TestDataCache(cache_dir=str(temp_cache_dir))

        uuid = "550e8400-e29b-41d4-a716-446655440000"
        cache.set_uuid("test_user", uuid)

        result = cache.get_uuid("test_user")

        assert result == uuid

    def test_get_missing_uuid(self, temp_cache_dir):
        """Test getting non-existent UUID."""
        cache = TestDataCache(cache_dir=str(temp_cache_dir))

        result = cache.get_uuid("nonexistent")

        assert result is None


class TestDryRunDecorators:
    """Tests for dry-run decorators."""

    def setup_method(self):
        """Reset dry-run state before each test."""
        set_dry_run(False)

    def teardown_method(self):
        """Reset dry-run state after each test."""
        set_dry_run(False)

    def test_set_and_is_dry_run(self):
        """Test global dry-run state management."""
        assert is_dry_run() is False

        set_dry_run(True)
        assert is_dry_run() is True

        set_dry_run(False)
        assert is_dry_run() is False

    def test_dry_run_aware_sync_normal(self):
        """Test sync function executes normally when not in dry-run mode."""

        @dry_run_aware(operation_name="test_op", return_value="dry-run-result")
        def sync_func():
            return "actual-result"

        result = sync_func()

        assert result == "actual-result"

    def test_dry_run_aware_sync_dry_run(self):
        """Test sync function returns dry-run value in dry-run mode."""
        set_dry_run(True)

        @dry_run_aware(operation_name="test_op", return_value="dry-run-result")
        def sync_func():
            return "actual-result"

        result = sync_func()

        assert result == "dry-run-result"

    @pytest.mark.asyncio
    async def test_dry_run_aware_async_normal(self):
        """Test async function executes normally when not in dry-run mode."""

        @dry_run_aware(operation_name="test_op", return_value="dry-run-result")
        async def async_func():
            return "actual-result"

        result = await async_func()

        assert result == "actual-result"

    @pytest.mark.asyncio
    async def test_dry_run_aware_async_dry_run(self):
        """Test async function returns dry-run value in dry-run mode."""
        set_dry_run(True)

        @dry_run_aware(operation_name="test_op", return_value="dry-run-result")
        async def async_func():
            return "actual-result"

        result = await async_func()

        assert result == "dry-run-result"

    def test_dry_run_skip_sync_normal(self):
        """Test skip decorator in normal mode."""

        @dry_run_skip(operation_name="skip_op")
        def skip_func():
            return "executed"

        result = skip_func()

        assert result == "executed"

    def test_dry_run_skip_sync_dry_run(self):
        """Test skip decorator in dry-run mode returns None."""
        set_dry_run(True)

        @dry_run_skip(operation_name="skip_op")
        def skip_func():
            return "executed"

        result = skip_func()

        assert result is None

    @pytest.mark.asyncio
    async def test_dry_run_skip_async_dry_run(self):
        """Test skip decorator with async function in dry-run mode."""
        set_dry_run(True)

        @dry_run_skip(operation_name="skip_op", skip_return={"skipped": True})
        async def async_skip():
            return "executed"

        result = await async_skip()

        assert result == {"skipped": True}

    def test_dry_run_context(self):
        """Test DryRunContext context manager."""
        results = []

        def func():
            if is_dry_run():
                results.append("dry-run")
            else:
                results.append("normal")

        assert is_dry_run() is False
        func()
        assert results == ["normal"]

        with DryRunContext(enabled=True):
            func()

        assert results == ["normal", "dry-run"]

        # Should be restored after context
        func()
        assert results == ["normal", "dry-run", "normal"]


class TestDryRunMixin:
    """Tests for DryRunMixin."""

    def test_instance_dry_run_state(self):
        """Test instance-level dry-run state."""

        class MyService(DryRunMixin):
            pass

        service = MyService()
        service._init_dry_run(enabled=True)

        assert service.is_dry_run() is True

    def test_instance_dry_run_toggle(self):
        """Test toggling instance dry-run state."""

        class MyService(DryRunMixin):
            pass

        service = MyService()
        service._init_dry_run(enabled=False)

        assert service.is_dry_run() is False

        service.set_dry_run(True)
        assert service.is_dry_run() is True
    @pytest.mark.asyncio
    async def test_dry_run_method_decorator(self):
        """Test dry_run_method decorator."""

        class MyService(DryRunMixin):
            def __init__(self, dry_run=False):
                self._init_dry_run(enabled=dry_run)

            @dry_run_method(return_value={"status": "skipped"})
            async def process(self, data):
                return {"status": "processed", "data": data}

        # Normal mode
        service = MyService(dry_run=False)
        result = await service.process("test")

        assert result == {"status": "processed", "data": "test"}

        # Dry-run mode
        service_dry = MyService(dry_run=True)
        result_dry = await service_dry.process("test")

        assert result_dry == {"status": "skipped"}


class TestCachedQueryMixin:
    """Tests for CachedQueryMixin."""

    def test_init_cache(self):
        """Test cache initialization."""

        class MockAdapter(CachedQueryMixin):
            pass

        adapter = MockAdapter()
        adapter._init_cache(ttl=60, max_size=500)

        assert adapter._cache_enabled is True
        assert adapter._query_cache.ttl == 60
        assert adapter._query_cache.max_size == 500

    def test_cache_disabled(self):
        """Test that caching can be disabled."""

        class MockAdapter(CachedQueryMixin):
            pass

        adapter = MockAdapter()
        adapter._init_cache(enabled=False)

        assert adapter._cache_enabled is False
