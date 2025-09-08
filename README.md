# Task Backend API

![CI](https://github.com/kmilodenisglez/actions/workflows/ci.yml/badge.svg)

A modern RESTful API for task management built with **FastAPI**, **SQLAlchemy 2.x (async)**, and **PostgreSQL**.
Designed for scalability, testability, and developer experience.

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
```

➡️ For **production build**:

```bash
make docker-prod
```

➡️ For **local (venv + Python)**:

```bash
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
make dev
```

---

## 🚀 Features

* FastAPI with Pydantic v2 and async/await
* Asynchronous database with `asyncpg` and `SQLAlchemy`
* PostgreSQL containerized with Docker/Podman
* Database migrations via **Alembic**
* Testing with `pytest`, `httpx`, and SQLite isolation
* Configurable environments via `.env`
* Code quality: `mypy`, `black`, `isort`, `flake8`, `pytest-cov`
* Developer workflow powered by `Makefile` and `pyproject.toml`

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

* `Dockerfile` → optimized for **production**
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

---

## 📂 Project Structure

```
task-backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── tests/
├── alembic/
│   └── versions/
├── .env.example
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── Makefile
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

---

## 📈 Code Coverage in CI/CD

* CI pipeline (`.github/workflows/ci.yml`) runs:

  * Linting, type checks, tests
  * Coverage report (`coverage.xml`, `htmlcov/`)
* Artifacts (`coverage-html`, `coverage-xml`) are uploaded for download

---

## 🛡 License

This project is licensed under the **MIT License**. See the `LICENSE` file.
