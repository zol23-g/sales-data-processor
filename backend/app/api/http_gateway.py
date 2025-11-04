from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import uuid

from app.core.config import settings
from app.core.logger import get_logger, configure_logger
from app.services.csv_processor import CSVProcessor
from app.services.file_storage import FileStorageService
from app.services.job_manager import JobManager

# Configure logger
configure_logger(settings.ENVIRONMENT)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
csv_processor = CSVProcessor()
file_storage = FileStorageService()
job_manager = JobManager()


@app.get("/")
async def root():
    return {"message": "Sales Data Processor API", "version": settings.APP_VERSION}


@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """HTTP endpoint for file upload with background processing."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    job_id = str(uuid.uuid4())
    logger.info("File upload received", job_id=job_id, filename=file.filename)
    
    # Create job
    job = job_manager.create_job(job_id)
    job.start_processing()
    
    # Process in background
    background_tasks.add_task(
        process_uploaded_file,
        file,
        job_id
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "File uploaded and processing started"
    }


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    download_url = ""
    if job.result_file:
        download_url = file_storage.get_download_url(job.result_file)
    
    return {
        "job_id": job_id,
        "status": job.status,
        "message": job.message,
        "progress": job.progress,
        "download_url": download_url
    }


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download processed result file."""
    file_path = file_storage.get_output_path(filename)
    
    if not file_storage.file_exists(filename):
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type='text/csv'
    )


async def process_uploaded_file(file: UploadFile, job_id: str):
    """Background task to process uploaded file."""
    try:
        job = job_manager.get_job(job_id)
        
        # Process file in chunks
        async def chunk_generator():
            async for chunk in file.file:
                yield chunk
        
        # Process CSV
        result = csv_processor.process_csv_stream(chunk_generator())
        
        # Write results
        output_filename = file_storage.generate_output_filename(job_id)
        output_path = file_storage.get_output_path(output_filename)
        csv_processor.write_results_to_csv(result, output_path)
        
        # Update job
        job.complete(output_filename)
        
        logger.info(
            "Background processing completed",
            job_id=job_id,
            total_rows=result.total_rows,
            valid_rows=result.valid_rows
        )
        
    except Exception as e:
        logger.error("Background processing failed", job_id=job_id, error=str(e))
        job.fail(str(e))
    finally:
        await file.close()