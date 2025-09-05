# Note: In TESTING mode, we use synchronous SQLite to avoid event loop issues.
# The production version of the app remains 100% asynchronous using asyncpg.


### 🧱 Switching to synchronous mode during tests using the "Dual-stack persistence" pattern

### 🎯 Advantages

1. ✅ **Eliminates asyncpg errors**
   Using synchronous SQLite for tests avoids the "operation in progress" issue.

2. ✅ **Faster and cleaner for testing**
   In-memory SQLite is faster than setting up a PostgreSQL database.

3. ✅ **Simpler and more readable tests**
   You don't need `@pytest.mark.asyncio`, `await`, or `AsyncClient`.

4. ✅ **Production remains asynchronous and efficient**
   Your production API still uses `asyncpg` and benefits from the full performance of asyncio.

5. ✅ **Perfect isolation between tests**
   Each test uses a new connection with transaction rollback.
