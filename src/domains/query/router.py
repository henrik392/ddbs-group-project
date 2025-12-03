"""Query router for distributed query processing."""

import re
from typing import Any


class QueryRouter:
    """Routes queries to appropriate DBMS based on fragmentation rules."""

    def route(self, sql: str) -> dict[str, Any]:
        """
        Analyze SQL and return routing plan.

        Returns:
            {
                "targets": ["DBMS1", "DBMS2"] or ["DBMS1"] or ["DBMS2"],
                "strategy": "parallel" or "single",
                "queries": {dbms: sql}
            }
        """
        sql_lower = sql.lower()

        # Extract table name
        table_match = re.search(r'from\s+"?(\w+)"?', sql_lower)
        if not table_match:
            raise ValueError("Could not parse table name from query")

        table = table_match.group(1)

        # Route based on table and conditions
        if table == "user":
            return self._route_user(sql, sql_lower)
        elif table == "article":
            return self._route_article(sql, sql_lower)
        elif table == "user_read":
            return self._route_read(sql)
        elif table == "be_read":
            return self._route_beread(sql, sql_lower)
        elif table == "popular_rank":
            return self._route_popularrank(sql, sql_lower)
        else:
            # Default: query all 3 and merge
            return {
                "targets": ["DBMS1", "DBMS2", "DBMS3"],
                "strategy": "parallel",
                "queries": {"DBMS1": sql, "DBMS2": sql, "DBMS3": sql},
            }

    def _route_user(self, sql: str, sql_lower: str) -> dict[str, Any]:
        """User table: route by region."""
        if "region" in sql_lower and "beijing" in sql_lower:
            return {
                "targets": ["DBMS1"],
                "strategy": "single",
                "queries": {"DBMS1": sql},
            }
        elif "region" in sql_lower and "hong kong" in sql_lower:
            return {
                "targets": ["DBMS2"],
                "strategy": "single",
                "queries": {"DBMS2": sql},
            }
        elif "region" in sql_lower and "shanghai" in sql_lower:
            return {
                "targets": ["DBMS3"],
                "strategy": "single",
                "queries": {"DBMS3": sql},
            }
        else:
            # No filter or other filter: query all 3 and merge
            return {
                "targets": ["DBMS1", "DBMS2", "DBMS3"],
                "strategy": "parallel",
                "queries": {"DBMS1": sql, "DBMS2": sql, "DBMS3": sql},
            }

    def _route_article(self, sql: str, sql_lower: str) -> dict[str, Any]:
        """Article table: route by category."""
        if "category" in sql_lower and "technology" in sql_lower:
            return {
                "targets": ["DBMS2"],
                "strategy": "single",
                "queries": {"DBMS2": sql},
            }
        elif "category" in sql_lower and "science" in sql_lower:
            # Science articles are replicated, query one (DBMS1 for load balancing)
            return {
                "targets": ["DBMS1"],
                "strategy": "single",
                "queries": {"DBMS1": sql},
            }
        else:
            # No filter: query DBMS1 and DBMS2 (DBMS3 has no articles)
            return {
                "targets": ["DBMS1", "DBMS2"],
                "strategy": "parallel",
                "queries": {"DBMS1": sql, "DBMS2": sql},
            }

    def _route_read(self, sql: str) -> dict[str, Any]:
        """Read table: co-located with User, query all 3 and merge."""
        return {
            "targets": ["DBMS1", "DBMS2", "DBMS3"],
            "strategy": "parallel",
            "queries": {"DBMS1": sql, "DBMS2": sql, "DBMS3": sql},
        }

    def _route_beread(self, sql: str, sql_lower: str) -> dict[str, Any]:
        """Be-Read table: replicated on both, query one for efficiency."""
        # For now, query DBMS2 as it has all articles
        return {"targets": ["DBMS2"], "strategy": "single", "queries": {"DBMS2": sql}}

    def _route_popularrank(self, sql: str, sql_lower: str) -> dict[str, Any]:
        """Popular-Rank table: route by temporalGranularity."""
        if "temporalgranularity" in sql_lower and "daily" in sql_lower:
            return {
                "targets": ["DBMS1"],
                "strategy": "single",
                "queries": {"DBMS1": sql},
            }
        elif "temporalgranularity" in sql_lower and (
            "weekly" in sql_lower or "monthly" in sql_lower
        ):
            return {
                "targets": ["DBMS2"],
                "strategy": "single",
                "queries": {"DBMS2": sql},
            }
        else:
            # No filter: query both
            return {
                "targets": ["DBMS1", "DBMS2"],
                "strategy": "parallel",
                "queries": {"DBMS1": sql, "DBMS2": sql},
            }
