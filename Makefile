.PHONY: dev build test lint deploy

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
DOCKER_DIR = infra/docker

# Default target
all: dev

# Run development environment using Docker Compose
dev:
	@echo "Starting development environment..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml up --build

# Build frontend and backend Docker images
build:
	@echo "Building Docker images..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml build

# Run tests for backend and frontend
test:
	@echo "Running backend tests..."
	@cd $(BACKEND_DIR) && pytest --cov=app
	@echo "Running frontend tests..."
	@cd $(FRONTEND_DIR) && npm test

# Run linting for backend and frontend
lint:
	@echo "Running backend linting..."
	@cd $(BACKEND_DIR) && poetry run black . && poetry run isort . && poetry run mypy app/
	@echo "Running frontend linting..."
	@cd $(FRONTEND_DIR) && npm run lint

# Deploy (placeholder - actual deployment logic would go here)
deploy:
	@echo "Deploying application... (Not implemented yet)"

clean:
	@echo "Cleaning up..."
	@docker-compose -f $(DOCKER_DIR)/docker-compose.yml down --volumes --remove-orphans
	@rm -rf $(BACKEND_DIR)/.pytest_cache
	@rm -rf $(BACKEND_DIR)/.mypy_cache
	@rm -rf $(BACKEND_DIR)/__pycache__
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(DOCKER_DIR)/backend_data

.PHONY: all dev build test lint deploy clean

