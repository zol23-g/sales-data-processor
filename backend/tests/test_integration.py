import pytest
import os
import tempfile
from app.services.csv_processor import CSVProcessor
from app.services.file_storage import FileStorageService
from app.services.job_manager import JobManager


class TestIntegration:
    
    @pytest.fixture
    def services(self):
        return {
            'processor': CSVProcessor(),
            'storage': FileStorageService(),
            'job_manager': JobManager()
        }
    
    @pytest.fixture
    def sample_csv_content(self):
        return """Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200
Electronics,2023-08-02,150
Clothing,2023-08-02,50"""
    
    def test_complete_processing_flow(self, services, sample_csv_content):
        """Test complete file processing flow."""
        processor = services['processor']
        storage = services['storage']
        job_manager = services['job_manager']
        
        # Create job
        job_id = "integration-test-job"
        job = job_manager.create_job(job_id)
        job.start_processing()
        
        # Process CSV
        def chunk_generator():
            yield sample_csv_content.encode('utf-8')
        
        result = processor.process_csv_stream(chunk_generator())
        
        # Verify processing result
        assert result.valid_rows == 4
        assert len(result.departments) == 2
        assert result.departments["Electronics"].total_sales == 250
        
        # Write results to file
        output_filename = storage.generate_output_filename(job_id)
        output_path = storage.get_output_path(output_filename)
        processor.write_results_to_csv(result, output_path)
        
        # Verify file was created
        assert os.path.exists(output_path)
        
        # Complete job
        job_manager.complete_job(job_id, output_filename)
        
        # Verify job status
        completed_job = job_manager.get_job(job_id)
        assert completed_job.status == "completed"
        assert completed_job.result_file == output_filename
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
    
    def test_file_upload_and_process_flow(self, services):
        """Test file upload and processing integration."""
        processor = services['processor']
        storage = services['storage']
        job_manager = services['job_manager']
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("""Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200""")
            temp_file = f.name
        
        try:
            # Simulate file upload by reading chunks
            def file_chunk_generator():
                with open(temp_file, 'rb') as file:
                    while True:
                        chunk = file.read(1024)
                        if not chunk:
                            break
                        yield chunk
            
            # Create and start job
            job_id = "upload-test-job"
            job = job_manager.create_job(job_id)
            job.start_processing()
            
            # Process the file
            result = processor.process_csv_stream(file_chunk_generator())
            
            # Verify processing
            assert result.valid_rows == 2
            assert result.departments["Electronics"].total_sales == 100
            
            # Write results
            output_filename = storage.generate_output_filename(job_id)
            output_path = storage.get_output_path(output_filename)
            processor.write_results_to_csv(result, output_path)
            
            # Complete job
            job_manager.complete_job(job_id, output_filename)
            
            # Verify download URL
            download_url = storage.get_download_url(output_filename)
            assert download_url == f"/api/download/{output_filename}"
            
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)
                
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)