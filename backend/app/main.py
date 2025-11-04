import asyncio
import sys
import logging
import grpc
from concurrent.futures import ThreadPoolExecutor
from grpc_reflection.v1alpha import reflection

from app.core.config import settings
from app.core.logger import configure_logger
from app.api.grpc_service import SalesDataProcessorServicer

# Generated protobuf code
from proto import sales_data_pb2
from proto import sales_data_pb2_grpc


async def serve_async():
    """Async server coroutine."""
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
    
    logging.info(f"gRPC server starting on {settings.GRPC_HOST}:{settings.GRPC_PORT}")
    
    await server.start()
    logging.info("gRPC server started successfully")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
        await server.stop(5)
        logging.info("gRPC server shut down successfully")


def run_grpc_server():
    """Run gRPC server."""
    configure_logger(settings.ENVIRONMENT)
    
    # Run the async server
    asyncio.run(serve_async())


if __name__ == "__main__":
    run_grpc_server()