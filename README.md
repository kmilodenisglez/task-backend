# Task Backend API

A modern RESTful API for task management built with **FastAPI**, **SQLAlchemy 2.x (async)**, and **PostgreSQL**. Designed for scalability, testability, and developer experience.

🚀 **Features:**
- FastAPI with Pydantic v2 and async/await
- Asynchronous database with `asyncpg` and `SQLAlchemy`
- PostgreSQL containerized with Podman/Docker
- Database migrations via **Alembic**
- Testing with `pytest`, `httpx`, and SQLite isolation
- Configurable environments using `.env`
- Code quality: `mypy`, `black`, `isort`, `flake8`, `pytest-cov`
- Development workflow with `Makefile` and `pyproject.toml`

---

## 📦 Requirements

- Python 3.10+
- [Podman](https://podman.io/) or [Docker](https://www.docker.com/)
- `make` (Linux/macOS)
- `pip` or `asdf` (recommended for Python version management)

---

## 🐳 Database Setup (PostgreSQL with Podman/Docker)

We use a containerized PostgreSQL instance for development and testing.

### 1. Create directories for persistent data

```bash
mkdir -p /home/kmilo/Downloads/developer/projects-test/task-backend/output/postgres_data
mkdir -p /home/kmilo/Downloads/developer/projects-test/task-backend/output/postgres_run
```

> 🔁 Replace the path with your project path if needed.

### 2. Run PostgreSQL container

```bash
podman run --name my_postgres \
  -e POSTGRES_USER=task_user \
  -e POSTGRES_PASSWORD=task_pass \
  -e POSTGRES_DB=task_db \
  -p 5432:5432 \
  -v /home/kmilo/Downloads/developer/projects-test/task-backend/output/postgres_data:/var/lib/postgresql/data:Z \
  -v /home/kmilo/Downloads/developer/projects-test/task-backend/output/postgres_run:/var/run/postgresql:Z \
  -d postgres:13.6-alpine
```

> 💡 For Docker, replace `podman` with `docker`.

---

## 🔧 Initialize PostgreSQL (First Time Only)

If the databases don't exist yet, create them and set up the user.

### Option 1: Manual Setup (Interactive)

```bash
podman exec -it my_postgres psql -U postgres
```

Then run inside `psql`:

```sql
-- Create user
CREATE USER task_user WITH PASSWORD 'task_pass';

-- Create databases
CREATE DATABASE task_db OWNER task_user;
CREATE DATABASE task_test_db OWNER task_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE task_db TO task_user;
GRANT ALL PRIVILEGES ON DATABASE task_test_db TO task_user;

-- Exit
\q
```

### Option 2: One-liner (Non-interactive)

```bash
podman exec -i my_postgres psql -U postgres <<EOF
CREATE USER task_user WITH PASSWORD 'task_pass';
CREATE DATABASE task_db OWNER task_user;
CREATE DATABASE task_test_db OWNER task_user;
GRANT ALL PRIVILEGES ON DATABASE task_db TO task_user;
GRANT ALL PRIVILEGES ON DATABASE task_test_db TO task_user;
EOF
```

### ✅ Verify Connection

```bash
podman exec -it my_postgres psql -U task_user -d task_db
```

If you connect without errors, your database is ready.

---

## 🧱 Migrations with Alembic

We use **Alembic** to manage database schema changes.

### 1. Generate a migration (after model changes)

```bash
alembic revision --autogenerate -m "create tasks table"
```

### 2. Apply migrations to the database

```bash
alembic upgrade head
```

> 📂 Migrations are stored in the `alembic/versions/` folder.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/task-backend.git
cd task-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
# Install production dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

---

## ⚙️ Configuration

Copy the example `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://task_user:task_pass@localhost/task_db
TEST_DATABASE_URL=postgresql+asyncpg://task_user:task_pass@localhost/task_test_db
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> 🔐 **Never commit your `.env` file to Git.**

---

## 🛠 Development

### Start the server in development mode

```bash
make dev
```

> 🔗 Server available at: `http://localhost:8000`  
> 📄 Swagger documentation: `http://localhost:8000/docs`

---

## 🧪 Run Tests

### Using SQLite (Recommended for Speed)

Ensure `TESTING=true` is set or use the sync mode in `app/config.py`. Then run:

```bash
# Run all tests
make test

# With code coverage
make coverage

# View HTML report
open htmlcov/index.html
```

---

## 🏗️ Docker Compose (Optional)

You can also use `docker-compose.yml` to run both PostgreSQL and FastAPI.

### 1. Start services

```bash
docker-compose up -d
```

This starts:
- `db`: PostgreSQL container
- `web`: FastAPI application

### 2. View logs

```bash
docker-compose logs -f db
docker-compose logs -f web
```

### 3. Start only PostgreSQL

```bash
docker-compose up -d db
```

Then run FastAPI locally with `make dev`.

---

## 🧰 Useful Commands (via Makefile)

| Command | Description |
|--------|-------------|
| `make dev` | Start FastAPI with reload |
| `make run` | Start without reload (local production) |
| `make test` | Run all tests |
| `make coverage` | Run tests with coverage |
| `make typecheck` | Run `mypy` |
| `make format` | Format with `black` and `isort` |
| `make lint` | Lint with `flake8` |
| `make clean` | Clean generated files |

---

## 🧬 Project Structure

```
task-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── api/
│   └── schemas/
├── app/tests/
│   ├── __init__.py
│   └── test_tasks.py
├── alembic/
│   ├── versions/
│   └── env.py
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── Makefile
└── README.md
```

---

## 🧪 Testing Strategy

- **Development/Production**: Async mode with PostgreSQL + `asyncpg`
- **Testing**: Can use either:
    - ✅ **SQLite + sync mode** (fast, isolated, no async issues)
    - ✅ **PostgreSQL + async mode** (realistic, but requires careful session isolation)
- Uses `settings.testing` flag to toggle behavior
- Each test runs in an isolated transaction with rollback

---

## 📈 Code Coverage

After running `make coverage`, open `htmlcov/index.html` to see which lines are covered by tests.

---

## 🛡 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
