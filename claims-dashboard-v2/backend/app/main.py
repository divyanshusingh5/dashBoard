"""
FastAPI Main Application
Claims Analytics Dashboard v2.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core import settings, check_database_connection
from app.db.models import Base
from app.core.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database Type: {settings.DATABASE_TYPE}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 80)

    # Create tables if they don't exist (SQLAlchemy will handle this)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables verified/created")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")

    # Check database connection
    connected = await check_database_connection()
    if connected:
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed!")
        raise Exception("Cannot start application - database connection failed")

    logger.info("🚀 Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    logger.info("👋 Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Claims Analytics Dashboard with dual database support (SQLite/Snowflake)",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.DATABASE_TYPE,
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns database connection status and configuration.
    """
    db_connected = await check_database_connection()

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": {
            "type": settings.DATABASE_TYPE,
            "connected": db_connected
        },
        "cache_enabled": settings.CACHE_ENABLED,
        "materialized_views_enabled": settings.MATERIALIZED_VIEWS_ENABLED
    }


# Import and include routers
from app.api.endpoints import claims, aggregation

app.include_router(claims.router, prefix=settings.API_V1_PREFIX)
app.include_router(aggregation.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
