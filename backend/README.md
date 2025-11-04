# Sales Data Processor

A high-performance backend service for processing large CSV files containing departmental sales data, built with Python gRPC and Next.js frontend.

## Features

- **Streaming CSV Processing**: Handles files that don't fit in memory
- **gRPC API**: High-performance bidirectional streaming
- **HTTP Gateway**: RESTful API for frontend integration
- **Background Processing**: Celery-based async job processing
- **Real-time Progress**: WebSocket-like status updates
- **Memory Efficient**: O(k) space complexity where k is unique departments
- **Dockerized**: Complete containerized development environment

## Architecture

### Backend Services
- **gRPC Service**: Primary processing endpoint with streaming
- **HTTP Gateway**: REST API for file uploads and downloads
- **Celery Worker**: Background job processing
- **Redis**: Job queue and result backend

### Frontend
- **Next.js 14**: App router with TypeScript
- **Tailwind CSS**: Modern UI styling
- **Real-time Updates**: Polling-based job status

## Algorithm & Performance

### Time Complexity
- **O(n)**: Where n is the number of rows in CSV
- Linear processing of each row with constant-time department lookups

### Space Complexity
- **O(k)**: Where k is the number of unique departments
- Only stores aggregated department totals, not individual rows

### Memory Efficiency Strategy
1. **Streaming Processing**: Files processed in configurable chunks
2. **Incremental Aggregation**: Department totals updated per row
3. **Buffer Management**: Efficient line-by-line processing with buffer handling

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd sales-data-processor

# Backend
cd backend
docker-compose up -d

# Frontend (new terminal)
cd ../frontend
docker-compose up -d