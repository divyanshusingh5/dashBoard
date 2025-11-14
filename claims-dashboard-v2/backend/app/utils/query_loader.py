"""
SQL Query Loader - Load SQL queries from organized .sql files.
Provides caching and template substitution for efficient query management.
"""

from pathlib import Path
from typing import Dict, Optional
import re

from app.core.config import settings


class QueryLoader:
    """
    Load and cache SQL queries from .sql files.

    Queries are organized in app/db/queries/ directory:
    - ddl/sqlite/ or ddl/snowflake/ - Table creation, indexes, views
    - dml/ - Insert, update, delete operations
    - dql/ - Select queries for data retrieval

    Examples:
        >>> loader = QueryLoader()
        >>> create_table_sql = loader.load_ddl("create_tables.sql")
        >>> claims_query = loader.load_dql("claims_queries.sql", "get_high_variance")
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "db" / "queries"
        self._cache: Dict[str, str] = {}
        self.db_type = settings.DATABASE_TYPE

    def load(self, query_path: str, use_cache: bool = True) -> str:
        """
        Load SQL query from file with optional caching.

        Args:
            query_path: Relative path from queries/ directory (e.g., "ddl/sqlite/create_tables.sql")
            use_cache: Whether to use cached version (default: True)

        Returns:
            str: SQL query content

        Raises:
            FileNotFoundError: If SQL file doesn't exist
        """
        if use_cache and query_path in self._cache:
            return self._cache[query_path]

        full_path = self.base_path / query_path

        if not full_path.exists():
            raise FileNotFoundError(f"SQL file not found: {full_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            query = f.read()

        if use_cache:
            self._cache[query_path] = query

        return query

    def load_ddl(self, filename: str) -> str:
        """
        Load DDL (Data Definition Language) query.
        Automatically selects correct database type (sqlite/snowflake).

        Args:
            filename: SQL filename (e.g., "create_tables.sql")

        Returns:
            str: SQL DDL query
        """
        return self.load(f"ddl/{self.db_type}/{filename}")

    def load_dml(self, filename: str) -> str:
        """
        Load DML (Data Manipulation Language) query.

        Args:
            filename: SQL filename (e.g., "refresh_materialized_views.sql")

        Returns:
            str: SQL DML query
        """
        return self.load(f"dml/{filename}")

    def load_dql(self, filename: str, query_name: Optional[str] = None) -> str:
        """
        Load DQL (Data Query Language) query.
        Optionally extract a named query from the file.

        Args:
            filename: SQL filename (e.g., "claims_queries.sql")
            query_name: Optional name of specific query to extract

        Returns:
            str: SQL DQL query

        Examples:
            >>> # Load entire file
            >>> loader.load_dql("claims_queries.sql")

            >>> # Load specific named query
            >>> loader.load_dql("claims_queries.sql", "get_high_variance")
        """
        content = self.load(f"dql/{filename}")

        if query_name:
            return self._extract_named_query(content, query_name)

        return content

    def _extract_named_query(self, content: str, query_name: str) -> str:
        """
        Extract a named query from SQL file.

        Named queries are marked with comments:
        -- QUERY: query_name
        SELECT ...
        -- END QUERY

        Args:
            content: Full SQL file content
            query_name: Name of query to extract

        Returns:
            str: Extracted SQL query

        Raises:
            ValueError: If named query not found
        """
        # Pattern: -- QUERY: name ... -- END QUERY
        pattern = rf"--\s*QUERY:\s*{query_name}\s*\n(.*?)--\s*END\s+QUERY"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if not match:
            raise ValueError(f"Named query '{query_name}' not found in file")

        return match.group(1).strip()

    def substitute(self, query: str, **params) -> str:
        """
        Substitute parameters in SQL query.

        Args:
            query: SQL query with {param} placeholders
            **params: Parameters to substitute

        Returns:
            str: Query with substituted parameters

        Examples:
            >>> query = "SELECT * FROM {table} WHERE id = {id}"
            >>> loader.substitute(query, table="claims", id=123)
            "SELECT * FROM claims WHERE id = 123"
        """
        return query.format(**params)

    def clear_cache(self):
        """Clear the query cache."""
        self._cache.clear()

    def reload(self, query_path: str) -> str:
        """
        Reload query from file, bypassing cache.

        Args:
            query_path: Relative path from queries/ directory

        Returns:
            str: Fresh SQL query content
        """
        return self.load(query_path, use_cache=False)


# Global instance
query_loader = QueryLoader()
