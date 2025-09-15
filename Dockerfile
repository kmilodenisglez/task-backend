# Dockerfile - Production optimized
FROM python:3.13.2-slim AS base

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user and directories
RUN useradd -ms /bin/bash appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app

WORKDIR /app
USER appuser

# Copy dependency files first for better caching
COPY --chown=appuser:appuser pyproject.toml README.md ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p logs output/postgres_data output/postgres_run

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
