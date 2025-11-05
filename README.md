# Sales Data Processor

A high-performance full-stack application for processing large CSV files containing departmental sales data. Built with Python gRPC backend and Next.js frontend.

## Features

- **Streaming CSV Processing**: Handles files that don't fit in memory
- **gRPC API**: High-performance bidirectional streaming
- **HTTP REST API**: Easy integration with frontend applications
- **Background Processing**: Celery-based async job processing
- **Real-time Progress**: Live status updates during processing
- **Memory Efficient**: O(k) space complexity where k is unique departments
- **Multi-environment Support**: Development, Testing, Staging, Production
- **Dockerized**: Complete containerized development environment

## Architecture

### Backend Services
- **gRPC Service**: Primary processing endpoint with streaming (Port 50051)
- **HTTP Gateway**: REST API for file uploads and downloads (Port 8000)
- **Celery Worker**: Background job processing
- **Redis**: Job queue and result backend (Port 6379)

### Frontend
- **Next.js 14**: App router with TypeScript
- **Tailwind CSS**: Modern UI styling
- **Real-time Updates**: Polling-based job status

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)
- Redis (handled by Docker)

##  Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/zol23-g/sales-data-processor.git
cd sales-data-processor

# Start all services
docker-compose up -d

# Or start backend and frontend separately
cd backend && docker-compose up -d
cd ../frontend && docker-compose up -d
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **gRPC Service**: localhost:50051

##  Manual Setup

### Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Generate protobuf code
make proto

# Create necessary directories
mkdir -p uploads outputs test_uploads test_outputs

# Start Redis
make redis

# Start services (in separate terminals)
make dev-http        # HTTP server on port 8000
make dev-celery      # Celery worker
make dev             # gRPC server on port 50051 (optional)
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

##  Usage

### 1. Upload CSV File

1. Open http://localhost:3000 in your browser
2. Drag and drop a CSV file or click to upload
3. Click "Process File"

### 2. Monitor Processing

- Watch real-time progress updates
- View processing status (pending → processing → completed)
- See job ID and processing metrics

### 3. Download Results

- Click "Download Results" when processing completes
- Get aggregated CSV with department totals

### CSV Format

**Input CSV Format:**
```csv
Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200
Electronics,2023-08-02,150
Clothing,2023-08-02,50
```

**Output CSV Format:**
```csv
Department Name,Total Number of Sales
Clothing,250
Electronics,250
```

## Configuration

### Environment Variables

#### Backend (.env.development)
```bash
ENVIRONMENT=development
DEBUG=True
GRPC_HOST=0.0.0.0
GRPC_PORT=50051
HTTP_HOST=0.0.0.0
HTTP_PORT=8000
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE=104857600
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_ENVIRONMENT=development
```

### Makefile Commands

#### Backend Commands
```bash
make dev-http          # Start HTTP server
make dev-celery        # Start Celery worker
make dev-all           # Start all development services
make test              # Run tests
make lint              # Run linting
make format            # Format code
make proto             # Generate protobuf code
```

#### Environment-specific
```bash
make test-http         # Start HTTP server (testing environment)
make staging-http      # Start HTTP server (staging environment)
make prod-http         # Start HTTP server (production environment)
```

##  Testing

### Backend Tests
```bash
cd backend
make test              # Run all tests
make test-cov          # Run tests with coverage
```

### Frontend Tests
```bash
cd frontend
npm test              # Run tests
npm run test:coverage # Run tests with coverage
```

### Test CSV Examples

Create test files to verify functionality:

**valid_sales.csv**
```csv
Department Name,Date,Number of Sales
Electronics,2023-08-01,100
Clothing,2023-08-01,200
Electronics,2023-08-02,150
```

**invalid_sales.csv**
```csv
Department Name,Date,Number of Sales
Electronics,2023-13-01,-100  # Invalid date and negative sales
Invalid,2023-08-01,abc       # Non-numeric sales
,2023-08-01,100              # Empty department
```

## API Documentation

### HTTP Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/upload` - Upload CSV file
- `GET /api/job/{job_id}` - Get job status
- `GET /api/download/{filename}` - Download result file

### gRPC Service

- `ProcessSalesData` - Stream CSV data for processing
- `GetJobStatus` - Check processing status
- `DownloadResult` - Get result file download info

### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Upload file
curl -X POST -F "file=@test.csv" http://localhost:8000/api/upload

# Check job status
curl http://localhost:8000/api/job/{job_id}

# Download results
curl http://localhost:8000/api/download/results_{job_id}.csv
```

##  Docker Deployment

### Production Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale celery-worker=4
```

### Docker Compose Files

- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production setup
- `docker-compose.staging.yml` - Staging setup

##  Environment Setup

### Development
```bash
cd backend && make env-dev
cd frontend && cp .env.local .env
```

### Staging
```bash
cd backend && make env-staging
cd frontend && cp .env.staging .env
```

### Production
```bash
cd backend && make env-prod
cd frontend && cp .env.production .env
```

##  Performance

### Algorithm Complexity
- **Time Complexity**: O(n) where n is number of rows
- **Space Complexity**: O(k) where k is number of unique departments

### Memory Efficiency
1. **Streaming Processing**: Files processed in configurable chunks
2. **Incremental Aggregation**: Department totals updated per row
3. **Buffer Management**: Efficient line-by-line processing

### Supported File Sizes
- **Maximum**: 100MB per file
- **Recommended**: Files up to 1GB (with adequate system resources)

##  Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   make redis
   # Or
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. **Port Already in Use**
   ```bash
   # Kill process on port
   sudo lsof -ti:8000 | xargs kill -9
   ```

3. **File Upload Fails**
   - Check file size (< 100MB)
   - Verify CSV format
   - Check backend logs

4. **Processing Stuck**
   - Check Celery worker status
   - Verify Redis is running
   - Check job queue

### Logs and Monitoring

```bash
# Backend logs
cd backend && make docker-logs

# Celery worker logs
docker-compose logs celery-worker

# Frontend logs
cd frontend && npm run dev
```

##  Development

### Code Structure

```
sales-data-processor/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and logging
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   ├── api/          # gRPC and HTTP endpoints
│   │   └── worker.py     # Celery worker
│   ├── tests/            # Test suite
│   ├── proto/            # Protocol buffers
│   └── docker-compose.yml
└── frontend/
    ├── app/              # Next.js app router
    ├── components/       # React components
    ├── lib/             # Utilities and API client
    ├── types/           # TypeScript definitions
    └── docker-compose.yml
```

### Adding New Features

1. **Backend Changes**
   - Add service logic in `app/services/`
   - Update API endpoints in `app/api/`
   - Add tests in `tests/`

2. **Frontend Changes**
   - Add components in `app/components/`
   - Update API client in `lib/api/`
   - Add types in `types/`

3. **Protocol Buffer Changes**
   - Update `.proto` files
   - Regenerate code: `make proto`


## Success!

Your Sales Data Processor is now running! 

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Ready to process CSV files!

---

**Next Steps**: 
- Try uploading a test CSV file
- Explore the API documentation
- Check the real-time processing status
- Download your first processed results!