import os
import uuid
from typing import Optional
import aiofiles

from app.core.config import settings
from app.core.logger import get_logger


class FileStorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.ensure_directories()
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    def generate_output_filename(self, job_id: str) -> str:
        """Generate unique output filename."""
        return f"results_{job_id}.csv"
    
    def get_output_path(self, filename: str) -> str:
        """Get full output file path."""
        return os.path.join(settings.OUTPUT_DIR, filename)
    
    async def save_upload_chunk(self, chunk_data: bytes, filename: str) -> str:
        """Save uploaded chunk to temporary file."""
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        async with aiofiles.open(file_path, 'ab') as f:
            await f.write(chunk_data)
        
        return file_path
    
    def get_download_url(self, filename: str) -> str:
        """Generate download URL for result file."""
        return f"/api/download/{filename}"
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in output directory."""
        file_path = self.get_output_path(filename)
        return os.path.exists(file_path)
    
    async def read_file_chunks(self, file_path: str, chunk_size: int = 8192):
        """Read file in chunks for streaming."""
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk