"""
Pydantic validation models for API endpoints
Ensures input validation for production 5M+ claims system
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class VenueShiftParams(BaseModel):
    """
    Validation model for venue shift analysis parameters
    """
    months: int = Field(
        default=6,
        ge=1,
        le=24,
        description="Analysis period in months (1-24)"
    )

    @field_validator('months')
    @classmethod
    def validate_months(cls, v):
        if v < 1:
            raise ValueError('months must be at least 1')
        if v > 24:
            raise ValueError('months cannot exceed 24 (performance constraint for 5M+ claims)')
        return v


class AggregatedDataParams(BaseModel):
    """
    Validation model for aggregated data endpoint
    """
    use_fast: bool = Field(
        default=True,
        description="Use materialized views for fast aggregation"
    )


class FilterParams(BaseModel):
    """
    Validation model for dashboard filter parameters
    """
    county: Optional[str] = Field(
        default=None,
        max_length=100,
        description="County name filter"
    )
    venue_rating: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Venue rating filter"
    )
    injury_group: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Injury group code filter"
    )
    severity: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Severity level filter"
    )
    date_from: Optional[str] = Field(
        default=None,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Start date in YYYY-MM-DD format"
    )
    date_to: Optional[str] = Field(
        default=None,
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="End date in YYYY-MM-DD format"
    )

    @field_validator('county', 'venue_rating', 'injury_group', 'severity')
    @classmethod
    def prevent_sql_injection(cls, v):
        """Prevent potential SQL injection attempts"""
        if v is not None:
            # Check for suspicious patterns
            dangerous_patterns = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
            v_upper = v.upper()
            for pattern in dangerous_patterns:
                if pattern in v_upper:
                    raise ValueError(f'Invalid characters detected in input')
        return v


class WeightUpdateParams(BaseModel):
    """
    Validation model for weight update parameters
    """
    factor_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Factor name to update"
    )
    new_weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="New weight value (0.0-1.0)"
    )

    @field_validator('new_weight')
    @classmethod
    def validate_weight_range(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v


class PaginationParams(BaseModel):
    """
    Validation model for pagination parameters
    """
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )
    page_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Number of items per page (1-1000)"
    )

    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v):
        if v > 1000:
            raise ValueError('page_size cannot exceed 1000 for performance reasons')
        return v
