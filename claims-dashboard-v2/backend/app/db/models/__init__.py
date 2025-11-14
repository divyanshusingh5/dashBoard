"""
Database models for Claims Analytics Dashboard.

All models inherit from BaseModel which provides:
- Auto-generated table names
- Primary key (id)
- Utility methods (to_dict, from_dict)
"""

from .base import Base, BaseModel
from .claim import Claim
from .ssnb import SSNB
from .weight import Weight
from .venue_statistics import VenueStatistics
from .aggregated_cache import AggregatedCache

__all__ = [
    'Base',
    'BaseModel',
    'Claim',
    'SSNB',
    'Weight',
    'VenueStatistics',
    'AggregatedCache',
]
