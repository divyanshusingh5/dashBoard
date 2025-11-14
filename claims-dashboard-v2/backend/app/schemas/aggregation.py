"""
Aggregation-related Pydantic schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class YearSeverityData(BaseModel):
    """Year and severity aggregation data."""

    year: int
    severity_category: str
    claim_count: int
    avg_actual_settlement: float
    avg_predicted_settlement: float
    avg_variance_pct: float
    high_variance_count: int


class CountyYearData(BaseModel):
    """County and year aggregation data."""

    county: str
    state: str
    year: int
    venue_rating: Optional[str] = None
    claim_count: int
    total_settlement: float
    avg_settlement: float
    avg_variance_pct: float
    high_variance_pct: float


class InjuryGroupData(BaseModel):
    """Injury group aggregation data."""

    injury_group: str
    injury_type: Optional[str] = None
    body_part: Optional[str] = None
    severity_category: str
    claim_count: int
    avg_settlement: float
    avg_predicted: float
    avg_variance_pct: float


class AdjusterPerformanceData(BaseModel):
    """Adjuster performance metrics."""

    adjuster_name: str
    claim_count: int
    avg_actual_settlement: float
    avg_predicted_settlement: float
    avg_variance_pct: float
    high_variance_count: int
    high_variance_pct: float


class VenueAnalysisData(BaseModel):
    """Venue analysis data."""

    venue_rating: str
    state: str
    county: str
    claim_count: int
    avg_settlement: float
    avg_predicted: float
    avg_variance_pct: float


class AggregatedDataResponse(BaseModel):
    """Complete aggregated dashboard data."""

    year_severity: List[YearSeverityData]
    county_year: List[CountyYearData]
    injury_group: List[InjuryGroupData]
    adjuster_performance: List[AdjusterPerformanceData]
    venue_analysis: List[VenueAnalysisData]
    kpis: Dict[str, Any]


class ExecutiveSummaryItem(BaseModel):
    """Executive summary variance driver item."""

    factor: str
    category: str
    claims: int
    avg_deviation: float
    abs_avg_deviation: float
    status: str


class ExecutiveSummaryResponse(BaseModel):
    """Executive summary with top variance drivers."""

    top_drivers: List[ExecutiveSummaryItem]
    total_analyzed: int
