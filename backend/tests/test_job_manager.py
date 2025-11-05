import pytest
import time
from app.services.job_manager import JobManager
from app.models.sales_data import JobStatus


class TestJobManager:
    
    @pytest.fixture
    def job_manager(self):
        return JobManager()
    
    @pytest.fixture
    def sample_job_id(self):
        return "test-job-123"
    
    def test_create_job(self, job_manager, sample_job_id):
        """Test job creation."""
        job = job_manager.create_job(sample_job_id)
        
        assert job is not None
        assert job.job_id == sample_job_id
        assert job.status == JobStatus.PENDING
        assert job_manager.get_job(sample_job_id) == job
    
    def test_get_job_exists(self, job_manager, sample_job_id):
        """Test retrieving existing job."""
        created_job = job_manager.create_job(sample_job_id)
        retrieved_job = job_manager.get_job(sample_job_id)
        
        assert retrieved_job == created_job
    
    def test_get_job_not_exists(self, job_manager):
        """Test retrieving non-existent job."""
        job = job_manager.get_job("non-existent-job")
        
        assert job is None
    
    def test_update_job_progress(self, job_manager, sample_job_id):
        """Test updating job progress."""
        job = job_manager.create_job(sample_job_id)
        job.start_processing()
        
        success = job_manager.update_job_progress(sample_job_id, 50, 100)
        
        assert success is True
        assert job.progress == 50
        assert job.processed_rows == 50
        assert job.total_rows == 100
    
    def test_update_job_progress_invalid_job(self, job_manager):
        """Test updating progress for non-existent job."""
        success = job_manager.update_job_progress("invalid-job", 50, 100)
        
        assert success is False
    
    def test_complete_job(self, job_manager, sample_job_id):
        """Test completing a job."""
        job = job_manager.create_job(sample_job_id)
        job.start_processing()
        
        result_file = "results_test.csv"
        success = job_manager.complete_job(sample_job_id, result_file)
        
        assert success is True
        assert job.status == JobStatus.COMPLETED
        assert job.result_file == result_file
        assert job.progress == 100
        assert job.end_time is not None
    
    def test_complete_job_invalid(self, job_manager):
        """Test completing non-existent job."""
        success = job_manager.complete_job("invalid-job", "results.csv")
        
        assert success is False
    
    def test_fail_job(self, job_manager, sample_job_id):
        """Test failing a job."""
        job = job_manager.create_job(sample_job_id)
        job.start_processing()
        
        error_message = "Test error occurred"
        success = job_manager.fail_job(sample_job_id, error_message)
        
        assert success is True
        assert job.status == JobStatus.FAILED
        assert job.error == error_message
        assert job.end_time is not None
    
    def test_fail_job_invalid(self, job_manager):
        """Test failing non-existent job."""
        success = job_manager.fail_job("invalid-job", "Error message")
        
        assert success is False
    
    def test_job_lifecycle(self, job_manager, sample_job_id):
        """Test complete job lifecycle."""
        # Create job
        job = job_manager.create_job(sample_job_id)
        assert job.status == JobStatus.PENDING
        
        # Start processing
        job.start_processing()
        assert job.status == JobStatus.PROCESSING
        assert job.start_time is not None
        
        # Update progress
        job_manager.update_job_progress(sample_job_id, 25, 100)
        assert job.progress == 25
        
        # Complete job
        job_manager.complete_job(sample_job_id, "results.csv")
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 100
        assert job.end_time is not None
    
    def test_multiple_jobs(self, job_manager):
        """Test managing multiple jobs simultaneously."""
        job_ids = ["job1", "job2", "job3"]
        jobs = []
        
        # Create multiple jobs
        for job_id in job_ids:
            job = job_manager.create_job(job_id)
            jobs.append(job)
        
        # Verify all jobs exist
        for job_id, expected_job in zip(job_ids, jobs):
            retrieved_job = job_manager.get_job(job_id)
            assert retrieved_job == expected_job
        
        # Update progress for one job
        job_manager.update_job_progress("job2", 75, 100)
        job2 = job_manager.get_job("job2")
        assert job2.progress == 75
        
        # Complete one job
        job_manager.complete_job("job1", "results1.csv")
        job1 = job_manager.get_job("job1")
        assert job1.status == JobStatus.COMPLETED
        
        # Others should remain unchanged
        job3 = job_manager.get_job("job3")
        assert job3.status == JobStatus.PENDING
    
    def test_job_status_transitions(self, job_manager, sample_job_id):
        """Test valid job status transitions."""
        job = job_manager.create_job(sample_job_id)
        
        # PENDING -> PROCESSING
        job.start_processing()
        assert job.status == JobStatus.PROCESSING
        
        # PROCESSING -> COMPLETED
        job.complete("results.csv")
        assert job.status == JobStatus.COMPLETED
        
        # Cannot transition from COMPLETED - create a new job to test this
        job2 = job_manager.create_job("test-job-456")
        job2.start_processing()
        job2.complete("results2.csv")
        
        # Try to restart completed job - should not change status
        original_status = job2.status
        job2.start_processing()
        assert job2.status == original_status  # Status should not change
            
    def test_job_timing(self, job_manager, sample_job_id):
        """Test job timing measurements."""
        job = job_manager.create_job(sample_job_id)
        
        # Start processing
        job.start_processing()
        assert job.start_time is not None
        start_time = job.start_time
        
        # Small delay
        time.sleep(0.01)
        
        # Complete job
        job.complete("results.csv")
        assert job.end_time is not None
        assert job.end_time > start_time