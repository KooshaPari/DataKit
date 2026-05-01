"""
Tests for pheno-storage package.
"""

import pytest
from pheno_storage import StorageClient, StorageProvider
from pheno_storage.core.file import StoredFile


class MockStorageProvider(StorageProvider):
    """Mock storage provider for testing."""

    def __init__(self):
        self._files = {}

    async def upload(
        self,
        path: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict | None = None,
    ) -> StoredFile:
        """Upload file."""
        self._files[path] = {
            "data": data,
            "content_type": content_type,
            "metadata": metadata or {},
        }
        return StoredFile(
            path=path,
            size=len(data),
            content_type=content_type,
            metadata=metadata,
        )

    async def download(self, path: str) -> bytes:
        """Download file."""
        if path not in self._files:
            raise FileNotFoundError(f"File not found: {path}")
        return self._files[path]["data"]

    async def delete(self, path: str):
        """Delete file."""
        if path in self._files:
            del self._files[path]

    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        return path in self._files

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get presigned URL."""
        return f"https://mock-storage.example.com/{path}?token=abc123"


class TestStoredFile:
    """Tests for StoredFile dataclass."""

    def test_stored_file_creation(self):
        """Test basic StoredFile creation."""
        file = StoredFile(
            path="test/file.txt",
            size=1024,
            content_type="text/plain",
        )

        assert file.path == "test/file.txt"
        assert file.size == 1024
        assert file.content_type == "text/plain"
        assert file.metadata is None  # Defaults to None, not {}

    def test_stored_file_with_metadata(self):
        """Test StoredFile with metadata."""
        metadata = {"author": "test", "version": 1}
        file = StoredFile(
            path="test/file.txt",
            size=1024,
            content_type="text/plain",
            metadata=metadata,
        )

        assert file.metadata == metadata

    def test_stored_file_etag(self):
        """Test StoredFile with etag."""
        file = StoredFile(
            path="test/file.txt",
            size=1024,
            content_type="text/plain",  # Required argument
            etag="abc123",
        )

        assert file.etag == "abc123"


class TestStorageProvider:
    """Tests for StorageProvider base class."""

    def test_provider_is_abstract(self):
        """Test that StorageProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StorageProvider()


class TestStorageClient:
    """Tests for StorageClient."""

    @pytest.fixture
    def client(self):
        """Create StorageClient with mock provider."""
        return StorageClient(MockStorageProvider())

    @pytest.mark.asyncio
    async def test_upload(self, client):
        """Test file upload."""
        data = b"Hello, World!"
        file = await client.upload("test/file.txt", data)

        assert file.path == "test/file.txt"
        assert file.size == len(data)

    @pytest.mark.asyncio
    async def test_upload_with_metadata(self, client):
        """Test upload with metadata."""
        metadata = {"author": "test"}
        file = await client.upload(
            "test/file.txt",
            b"content",
            metadata=metadata,
        )

        assert file.metadata == metadata

    @pytest.mark.asyncio
    async def test_download(self, client):
        """Test file download."""
        data = b"Test content for download"
        await client.upload("test/file.txt", data)

        downloaded = await client.download("test/file.txt")

        assert downloaded == data

    @pytest.mark.asyncio
    async def test_download_missing_file(self, client):
        """Test downloading non-existent file."""
        with pytest.raises(FileNotFoundError):
            await client.download("nonexistent/file.txt")

    @pytest.mark.asyncio
    async def test_delete(self, client):
        """Test file deletion."""
        await client.upload("test/file.txt", b"content")

        assert await client.exists("test/file.txt") is True

        await client.delete("test/file.txt")

        assert await client.exists("test/file.txt") is False

    @pytest.mark.asyncio
    async def test_exists(self, client):
        """Test file existence check."""
        assert await client.exists("test/file.txt") is False

        await client.upload("test/file.txt", b"content")

        assert await client.exists("test/file.txt") is True

    @pytest.mark.asyncio
    async def test_get_url(self, client):
        """Test getting presigned URL."""
        await client.upload("test/file.txt", b"content")

        url = await client.get_url("test/file.txt")

        assert "test/file.txt" in url
        assert "token=" in url

    @pytest.mark.asyncio
    async def test_get_url_custom_expiry(self, client):
        """Test getting URL with custom expiration."""
        await client.upload("test/file.txt", b"content")

        url = await client.get_url("test/file.txt", expires_in=7200)

        assert url is not None
