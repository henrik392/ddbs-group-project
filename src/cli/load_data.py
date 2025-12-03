#!/usr/bin/env python3
"""Load partitioned data into distributed database."""

import click
import psycopg
from pathlib import Path


@click.group()
def cli():
    """Data loading commands."""
    pass


@cli.command()
@click.option(
    "--sql-dir",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Directory containing partitioned SQL files",
)
def bulk_load(sql_dir: Path):
    """Load partitioned SQL files into DBMS."""
    print("Loading data into distributed database...\n")

    # Define connections
    dbms1_conn = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
    dbms1_standby_conn = "postgresql://ddbs:ddbs@localhost:5435/ddbs1"
    dbms2_conn = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"

    # Files to load into each DBMS
    dbms1_files = ["user_dbms1.sql", "article_dbms1.sql", "read_dbms1.sql"]
    dbms2_files = ["user_dbms2.sql", "article_dbms2.sql", "read_dbms2.sql"]

    # Load into DBMS1
    print("Loading data into DBMS1 (Beijing)...")
    with psycopg.connect(dbms1_conn) as conn:
        for filename in dbms1_files:
            file_path = sql_dir / filename
            if not file_path.exists():
                print(f"  ⚠ Skipping {filename} (not found)")
                continue

            print(f"  Loading {filename}...")
            sql = file_path.read_text()

            if not sql.strip() or "INSERT INTO" not in sql:
                print("    → Empty or invalid, skipped")
                continue

            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()

                # Count rows
                table_name = filename.split("_")[0]
                if table_name == "user":
                    table_name = '"user"'
                elif table_name == "article":
                    table_name = '"article"'
                elif table_name == "read":
                    table_name = '"user_read"'

                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cur.fetchone()[0]
                print(f"    ✓ Loaded {count} rows")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                conn.rollback()
                raise

    # Load into DBMS1-STANDBY (replica)
    print("\nLoading data into DBMS1-STANDBY (Hot Standby)...")
    with psycopg.connect(dbms1_standby_conn) as conn:
        for filename in dbms1_files:
            file_path = sql_dir / filename
            if not file_path.exists():
                print(f"  ⚠ Skipping {filename} (not found)")
                continue

            print(f"  Loading {filename}...")
            sql = file_path.read_text()

            if not sql.strip() or "INSERT INTO" not in sql:
                print("    → Empty or invalid, skipped")
                continue

            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()

                # Count rows
                table_name = filename.split("_")[0]
                if table_name == "user":
                    table_name = '"user"'
                elif table_name == "article":
                    table_name = '"article"'
                elif table_name == "read":
                    table_name = '"user_read"'

                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cur.fetchone()[0]
                print(f"    ✓ Loaded {count} rows")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                conn.rollback()
                raise

    # Load into DBMS2
    print("\nLoading data into DBMS2 (Hong Kong)...")
    with psycopg.connect(dbms2_conn) as conn:
        for filename in dbms2_files:
            file_path = sql_dir / filename
            if not file_path.exists():
                print(f"  ⚠ Skipping {filename} (not found)")
                continue

            print(f"  Loading {filename}...")
            sql = file_path.read_text()

            if not sql.strip() or "INSERT INTO" not in sql:
                print("    → Empty or invalid, skipped")
                continue

            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()

                # Count rows
                table_name = filename.split("_")[0]
                if table_name == "user":
                    table_name = '"user"'
                elif table_name == "article":
                    table_name = '"article"'
                elif table_name == "read":
                    table_name = '"user_read"'

                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cur.fetchone()[0]
                print(f"    ✓ Loaded {count} rows")
            except Exception as e:
                print(f"    ✗ Error: {e}")
                conn.rollback()
                raise

    print("\n✓ Data loading complete!")
    print("\nData distribution:")
    print("  DBMS1 (Beijing): Beijing users + science articles + Beijing reads")
    print("  DBMS1-STANDBY (Hot Standby): Same as DBMS1 (for fault tolerance)")
    print("  DBMS2 (Hong Kong): Hong Kong users + all articles + Hong Kong reads")


@cli.command()
def verify():
    """Verify data distribution across DBMS."""
    print("Verifying data distribution...\n")

    dbms1_conn = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
    dbms2_conn = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"

    # Check DBMS1
    print("DBMS1 (Beijing):")
    with psycopg.connect(dbms1_conn) as conn:
        with conn.cursor() as cur:
            # User count by region
            cur.execute('SELECT COUNT(*) FROM "user"')
            user_count = cur.fetchone()[0]
            cur.execute('SELECT region, COUNT(*) FROM "user" GROUP BY region')
            regions = cur.fetchall()

            # Article count by category
            cur.execute('SELECT COUNT(*) FROM "article"')
            article_count = cur.fetchone()[0]
            cur.execute('SELECT category, COUNT(*) FROM "article" GROUP BY category')
            categories = cur.fetchall()

            # Read count
            cur.execute('SELECT COUNT(*) FROM "user_read"')
            read_count = cur.fetchone()[0]

    print(f"  Users: {user_count} total")
    for region, count in regions:
        print(f"    - {region}: {count}")
    print(f"  Articles: {article_count} total")
    for category, count in categories:
        print(f"    - {category}: {count}")
    print(f"  Reads: {read_count} total")

    # Check DBMS2
    print("\nDBMS2 (Hong Kong):")
    with psycopg.connect(dbms2_conn) as conn:
        with conn.cursor() as cur:
            # User count by region
            cur.execute('SELECT COUNT(*) FROM "user"')
            user_count = cur.fetchone()[0]
            cur.execute('SELECT region, COUNT(*) FROM "user" GROUP BY region')
            regions = cur.fetchall()

            # Article count by category
            cur.execute('SELECT COUNT(*) FROM "article"')
            article_count = cur.fetchone()[0]
            cur.execute('SELECT category, COUNT(*) FROM "article" GROUP BY category')
            categories = cur.fetchall()

            # Read count
            cur.execute('SELECT COUNT(*) FROM "user_read"')
            read_count = cur.fetchone()[0]

    print(f"  Users: {user_count} total")
    for region, count in regions:
        print(f"    - {region}: {count}")
    print(f"  Articles: {article_count} total")
    for category, count in categories:
        print(f"    - {category}: {count}")
    print(f"  Reads: {read_count} total")

    print("\n✓ Verification complete")


if __name__ == "__main__":
    cli()
