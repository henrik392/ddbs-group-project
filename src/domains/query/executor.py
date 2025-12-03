"""Query executor for distributed queries."""

import psycopg
from typing import Any


class QueryExecutor:
    """Executes queries on target DBMS."""

    def __init__(self):
        self.connections = {
            "DBMS1": "postgresql://ddbs:ddbs@localhost:5434/ddbs1",
            "DBMS1-STANDBY": "postgresql://ddbs:ddbs@localhost:5435/ddbs1",
            "DBMS2": "postgresql://ddbs:ddbs@localhost:5433/ddbs2",
            "DBMS3": "postgresql://ddbs:ddbs@localhost:5436/ddbs3",
        }
        self.standby_map = {"DBMS1": "DBMS1-STANDBY"}  # Primary -> Standby mapping

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

        elif routing_plan["strategy"] == "join":
            # Execute join query (Popular-Rank with Article details)
            results = self._execute_join(routing_plan)

        return results

    def _execute_join(self, routing_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute distributed join for Popular-Rank + Article."""
        # Step 1: Get Popular-Rank data
        rank_target = routing_plan["rank_target"]
        rank_query = routing_plan["rank_query"]
        rank_results = self._execute_on_dbms(rank_target, rank_query)

        if not rank_results:
            return []

        # Step 2: Extract article IDs from ranking
        article_aids = rank_results[0]["articleaidlist"].split(",")

        # Step 3: Fetch article details for those IDs
        aids_str = ",".join(f"'{aid}'" for aid in article_aids)
        article_query = (
            f'SELECT aid, title, category, abstract, text, image, video FROM "article" '
            f"WHERE aid IN ({aids_str})"
        )

        # Query both DBMS to get all articles
        article_results = []
        for target in ["DBMS1", "DBMS2"]:
            target_results = self._execute_on_dbms(target, article_query)
            article_results.extend(target_results)

        # Step 4: Merge ranking with article details (maintain order)
        merged = []
        article_map = {str(a["aid"]): a for a in article_results}
        for aid in article_aids:
            if aid in article_map:
                merged.append(article_map[aid])

        return merged

    def _execute_on_dbms(self, dbms: str, sql: str) -> list[dict[str, Any]]:
        """Execute SQL on specific DBMS with standby fallback."""
        try:
            # Try primary DBMS
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

        except Exception as e:
            # Try standby if primary fails
            if dbms in self.standby_map:
                standby_dbms = self.standby_map[dbms]
                print(f"⚠ {dbms} failed, trying standby {standby_dbms}")

                with psycopg.connect(self.connections[standby_dbms]) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql)

                        # Get column names
                        columns = (
                            [desc[0] for desc in cur.description]
                            if cur.description
                            else []
                        )

                        # Fetch all rows
                        rows = cur.fetchall()

                        # Return as list of dicts
                        return [dict(zip(columns, row)) for row in rows]
            else:
                # No standby available, re-raise exception
                raise e
