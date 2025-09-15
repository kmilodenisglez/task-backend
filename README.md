# Task Backend API

[![CI](https://github.com/kmilodenisglez/task-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/kmilodenisglez/task-backend/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-lightgrey)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI/CD-green)
![SQLite](https://img.shields.io/badge/SQLite-Test-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-purple)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![Coverage](https://img.shields.io/badge/Coverage-0.0%25-green)

A modern RESTful API for task management built with **FastAPI**, **SQLAlchemy 2.x (async)**, and **PostgreSQL**.
Designed for scalability, testability, and developer experience with advanced monitoring and observability features.

---

## ⚡ Quickstart

Clone the repo, create `.env`, and run the app with Docker:

```bash
# 1. Clone repository
git clone https://github.com/kmilodenisglez/task-backend.git
cd task-backend

# 2. Copy environment file
cp .env.example .env

# 3. Start dev environment (Docker + hot reload)
make docker-dev

# 4. Open in browser
# API:   http://localhost:8000
# Docs:  http://localhost:8000/docs
# Health: http://localhost:8000/health/health
```

🛠️ For **production build**:

```bash
make docker-prod
```

🛠️ For Development **local (venv + Python)**:

```bash
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
make dev
```

### Lint & format

```bash
make -f Makefile.ci format   # Auto-format code
make -f Makefile.ci lint     # Check code style
```

### Run tests

```bash
make -f Makefile.ci test
make -f Makefile.ci coverage
```

---

## �� Features

### Core Features
* **FastAPI backend** with **Pydantic v2** and async/await support
* **Asynchronous database** access with `asyncpg` and SQLAlchemy (async mode)
* **PostgreSQL** containerized using **Docker** / **Podman**
* **Database migrations** powered by **Alembic**
* **Isolated testing** with `pytest`, `pytest-asyncio`, `httpx`, and SQLite (async mode)
* **Configurable environments** via `.env` files and `pydantic-settings`

### Advanced Features
* **API Versioning** - v1 and v2 with backward compatibility
* **Structured Logging** - JSON logging with request tracking and correlation IDs
* **Health Checks** - Basic and detailed health monitoring with system metrics
* **Rate Limiting** - Configurable rate limiting with sliding window algorithm
* **Monitoring** - System metrics, performance monitoring, and observability
* **Security** - JWT authentication, password validation, and user isolation

### Developer Experience
* **Code quality tools**: `mypy`, `black`, `isort`, `flake8`, `pytest-cov`
* **Developer workflow** streamlined with **Makefile** and `pyproject.toml`
* **Continuous Integration (CI)** via **GitHub Actions** for automated linting, testing, type checking, and coverage reports
* **Docker support** with development and production configurations

---

## 📦 Requirements

* Python **3.10+** (3.13 recommended)
* [Podman](https://podman.io/) or [Docker](https://www.docker.com/)
* `make` (Linux/macOS)
* `pip` or [asdf](https://asdf-vm.com/) (recommended for Python version management)

---

## ⚙️ Environment Setup

1. Copy the example env file:

   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your secrets and DB credentials.

   > 🔐 **Do not commit `.env`** – only `.env.example` is versioned.

---

## 🐘 Database Setup (PostgreSQL)

We use a containerized PostgreSQL for dev and test.

### Create persistent directories

```bash
mkdir -p ./output/postgres_data
mkdir -p ./output/postgres_run
```

### Start PostgreSQL with Podman

```bash
podman run --name my_postgres \
  -e POSTGRES_USER=task_user \
  -e POSTGRES_PASSWORD=task_pass \
  -e POSTGRES_DB=task_db \
  -p 5432:5432 \
  -v ./output/postgres_data:/var/lib/postgresql/data:Z \
  -v ./output/postgres_run:/var/run/postgresql:Z \
  -d postgres:13.6-alpine
```

> 💡 Replace `podman` with `docker` if you prefer Docker.

### Initialize (first time only)

```bash
podman exec -i my_postgres psql -U postgres <<EOF
CREATE USER task_user WITH PASSWORD 'task_pass';
CREATE DATABASE task_db OWNER task_user;
CREATE DATABASE task_test_db OWNER task_user;
GRANT ALL PRIVILEGES ON DATABASE task_db TO task_user;
GRANT ALL PRIVILEGES ON DATABASE task_test_db TO task_user;
EOF
```

---

## 🧱 Database Migrations (Alembic)

* Generate new migration:

  ```bash
  alembic revision --autogenerate -m "create tasks table"
  ```
* Apply migrations:

  ```bash
  alembic upgrade head
  ```

---

## 🐳 Run the Application with Docker Compose

This project provides **two Dockerfiles**:

* `Dockerfile` → optimized for **production** with monitoring and logging
* `Dockerfile.dev` → for **development** (hot reload, dev dependencies)

### Development (hot reload)

```bash
make docker-dev
```

### Production

```bash
make docker-prod
```

### Stop all services

```bash
make stop
```

### View logs

```bash
make logs
```

---

## 💻 Run Locally with Python + venv

1. Clone the repository:

   ```bash
   git clone https://github.com/kmilodenisglez/task-backend.git
   cd task-backend
   ```

2. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   pip install -e ".[dev]"
   ```

4. Start server (with reload):

   ```bash
   make dev
   ```

Server available at:

* API → [http://localhost:8000](http://localhost:8000)
* Docs → [http://localhost:8000/docs](http://localhost:8000/docs)
* Health → [http://localhost:8000/health/health](http://localhost:8000/health/health)

---

## 🧪 Running Tests

* Run tests:

  ```bash
  make test
  ```

* Run with coverage:

  ```bash
  make coverage
  ```

* Open HTML coverage report:

  ```bash
  open htmlcov/index.html   # macOS
  xdg-open htmlcov/index.html  # Linux
  ```

---

## 🧰 Useful Makefile Commands

| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `make dev`         | Run FastAPI locally (reload)             |
| `make run`         | Run FastAPI locally (no reload)          |
| `make docker-dev`  | Run dev environment with Docker Compose  |
| `make docker-prod` | Run prod environment with Docker Compose |
| `make stop`        | Stop Docker services                     |
| `make logs`        | Show Docker logs                         |
| `make test`        | Run all tests                            |
| `make coverage`    | Run tests with coverage                  |
| `make typecheck`   | Type checking with `mypy`                |
| `make format`      | Format with `black` + `isort`            |
| `make lint`        | Lint with `flake8`                       |
| `make migrate`     | Create new Alembic migration             |
| `make upgrade`     | Apply Alembic migrations                 |
| `make downgrade`   | Rollback last migration                  |

### Monitoring Commands

| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `make health`      | Basic health check                       |
| `make health-detailed` | Detailed health check with metrics    |
| `make metrics`     | View application metrics                 |
| `make logs-tail`   | Follow application logs                  |
| `make logs-errors` | View error logs only                     |
| `make test-rate-limit` | Test rate limiting functionality    |

---

## 📂 Project Structure

```
task-backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   │   ├── v1/           # API version 1
│   │   │   ├── auth.py
│   │   │   └── tasks.py
│   │   ├── v2/           # API version 2 (enhanced)
│   │   │   ├── auth.py
│   │   │   └── tasks.py
│   │   └── health.py     # Health check endpoints
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   │   ├── auth.py
│   │   ├── logging.py    # Structured logging
│   │   ├── rate_limiting.py
│   │   └── validators.py
│   └── tests/
├── alembic/
│   └── versions/
├── logs/                 # Application logs
├── .env.example
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── Makefile
├── Makefile.ci
├── pyproject.toml
└── README.md
```

---

## 🧪 Testing Strategy

* **Development/Production**: async mode with PostgreSQL + `asyncpg`
* **Testing**:

  * ✅ SQLite (fast, isolated)
  * ✅ PostgreSQL async (realistic, slower)
* Controlled via `settings.testing` flag

See [TESTING.md](TESTING.md) for detailed testing documentation.

---

## 📈 CI/CD (GitHub Actions)

* Linting, type checking, tests, coverage
* Coverage reports uploaded as artifacts (`coverage-html`, `coverage-xml`)
* Workflow: `.github/workflows/ci.yml`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_CALLS` | Rate limit requests per window | `100` |
| `RATE_LIMIT_PERIOD` | Rate limit window in seconds | `3600` |
| `ENABLE_METRICS` | Enable metrics endpoint | `true` |

### Logging Configuration

The application uses structured JSON logging with:
- Request/response logging with correlation IDs
- Error tracking and monitoring
- Performance metrics
- User activity tracking

### Rate Limiting

Configurable rate limiting with:
- Sliding window algorithm
- Per-IP limiting
- Configurable limits and windows
- Informative response headers

---

## 🛡 License

This project is licensed under the **MIT License**. See the `LICENSE` file.
