import os
from celery import Celery
from app.core.config import settings
from app.core.logger import configure_logger, get_logger

# Configure logger
configure_logger(settings.ENVIRONMENT)
logger = get_logger(__name__)


def log_celery_environment_settings():
    """Log environment and key settings for Celery worker."""
    # Log environment information
    logger.info("=" * 60)
    logger.info(f"Starting Celery Worker")
    logger.info(f"Environment: {settings.ENVIRONMENT.upper()}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 60)
    
    # Log Redis configuration
    logger.info(" Redis Configuration:")
    logger.info(f"   Redis URL: {settings.REDIS_URL}")
    logger.info(f"   Celery Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"   Celery Backend: {settings.CELERY_RESULT_BACKEND}")
    
    # Log storage configuration
    logger.info(" Storage Configuration:")
    logger.info(f"   Upload Directory: {settings.UPLOAD_DIR}")
    logger.info(f"   Output Directory: {settings.OUTPUT_DIR}")
    
    logger.info("=" * 60)


# Log settings before creating Celery app
log_celery_environment_settings()

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
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Log available tasks
logger.info(" Registered Tasks:")
for task_name in celery_app.tasks.keys():
    if not task_name.startswith('celery.'):
        logger.info(f"   📝 {task_name}")


@celery_app.task(bind=True)
def process_sales_data_task(self, file_path: str, job_id: str):
    """Celery task for processing sales data."""
    from app.services.csv_processor import CSVProcessor
    from app.services.file_storage import FileStorageService
    from app.services.job_manager import JobManager
    
    logger.info(f" Starting task processing for job: {job_id}")
    
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
        
        logger.info(
            " Task completed successfully",
            job_id=job_id,
            total_rows=result.total_rows,
            valid_rows=result.valid_rows,
            processing_time=result.processing_time
        )
        
        return {
            "job_id": job_id,
            "status": "completed",
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        logger.error(f" Task failed for job {job_id}", error=str(e))
        if job:
            job.fail(str(e))
        raise e
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f" Cleaned up temporary file: {file_path}")


def start_celery_worker():
    """Start Celery worker."""
    logger.info(" Starting Celery worker...")
    celery_app.worker_main(['worker', '--loglevel=info'])