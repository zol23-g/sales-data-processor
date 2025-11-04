.PHONY: install test lint format clean proto build run setup dev dev-http dev-celery dev-all
.PHONY: test-env test-run staging prod help

# Default environment
ENV ?= development

# Installation
install:
	poetry install

setup: install proto
	@echo "Development environment setup complete"

# Development (default)
dev:
	ENVIRONMENT=development poetry run python -m app.main

dev-http:
	ENVIRONMENT=development poetry run uvicorn app.api.http_gateway:app --reload --host 0.0.0.0 --port 8000

dev-celery:
	ENVIRONMENT=development poetry run celery -A app.worker.celery_app worker --loglevel=info

# Testing environment
test-env:
	ENVIRONMENT=testing poetry run python -m app.main

test-http:
	ENVIRONMENT=testing poetry run uvicorn app.api.http_gateway:app --reload --host 0.0.0.0 --port 8001

test-celery:
	ENVIRONMENT=testing poetry run celery -A app.worker.celery_app worker --loglevel=info

# Staging environment
staging:
	ENVIRONMENT=staging poetry run python -m app.main

staging-http:
	ENVIRONMENT=staging poetry run uvicorn app.api.http_gateway:app --host 0.0.0.0 --port 8000

staging-celery:
	ENVIRONMENT=staging poetry run celery -A app.worker.celery_app worker --loglevel=info

# Production environment
prod:
	ENVIRONMENT=production poetry run python -m app.main

prod-http:
	ENVIRONMENT=production poetry run uvicorn app.api.http_gateway:app --host 0.0.0.0 --port 8000

prod-celery:
	ENVIRONMENT=production poetry run celery -A app.worker.celery_app worker --loglevel=info

# Generic commands with environment
run:
	ENVIRONMENT=$(ENV) poetry run python -m app.main

run-http:
	ENVIRONMENT=$(ENV) poetry run uvicorn app.api.http_gateway:app --host 0.0.0.0 --port 8000

run-celery:
	ENVIRONMENT=$(ENV) poetry run celery -A app.worker.celery_app worker --loglevel=info

# Testing
test:
	ENVIRONMENT=testing poetry run pytest -v

test-cov:
	ENVIRONMENT=testing poetry run pytest --cov=app --cov-report=html

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
	docker run -d -p 6379:6379 --name redis-dev redis:7-alpine

redis-test:
	docker run -d -p 6378:6379 --name redis-test redis:7-alpine

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov
	rm -rf uploads/* outputs/* test_uploads/* test_outputs/*

clean-test:
	rm -rf test_uploads/* test_outputs/*

# Full development setup
dev-all: redis
	@echo "Starting all development services..."
	make dev-http &
	make dev-celery &
	@echo "Development Environment:"
	@echo "  HTTP Server: http://localhost:8000"
	@echo "  Celery Worker: Started"
	@echo "  Redis: localhost:6379"

test-all: redis-test
	@echo "Starting all testing services..."
	make test-http &
	make test-celery &
	@echo "Testing Environment:"
	@echo "  HTTP Server: http://localhost:8001"
	@echo "  Celery Worker: Started"
	@echo "  Redis: localhost:6378"

# Environment setup
env-dev:
	cp .env.development .env
	@echo "Development environment set"

env-test:
	cp .env.testing .env
	@echo "Testing environment set"

env-staging:
	cp .env.staging .env
	@echo "Staging environment set"

env-prod:
	cp .env.production .env
	@echo "Production environment set"

# Help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev-http      - Start HTTP server (development)"
	@echo "  make dev-celery    - Start Celery worker (development)"
	@echo "  make dev-all       - Start all development services"
	@echo ""
	@echo "Testing:"
	@echo "  make test-http     - Start HTTP server (testing)"
	@echo "  make test-celery   - Start Celery worker (testing)"
	@echo "  make test-all      - Start all testing services"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Staging:"
	@echo "  make staging-http  - Start HTTP server (staging)"
	@echo "  make staging-celery - Start Celery worker (staging)"
	@echo ""
	@echo "Production:"
	@echo "  make prod-http     - Start HTTP server (production)"
	@echo "  make prod-celery   - Start Celery worker (production)"
	@echo ""
	@echo "Generic:"
	@echo "  make run-http ENV=environment - Start HTTP server with custom environment"
	@echo "  make run-celery ENV=environment - Start Celery with custom environment"
	@echo ""
	@echo "Environment setup:"
	@echo "  make env-dev       - Set development environment"
	@echo "  make env-test      - Set testing environment"
	@echo "  make env-staging   - Set staging environment"
	@echo "  make env-prod      - Set production environment"