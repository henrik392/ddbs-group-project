"""Query executor for distributed queries."""

import psycopg
from typing import Any


class QueryExecutor:
    """Executes queries on target DBMS."""

    def __init__(self):
        self.connections = {
            "DBMS1": "postgresql://ddbs:ddbs@localhost:5434/ddbs1",
            "DBMS2": "postgresql://ddbs:ddbs@localhost:5433/ddbs2",
        }

    def execute(self, routing_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute query based on routing plan and return results."""
        results = []

        if routing_plan["strategy"] == "single":
            # Execute on single DBMS
            target = routing_plan["targets"][0]
            sql = routing_plan["queries"][target]
            results = self._execute_on_dbms(target, sql)

        elif routing_plan["strategy"] == "parallel":
            # Execute on all targets and merge results
            for target in routing_plan["targets"]:
                sql = routing_plan["queries"][target]
                target_results = self._execute_on_dbms(target, sql)
                results.extend(target_results)

        return results

    def _execute_on_dbms(self, dbms: str, sql: str) -> list[dict[str, Any]]:
        """Execute SQL on specific DBMS."""
        with psycopg.connect(self.connections[dbms]) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)

                # Get column names
                columns = (
                    [desc[0] for desc in cur.description] if cur.description else []
                )

                # Fetch all rows
                rows = cur.fetchall()

                # Return as list of dicts
                return [dict(zip(columns, row)) for row in rows]
