.PHONY: help install test test-unit test-integration test-e2e test-coverage lint format type-check clean dev setup

# Default target
help: ## Show this help message
	@echo "AI Strategic Co-pilot - Available Commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dependencies
	./venv/bin/pip install -r requirements.txt

setup: ## Interactive environment setup
	./venv/bin/python scripts/setup_env.py

dev: ## Start development server
	./venv/bin/uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test: ## Run all tests
	./venv/bin/pytest

test-unit: ## Run unit tests only
	./venv/bin/pytest -m unit

test-integration: ## Run integration tests only
	./venv/bin/pytest -m integration

test-e2e: ## Run end-to-end tests only
	./venv/bin/pytest -m e2e

test-coverage: ## Run tests with detailed coverage report
	./venv/bin/pytest --cov-report=html --cov-report=term-missing

test-fast: ## Run tests excluding slow ones
	./venv/bin/pytest -m "not slow"

test-agents: ## Run agent-specific tests
	./venv/bin/pytest -m agent

test-api: ## Run API tests
	./venv/bin/pytest -m api

test-models: ## Run model tests
	./venv/bin/pytest -m models

test-utils: ## Run utility tests
	./venv/bin/pytest -m utils

# Code quality
lint: ## Run linting
	./venv/bin/ruff check src/ tests/

lint-fix: ## Run linting with auto-fix
	./venv/bin/ruff check --fix src/ tests/

format: ## Format code
	./venv/bin/black src/ tests/

format-check: ## Check code formatting
	./venv/bin/black --check src/ tests/

type-check: ## Run type checking
	./venv/bin/mypy src/

quality: lint format-check type-check ## Run all code quality checks

# Cleaning
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name "coverage.xml" -delete
	find . -name ".coverage" -delete

clean-sessions: ## Clean up test session files
	rm -rf data/sessions/*_strategy_map.json
	rm -rf test_data/

clean-logs: ## Clean up log files
	rm -rf logs/*.log
	rm -rf test_logs/

clean-all: clean clean-sessions clean-logs ## Clean everything

# Development helpers
requirements: ## Generate requirements.txt from current environment
	pip freeze > requirements-freeze.txt

tree: ## Show project structure
	tree -I 'venv|__pycache__|*.pyc|.git|.pytest_cache|htmlcov|.DS_Store'

check: quality test ## Run all checks (quality + tests)

# Docker (future)
# docker-build: ## Build Docker image
# 	docker build -t strategy-coach-app .

# docker-run: ## Run Docker container
# 	docker run -p 8000:8000 strategy-coach-app