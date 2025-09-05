.PHONY: run dev

# Levantar FastAPI en modo desarrollo
dev:
	@echo "Starting FastAPI in development mode..."
	@uvicorn app.main:app \
		--reload \
		--reload-dir app \
		--reload-dir alembic \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file .env

# Levantar FastAPI sin reload (producción local)
run:
	@echo "Starting FastAPI without reload..."
	@uvicorn app.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--env-file .env

typecheck:
	mypy app/