from typing import Dict, Optional
import threading

from app.models.sales_data import JobStatus
from app.core.logger import get_logger


class JobManager:
    """Manages processing job status and results."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._jobs: Dict[str, JobStatus] = {}
        self._lock = threading.Lock()
    
    def create_job(self, job_id: str) -> JobStatus:
        """Create a new processing job."""
        with self._lock:
            job = JobStatus(job_id)
            self._jobs[job_id] = job
            self.logger.info("Job created", job_id=job_id)
            return job
    
    def get_job(self, job_id: str) -> Optional[JobStatus]:
        """Get job by ID."""
        with self._lock:
            return self._jobs.get(job_id)
    
    def update_job_progress(self, job_id: str, processed: int, total: int) -> bool:
        """Update job progress."""
        job = self.get_job(job_id)
        if job:
            job.update_progress(processed, total)
            return True
        return False
    
    def complete_job(self, job_id: str, result_file: str) -> bool:
        """Mark job as completed."""
        job = self.get_job(job_id)
        if job:
            job.complete(result_file)
            self.logger.info("Job completed", job_id=job_id, result_file=result_file)
            return True
        return False
    
    def fail_job(self, job_id: str, error: str) -> bool:
        """Mark job as failed."""
        job = self.get_job(job_id)
        if job:
            job.fail(error)
            self.logger.error("Job failed", job_id=job_id, error=error)
            return True
        return False