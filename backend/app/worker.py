import os
from celery import Celery
from app.core.config import settings
from app.core.logger import configure_logger

# Configure logger
configure_logger(settings.ENVIRONMENT)

# Create Celery app
celery_app = Celery(
    "sales_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True)
def process_sales_data_task(self, file_path: str, job_id: str):
    """Celery task for processing sales data."""
    from app.services.csv_processor import CSVProcessor
    from app.services.file_storage import FileStorageService
    from app.services.job_manager import JobManager
    
    csv_processor = CSVProcessor()
    file_storage = FileStorageService()
    job_manager = JobManager()
    
    try:
        # Update job status
        job = job_manager.get_job(job_id)
        if job:
            job.start_processing()
        
        # Process file
        def file_chunk_generator():
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        
        result = csv_processor.process_csv_stream(file_chunk_generator())
        
        # Update progress
        if job:
            job.update_progress(result.valid_rows, result.total_rows)
        
        # Write results
        output_filename = file_storage.generate_output_filename(job_id)
        output_path = file_storage.get_output_path(output_filename)
        csv_processor.write_results_to_csv(result, output_path)
        
        # Update job
        if job:
            job.complete(output_filename)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        if job:
            job.fail(str(e))
        raise e
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


def start_celery_worker():
    """Start Celery worker."""
    celery_app.worker_main(['worker', '--loglevel=info'])