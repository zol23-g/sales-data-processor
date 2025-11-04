.PHONY: install test lint format clean proto build run setup dev dev-http dev-celery

# Installation
install:
	poetry install

setup: install proto
	@echo "Development environment setup complete"

# Development
dev:
	poetry run python -m app.main

dev-http:
	poetry run uvicorn app.api.http_gateway:app --reload --host 0.0.0.0 --port 8000

dev-celery:
	poetry run celery -A app.worker.celery_app worker --loglevel=info

# Testing
test:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=app --cov-report=html

# Linting and Formatting
lint:
	poetry run flake8 app tests
	poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests

# Code generation
proto:
	python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. --pyi_out=. ./proto/sales_data.proto
	sed -i 's/import sales_data_pb2/from proto import sales_data_pb2/g' proto/sales_data_pb2_grpc.py

# Pre-commit
pre-commit:
	poetry run pre-commit run --all-files

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
redis:
	docker run -d -p 6379:6379 redis:7-alpine

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov
	rm -rf uploads/* outputs/*

# Full development setup
dev-all: redis
	@echo "Starting all services..."
	make dev-http &
	make dev-celery &
	@echo "HTTP Server: http://localhost:8000"
	@echo "Celery Worker: Started"
	@echo "Redis: localhost:6379"