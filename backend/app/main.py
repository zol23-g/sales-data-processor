import asyncio
import sys
import logging
import grpc
from concurrent.futures import ThreadPoolExecutor
from grpc_reflection.v1alpha import reflection

from app.core.config import Settings, settings
from app.core.logger import configure_logger, get_logger
from app.api.grpc_service import SalesDataProcessorServicer

# Generated protobuf code
from proto import sales_data_pb2
from proto import sales_data_pb2_grpc


def log_environment_settings():
    """Log environment and key settings for visibility."""
    logger = get_logger(__name__)
    
    # Log environment information
    logger.info("=" * 60)
    logger.info(f" Starting Sales Data Processor")
    logger.info(f" Environment: {settings.ENVIRONMENT.upper()}")
    logger.info(f" Debug Mode: {settings.DEBUG}")
    logger.info(f" Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 60)
    
    # Log server configuration
    logger.info(" Server Configuration:")
    logger.info(f"   gRPC Host: {settings.GRPC_HOST}:{settings.GRPC_PORT}")
    logger.info(f"   HTTP Host: {settings.HTTP_HOST}:{settings.HTTP_PORT}")
    
    # Log storage configuration
    logger.info(" Storage Configuration:")
    logger.info(f"   Upload Directory: {settings.UPLOAD_DIR}")
    logger.info(f"   Output Directory: {settings.OUTPUT_DIR}")
    logger.info(f"   Max File Size: {settings.MAX_FILE_SIZE / 1024 / 1024} MB")
    
    # Log Redis configuration
    logger.info(" Redis Configuration:")
    logger.info(f"   Redis URL: {settings.REDIS_URL}")
    logger.info(f"   Celery Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"   Celery Backend: {settings.CELERY_RESULT_BACKEND}")
    
    # Log security configuration (mask sensitive info)
    secret_display = "***" + settings.SECRET_KEY[-4:] if settings.SECRET_KEY else "Not Set"
    logger.info(" Security Configuration:")
    logger.info(f"   Secret Key: {secret_display}")
    logger.info(f"   Token Expire: {settings.TOKEN_EXPIRE_MINUTES} minutes")
    
    # Log CORS configuration
    logger.info(" CORS Configuration:")
    for origin in settings.ALLOWED_ORIGINS:
        logger.info(f"   Allowed Origin: {origin}")
    
    logger.info("=" * 60)


async def serve_async():
    """Async server coroutine."""
    logger = get_logger(__name__)
    
    # Create gRPC server
    server = grpc.aio.server()
    
    # Add servicer
    sales_data_pb2_grpc.add_SalesDataProcessorServicer_to_server(
        SalesDataProcessorServicer(), server
    )
    
    # Enable reflection
    SERVICE_NAMES = (
        sales_data_pb2.DESCRIPTOR.services_by_name['SalesDataProcessor'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Start server
    server.add_insecure_port(f"{settings.GRPC_HOST}:{settings.GRPC_PORT}")
    
    logger.info(f" gRPC server starting on {settings.GRPC_HOST}:{settings.GRPC_PORT}")
    
    await server.start()
    logger.info(" gRPC server started successfully")
    
    try:
        logger.info(" gRPC server is ready to accept requests")
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("  Received keyboard interrupt, shutting down...")
        await server.stop(5)
        logger.info(" gRPC server shut down successfully")


def run_grpc_server():
    """Run gRPC server."""
    # Configure logger first
    configure_logger(settings.ENVIRONMENT)
    
    # Log environment and settings
    log_environment_settings()
    
    # Run the async server
    asyncio.run(serve_async())


if __name__ == "__main__":
    run_grpc_server()