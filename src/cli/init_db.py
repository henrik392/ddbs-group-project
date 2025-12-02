#!/usr/bin/env python3
"""Initialize database schemas on both DBMS."""

import psycopg
from pathlib import Path


def init_databases():
    """Initialize both DBMS with schema."""
    # Get schema file path
    schema_path = Path(__file__).parent.parent.parent / "sql" / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema_sql = schema_path.read_text()

    # Initialize DBMS1
    print("Initializing DBMS1 (Beijing)...")
    try:
        with psycopg.connect("postgresql://ddbs:ddbs@localhost:5434/ddbs1") as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        print("✓ DBMS1 initialized successfully")
    except Exception as e:
        print(f"✗ DBMS1 initialization failed: {e}")
        raise

    # Initialize DBMS2
    print("Initializing DBMS2 (Hong Kong)...")
    try:
        with psycopg.connect("postgresql://ddbs:ddbs@localhost:5433/ddbs2") as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        print("✓ DBMS2 initialized successfully")
    except Exception as e:
        print(f"✗ DBMS2 initialization failed: {e}")
        raise

    print("\n✓ Database initialization complete!")
    print("  DBMS1: postgresql://ddbs:ddbs@localhost:5434/ddbs1")
    print("  DBMS2: postgresql://ddbs:ddbs@localhost:5433/ddbs2")


if __name__ == "__main__":
    init_databases()
