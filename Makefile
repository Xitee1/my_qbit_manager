.PHONY: help install install-dev run test lint format clean docker-build docker-run docker-stop

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev]"

run: ## Run the application once
	python -m my_qbit_manager.main --mode once

run-scheduler: ## Run the scheduler
	python -m my_qbit_manager.main --mode scheduler

run-module: ## Run a specific module (use MODULE=module_name)
	python -m my_qbit_manager.main --mode module --module $(MODULE)

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov=my_qbit_manager --cov-report=html --cov-report=term

lint: ## Run linters
	flake8 src/my_qbit_manager/
	pylint src/my_qbit_manager/

format: ## Format code with black
	black src/ tests/

type-check: ## Run type checking with mypy
	mypy src/my_qbit_manager/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run with Docker Compose
	docker-compose up

docker-run-detached: ## Run with Docker Compose in detached mode
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker container logs
	docker-compose logs -f

docker-rebuild: ## Rebuild and restart Docker containers
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

setup-env: ## Copy .env.example to .env
	cp .env.example .env
	@echo "Please edit .env with your qBittorrent credentials"

init: setup-env install ## Initialize the project (copy env and install deps)
	@echo "Project initialized! Edit .env and config/config.yaml before running."
