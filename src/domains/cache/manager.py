"""Location-aware cache manager with failover support."""

import hashlib
import json
from typing import Any, Literal, Optional

import redis

from src.config import CACHE_KEY_PREFIX, CACHE_TTL, get_redis_for_datacenter


class CacheManager:
    """Manages caching with datacenter awareness and failover."""

    def __init__(self):
        self.ttl = CACHE_TTL
        self.connections = {}

    def _get_redis_client(
        self, datacenter: Literal["DC1", "DC2", "STANDBY"]
    ) -> redis.Redis:
        """Get or create Redis client with connection pooling."""
        if datacenter not in self.connections:
            config = get_redis_for_datacenter(datacenter)
            self.connections[datacenter] = redis.Redis(
                host=config["host"],
                port=config["port"],
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

        return self.connections[datacenter]

    def get(
        self, sql: str, datacenter: Literal["DC1", "DC2"]
    ) -> Optional[list[dict[str, Any]]]:
        """Get cached query result from datacenter-specific cache."""
        cache_key = self._cache_key(sql)

        try:
            # Try datacenter primary cache
            client = self._get_redis_client(datacenter)
            cached = client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"⚠ {datacenter} Redis failed: {e}")

            # Fallback to shared standby
            try:
                client = self._get_redis_client("STANDBY")
                cached = client.get(cache_key)
                if cached:
                    print(f"✓ Cache hit from shared standby (for {datacenter})")
                    return json.loads(cached)
            except Exception as standby_error:
                print(f"⚠ Standby Redis also failed: {standby_error}")

        return None

    def set(
        self, sql: str, results: list[dict[str, Any]], datacenter: Literal["DC1", "DC2"]
    ):
        """Cache query result in datacenter-specific cache."""
        cache_key = self._cache_key(sql)
        value = json.dumps(results)

        try:
            client = self._get_redis_client(datacenter)
            client.setex(cache_key, self.ttl, value)
        except Exception as e:
            print(f"⚠ Failed to cache in {datacenter} Redis: {e}")

    def clear(self, datacenter: Optional[Literal["DC1", "DC2", "STANDBY"]] = None):
        """Clear cache (specific datacenter or all)."""
        datacenters = [datacenter] if datacenter else ["DC1", "DC2", "STANDBY"]

        for dc in datacenters:
            pattern = f"{CACHE_KEY_PREFIX}:*"
            try:
                client = self._get_redis_client(dc)
                for key in client.scan_iter(pattern):
                    client.delete(key)
            except Exception as e:
                print(f"⚠ Failed to clear {dc} cache: {e}")

    def _cache_key(self, sql: str) -> str:
        """Generate cache key from SQL."""
        return f"{CACHE_KEY_PREFIX}:{hashlib.md5(sql.encode()).hexdigest()}"
