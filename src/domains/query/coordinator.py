"""Query coordinator with caching."""

import redis
import json
import hashlib
from typing import Any
from .router import QueryRouter
from .executor import QueryExecutor


class QueryCoordinator:
    """Main query coordinator with caching."""

    def __init__(self):
        self.router = QueryRouter()
        self.executor = QueryExecutor()
        self.cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.cache_ttl = 60  # 60 seconds default

    def execute(self, sql: str, use_cache: bool = True) -> list[dict[str, Any]]:
        """Execute distributed query with caching."""
        # Check cache first
        if use_cache:
            cache_key = self._cache_key(sql)
            cached = self.cache.get(cache_key)
            if cached:
                print("✓ Cache hit")
                return json.loads(cached)

        # Route query
        routing_plan = self.router.route(sql)
        print(
            f"✓ Routing: {routing_plan['strategy']} on {', '.join(routing_plan['targets'])}"
        )

        # Execute
        results = self.executor.execute(routing_plan)
        print(f"✓ Retrieved {len(results)} rows")

        # Cache results
        if use_cache:
            cache_key = self._cache_key(sql)
            self.cache.setex(cache_key, self.cache_ttl, json.dumps(results))

        return results

    def _cache_key(self, sql: str) -> str:
        """Generate cache key from SQL."""
        return f"query:{hashlib.md5(sql.encode()).hexdigest()}"

    def clear_cache(self):
        """Clear all cached queries."""
        pattern = "query:*"
        for key in self.cache.scan_iter(pattern):
            self.cache.delete(key)
        print("✓ Cache cleared")
