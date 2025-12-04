#!/usr/bin/env python3
"""Populate Be-Read table from Read table data."""

import time
from collections import defaultdict

import psycopg

from src.config import DBMS_CONNECTIONS


def populate_beread():
    """Aggregate Read table data into Be-Read table."""
    print("Populating Be-Read table from Read table...\n")

    # Connect to both DBMS
    dbms1_conn = DBMS_CONNECTIONS["DBMS1"]
    dbms2_conn = DBMS_CONNECTIONS["DBMS2"]

    conn1 = psycopg.connect(dbms1_conn)
    conn2 = psycopg.connect(dbms2_conn)

    try:
        # Step 1: Collect all Read records from both DBMS
        print("Step 1: Collecting Read records from both DBMS...")
        reads = []

        with conn1.cursor() as cur:
            cur.execute(
                'SELECT uid, aid, agreeOrNot, commentOrNot, shareOrNot FROM "user_read"'
            )
            dbms1_reads = cur.fetchall()
            reads.extend(dbms1_reads)
            print(f"  DBMS1: {len(dbms1_reads)} reads")

        with conn2.cursor() as cur:
            cur.execute(
                'SELECT uid, aid, agreeOrNot, commentOrNot, shareOrNot FROM "user_read"'
            )
            dbms2_reads = cur.fetchall()
            reads.extend(dbms2_reads)
            print(f"  DBMS2: {len(dbms2_reads)} reads")

        print(f"  Total: {len(reads)} reads collected\n")

        # Step 2: Aggregate by article (aid)
        print("Step 2: Aggregating data by article...")
        stats = defaultdict(
            lambda: {
                "readNum": 0,
                "readUids": set(),
                "agreeNum": 0,
                "agreeUids": set(),
                "commentNum": 0,
                "commentUids": set(),
                "shareNum": 0,
                "shareUids": set(),
            }
        )

        for uid, aid, agree, comment, share in reads:
            stats[aid]["readNum"] += 1
            stats[aid]["readUids"].add(uid)

            if agree == "1":
                stats[aid]["agreeNum"] += 1
                stats[aid]["agreeUids"].add(uid)

            if comment == "1":
                stats[aid]["commentNum"] += 1
                stats[aid]["commentUids"].add(uid)

            if share == "1":
                stats[aid]["shareNum"] += 1
                stats[aid]["shareUids"].add(uid)

        print(f"  Aggregated data for {len(stats)} articles\n")

        # Step 3: Get article categories to determine replication
        print("Step 3: Determining article categories for replication...")
        article_categories = {}

        # Get articles from DBMS1 (science only)
        with conn1.cursor() as cur:
            cur.execute('SELECT aid, category FROM "article"')
            for aid, category in cur.fetchall():
                article_categories[aid] = category

        # Get articles from DBMS2 (science + technology)
        with conn2.cursor() as cur:
            cur.execute('SELECT aid, category FROM "article"')
            for aid, category in cur.fetchall():
                if aid not in article_categories:  # Add technology articles
                    article_categories[aid] = category

        print(f"  Found {len(article_categories)} articles\n")

        # Step 4: Insert into Be-Read tables with proper replication
        print("Step 4: Inserting into Be-Read tables...")
        timestamp = int(time.time() * 1000)

        inserted_dbms1 = 0
        inserted_dbms2 = 0

        for aid, data in stats.items():
            category = article_categories.get(aid, "technology")

            beread_id = f"br{aid}"
            readUidList = ",".join(str(uid) for uid in sorted(data["readUids"]))
            commentUidList = ",".join(str(uid) for uid in sorted(data["commentUids"]))
            agreeUidList = ",".join(str(uid) for uid in sorted(data["agreeUids"]))
            shareUidList = ",".join(str(uid) for uid in sorted(data["shareUids"]))

            insert_sql = """
                INSERT INTO "be_read" (
                    id, timestamp, aid, readNum, readUidList,
                    commentNum, commentUidList, agreeNum, agreeUidList,
                    shareNum, shareUidList
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                beread_id,
                timestamp,
                aid,
                data["readNum"],
                readUidList,
                data["commentNum"],
                commentUidList,
                data["agreeNum"],
                agreeUidList,
                data["shareNum"],
                shareUidList,
            )

            # Science articles go to both DBMS (replicated)
            if category == "science":
                with conn1.cursor() as cur:
                    cur.execute(insert_sql, values)
                with conn2.cursor() as cur:
                    cur.execute(insert_sql, values)
                inserted_dbms1 += 1
                inserted_dbms2 += 1
            else:  # Technology articles go to DBMS2 only
                with conn2.cursor() as cur:
                    cur.execute(insert_sql, values)
                inserted_dbms2 += 1

        # Commit transactions
        conn1.commit()
        conn2.commit()

        print(f"  DBMS1: {inserted_dbms1} Be-Read records (science articles)")
        print(f"  DBMS2: {inserted_dbms2} Be-Read records (science + technology)")

        print("\n✓ Be-Read table population complete!")

    finally:
        conn1.close()
        conn2.close()


def verify_beread():
    """Verify Be-Read table content."""
    print("Verifying Be-Read table...\n")

    from src.config import DBMS_CONNECTIONS

    dbms1_conn = DBMS_CONNECTIONS["DBMS1"]
    dbms2_conn = DBMS_CONNECTIONS["DBMS2"]

    # Check DBMS1
    with psycopg.connect(dbms1_conn) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "be_read"')
            count = cur.fetchone()[0]
            print(f"DBMS1 Be-Read records: {count}")

            if count > 0:
                cur.execute(
                    'SELECT aid, readNum, agreeNum, commentNum, shareNum FROM "be_read" ORDER BY readNum DESC LIMIT 3'
                )
                print("  Top 3 articles by reads:")
                for aid, readNum, agreeNum, commentNum, shareNum in cur.fetchall():
                    print(
                        f"    Article {aid}: {readNum} reads, {agreeNum} agrees, {commentNum} comments, {shareNum} shares"
                    )

    # Check DBMS2
    with psycopg.connect(dbms2_conn) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "be_read"')
            count = cur.fetchone()[0]
            print(f"\nDBMS2 Be-Read records: {count}")

            if count > 0:
                cur.execute(
                    'SELECT aid, readNum, agreeNum, commentNum, shareNum FROM "be_read" ORDER BY readNum DESC LIMIT 3'
                )
                print("  Top 3 articles by reads:")
                for aid, readNum, agreeNum, commentNum, shareNum in cur.fetchall():
                    print(
                        f"    Article {aid}: {readNum} reads, {agreeNum} agrees, {commentNum} comments, {shareNum} shares"
                    )

    print("\n✓ Verification complete")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_beread()
    else:
        populate_beread()
