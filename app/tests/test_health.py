"""
Tests for health check endpoints
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "task-backend"


@pytest.mark.asyncio
async def test_detailed_health_check(override_get_db):
    """Test detailed health check with database dependency"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/detailed")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "warning"]
    assert "checks" in data
    assert "database" in data["checks"]
    assert "system" in data["checks"]
    assert "application" in data["checks"]


@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test metrics endpoint"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/metrics")

    assert response.status_code == 200
    # Check that it returns Prometheus-style metrics
    content = response.text
    assert "system_cpu_percent" in content
    assert "system_memory_percent" in content
    assert "system_disk_percent" in content
