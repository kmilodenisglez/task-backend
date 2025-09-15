# Makefile
#
# Useful commands for developing the FastAPI project
#
# Usage:
#   make install-dev  # Install development dependencies
#   make dev          # Development mode with auto-reload (local)
#   make run          # Local production environment
#   make test         # Run tests (local)
#   make coverage     # Run tests with coverage (local)
#   make typecheck    # Perform type checking with mypy
#   make format       # Format code with black and isort
#   make lint         # Lint code with flake8
#   make docker-dev   # Run app + db in Docker (dev mode, hot reload)
#   make docker-prod  # Run app + db in Docker (prod mode)
#   make stop         # Stop all docker services
#   make logs         # View docker logs (app + db)
#   make clean        # Clean generated files
#
#   make migrate      # Alembic: create revision
#   make upgrade      # Alembic: apply latest migration
#   make downgrade    # Alembic: rollback last migration
#   make db-status    # Alembic: show current revision

# Variables
PYTHON := python
UVICORN := uvicorn
PYTEST := pytest
MYPY := mypy
BLACK := black
ISORT := isort
FLAKE8 := flake8
DOCKER_COMPOSE := docker-compose

# Directories and files
APP_DIR := app
TEST_DIR := app/tests
COVERAGE_DIR := htmlcov
ENV_FILE := .env

# Main commands
.PHONY: dev run test coverage typecheck format lint clean install install-dev \
        docker-dev docker-prod stop logs migrate upgrade downgrade db-status

# --- Development (local) ---

dev:
	@echo "🚀 Starting FastAPI in development mode (local)..."
	$(UVICORN) $(APP_DIR).main:app \
		--reload \
		--reload-dir=$(APP_DIR) \
		--reload-dir=alembic \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file $(ENV_FILE)

run:
	@echo "📦 Starting FastAPI in production mode (local)..."
	$(UVICORN) $(APP_DIR).main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file $(ENV_FILE)

# --- Testing (local) ---

test:
	@echo "🧪 Running tests..."
	rm -f test.db test.db-journal test.db-shm test.db-wal
	$(PYTEST) $(TEST_DIR)/ -v -s

coverage:
	@echo "📊 Running tests with coverage..."
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(APP_DIR) \
		--cov-report=term-missing \
		--cov-report=html:$(COVERAGE_DIR) \
		--cov-report=xml

# --- Code quality (local) ---

typecheck:
	@echo "🔍 Checking types with mypy..."
	$(MYPY) $(APP_DIR)/

format:
	@echo "🧹 Formatting code with black and isort..."
	$(BLACK) $(APP_DIR)/
	$(ISORT) $(APP_DIR)/

lint:
	@echo "🔎 Linting code with flake8..."
	$(FLAKE8) $(APP_DIR)/

# --- Docker workflows ---

docker-dev:
	@echo "🐳 Starting Docker (dev profile: hot reload + dev deps)..."
	$(DOCKER_COMPOSE) --profile dev up -d --build

docker-prod:
	@echo "🐳 Starting Docker (prod profile: optimized image)..."
	$(DOCKER_COMPOSE) --profile prod up -d --build

stop:
	@echo "🛑 Stopping all Docker services..."
	$(DOCKER_COMPOSE) down

logs:
	@echo "📜 Showing Docker logs (follow mode)..."
	$(DOCKER_COMPOSE) logs -f

# --- Deploy (local installs) ---

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

# --- Alembic ---

migrate:
	alembic revision --autogenerate -m "auto"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

db-status:
	alembic current

# --- Monitoring ---
logs-tail:
	@echo "📜 Following application logs..."
	tail -f logs/app.log

logs-errors:
	@echo "🚨 Showing error logs..."
	tail -f logs/errors.log

# --- Health Checks ---
health:
	@echo "🏥 Checking application health..."
	curl -s http://localhost:8000/health/health | jq .

health-detailed:
	@echo "🏥 Detailed health check..."
	curl -s http://localhost:8000/health/detailed | jq .

# --- Metrics ---
metrics:
	@echo "📊 Application metrics..."
	curl -s http://localhost:8000/health/metrics

# --- Rate Limiting Test ---
test-rate-limit:
	@echo "🚦 Testing rate limiting..."
	for i in {1..5}; do \
		echo "Request $$i:"; \
		curl -s -w "Status: %{http_code}\n" http://localhost:8000/api/v1/tasks/; \
		echo ""; \
	done