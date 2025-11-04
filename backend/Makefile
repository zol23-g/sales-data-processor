.PHONY: install test lint format clean proto build run

# Installation
install:
	poetry install

# Development
dev:
	poetry run python -m app.main

dev-http:
	poetry run uvicorn app.api.http_gateway:app --reload --host 0.0.0.0 --port 8000

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

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov

# Database
redis:
	docker run -d -p 6379:6379 redis:7-alpine

# All-in-one development setup
setup: install proto
	@echo "Development environment setup complete"