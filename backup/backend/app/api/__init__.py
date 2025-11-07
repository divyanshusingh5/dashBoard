from fastapi import APIRouter
from app.api.endpoints import claims_router, recalibration_router, analytics_router, aggregation_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(claims_router, prefix="/claims", tags=["claims"])
api_router.include_router(recalibration_router, prefix="/recalibration", tags=["recalibration"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(aggregation_router, prefix="/aggregation", tags=["aggregation"])

__all__ = ["api_router"]

