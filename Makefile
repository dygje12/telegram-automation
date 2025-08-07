.PHONY: help dev test build deploy clean install lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  make dev      - Start development environment"
	@echo "  make test     - Run all tests"
	@echo "  make build    - Build all components"
	@echo "  make deploy   - Deploy to production"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make install  - Install dependencies"
	@echo "  make lint     - Run linting"
	@echo "  make format   - Format code"

# Development environment
dev:
	@echo "Starting development environment..."
	docker-compose -f infra/docker/docker-compose.yml up --build

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements/dev.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest app/tests/ --cov=app --cov-report=term-missing --cov-fail-under=80
	@echo "Running frontend tests..."
	cd frontend && npm test

# Linting
lint:
	@echo "Running backend linting..."
	cd backend && black --check app/
	cd backend && isort --check-only app/
	cd backend && mypy app/
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	cd backend && black app/
	cd backend && isort app/
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Build
build:
	@echo "Building backend..."
	docker build -f infra/docker/Dockerfile.backend -t telegram-automation-backend .
	@echo "Building frontend..."
	docker build -f infra/docker/Dockerfile.frontend -t telegram-automation-frontend .

# Deploy
deploy:
	@echo "Deploying to production..."
	docker-compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.prod.yml up -d

# Clean
clean:
	@echo "Cleaning build artifacts..."
	docker system prune -f
	cd frontend && rm -rf dist/ node_modules/.cache/
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} +
	cd backend && find . -name "*.pyc" -delete

