"""
Database connection management with support for both SQLite and Snowflake.
Provides connection factory, session management, and dependency injection.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings


class DatabaseFactory:
    """Factory for creating database engines based on configuration."""

    @staticmethod
    def create_engine() -> Engine:
        """Create appropriate database engine based on DATABASE_TYPE."""

        if settings.is_sqlite:
            return DatabaseFactory._create_sqlite_engine()
        elif settings.is_snowflake:
            return DatabaseFactory._create_snowflake_engine()
        else:
            raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")

    @staticmethod
    def _create_sqlite_engine() -> Engine:
        """Create SQLite engine with optimized settings."""
        engine = create_engine(
            settings.database_url,
            echo=settings.DEBUG,
            connect_args={
                "check_same_thread": False,  # Required for FastAPI
                "timeout": 30,
            },
            poolclass=StaticPool,  # Use static pool for SQLite
            pool_pre_ping=True,  # Verify connections before using
        )

        # Enable foreign key constraints for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            cursor.close()

        return engine

    @staticmethod
    def _create_snowflake_engine() -> Engine:
        """Create Snowflake engine with optimized settings."""
        engine = create_engine(
            settings.database_url,
            echo=settings.DEBUG,
            pool_size=settings.SNOWFLAKE_POOL_SIZE,
            max_overflow=settings.SNOWFLAKE_MAX_OVERFLOW,
            pool_timeout=30,
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True,  # Verify connections before using
        )

        return engine


# Create global engine instance
engine = DatabaseFactory.create_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
            pass

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """
    Get a new database session (for use outside of FastAPI dependency injection).

    Returns:
        Session: SQLAlchemy database session

    Note:
        Remember to close the session when done: session.close()
    """
    return SessionLocal()


# Health check function
async def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = get_session()
        # Try a simple query
        db.execute("SELECT 1" if settings.is_sqlite else "SELECT 1 as test")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
