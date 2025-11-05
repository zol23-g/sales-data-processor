import pytest
import os
import aiofiles
from unittest.mock import patch, AsyncMock
from app.services.file_storage import FileStorageService
from app.core.config import settings


class TestFileStorageService:
    
    @pytest.fixture
    def storage_service(self):
        return FileStorageService()
    
    @pytest.fixture
    def test_data(self):
        return b"test file content"
    
    @pytest.fixture
    def test_filename(self):
        return "test_file.txt"
    
    def test_ensure_directories(self, storage_service):
        """Test that required directories are created."""
        # Remove directories if they exist
        if os.path.exists(settings.UPLOAD_DIR):
            os.rmdir(settings.UPLOAD_DIR)
        if os.path.exists(settings.OUTPUT_DIR):
            os.rmdir(settings.OUTPUT_DIR)
        
        # Call ensure_directories
        storage_service.ensure_directories()
        
        # Verify directories exist
        assert os.path.exists(settings.UPLOAD_DIR)
        assert os.path.exists(settings.OUTPUT_DIR)
    
    def test_generate_output_filename(self, storage_service):
        """Test output filename generation."""
        job_id = "test-job-123"
        filename = storage_service.generate_output_filename(job_id)
        
        assert filename.startswith("results_")
        assert job_id in filename
        assert filename.endswith(".csv")
    
    def test_get_output_path(self, storage_service):
        """Test output path generation."""
        filename = "test_file.csv"
        expected_path = os.path.join(settings.OUTPUT_DIR, filename)
        
        actual_path = storage_service.get_output_path(filename)
        
        assert actual_path == expected_path
    
    def test_get_download_url(self, storage_service):
        """Test download URL generation."""
        filename = "results_test.csv"
        expected_url = f"/api/download/{filename}"
        
        actual_url = storage_service.get_download_url(filename)
        
        assert actual_url == expected_url
    
    def test_file_exists(self, storage_service, tmp_path):
        """Test file existence check."""
        # Create a test file
        test_file = tmp_path / "test_exist.txt"
        test_file.write_text("test content")
        
        # Test with existing file
        assert storage_service.file_exists(str(test_file.name)) is False  # Not in output dir
        
        # Test with non-existent file
        assert storage_service.file_exists("non_existent_file.csv") is False
    
    @pytest.mark.asyncio
    async def test_save_upload_chunk(self, storage_service, test_data, test_filename):
        """Test saving upload chunks."""
        file_path = await storage_service.save_upload_chunk(test_data, test_filename)
        
        # Verify file was created
        assert os.path.exists(file_path)
        
        # Verify file content
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        assert content == test_data
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
    
    @pytest.mark.asyncio
    async def test_save_upload_chunk_append(self, storage_service, test_data, test_filename):
        """Test appending to existing file."""
        # Save first chunk
        file_path = await storage_service.save_upload_chunk(b"first ", test_filename)
        
        # Save second chunk (should append)
        await storage_service.save_upload_chunk(b"second", test_filename)
        
        # Verify combined content
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        assert content == b"first second"
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
    
    @pytest.mark.asyncio
    async def test_read_file_chunks(self, storage_service, tmp_path):
        """Test reading file in chunks."""
        # Create test file
        test_content = b"a" * 5000 + b"b" * 5000  # 10KB content
        test_file = tmp_path / "chunk_test.txt"
        test_file.write_bytes(test_content)
        
        # Read in chunks
        chunks = []
        async for chunk in storage_service.read_file_chunks(str(test_file), chunk_size=2000):
            chunks.append(chunk)
        
        # Verify all content was read
        combined = b"".join(chunks)
        assert combined == test_content
        
        # Verify chunk sizes (except possibly last chunk)
        for chunk in chunks[:-1]:
            assert len(chunk) == 2000
    
    @pytest.mark.asyncio
    async def test_read_file_chunks_empty(self, storage_service, tmp_path):
        """Test reading empty file."""
        # Create empty file
        test_file = tmp_path / "empty_test.txt"
        test_file.write_bytes(b"")
        
        # Read chunks
        chunks = []
        async for chunk in storage_service.read_file_chunks(str(test_file)):
            chunks.append(chunk)
        
        # Should get no chunks
        assert len(chunks) == 0
    
    def test_initialization_creates_directories(self):
        """Test that directories are created on service initialization."""
        # Remove directories if they exist
        if os.path.exists(settings.UPLOAD_DIR):
            os.rmdir(settings.UPLOAD_DIR)
        if os.path.exists(settings.OUTPUT_DIR):
            os.rmdir(settings.OUTPUT_DIR)
        
        # Create new service instance
        service = FileStorageService()
        
        # Verify directories were created
        assert os.path.exists(settings.UPLOAD_DIR)
        assert os.path.exists(settings.OUTPUT_DIR)