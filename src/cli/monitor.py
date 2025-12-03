#!/usr/bin/env python3
"""Monitoring system for distributed DBMS."""

import click
import psycopg
import redis
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@click.group()
def cli():
    """DBMS monitoring commands."""
    pass


@cli.command()
def status():
    """Show DBMS connection status and health."""
    print("=" * 60)
    print("DBMS STATUS REPORT")
    print("=" * 60)
    print()

    dbms_configs = {
        "DBMS1": {
            "host": "localhost",
            "port": 5434,
            "user": "ddbs",
            "password": "ddbs",
            "dbname": "ddbs1",
        },
        "DBMS1-STANDBY": {
            "host": "localhost",
            "port": 5435,
            "user": "ddbs",
            "password": "ddbs",
            "dbname": "ddbs1",
        },
        "DBMS2": {
            "host": "localhost",
            "port": 5433,
            "user": "ddbs",
            "password": "ddbs",
            "dbname": "ddbs2",
        },
        "DBMS3": {
            "host": "localhost",
            "port": 5436,
            "user": "ddbs",
            "password": "ddbs",
            "dbname": "ddbs3",
        },
    }

    for name, config in dbms_configs.items():
        print(f"[{name}] {config['host']}:{config['port']}")

        try:
            conn_str = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
            with psycopg.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    # Check connection
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]
                    print("  Status: ✓ ONLINE")
                    print(f"  Version: {version.split(',')[0]}")

                    # Database size
                    cur.execute(
                        f"SELECT pg_size_pretty(pg_database_size('{config['dbname']}'))"
                    )
                    db_size = cur.fetchone()[0]
                    print(f"  Database Size: {db_size}")

                    # Active connections
                    cur.execute(
                        f"SELECT count(*) FROM pg_stat_activity WHERE datname = '{config['dbname']}'"
                    )
                    connections = cur.fetchone()[0]
                    print(f"  Active Connections: {connections}")

                    print()

        except Exception as e:
            print("  Status: ✗ OFFLINE")
            print(f"  Error: {e}")
            print()

    # Check Redis
    print("[REDIS CACHE] localhost:6379")
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        info = r.info()
        print("  Status: ✓ ONLINE")
        print(f"  Version: {info['redis_version']}")
        print(f"  Memory Used: {info['used_memory_human']}")
        print(f"  Connected Clients: {info['connected_clients']}")
    except Exception as e:
        print("  Status: ✗ OFFLINE")
        print(f"  Error: {e}")

    print()


@cli.command()
def distribution():
    """Show data distribution across DBMS."""
    print("=" * 60)
    print("DATA DISTRIBUTION REPORT")
    print("=" * 60)
    print()

    # Fragmentation rules
    print("FRAGMENTATION RULES:")
    print("-" * 60)
    print("User Table:")
    print("  • region='Beijing' → DBMS1")
    print("  • region='Hong Kong' → DBMS2")
    print("  • region='Shanghai' → DBMS3")
    print()
    print("Article Table:")
    print("  • category='science' → DBMS1 & DBMS2 (replicated)")
    print("  • category='technology' → DBMS2")
    print("  • DBMS3 has no articles (users only)")
    print()
    print("Read Table:")
    print("  • Co-located with User table (no replication)")
    print("  • Beijing users' reads → DBMS1")
    print("  • Hong Kong users' reads → DBMS2")
    print("  • Shanghai users' reads → DBMS3")
    print()
    print("Be-Read Table:")
    print("  • Replicated on DBMS1, DBMS2, & DBMS3")
    print()
    print("Popular-Rank Table:")
    print("  • temporalGranularity='daily' → DBMS1")
    print("  • temporalGranularity='weekly' → DBMS2")
    print("  • temporalGranularity='monthly' → DBMS2")
    print()

    # Actual data distribution
    print("=" * 60)
    print("ACTUAL DATA DISTRIBUTION:")
    print("-" * 60)
    print()

    dbms_configs = {
        "DBMS1": "postgresql://ddbs:ddbs@localhost:5434/ddbs1",
        "DBMS1-STANDBY": "postgresql://ddbs:ddbs@localhost:5435/ddbs1",
        "DBMS2": "postgresql://ddbs:ddbs@localhost:5433/ddbs2",
        "DBMS3": "postgresql://ddbs:ddbs@localhost:5436/ddbs3",
    }

    tables = ["user", "article", "user_read", "be_read", "popular_rank"]

    for dbms_name, conn_str in dbms_configs.items():
        try:
            with psycopg.connect(conn_str) as conn:
                print(f"[{dbms_name}]")
                with conn.cursor() as cur:
                    for table in tables:
                        try:
                            # Get row count
                            cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                            count = cur.fetchone()[0]

                            # Get table size
                            cur.execute(
                                f"SELECT pg_size_pretty(pg_total_relation_size('\"{table}\"'))"
                            )
                            size = cur.fetchone()[0]

                            print(f"  {table:20s} {count:8d} rows  {size:>10s}")
                        except Exception:
                            print(f"  {table:20s} (not found)")

                print()

        except Exception as e:
            print(f"[{dbms_name}] ERROR: {e}")
            print()


