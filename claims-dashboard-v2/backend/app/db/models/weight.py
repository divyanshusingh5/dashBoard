"""
Weight model - Feature weights configuration for predictive model.
"""

from sqlalchemy import Column, Integer, String, Float, Text, Index

from .base import BaseModel


class Weight(BaseModel):
    """
    Weights table - stores feature weights from weights.csv.

    Used for:
    - Model weight configuration
    - Recalibration bounds (min/max)
    - Feature categorization
    """

    __tablename__ = 'weights'

    # ==========================================
    # Weight Configuration
    # ==========================================
    factor_name = Column(String(200), unique=True, nullable=False, index=True)
    base_weight = Column(Float, nullable=False)
    min_weight = Column(Float, nullable=False)
    max_weight = Column(Float, nullable=False)
    category = Column(String(100), index=True)
    description = Column(Text)

    # ==========================================
    # Indexes
    # ==========================================
    __table_args__ = (
        Index('idx_category', 'category'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Weight(factor={self.factor_name}, base={self.base_weight})>"

    @property
    def weight_range(self) -> tuple:
        """Get (min, max) weight range."""
        return (self.min_weight, self.max_weight)

    @property
    def weight_span(self) -> float:
        """Get the span between min and max weights."""
        return self.max_weight - self.min_weight

    def is_within_bounds(self, weight: float) -> bool:
        """
        Check if a weight value is within allowed bounds.

        Args:
            weight: Weight value to check

        Returns:
            True if weight is within [min_weight, max_weight]
        """
        return self.min_weight <= weight <= self.max_weight

    def clamp_weight(self, weight: float) -> float:
        """
        Clamp weight to valid range.

        Args:
            weight: Weight value to clamp

        Returns:
            Weight clamped to [min_weight, max_weight]
        """
        return max(self.min_weight, min(weight, self.max_weight))
