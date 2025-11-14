"""
Base model class for all database models.
Provides common functionality and declarative base.
"""

from typing import Any, Dict
from sqlalchemy import Integer, Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common functionality.

    All models should inherit from this class to get:
    - Auto-generated table names
    - Common primary key
    - Utility methods (to_dict, from_dict)
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Auto-generate table name from class name (lowercase)."""
        return cls.__name__.lower()

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.

        Args:
            exclude: Set of column names to exclude

        Returns:
            Dictionary representation of the model

        Example:
            >>> claim = Claim(CLAIMID=123, DOLLARAMOUNTHIGH=50000)
            >>> claim.to_dict(exclude={'id'})
            {'CLAIMID': 123, 'DOLLARAMOUNTHIGH': 50000, ...}
        """
        exclude = exclude or set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary with column names as keys

        Returns:
            New model instance

        Example:
            >>> data = {'CLAIMID': 123, 'DOLLARAMOUNTHIGH': 50000}
            >>> claim = Claim.from_dict(data)
        """
        return cls(**{
            key: value
            for key, value in data.items()
            if hasattr(cls, key)
        })

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model instance from dictionary.

        Args:
            data: Dictionary with column names and new values

        Example:
            >>> claim.update_from_dict({'DOLLARAMOUNTHIGH': 60000})
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
