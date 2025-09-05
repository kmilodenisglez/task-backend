# Testing Strategy

> **Note:** In `TESTING` mode, we use **synchronous SQLite** to avoid event loop and asyncpg issues.  
> The production version of the app remains **100% asynchronous** using `asyncpg`.

This document explains the testing architecture and best practices for the project.

---

## 🧱 Testing Architecture: "Dual-Stack Persistence" Pattern

We use a **dual-stack persistence** strategy to separate concerns between development/production and testing:

- ✅ **Production/Development**: Asynchronous mode with `asyncpg` + PostgreSQL
- ✅ **Testing**: Synchronous mode with SQLite in-memory database

This approach avoids common concurrency issues like:
```
asyncpg.exceptions._base.InterfaceError: cannot perform operation: another operation is in progress
```
and
```
RuntimeError: Task ... got Future ... attached to a different loop
```

---

## ✅ Advantages of This Approach

| Benefit | Description |
|-------|-------------|
| 🚫 No asyncpg errors | SQLite is synchronous, so no event loop conflicts |
| ⚡ Faster tests | In-memory DB is much faster than spinning up PostgreSQL |
| 🧼 Cleaner tests | No need for `@pytest.mark.asyncio`, `await`, or `AsyncClient` |
| 🐍 Production-safe | The real app still runs async with full performance |
| 🔒 Isolation | Each test runs in a transaction that is rolled back after execution |

---

## 🔧 How It Works

### 1. Mode Detection
The `TESTING` mode is controlled via the `settings.testing` flag (from `pydantic-settings`), not environment variables.

```python
# app/config.py
class Settings(BaseSettings):
    testing: bool = False  # Can be set in .env or overridden in tests
```

During tests, this is set automatically in `conftest.py`.

### 2. Database Switching
In `app/database.py`, the engine and session type are chosen based on `settings.testing`:

- `settings.testing = True` → SQLite + `Session` (synchronous)
- `settings.testing = False` → PostgreSQL + `AsyncSession` (asynchronous)

### 3. Session Isolation
Each test gets a fresh database session wrapped in a transaction. After the test, the transaction is **rolled back**, ensuring no data leaks.

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

- This setup uses `TestClient` from `fastapi.testclient`, not `AsyncClient`.
- The `TESTING` mode is activated automatically in `conftest.py`.
- Never commit `.env` or `*.egg-info/` to Git — they are ignored via `.gitignore`.

---

## 🧪 Why Not Use Async Tests?

While possible, fully asynchronous tests with `AsyncClient` and `asyncpg` require:
- Complex session and transaction lifecycle management
- Careful event loop handling
- Shared connection issues

This synchronous testing layer is **simpler, faster, and more reliable** for unit and integration tests.

For end-to-end async testing (e.g., WebSockets), consider a separate `tests_async/` suite.
