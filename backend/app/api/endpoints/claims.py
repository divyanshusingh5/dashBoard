from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from app.api.schemas import (
    ClaimsResponse,
    AggregatedData,
    KPIData,
    FilterOptions,
)
# Switch to SQLite data service for better performance
from app.services.data_service_sqlite import data_service_sqlite as data_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/claims", response_model=ClaimsResponse)
async def get_claims(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    injury_group: Optional[List[str]] = Query(None, description="Filter by injury groups"),
    adjuster: Optional[List[str]] = Query(None, description="Filter by adjusters"),
    state: Optional[List[str]] = Query(None, description="Filter by states"),
    year: Optional[List[int]] = Query(None, description="Filter by years"),
):
    """
    Get paginated claims with optional filters
    """
    try:
        filters = {}
        if injury_group:
            filters['injury_group'] = injury_group
        if adjuster:
            filters['adjuster'] = adjuster
        if state:
            filters['state'] = state
        if year:
            filters['year'] = year

        result = await data_service.get_paginated_claims(
            page=page,
            page_size=page_size,
            filters=filters if filters else None
        )

        return result

    except Exception as e:
        logger.error(f"Error getting claims: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/full")
async def get_full_claims():
    """
    Get all claims data (use with caution for large datasets)
    """
    try:
        claims = await data_service.get_full_claims_data()
        return {
            "claims": claims,
            "total": len(claims)
        }
    except Exception as e:
        logger.error(f"Error getting full claims: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# DEPRECATED: Aggregation moved to /api/v1/aggregation/aggregated
# This endpoint remains for backward compatibility but redirects internally
@router.get("/claims/aggregated")
async def get_aggregated_claims():
    """
    DEPRECATED: Use /api/v1/aggregation/aggregated instead
    This endpoint provides backward compatibility
    """
    from app.api.endpoints.aggregation import get_aggregated_data
    return await get_aggregated_data()

@router.get("/claims/kpis", response_model=KPIData)
async def get_kpis():
    """
    Get KPIs calculated from claims data
    """
    try:
        kpis = await data_service.calculate_kpis()
        return kpis
    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/filters", response_model=FilterOptions)
async def get_filter_options():
    """
    Get available filter options from data
    """
    try:
        options = await data_service.get_filter_options()
        return options
    except Exception as e:
        logger.error(f"Error getting filter options: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claims/stats")
async def get_claims_stats():
    """
    Get statistical summary of claims data
    """
    try:
        claims = await data_service.get_full_claims_data()

        if not claims:
            return {"error": "No data available"}

        import pandas as pd
        df = pd.DataFrame(claims)

        stats = {
            "total_claims": len(df),
            "numeric_columns": {},
            "categorical_columns": {}
        }

        # Numeric column stats
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            stats["numeric_columns"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            }

        # Categorical column stats
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:10]:  # Limit to first 10
            stats["categorical_columns"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict()
            }

        return stats

    except Exception as e:
        logger.error(f"Error getting claims stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
