"""
Claims API Endpoints
Handles claim retrieval, filtering, pagination, and statistics.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc, asc, text
from typing import List, Optional
import logging

from app.core.database import get_db
from app.db.models import Claim, SSNB
from app.schemas.claim import (
    ClaimResponse,
    ClaimListResponse,
    ClaimFilters,
    KPIResponse,
    FilterOptionsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("/", response_model=ClaimListResponse)
def get_claims(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=10000, description="Items per page"),
    version_id: Optional[List[int]] = Query(None),
    county: Optional[List[str]] = Query(None),
    venue_rating: Optional[List[str]] = Query(None),
    year: Optional[List[int]] = Query(None),
    adjuster: Optional[List[str]] = Query(None),
    injury_group: Optional[List[str]] = Query(None),
    caution_level: Optional[List[str]] = Query(None),
    min_variance: Optional[float] = Query(None),
    max_variance: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("CLAIMID", description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of claims with optional filters.

    Supports filtering by:
    - version_id, county, venue_rating, year
    - adjuster, injury_group, caution_level
    - variance range (min_variance, max_variance)

    Returns paginated results with total count.
    """
    try:
        query = db.query(Claim)

        # Apply filters
        if version_id:
            query = query.filter(Claim.VERSIONID.in_(version_id))
        if county:
            query = query.filter(Claim.COUNTYNAME.in_(county))
        if venue_rating:
            query = query.filter(Claim.VENUERATING.in_(venue_rating))
        if year:
            # Extract year from CLAIMCLOSEDDATE string
            year_conditions = [
                func.substr(Claim.CLAIMCLOSEDDATE, 1, 4) == str(y) for y in year
            ]
            query = query.filter(func.or_(*year_conditions))
        if adjuster:
            query = query.filter(Claim.ADJUSTERNAME.in_(adjuster))
        if injury_group:
            query = query.filter(Claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY.in_(injury_group))
        if caution_level:
            query = query.filter(Claim.CAUTION_LEVEL.in_(caution_level))
        if min_variance is not None:
            query = query.filter(Claim.variance_pct >= min_variance)
        if max_variance is not None:
            query = query.filter(Claim.variance_pct <= max_variance)

        # Get total count
        total = query.count()

        # Apply sorting
        if sort_by and hasattr(Claim, sort_by):
            column = getattr(Claim, sort_by)
            if sort_order == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))

        # Apply pagination
        offset = (page - 1) * page_size
        claims = query.offset(offset).limit(page_size).all()

        # Convert to response models
        claim_responses = [ClaimResponse.from_orm(claim) for claim in claims]

        total_pages = (total + page_size - 1) // page_size

        return ClaimListResponse(
            data=claim_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error fetching claims: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis", response_model=KPIResponse)
def get_kpis(db: Session = Depends(get_db)):
    """
    Get overall KPI metrics from materialized view or calculate from claims.

    Returns:
    - total_claims: Total number of claims
    - avg_settlement: Average settlement amount
    - avg_days: Average settlement days
    - avg_variance: Average variance percentage
    - high_variance_pct: Percentage with >20% variance
    - overprediction_rate: Percentage overpredicted
    - underprediction_rate: Percentage underpredicted
    """
    try:
        # Try to get from materialized view first
        try:
            result = db.execute(text("SELECT * FROM mv_kpi_summary")).first()
            if result:
                return KPIResponse(
                    total_claims=result[0] or 0,
                    avg_settlement=round(result[1] or 0, 2),
                    avg_days=round(result[2] or 0, 2),
                    avg_variance=round(result[3] or 0, 2),
                    high_variance_pct=round(result[4] or 0, 2),
                    overprediction_rate=round(result[5] or 0, 2),
                    underprediction_rate=round(result[6] or 0, 2)
                )
        except:
            logger.info("Materialized view not found, calculating KPIs from claims table")

        # Calculate from claims table if view doesn't exist
        stats = db.query(
            func.count(Claim.id).label('total_claims'),
            func.avg(Claim.DOLLARAMOUNTHIGH).label('avg_settlement'),
            func.avg(Claim.SETTLEMENT_DAYS).label('avg_days'),
            func.avg(func.abs(Claim.variance_pct)).label('avg_variance')
        ).first()

        total = stats.total_claims or 0

        if total == 0:
            return KPIResponse(
                total_claims=0,
                avg_settlement=0,
                avg_days=0,
                avg_variance=0,
                high_variance_pct=0,
                overprediction_rate=0,
                underprediction_rate=0
            )

        # Calculate percentages
        high_variance = db.query(func.count(Claim.id)).filter(
            func.abs(Claim.variance_pct) > 20
        ).scalar() or 0

        overpredictions = db.query(func.count(Claim.id)).filter(
            Claim.variance_pct < 0
        ).scalar() or 0

        underpredictions = db.query(func.count(Claim.id)).filter(
            Claim.variance_pct > 0
        ).scalar() or 0

        return KPIResponse(
            total_claims=total,
            avg_settlement=round(stats.avg_settlement or 0, 2),
            avg_days=round(stats.avg_days or 0, 2),
            avg_variance=round(stats.avg_variance or 0, 2),
            high_variance_pct=round((high_variance / total) * 100, 2),
            overprediction_rate=round((overpredictions / total) * 100, 2),
            underprediction_rate=round((underpredictions / total) * 100, 2)
        )

    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters", response_model=FilterOptionsResponse)
def get_filter_options(db: Session = Depends(get_db)):
    """
    Get available filter options for claims.

    Returns distinct values for:
    - versions, counties, venue_ratings, years
    - adjusters, injury_groups, caution_levels
    """
    try:
        versions = [v[0] for v in db.query(distinct(Claim.VERSIONID)).filter(
            Claim.VERSIONID.isnot(None)
        ).order_by(Claim.VERSIONID).all()]

        counties = [c[0] for c in db.query(distinct(Claim.COUNTYNAME)).filter(
            Claim.COUNTYNAME.isnot(None),
            Claim.COUNTYNAME != ''
        ).order_by(Claim.COUNTYNAME).all()]

        venue_ratings = [v[0] for v in db.query(distinct(Claim.VENUERATING)).filter(
            Claim.VENUERATING.isnot(None),
            Claim.VENUERATING != ''
        ).order_by(Claim.VENUERATING).all()]

        # Extract years from date strings
        years_raw = db.query(
            distinct(func.substr(Claim.CLAIMCLOSEDDATE, 1, 4))
        ).filter(
            Claim.CLAIMCLOSEDDATE.isnot(None)
        ).all()
        years = sorted([int(y[0]) for y in years_raw if y[0] and y[0].isdigit()])

        adjusters = [a[0] for a in db.query(distinct(Claim.ADJUSTERNAME)).filter(
            Claim.ADJUSTERNAME.isnot(None),
            Claim.ADJUSTERNAME != '',
            Claim.ADJUSTERNAME != 'System System'
        ).order_by(Claim.ADJUSTERNAME).limit(100).all()]

        injury_groups = [i[0] for i in db.query(
            distinct(Claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY)
        ).filter(
            Claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY.isnot(None),
            Claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY != ''
        ).order_by(Claim.PRIMARY_INJURYGROUP_CODE_BY_SEVERITY).all()]

        caution_levels = [c[0] for c in db.query(distinct(Claim.CAUTION_LEVEL)).filter(
            Claim.CAUTION_LEVEL.isnot(None),
            Claim.CAUTION_LEVEL != ''
        ).order_by(Claim.CAUTION_LEVEL).all()]

        return FilterOptionsResponse(
            versions=versions,
            counties=counties,
            venue_ratings=venue_ratings,
            years=years,
            adjusters=adjusters,
            injury_groups=injury_groups,
            caution_levels=caution_levels
        )

    except Exception as e:
        logger.error(f"Error fetching filter options: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ssnb")
def get_ssnb_data(
    limit: int = Query(1000, ge=1, le=100000),
    db: Session = Depends(get_db)
):
    """
    Get SSNB (Single injury, Soft tissue, Neck/Back) data for recalibration.

    Returns claims used for weight recalibration with float-based clinical factors.
    """
    try:
        ssnb_records = db.query(SSNB).limit(limit).all()

        return {
            "data": [record.to_dict() for record in ssnb_records],
            "total": db.query(func.count(SSNB.id)).scalar()
        }

    except Exception as e:
        logger.error(f"Error fetching SSNB data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
