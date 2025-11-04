import os
import uuid
from typing import AsyncIterator
import grpc
from grpc import aio

from app.core.config import settings
from app.core.logger import get_logger
from app.services.csv_processor import CSVProcessor
from app.services.file_storage import FileStorageService
from app.services.job_manager import JobManager

# Generated protobuf code
from proto import sales_data_pb2
from proto import sales_data_pb2_grpc


class SalesDataProcessorServicer(sales_data_pb2_grpc.SalesDataProcessorServicer):
    """gRPC service implementation for sales data processing."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.csv_processor = CSVProcessor()
        self.file_storage = FileStorageService()
        self.job_manager = JobManager()
    
    async def ProcessSalesData(
        self, 
        request_iterator: AsyncIterator[sales_data_pb2.SalesDataChunk],
        context: grpc.aio.ServicerContext
    ) -> sales_data_pb2.ProcessResponse:
        """Process sales data stream."""
        job_id = str(uuid.uuid4())
        self.logger.info("Starting sales data processing", job_id=job_id)
        
        try:
            # Initialize job
            job = self.job_manager.create_job(job_id)
            job.start_processing()
            
            # Collect chunks and process
            def chunk_generator():
                for request in request_iterator:
                    yield request.chunk_data
            
            # Process CSV stream
            result = self.csv_processor.process_csv_stream(chunk_generator())
            
            # Write results to file
            output_filename = self.file_storage.generate_output_filename(job_id)
            output_path = self.file_storage.get_output_path(output_filename)
            self.csv_processor.write_results_to_csv(result, output_path)
            
            # Update job status
            download_url = self.file_storage.get_download_url(output_filename)
            job.complete(output_filename)
            
            self.logger.info(
                "Sales data processing completed",
                job_id=job_id,
                total_rows=result.total_rows,
                valid_rows=result.valid_rows,
                processing_time=result.processing_time
            )
            
            return sales_data_pb2.ProcessResponse(
                job_id=job_id,
                status="completed",
                message="Processing completed successfully",
                download_url=download_url,
                total_rows=result.total_rows,
                total_departments=len(result.departments),
                processing_time=result.processing_time
            )
            
        except Exception as e:
            self.logger.error("Sales data processing failed", job_id=job_id, error=str(e))
            job.fail(str(e))
            
            return sales_data_pb2.ProcessResponse(
                job_id=job_id,
                status="failed",
                message=f"Processing failed: {str(e)}",
                download_url="",
                total_rows=0,
                total_departments=0,
                processing_time=0.0
            )
    
    async def GetJobStatus(
        self, 
        request: sales_data_pb2.JobStatusRequest, 
        context: grpc.aio.ServicerContext
    ) -> sales_data_pb2.JobStatusResponse:
        """Get processing job status."""
        job_id = request.job_id
        job = self.job_manager.get_job(job_id)
        
        if not job:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Job {job_id} not found")
        
        download_url = ""
        if job.result_file:
            download_url = self.file_storage.get_download_url(job.result_file)
        
        return sales_data_pb2.JobStatusResponse(
            job_id=job_id,
            status=job.status,
            message=job.message,
            progress=job.progress,
            download_url=download_url
        )
    
    async def DownloadResult(
        self, 
        request: sales_data_pb2.DownloadRequest, 
        context: grpc.aio.ServicerContext
    ) -> sales_data_pb2.DownloadResponse:
        """Get download information for result file."""
        job_id = request.job_id
        job = self.job_manager.get_job(job_id)
        
        if not job or not job.result_file:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Result file not found")
        
        file_path = self.file_storage.get_output_path(job.result_file)
        
        if not self.file_storage.file_exists(job.result_file):
            await context.abort(grpc.StatusCode.NOT_FOUND, "Result file not found")
        
        download_url = self.file_storage.get_download_url(job.result_file)
        
        return sales_data_pb2.DownloadResponse(
            download_url=download_url,
            filename=job.result_file,
            file_size=os.path.getsize(file_path)
        )