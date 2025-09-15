# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.api.health import router as health_router
from app.utils.logging import LoggingMiddleware, setup_logging
from app.utils.rate_limiting import RateLimitMiddleware

# Setup logging first
setup_logging()

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A modern task management API with advanced features",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=3600)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/health",
    }
