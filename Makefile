.PHONY: help install install-dev build test lint clean dist upload

help: ## Show this help message
	@echo "PBT (Prompt Build Tool) - Development Commands"
	@echo "=============================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

install: ## Install PBT in development mode
	pip install -e .

install-dev: ## Install PBT with development dependencies
	pip install -e ".[dev]"

install-all: ## Install PBT with all dependencies
	pip install -e ".[all]"

##@ Building

build: clean ## Build distribution packages
	python -m build

build-wheel: clean ## Build wheel package only
	python -m build --wheel

##@ Testing

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=pbt --cov-report=html --cov-report=term

lint: ## Run linting
	black --check pbt/
	isort --check-only pbt/
	flake8 pbt/

lint-fix: ## Fix linting issues
	black pbt/
	isort pbt/

##@ Distribution

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dist: build ## Create distribution packages
	@echo "Distribution packages created in dist/"
	@ls -la dist/

upload-test: dist ## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload: dist ## Upload to PyPI
	python -m twine upload dist/*

##@ Documentation

docs-serve: ## Serve documentation locally
	mkdocs serve

docs-build: ## Build documentation
	mkdocs build

##@ Local Development

dev-setup: ## Set up development environment
	python -m venv venv
	. venv/bin/activate && pip install -e ".[dev]"
	@echo "Development environment created!"
	@echo "Activate with: source venv/bin/activate"

example: ## Run example project
	mkdir -p example-project
	cd example-project && pbt init --name "Example Project"
	@echo "Example project created in example-project/"

##@ Server

serve: ## Start PBT server
	pbt serve --reload

serve-prod: ## Start PBT server in production mode
	pbt serve --host 0.0.0.0 --port 8000