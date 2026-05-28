from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import BASE_DIR
from app.database import engine, Base
import app.models
from app.routes.health import router as health_router
from app.routes.document import router as document_router
from app.routes.department import router as department_router
from app.routes.worker import router as worker_router
from app.routes.company import router as company_router
from app.routes.company_logo import router as company_logo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Daily Report Automation Backend",
    description="A refactored FastAPI backend following Route-Repository-Service-Schema-Database pattern.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder (ensure the folder path is correct relative to BASE_DIR)
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register routes
app.include_router(health_router, prefix="")
app.include_router(document_router, prefix="")

app.include_router(worker_router,prefix="")
app.include_router(department_router, prefix="")
app.include_router(company_router, prefix="")
app.include_router(company_logo_router, prefix="")
    