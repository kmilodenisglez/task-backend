# app/main.py
from fastapi import FastAPI
from app.api.v1 import api_router
# from app.database import Base, engine

# Create tables (for initial development only, then use Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task API", version="1.0")

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Task API"}