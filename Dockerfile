# Dockerfile
FROM python:3.13.2-slim AS base

# Evita que Python genere .pyc y buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Instala dependencias del sistema necesarias para psycopg2 y asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Usuario no root
RUN useradd -ms /bin/bash appuser
WORKDIR /app
USER appuser

# Copia solo los archivos necesarios para instalar dependencias
COPY --chown=appuser:appuser pyproject.toml README.md ./

# Instala dependencias (prod por defecto)
RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

# Copia el resto del código
COPY --chown=appuser:appuser . .

# Puerto expuesto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
