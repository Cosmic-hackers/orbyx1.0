"""FastAPI application — main entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database.models import initialize_database
from src.logging_config import setup_logging
from src.api.routes import satellites, collision, visibility, websocket_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown."""
    logger = setup_logging()
    logger.info("Starting Satellite Orbit Tools API")
    initialize_database()
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Satellite Orbit Tools API",
    description="Real-time satellite collision detection and monitoring system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(satellites.router, prefix="/api/v1/satellites", tags=["Satellites"])
app.include_router(collision.router, prefix="/api/v1/collision", tags=["Collision Detection"])
app.include_router(visibility.router, prefix="/api/v1/visibility", tags=["Visibility"])
app.include_router(websocket_routes.router, tags=["WebSocket"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Satellite Orbit Tools API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    from src.engine.cache import get_cache_stats
    from src.database.manager import SatelliteDB

    with SatelliteDB() as db:
        sat_count = db.get_satellite_count()

    return {
        "status": "healthy",
        "satellites_in_catalog": sat_count,
        "cache": get_cache_stats(),
    }
