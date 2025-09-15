"""
Health check and monitoring endpoints
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger("health")


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "task-backend",
        "version": "1.0.0",
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with system metrics.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "task-backend",
        "version": "1.0.0",
        "checks": {},
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        health_status["status"] = "unhealthy"
        logger.error("Database health check failed", extra={"error": str(e)})

    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_status["checks"]["system"] = {
            "status": "healthy",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
            },
        }

        # Alert if resources are high
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            health_status["checks"]["system"]["status"] = "warning"
            health_status["checks"]["system"][
                "message"
            ] = "High resource usage detected"

    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "unhealthy",
            "message": f"System metrics unavailable: {str(e)}",
        }
        logger.error("System health check failed", extra={"error": str(e)})

    # Application metrics
    health_status["checks"]["application"] = {
        "status": "healthy",
        "metrics": {
            "python_version": os.sys.version,
            "process_id": os.getpid(),
            "uptime_seconds": (
                datetime.now(timezone.utc)
                - datetime.fromtimestamp(psutil.Process().create_time(), timezone.utc)
            ).total_seconds(),
        },
    }

    return health_status


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus-style metrics endpoint.
    """
    metrics = []

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    metrics.extend(
        [
            f"# HELP system_cpu_percent CPU usage percentage",
            f"# TYPE system_cpu_percent gauge",
            f"system_cpu_percent {cpu_percent}",
            "",
            f"# HELP system_memory_percent Memory usage percentage",
            f"# TYPE system_memory_percent gauge",
            f"system_memory_percent {memory.percent}",
            "",
            f"# HELP system_disk_percent Disk usage percentage",
            f"# TYPE system_disk_percent gauge",
            f"system_disk_percent {disk.percent}",
            "",
        ]
    )

    return "\n".join(metrics)
