# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Distributed database system for a news article platform implementing horizontal fragmentation, replication, and distributed query processing across two PostgreSQL instances with Redis caching.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Start infrastructure
docker compose up -d

# Stop infrastructure
docker compose down

# Clean restart (removes all data)
docker compose down -v && docker compose up -d
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

### Database Operations
```bash
# Initialize schemas on both DBMS
uv run python src/cli/init_db.py

# Generate test data
uv run python db-generation/generate_test_data.py

# Load data with partitioning
uv run python src/cli/load_data.py bulk-load

# Verify data distribution
uv run python src/cli/load_data.py verify

# Populate Be-Read table
uv run python src/cli/populate_beread.py

# Populate Popular-Rank table
uv run python src/cli/populate_popularrank.py
```

### Query Operations
```bash
# Interactive query shell
uv run python src/cli/query.py execute --interactive

# Execute single query
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" LIMIT 5"

# Top-5 popular articles (daily/weekly/monthly)
uv run python src/cli/query.py top5 -g daily

# View example queries
uv run python src/cli/query.py examples
```

### Monitoring
```bash
# System overview
uv run python src/cli/monitor.py summary

# DBMS health status
uv run python src/cli/monitor.py status

# Data distribution report
uv run python src/cli/monitor.py distribution

# Query workload statistics
uv run python src/cli/monitor.py workload
```

## Architecture

### Distributed Database Infrastructure

**Two PostgreSQL instances:**
- DBMS1 (port 5434): Beijing region data + science articles (replicated)
- DBMS2 (port 5433): Hong Kong region data + all articles

**Redis (port 6379):** Query result caching with 60-second TTL

**MinIO (ports 9000/9001):** Unstructured data storage (text, images, videos)

### Data Fragmentation Rules

| Table | Fragmentation Attribute | DBMS1 | DBMS2 |
|-------|------------------------|-------|-------|
| User | region | Beijing | Hong Kong |
| Article | category | science (replicated) | science + technology |
| Read | Co-located with User | Beijing users' reads | Hong Kong users' reads |
| Be-Read | category (replicated) | science | science + technology |
| Popular-Rank | temporalGranularity | daily | weekly, monthly |

### Query Processing Flow

1. **QueryCoordinator** (`src/domains/query/coordinator.py`):
   - Entry point for all queries
   - Checks Redis cache first (cache key = MD5 of SQL)
   - If cache miss, delegates to Router → Executor
   - Caches results with 60s TTL

2. **QueryRouter** (`src/domains/query/router.py`):
   - Parses SQL to identify table and conditions
   - Applies fragmentation rules to determine targets
   - Returns routing plan with strategy:
     - `single`: Query one DBMS only
     - `parallel`: Query both DBMS, merge results
     - `join`: Distributed join (Popular-Rank + Article)

3. **QueryExecutor** (`src/domains/query/executor.py`):
   - Executes queries on target DBMS
   - For parallel strategy: fetches from both, merges results
   - For join strategy: fetches ranking, then article details, preserves order

### Connection Strings

```python
DBMS1 = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
DBMS2 = "postgresql://ddbs:ddbs@localhost:5433/dbms2"
REDIS = "localhost:6379"
```

## Important Implementation Details

### Table Names Require Double Quotes
PostgreSQL table names must be quoted in SQL queries:
```sql
SELECT * FROM "user" WHERE region='Beijing'  -- Correct
SELECT * FROM user WHERE region='Beijing'     -- Will fail
```

### Data Loading Process
1. Generate partitioned SQL files (separate for DBMS1/DBMS2)
2. Bulk load applies fragmentation during generation, not during load
3. Be-Read table aggregates Read data from both DBMS, then replicates based on article category
4. Popular-Rank table groups Be-Read by temporal granularity

### Cache Key Generation
MD5 hash of SQL query string (case-sensitive, whitespace-sensitive):
```python
cache_key = f"query:{hashlib.md5(sql.encode()).hexdigest()}"
```

### Distributed Join Implementation
For top-5 queries:
1. Fetch ranking from appropriate DBMS (daily→DBMS1, weekly/monthly→DBMS2)
2. Parse article IDs from comma-separated list
3. Query both DBMS for article details
4. Merge results maintaining ranking order

## Development Workflow

### Adding New Features
1. Create feature branch: `git checkout -b feature/name`
2. Implement feature
3. Run linting: `uv run ruff format . && uv run ruff check --fix .`
4. Test manually with monitoring tools
5. Commit without "Co-Authored-By: Claude" footer
6. Create PR, squash and merge

### Testing Changes
No automated tests. Verify manually:
1. `monitor.py distribution` - Check data distribution
2. `monitor.py status` - Verify DBMS connectivity
3. `query.py execute` - Test queries
4. `monitor.py workload` - Check cache hits

### Common Issues

**Port conflicts:** Change ports in `docker-compose.yml` if 5433/5434/6379/9000 are taken

**Database not ready:** Wait 10-15 seconds after `docker compose up -d` for PostgreSQL initialization

**Empty query results:** Ensure data is loaded with `load_data.py bulk-load`

**Cache not working:** Verify Redis is running with `docker compose ps redis`

## Project Goals

This is a university project for Distributed Database Systems course at Tsinghua University. Goals:
- Demonstrate horizontal fragmentation concepts
- Implement distributed query processing
- Show replication strategies
- Simple, maintainable implementation over complexity
- Full marks without optional advanced features (hot standby, DBMS expansion)

## Reference Documentation

- Project plan: `docs/PLAN.md`
- System manual: `docs/MANUAL.md`
- Report template: `docs/REPORT_TEMPLATE.md`
- README: `README.md`
