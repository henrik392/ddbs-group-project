#!/usr/bin/env python3
"""Load partitioned data into distributed database."""

from pathlib import Path

import click
import psycopg

from src.config import DBMS_CONNECTIONS


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
    dbms1_conn = DBMS_CONNECTIONS["DBMS1"]
    dbms1_standby_conn = DBMS_CONNECTIONS["DBMS-STANDBY"]
    dbms2_conn = DBMS_CONNECTIONS["DBMS2"]

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


@cli.command()
@click.option(
    "--mock-dir",
    type=click.Path(exists=True, path_type=Path),
    default="mock_articles",
    help="Directory containing mock article files",
)
@click.option(
    "--workers",
    type=int,
    default=20,
    help="Number of parallel upload workers",
)
def upload_media(mock_dir: Path, workers: int):
    """Upload article media files to HDFS with parallel workers."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from threading import Lock

    from src.domains.storage.hdfs_manager import HDFSManager

    print("Uploading article media files to HDFS...\n")

    hdfs = HDFSManager()

    info = hdfs.get_storage_info()
    if not info.get("available"):
        print(f"✗ HDFS not available: {info.get('error')}")
        return

    print(f"✓ HDFS available at {info['base_path']}")
    print(f"  Replication factor: {info['replication']}")
    print(f"  Parallel workers: {workers}\n")

    # Collect all files to upload
    files_to_upload = []
    for article_dir in sorted(mock_dir.iterdir()):
        if not article_dir.is_dir():
            continue
        for file_path in article_dir.iterdir():
            hdfs_path = f"{article_dir.name}/{file_path.name}"
            files_to_upload.append((str(file_path), hdfs_path))

    total_files = len(files_to_upload)
    print(f"Found {total_files:,} files to upload\n")

    # Upload function for worker threads
    def upload_file(local_path, hdfs_path):
        """Upload a single file (creates own HDFS client)."""
        try:
            hdfs_client = HDFSManager()
            return hdfs_client.upload_file(local_path, hdfs_path)
        except Exception as e:
            print(f"⚠ Error uploading {hdfs_path}: {e}")
            return False

    # Parallel upload with progress tracking
    uploaded = 0
    failed = 0
    lock = Lock()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all upload tasks
        futures = {
            executor.submit(upload_file, local_path, hdfs_path): (local_path, hdfs_path)
            for local_path, hdfs_path in files_to_upload
        }

        # Process completed uploads
        for i, future in enumerate(as_completed(futures), 1):
            _, hdfs_path = futures[future]
            try:
                success = future.result()
                with lock:
                    if success:
                        uploaded += 1
                    else:
                        failed += 1

                    # Show progress every 100 files
                    if i % 100 == 0 or i == total_files:
                        print(
                            f"Progress: {i:,}/{total_files:,} "
                            f"({uploaded:,} uploaded, {failed:,} failed)"
                        )
            except Exception as e:
                with lock:
                    failed += 1
                print(f"⚠ Exception uploading {hdfs_path}: {e}")

    print(f"\n✓ Upload complete: {uploaded:,} files uploaded, {failed:,} failed")


if __name__ == "__main__":
    cli()
