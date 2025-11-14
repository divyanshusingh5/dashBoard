"""
VenueStatistics model - Pre-computed venue rating statistics.
Used for fast venue shift recommendations.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index

from .base import BaseModel


class VenueStatistics(BaseModel):
    """
    Pre-computed venue rating statistics table.

    Stores aggregated settlement statistics by:
    - Venue rating
    - Severity category (Low/Medium/High)
    - Causation category (Low/Medium/High)
    - Impact on Life (IOL)

    Used for fast venue rating shift recommendations.
    """

    __tablename__ = 'venue_statistics'

    # ==========================================
    # Grouping Dimensions
    # ==========================================
    VENUERATING = Column(String(50), nullable=False, index=True)
    VENUERATINGTEXT = Column(String(100))
    RATINGWEIGHT = Column(Float)
    SEVERITY_CATEGORY = Column(String(20), nullable=False, index=True)  # Low/Medium/High
    CAUSATION_CATEGORY = Column(String(20), nullable=False, index=True)  # Low/Medium/High
    IOL = Column(Integer, nullable=False, index=True)

    # ==========================================
    # Actual Settlement Statistics
    # ==========================================
    mean_actual = Column(Float)
    median_actual = Column(Float)
    stddev_actual = Column(Float)
    min_actual = Column(Float)
    max_actual = Column(Float)

    # ==========================================
    # Predicted Statistics
    # ==========================================
    mean_predicted = Column(Float)
    median_predicted = Column(Float)
    mode_predicted = Column(Float)
    stddev_predicted = Column(Float)

    # ==========================================
    # Error Metrics
    # ==========================================
    mean_absolute_error = Column(Float, index=True)  # Primary metric for recommendations
    median_absolute_error = Column(Float)
    mean_error_pct = Column(Float)

    # ==========================================
    # Statistical Measures
    # ==========================================
    coefficient_of_variation = Column(Float)  # stddev/mean - predictability measure

    # ==========================================
    # Confidence Metrics
    # ==========================================
    sample_size = Column(Integer, nullable=False, index=True)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)

    # ==========================================
    # Data Quality
    # ==========================================
    last_updated = Column(DateTime)
    data_period_start = Column(String(50))
    data_period_end = Column(String(50))

    # ==========================================
    # Composite Indexes for Fast Lookups
    # ==========================================
    __table_args__ = (
        Index('idx_venue_lookup', 'VENUERATING', 'SEVERITY_CATEGORY', 'CAUSATION_CATEGORY', 'IOL'),
        Index('idx_error_ranking', 'mean_absolute_error', 'sample_size'),
        Index('idx_venue_category', 'VENUERATING', 'SEVERITY_CATEGORY'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<VenueStatistics(rating={self.VENUERATING}, "
            f"sev={self.SEVERITY_CATEGORY}, "
            f"caus={self.CAUSATION_CATEGORY}, "
            f"iol={self.IOL}, "
            f"n={self.sample_size})>"
        )

    @property
    def is_statistically_significant(self) -> bool:
        """
        Check if sample size is large enough for reliable statistics.

        Returns:
            True if sample_size >= 30 (common threshold)
        """
        return self.sample_size >= 30

    @property
    def error_percentage(self) -> float:
        """
        Get mean absolute error as percentage of mean actual.

        Returns:
            Error percentage, or 0 if mean_actual is 0
        """
        if self.mean_actual and self.mean_actual != 0:
            return (self.mean_absolute_error / self.mean_actual) * 100
        return 0.0

    @property
    def predictability_rating(self) -> str:
        """
        Get predictability rating based on coefficient of variation.

        Returns:
            'Excellent', 'Good', 'Fair', or 'Poor'
        """
        if not self.coefficient_of_variation:
            return 'Unknown'

        cv = self.coefficient_of_variation
        if cv < 0.25:
            return 'Excellent'
        elif cv < 0.50:
            return 'Good'
        elif cv < 0.75:
            return 'Fair'
        else:
            return 'Poor'
