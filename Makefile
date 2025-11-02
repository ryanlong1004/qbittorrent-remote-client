.PHONY: help install install-dev test test-cov lint format type-check security clean build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest -v --cov=qbt_api --cov=qbt_client --cov=qbittorrent_remote_client --cov-report=term-missing --cov-report=html

test-integration: ## Run integration tests
	pytest -v -m integration

lint: ## Run all linters
	flake8 .
	pylint qbt_api.py qbt_client.py qbittorrent_remote_client/
	bandit -r . -ll

format: ## Format code
	black .
	isort .

format-check: ## Check code formatting
	black --check --diff .
	isort --check-only --diff .

type-check: ## Run type checking
	mypy qbt_api.py qbt_client.py qbittorrent_remote_client/ --ignore-missing-imports

security: ## Run security checks
	bandit -r . -f json -o bandit-report.json
	bandit -r . -ll

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	python -m build

build-check: ## Check built package
	python -m build
	twine check dist/*

ci: format-check lint type-check security test ## Run all CI checks locally

dev-setup: install-dev ## Set up development environment
	@echo "Development environment set up successfully!"
	@echo "Run 'make help' to see available commands."
