from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StyleLeap Claims Analytics API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }

@app.on_event("startup")
async def startup_event():
    """Execute on startup"""
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"API docs available at: {settings.API_V1_STR}/docs")
    logger.info(f"Data directory: {settings.DATA_DIR}")

    # Check and initialize materialized views for performance
    try:
        from app.db.materialized_views import check_materialized_views_exist, create_all_materialized_views
        import asyncio

        loop = asyncio.get_event_loop()
        views_exist = await loop.run_in_executor(None, check_materialized_views_exist)

        if not views_exist:
            logger.warning("⚠ Materialized views not found - Performance may be degraded for large datasets")
            logger.info("Creating materialized views...")
            await loop.run_in_executor(None, create_all_materialized_views)
            logger.info("✓ Materialized views created. Run POST /api/v1/aggregation/refresh-cache to populate with data.")
        else:
            logger.info("✓ Materialized views active - Ready for 5M+ record performance")

    except Exception as e:
        logger.warning(f"Could not check materialized views: {e}")
        logger.warning("Dashboard will work but may be slower for large datasets")

@app.on_event("shutdown")
async def shutdown_event():
    """Execute on shutdown"""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
