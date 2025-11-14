"""
Claim-related Pydantic schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ClaimBase(BaseModel):
    """Base claim schema with common fields."""

    CLAIMID: int
    VERSIONID: Optional[int] = None
    DOLLARAMOUNTHIGH: Optional[float] = None
    CAUSATION_HIGH_RECOMMENDATION: Optional[float] = None
    variance_pct: Optional[float] = None
    CLAIMCLOSEDDATE: Optional[str] = None
    COUNTYNAME: Optional[str] = None
    VENUERATING: Optional[str] = None
    PRIMARY_INJURY_BY_SEVERITY: Optional[str] = None
    ADJUSTERNAME: Optional[str] = None


class ClaimResponse(ClaimBase):
    """Full claim response with all fields."""

    id: int
    EXPSR_NBR: Optional[str] = None
    SETTLEMENTAMOUNT: Optional[int] = None
    GENERALS: Optional[float] = None
    PRIMARY_BODYPART_BY_SEVERITY: Optional[str] = None
    PRIMARY_INJURYGROUP_CODE_BY_SEVERITY: Optional[str] = None
    PRIMARY_INJURY_SEVERITY_SCORE: Optional[float] = None
    CALCULATED_SEVERITY_SCORE: Optional[float] = None
    CALCULATED_CAUSATION_SCORE: Optional[float] = None
    VENUESTATE: Optional[str] = None
    IOL: Optional[int] = None
    AGE: Optional[int] = None
    GENDER: Optional[str] = None
    HASATTORNEY: Optional[str] = None
    SETTLEMENT_DAYS: Optional[int] = None
    CAUTION_LEVEL: Optional[str] = None

    class Config:
        from_attributes = True


class ClaimFilters(BaseModel):
    """Claim filtering parameters."""

    version_id: Optional[List[int]] = Field(None, description="Filter by version IDs")
    county: Optional[List[str]] = Field(None, description="Filter by counties")
    venue_rating: Optional[List[str]] = Field(None, description="Filter by venue ratings")
    year: Optional[List[int]] = Field(None, description="Filter by claim year")
    adjuster: Optional[List[str]] = Field(None, description="Filter by adjuster names")
    injury_group: Optional[List[str]] = Field(None, description="Filter by injury groups")
    caution_level: Optional[List[str]] = Field(None, description="Filter by caution levels")
    min_variance: Optional[float] = Field(None, description="Minimum variance percentage")
    max_variance: Optional[float] = Field(None, description="Maximum variance percentage")
    min_amount: Optional[float] = Field(None, description="Minimum settlement amount")
    max_amount: Optional[float] = Field(None, description="Maximum settlement amount")


class ClaimListResponse(BaseModel):
    """Paginated list of claims."""

    data: List[ClaimResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class KPIResponse(BaseModel):
    """Overall KPI metrics."""

    total_claims: int = Field(..., description="Total number of claims")
    avg_settlement: float = Field(..., description="Average settlement amount")
    avg_days: float = Field(..., description="Average settlement days")
    avg_variance: float = Field(..., description="Average variance percentage")
    high_variance_pct: float = Field(..., description="Percentage of high variance claims")
    overprediction_rate: float = Field(..., description="Overprediction rate")
    underprediction_rate: float = Field(..., description="Underprediction rate")


class FilterOptionsResponse(BaseModel):
    """Available filter options."""

    versions: List[int]
    counties: List[str]
    venue_ratings: List[str]
    years: List[int]
    adjusters: List[str]
    injury_groups: List[str]
    caution_levels: List[str]
