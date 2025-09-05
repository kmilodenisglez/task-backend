# Makefile
#
# Useful commands for developing the FastAPI project
#
# Usage:
#   make dev          # Development mode with auto-reload
#   make run          # Local production environment
#   make test         # Run tests
#   make coverage     # Run tests and generate code coverage report
#   make typecheck    # Perform type checking with mypy
#   make format       # Format code with black and isort
#   make lint         # Lint code with flake8
#   make install-dev  # Install development dependencies
#   make clean        # Clean generated files

# Variables
PYTHON := python
UVICORN := uvicorn
PYTEST := pytest
MYPY := mypy
BLACK := black
ISORT := isort
FLAKE8 := flake8

# Directories and files
APP_DIR := app
TEST_DIR := app/tests
COVERAGE_DIR := htmlcov
ENV_FILE := .env

# Main commands
.PHONY: dev run test coverage typecheck format lint clean install install-dev

# --- Development ---

dev:
	@echo "🚀 Starting FastAPI in development mode..."
	$(UVICORN) $(APP_DIR).main:app \
		--reload \
		--reload-dir=$(APP_DIR) \
		--reload-dir=alembic \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file $(ENV_FILE)

run:
	@echo "📦 Starting FastAPI in production mode..."
	$(UVICORN) $(APP_DIR).main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file $(ENV_FILE)

# --- Testing ---

test:
	@echo "🧪 Running tests..."
	$(PYTEST) $(TEST_DIR)/ -v

coverage:
	@echo "📊 Running tests with coverage..."
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(APP_DIR) \
		--cov-report=term-missing \
		--cov-report=html:$(COVERAGE_DIR) \
		--cov-report=xml

# --- Code quality ---

typecheck:
	@echo "🔍 Checking types with mypy..."
	$(MYPY) $(APP_DIR)/

format:
	@echo "🧹 Formatting code with black and isort..."
	$(BLACK) $(APP_DIR)/
	$(ISORT) $(APP_DIR)/

lint:
	@echo " linting code with flake8..."
	$(FLAKE8) $(APP_DIR)/

# --- deploy ---

install:
	@echo "📦 Installing production dependencies..."
	pip install .

install-dev: install
	@echo "📦 Installing development dependencies..."
	pip install ".[dev]"

# --- Cleaning ---

clean:
	@echo "🗑️  Cleaning up..."
	rm -rf $(COVERAGE_DIR)/ .pytest_cache/ .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete"
	
	
# ----- Alembic ----
migrate:
	alembic revision --autogenerate -m "auto"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

db-status:
	alembic current