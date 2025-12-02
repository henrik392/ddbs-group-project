#!/usr/bin/env python3
"""Query CLI for distributed database."""

import click
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.domains.query.coordinator import QueryCoordinator
from src.domains.query.executor import QueryExecutor


@click.group()
def cli():
    """Distributed query commands."""
    pass


@cli.command()
@click.option("--sql", help="SQL query to execute")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
@click.option("--no-cache", is_flag=True, help="Disable cache")
def execute(sql, interactive, no_cache):
    """Execute distributed queries."""
    coordinator = QueryCoordinator()
    use_cache = not no_cache

    if interactive:
        print("DDBS Interactive Query Shell")
        print("Type 'exit' or 'quit' to quit")
        print("Type 'clear cache' to clear query cache\n")

        while True:
            try:
                query = input("SQL> ").strip()

                if query.lower() in ["exit", "quit"]:
                    break

                if not query:
                    continue

                if query.lower() == "clear cache":
                    coordinator.clear_cache()
                    continue

                print()
                results = coordinator.execute(query, use_cache=use_cache)

                if not results:
                    print("No results returned\n")
                    continue

                # Print results
                print(f"\nReturned {len(results)} rows:")

                # Show first 10 rows
                for i, row in enumerate(results[:10]):
                    print(f"{i + 1}. {row}")

                if len(results) > 10:
                    print(f"... and {len(results) - 10} more rows")

                print()

            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                print(f"Error: {e}\n")

    else:
        if not sql:
            print("Error: --sql is required in non-interactive mode")
            sys.exit(1)

        try:
            results = coordinator.execute(sql, use_cache=use_cache)

            if not results:
                print("No results returned")
            else:
                for row in results:
                    print(row)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


@cli.command()
@click.option(
    "--granularity",
    "-g",
    type=click.Choice(["daily", "weekly", "monthly"]),
    default="daily",
    help="Temporal granularity",
)
def top5(granularity):
    """Query top-5 popular articles with details."""
    executor = QueryExecutor()

    # Determine which DBMS has the ranking
    if granularity == "daily":
        rank_target = "DBMS1"
    else:
        rank_target = "DBMS2"

    # Create routing plan for distributed join
    routing_plan = {
        "strategy": "join",
        "rank_target": rank_target,
        "rank_query": f"SELECT articleAidList FROM \"popular_rank\" WHERE temporalGranularity='{granularity}'",
    }

    print(f"Querying top-5 {granularity} popular articles...\n")

    try:
        results = executor.execute(routing_plan)

        if not results:
            print("No results found")
            return

        print(f"Top-5 {granularity} popular articles:\n")
        for i, article in enumerate(results, 1):
            print(f"{i}. Article {article['aid']}: {article.get('title', 'N/A')}")
            print(f"   Category: {article.get('category', 'N/A')}")
            print(f"   Abstract: {article.get('abstract', 'N/A')[:100]}...")
            if article.get("text"):
                print("   Text: Available")
            if article.get("image"):
                print(f"   Image: {article['image']}")
            if article.get("video"):
                print(f"   Video: {article['video']}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


@cli.command()
def examples():
    """Show example queries."""
    print("Example Distributed Queries:\n")

    examples_list = [
        (
            "1. Query users in Beijing (single DBMS)",
            "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5",
        ),
        (
            "2. Query users in Hong Kong (single DBMS)",
            "SELECT * FROM \"user\" WHERE region='Hong Kong' LIMIT 5",
        ),
        (
            "3. Query all users (distributed, merge results)",
            'SELECT uid, name, region FROM "user" LIMIT 10',
        ),
        (
            "4. Query science articles (replicated, single DBMS)",
            "SELECT * FROM \"article\" WHERE category='science' LIMIT 5",
        ),
        (
            "5. Query technology articles (single DBMS)",
            "SELECT * FROM \"article\" WHERE category='technology' LIMIT 5",
        ),
        (
            "6. Query all articles (distributed)",
            'SELECT aid, title, category FROM "article" LIMIT 10',
        ),
        (
            "7. Query Be-Read stats (from DBMS2)",
            'SELECT aid, readNum, agreeNum, commentNum FROM "be_read" ORDER BY readNum DESC LIMIT 5',
        ),
        (
            "8. Query reads (distributed)",
            'SELECT id, uid, aid, agreeOrNot FROM "user_read" LIMIT 5',
        ),
        (
            "9. Query Popular-Rank (by granularity)",
            "SELECT * FROM \"popular_rank\" WHERE temporalGranularity='daily'",
        ),
    ]

    for title, query in examples_list:
        print(f"{title}")
        print(f"  {query}\n")

    print("\nSpecial Commands:")
    print("  Top-5 popular articles:")
    print("    uv run python src/cli/query.py top5 --granularity daily")
    print("    uv run python src/cli/query.py top5 -g weekly")
    print("    uv run python src/cli/query.py top5 -g monthly\n")

    print("To execute a query:")
    print('  uv run python src/cli/query.py execute --sql "<query>"')
    print("\nTo start interactive mode:")
    print("  uv run python src/cli/query.py execute --interactive")


if __name__ == "__main__":
    cli()
