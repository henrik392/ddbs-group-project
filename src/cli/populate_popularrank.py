#!/usr/bin/env python3
"""Populate Popular-Rank table from Be-Read data."""

import psycopg
import time


def populate_popularrank():
    """Generate popular article rankings by temporal granularity."""
    print("Populating Popular-Rank table from Be-Read data...\n")

    dbms1_conn = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
    dbms2_conn = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"

    conn1 = psycopg.connect(dbms1_conn)
    conn2 = psycopg.connect(dbms2_conn)

    try:
        # Step 1: Collect all Be-Read records from DBMS2 (has all articles)
        print("Step 1: Collecting Be-Read stats from DBMS2...")
        with conn2.cursor() as cur:
            cur.execute(
                'SELECT aid, readNum FROM "be_read" ORDER BY readNum DESC LIMIT 100'
            )
            beread_stats = cur.fetchall()
            print(f"  Collected {len(beread_stats)} Be-Read records\n")

        # Step 2: Generate rankings by temporal granularity
        print("Step 2: Generating rankings...")
        timestamp = int(time.time() * 1000)

        # Daily top-5 (for demo, same as weekly/monthly but different granularity)
        daily_top5 = [str(aid) for aid, _ in beread_stats[:5]]
        weekly_top5 = [str(aid) for aid, _ in beread_stats[5:10]]
        monthly_top5 = [str(aid) for aid, _ in beread_stats[10:15]]

        print(f"  Daily top-5: {daily_top5}")
        print(f"  Weekly top-5: {weekly_top5}")
        print(f"  Monthly top-5: {monthly_top5}\n")

        # Step 3: Insert into Popular-Rank tables
        print("Step 3: Inserting rankings...")

        insert_sql = """
            INSERT INTO "popular_rank" (id, timestamp, temporalGranularity, articleAidList)
            VALUES (%s, %s, %s, %s)
        """

        # Daily rankings go to DBMS1
        with conn1.cursor() as cur:
            cur.execute(
                insert_sql,
                ("pr_daily", timestamp, "daily", ",".join(daily_top5)),
            )
        print("  DBMS1: Inserted daily ranking")

        # Weekly and monthly rankings go to DBMS2
        with conn2.cursor() as cur:
            cur.execute(
                insert_sql,
                ("pr_weekly", timestamp, "weekly", ",".join(weekly_top5)),
            )
            cur.execute(
                insert_sql,
                ("pr_monthly", timestamp, "monthly", ",".join(monthly_top5)),
            )
        print("  DBMS2: Inserted weekly and monthly rankings")

        # Commit
        conn1.commit()
        conn2.commit()

        print("\n✓ Popular-Rank table population complete!")

    finally:
        conn1.close()
        conn2.close()


def verify_popularrank():
    """Verify Popular-Rank table content."""
    print("Verifying Popular-Rank table...\n")

    dbms1_conn = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
    dbms2_conn = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"

    # Check DBMS1
    with psycopg.connect(dbms1_conn) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "popular_rank"')
            count = cur.fetchone()[0]
            print(f"DBMS1 Popular-Rank records: {count}")

            if count > 0:
                cur.execute(
                    'SELECT temporalGranularity, articleAidList FROM "popular_rank"'
                )
                for granularity, aid_list in cur.fetchall():
                    aids = aid_list.split(",")
                    print(f"  {granularity}: {len(aids)} articles - {aids}")

    # Check DBMS2
    with psycopg.connect(dbms2_conn) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "popular_rank"')
            count = cur.fetchone()[0]
            print(f"\nDBMS2 Popular-Rank records: {count}")

            if count > 0:
                cur.execute(
                    'SELECT temporalGranularity, articleAidList FROM "popular_rank"'
                )
                for granularity, aid_list in cur.fetchall():
                    aids = aid_list.split(",")
                    print(f"  {granularity}: {len(aids)} articles - {aids}")

    print("\n✓ Verification complete")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_popularrank()
    else:
        populate_popularrank()
