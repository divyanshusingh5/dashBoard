"""
AggregatedCache model - Cache for pre-computed aggregations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
import json
from typing import Any, Dict

from .base import BaseModel


class AggregatedCache(BaseModel):
    """
    Cache table for pre-computed aggregations.

    Speeds up dashboard loading for large datasets by storing
    frequently-accessed aggregated data as JSON.

    Cache types include:
    - 'county_year' - County-year aggregations
    - 'venue' - Venue analysis
    - 'year_severity' - Year-severity summaries
    - 'kpi_summary' - Overall KPIs
    """

    __tablename__ = 'aggregated_cache'

    # ==========================================
    # Cache Configuration
    # ==========================================
    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    cache_type = Column(String(100), index=True)
    data_json = Column(Text)  # Stored as JSON string
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # ==========================================
    # Indexes
    # ==========================================
    __table_args__ = (
        Index('idx_cache_type', 'cache_type', 'updated_at'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AggregatedCache(key={self.cache_key}, type={self.cache_type})>"

    @property
    def data(self) -> Dict[str, Any]:
        """
        Get cached data as dictionary.

        Returns:
            Parsed JSON data, or empty dict if parsing fails
        """
        if not self.data_json:
            return {}

        try:
            return json.loads(self.data_json)
        except json.JSONDecodeError:
            return {}

    @data.setter
    def data(self, value: Dict[str, Any]) -> None:
        """
        Set cached data from dictionary.

        Args:
            value: Dictionary to cache
        """
        self.data_json = json.dumps(value)
        self.updated_at = datetime.utcnow()

    @property
    def age_seconds(self) -> float:
        """
        Get cache age in seconds.

        Returns:
            Seconds since last update, or infinity if no update time
        """
        if not self.updated_at:
            return float('inf')

        return (datetime.utcnow() - self.updated_at).total_seconds()

    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """
        Check if cache is stale.

        Args:
            max_age_seconds: Maximum age in seconds (default: 5 minutes)

        Returns:
            True if cache is older than max_age_seconds
        """
        return self.age_seconds > max_age_seconds

    def refresh(self, data: Dict[str, Any]) -> None:
        """
        Refresh cache with new data.

        Args:
            data: New data to cache
        """
        self.data = data
        self.updated_at = datetime.utcnow()
