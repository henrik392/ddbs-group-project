"""Query coordinator with datacenter-aware caching."""

from typing import Any

from src.config import get_datacenter_for_dbms
from src.domains.cache.manager import CacheManager

from .executor import QueryExecutor
from .router import QueryRouter


class QueryCoordinator:
    """Main query coordinator with location-aware caching."""

    def __init__(self):
        self.router = QueryRouter()
        self.executor = QueryExecutor()
        self.cache = CacheManager()

    def execute(self, sql: str, use_cache: bool = True) -> list[dict[str, Any]]:
        """Execute distributed query with datacenter-aware caching."""

        # Route query FIRST to determine target datacenter
        routing_plan = self.router.route(sql)
        target_datacenter = self._determine_cache_datacenter(routing_plan)

        # Check cache
        if use_cache:
            cached = self.cache.get(sql, datacenter=target_datacenter)
            if cached:
                print(f"✓ Cache hit ({target_datacenter})")
                return cached

        # Execute query
        print(
            f"✓ Routing: {routing_plan['strategy']} on {', '.join(routing_plan['targets'])}"
        )
        results = self.executor.execute(routing_plan)
        print(f"✓ Retrieved {len(results)} rows")

        # Cache results
        if use_cache:
            self.cache.set(sql, results, datacenter=target_datacenter)

        return results

    def _determine_cache_datacenter(self, routing_plan: dict) -> str:
        """Determine which datacenter cache to use.

        - DBMS1 only → DC1
        - DBMS2 only → DC2
        - Both → DC1 (default)
        """
        targets = routing_plan["targets"]

        all_dc1 = all(get_datacenter_for_dbms(t) == "DC1" for t in targets)
        if all_dc1:
            return "DC1"

        all_dc2 = all(get_datacenter_for_dbms(t) == "DC2" for t in targets)
        if all_dc2:
            return "DC2"

        return "DC1"

    def clear_cache(self, datacenter=None):
        """Clear cache."""
        self.cache.clear(datacenter)
        if datacenter:
            print(f"✓ Cache cleared ({datacenter})")
        else:
            print("✓ Cache cleared (all datacenters)")
