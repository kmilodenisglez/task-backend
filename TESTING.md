# 🧪 Testing Strategy (Async-First)

> **Note:** The entire application — including tests — now runs **asynchronously** using `AsyncSession` and `AsyncClient`.

This document explains the current testing architecture and best practices for the project.

---

## 🧱 Testing Architecture: "Async-Consistent" Pattern

We follow an **async-consistent** strategy where:

- ✅ **Production**: Asynchronous mode with `asyncpg` + PostgreSQL
- ✅ **Testing**: Asynchronous mode with `aiosqlite` (in-memory or file-based)
- ✅ **Development**: Asynchronous mode with `asyncpg` + PostgreSQL

This ensures:
- 🔄 Consistent behavior across environments
- ⚡ No "synchronous vs async" bugs slipping through
- 🛠 Easier debugging and realistic test conditions

We avoid legacy patterns like `.query()` or sync-style commits by using **pure async/await** throughout.

---

## ✅ Advantages of This Approach

| Benefit | Description |
|-------|-------------|
| ✅ Consistency | Same async code runs in test, dev, and prod |
| ⚡ Fast & Isolated | `aiosqlite` in-memory DB is fast and isolated |
| 🧼 Clean Sessions | Each test uses a fresh `AsyncSession` with rollback |
| 🔒 Secure by Default | Users only access their own data (tested) |
| 📈 Realistic Performance | No hidden sync bottlenecks |

---

## 🔧 How It Works

### 1. Mode Detection via Settings

The `testing` flag is controlled via `Settings` and set **before** importing database components:

```python
# conftest.py
from app.config import settings
settings.testing = True  # ← Must be set before importing database
```

```python
# app/config.py
class Settings(BaseSettings):
    testing: bool = False
    database_url: str = "postgresql+psycopg2://user:pass@localhost/taskdb"

    @property
    def database_url_for_async(self) -> str:
        if self.testing:
            return "sqlite+aiosqlite:///:memory:"
        return self.database_url.replace("postgresql+psycopg2", "postgresql+asyncpg")
```

---

### 2. Async Database Setup

We use `AsyncSession` everywhere:

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = settings.database_url_for_async
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
```

No more conditional `DBSession = Session if testing else AsyncSession`.

---

### 3. Test Isolation with Transactions

Each test runs in an isolated async session. We use `override_get_db` to inject a test session:

```python
@pytest_asyncio.fixture
async def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()
```

After each test, the session is cleaned up properly.

---

## 🛠 Running Tests

### Run all tests
```bash
make test
```

### Run tests with coverage
```bash
make coverage
```

### View HTML coverage report
```bash
open htmlcov/index.html
# or on Linux:
xdg-open htmlcov/index.html
```

---

## 📚 Notes

- ✅ All tests use `AsyncClient` with `ASGITransport`.
- ✅ `settings.testing = True` is set **before** importing database modules.
- ✅ We use `select(...)` + `execute()` instead of `.query()`.
- ✅ All DB operations use `await db.commit()` and `await db.refresh()`.
- ✅ Users can only access their own tasks (ownership enforced in endpoints).
- ❌ Never use `db.commit()` without `await` — it causes `RuntimeWarning`.
- ❌ Never use `next(override_get_db())` — it breaks async context.

---

## 🧪 Why Use Async Tests?

Using **fully asynchronous tests** ensures:

| Reason | Explanation |
|------|-------------|
| 🔁 Realism | Tests mirror production behavior exactly |
| 🐞 Fewer Bugs | No "works in dev, fails in prod" due to sync/async mismatch |
| 🔐 Security | Full end-to-end auth flow with JWT and async DB lookup |
| 📦 Simplicity | One code path, not two (no dual-stack complexity) |

We no longer need to maintain separate sync/async logic.

---

## 📋 Best Practices for Writing Tests

### ✅ Use `authenticated_client` fixture
```python
@pytest_asyncio.fixture
async def authenticated_client(override_get_db, test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    async with AsyncClient(...) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c
```

### ✅ Always `await` async operations
```python
await db_session.commit()
await db_session.refresh(task)
```

### ✅ Filter by `user_id` in queries
```python
result = await db.execute(
    select(Task).where(Task.user_id == current_user.id)
)
```

### ✅ Validate response structure
```python
data = response.json()
assert data["user_id"] == test_user.id
```

---

## 🧹 Cleanup

We clean up SQLite test files before running tests:

```makefile
test:
	@echo "🧪 Running tests..."
	rm -f test.db test.db-journal test.db-shm test.db-wal
	$(PYTEST) $(TEST_DIR)/ -v -s
```

Or use `:memory:` for full isolation.

---

## ✅ Final Architecture Summary

| Layer | Technology |
|------|------------|
| **Database (Prod)** | PostgreSQL + `asyncpg` |
| **Database (Test)** | SQLite + `aiosqlite` |
| **ORM** | SQLAlchemy 2.0+ with `AsyncSession` |
| **Test Client** | `httpx.AsyncClient` + `ASGITransport` |
| **Auth** | JWT + `get_current_user` dependency |
| **Ownership** | Enforced in all task endpoints |