@cli.command()
def workload():
    """Show query workload statistics from Redis cache."""
    print("=" * 60)
    print("WORKLOAD STATISTICS")
    print("=" * 60)
    print()

    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)

        # Get all cache keys
        keys = r.keys("query:*")
        total_queries = len(keys)

        print(f"Cached Queries: {total_queries}")
        print()

        if total_queries > 0:
            print("CACHE DETAILS:")
            print("-" * 60)

            # Get Redis stats
            info = r.info("stats")
            keyspace_hits = info.get("keyspace_hits", 0)
            keyspace_misses = info.get("keyspace_misses", 0)
            total_requests = keyspace_hits + keyspace_misses

            if total_requests > 0:
                hit_rate = (keyspace_hits / total_requests) * 100
                print(f"  Total Requests: {total_requests}")
                print(f"  Cache Hits: {keyspace_hits}")
                print(f"  Cache Misses: {keyspace_misses}")
                print(f"  Hit Rate: {hit_rate:.2f}%")
                print()

            # Show recent queries (first 10)
            print("RECENT CACHED QUERIES (up to 10):")
            print("-" * 60)
            for i, key in enumerate(keys[:10], 1):
                ttl = r.ttl(key)
                value = r.get(key)
                size = len(value) if value else 0
                print(f"{i}. Key: {key}")
                print(f"   TTL: {ttl}s remaining")
                print(f"   Size: {size} bytes")
                print()

            if total_queries > 10:
                print(f"... and {total_queries - 10} more cached queries")
                print()

        else:
            print("No queries cached yet.")
            print()
            print("CACHE STATISTICS:")
            print("-" * 60)
            info = r.info("stats")
            keyspace_hits = info.get("keyspace_hits", 0)
            keyspace_misses = info.get("keyspace_misses", 0)
            total_requests = keyspace_hits + keyspace_misses

            if total_requests > 0:
                hit_rate = (keyspace_hits / total_requests) * 100
                print(f"  Total Requests: {total_requests}")
                print(f"  Cache Hits: {keyspace_hits}")
                print(f"  Cache Misses: {keyspace_misses}")
                print(f"  Hit Rate: {hit_rate:.2f}%")
            else:
                print("  No cache activity yet")
            print()

    except Exception as e:
        print("ERROR: Unable to connect to Redis")
        print(f"Details: {e}")
        print()


@cli.command()
def summary():
    """Show comprehensive monitoring summary."""
    print("=" * 60)
    print("DISTRIBUTED DBMS MONITORING SUMMARY")
    print("=" * 60)
    print()

    # DBMS Status
    print("[1] DBMS STATUS")
    print("-" * 60)

    dbms_configs = {
        "DBMS1": "postgresql://ddbs:ddbs@localhost:5434/ddbs1",
        "DBMS1-STANDBY": "postgresql://ddbs:ddbs@localhost:5435/ddbs1",
        "DBMS2": "postgresql://ddbs:ddbs@localhost:5433/ddbs2",
        "DBMS3": "postgresql://ddbs:ddbs@localhost:5436/ddbs3",
    }

    dbms_status = {}
    for name, conn_str in dbms_configs.items():
        try:
            with psycopg.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM pg_stat_activity")
                    dbms_status[name] = "✓ ONLINE"
        except Exception:
            dbms_status[name] = "✗ OFFLINE"

    for name, status in dbms_status.items():
        print(f"  {name}: {status}")

    print()

    # Data Summary
    print("[2] DATA SUMMARY")
    print("-" * 60)

    total_rows = {"user": 0, "article": 0, "user_read": 0, "be_read": 0}

    for dbms_name, conn_str in dbms_configs.items():
        try:
            with psycopg.connect(conn_str) as conn:
                with conn.cursor() as cur:
                    for table in total_rows.keys():
                        try:
                            cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                            count = cur.fetchone()[0]
                            total_rows[table] += count
                        except Exception:
                            pass
        except Exception:
            pass

    for table, count in total_rows.items():
        print(f"  {table:15s} {count:8d} total rows")

    print()

    # Cache Summary
    print("[3] CACHE STATUS")
    print("-" * 60)

    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        keys = r.keys("query:*")
        info = r.info("stats")
        keyspace_hits = info.get("keyspace_hits", 0)
        keyspace_misses = info.get("keyspace_misses", 0)
        total_requests = keyspace_hits + keyspace_misses

        print("  Redis: ✓ ONLINE")
        print(f"  Cached Queries: {len(keys)}")
        if total_requests > 0:
            hit_rate = (keyspace_hits / total_requests) * 100
            print(f"  Hit Rate: {hit_rate:.2f}%")
    except Exception:
        print("  Redis: ✗ OFFLINE")

    print()
    print("=" * 60)
    print("Use 'monitor status', 'monitor distribution', or 'monitor workload'")
    print("for detailed reports.")
    print("=" * 60)


if __name__ == "__main__":
    cli()
