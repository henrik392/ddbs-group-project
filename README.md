# Distributed Database System

A distributed database system implementing horizontal fragmentation, replication, and distributed query processing for a news article platform.

## Quick Start

### 1. Setup
```bash
# Install dependencies
uv sync

# Start infrastructure (PostgreSQL × 2, Redis, MinIO)
docker compose up -d
```

### 2. Initialize Database
```bash
# Create schemas on both DBMS
uv run python src/cli/init_db.py
```

### 3. Load Data
```bash
# Generate test data
uv run python db-generation/generate_test_data.py

# Load data into DBMS
uv run python src/cli/load_data.py bulk-load

# Populate Be-Read table
uv run python src/cli/populate_beread.py
```

### 4. Query Data
```bash
# Interactive query shell
uv run python src/cli/query.py execute --interactive

# Single query
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# View example queries
uv run python src/cli/query.py examples
```

### 5. Popular Articles
```bash
# Populate Popular-Rank table
uv run python src/cli/populate_popularrank.py

# Query top-5 daily popular articles
uv run python src/cli/query.py top5 --granularity daily

# Query top-5 weekly popular articles
uv run python src/cli/query.py top5 -g weekly

# Query top-5 monthly popular articles
uv run python src/cli/query.py top5 -g monthly
```

### 6. Monitor System
```bash
# Quick system summary
uv run python src/cli/monitor.py summary

# Detailed DBMS status
uv run python src/cli/monitor.py status

# Data distribution report
uv run python src/cli/monitor.py distribution

# Query workload statistics
uv run python src/cli/monitor.py workload
```

## Query Examples

### Basic Queries
```bash
# Query users in Beijing (single DBMS)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# Query all users (distributed, merges results from both DBMS)
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" LIMIT 10"

# Query science articles (replicated, queries one DBMS)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"article\" WHERE category='science' LIMIT 5"

# Query Be-Read stats
uv run python src/cli/query.py execute --sql "SELECT aid, readNum, agreeNum FROM \"be_read\" ORDER BY readNum DESC LIMIT 5"

# Disable cache for a query
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" LIMIT 5" --no-cache
```

### Top-5 Popular Articles with Details
```bash
# Daily top-5 articles (from DBMS1)
uv run python src/cli/query.py top5 --granularity daily

# Weekly top-5 articles (from DBMS2)
uv run python src/cli/query.py top5 -g weekly

# Monthly top-5 articles (from DBMS2)
uv run python src/cli/query.py top5 -g monthly
```

**Example Output:**
```
Top-5 daily popular articles:

1. Article 6: title6
   Category: technology
   Abstract: abstract of article 6...
   Text: Available
   Image: articles/article6/image_a6_0.jpg

2. Article 47: title47
   Category: science
   Abstract: abstract of article 47...
   Text: Available
   Image: articles/article47/image_a47_0.jpg
...
```

## Interactive Shell

```bash
uv run python src/cli/query.py execute -i

SQL> SELECT * FROM "user" WHERE region='Beijing' LIMIT 3
✓ Routing: single on DBMS1
✓ Retrieved 3 rows

Returned 3 rows:
1. {'uid': 'u0', 'name': 'Alice', 'region': 'Beijing', ...}
2. {'uid': 'u2', 'name': 'Charlie', 'region': 'Beijing', ...}
3. {'uid': 'u4', 'name': 'Eve', 'region': 'Beijing', ...}

SQL> clear cache
✓ Cache cleared

SQL> exit
```

## Monitoring

### System Summary
```bash
uv run python src/cli/monitor.py summary
```

**Output:**
```
============================================================
DISTRIBUTED DBMS MONITORING SUMMARY
============================================================

[1] DBMS STATUS
------------------------------------------------------------
  DBMS1: ✓ ONLINE
  DBMS2: ✓ ONLINE

[2] DATA SUMMARY
------------------------------------------------------------
  user                 100 total rows
  article               75 total rows
  user_read            500 total rows
  be_read               75 total rows

[3] CACHE STATUS
------------------------------------------------------------
  Redis: ✓ ONLINE
  Cached Queries: 0
  Hit Rate: 16.67%
============================================================
```

### DBMS Status
```bash
uv run python src/cli/monitor.py status
```

Shows:
- Connection status (ONLINE/OFFLINE)
- PostgreSQL version
- Database size
- Active connections
- Redis cache status and memory usage

### Data Distribution
```bash
uv run python src/cli/monitor.py distribution
```

Shows:
- Fragmentation rules for all tables
- Actual row counts per DBMS
- Table sizes
- Data replication status

### Workload Statistics
```bash
uv run python src/cli/monitor.py workload
```

Shows:
- Number of cached queries
- Cache hit rate
- Recent queries with TTL
- Redis statistics

## Architecture

**Data Distribution:**
- **User**: Beijing → DBMS1, Hong Kong → DBMS2
- **Article**: science → both DBMS, technology → DBMS2
- **Read**: Co-located with User table
- **Be-Read**: Replicated on both DBMS
- **Popular-Rank**: daily → DBMS1, weekly/monthly → DBMS2

**Query Coordinator:**
- Routes queries based on fragmentation rules
- Executes on single or multiple DBMS
- Caches results in Redis (60 second TTL)
- Merges results from distributed queries

## Docker Management

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Clean slate (removes data)
docker compose down -v

# View logs
docker compose logs -f

# Access PostgreSQL
docker compose exec dbms1 psql -U ddbs -d ddbs1
docker compose exec dbms2 psql -U ddbs -d ddbs2

# Access Redis
docker compose exec redis redis-cli

# MinIO Console
# http://localhost:9001 (minioadmin/minioadmin)
```

## Development

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

## Project Structure

```
.
├── docker-compose.yml          # Infrastructure (Postgres, Redis, MinIO)
├── sql/schema.sql              # Database schema
├── db-generation/              # Test data generation
├── src/
│   ├── cli/
│   │   ├── init_db.py              # Initialize databases
│   │   ├── load_data.py            # Load data with partitioning
│   │   ├── populate_beread.py      # Populate Be-Read table
│   │   ├── populate_popularrank.py # Populate Popular-Rank table
│   │   ├── query.py                # Query CLI (execute, top5, examples)
│   │   └── monitor.py              # Monitoring CLI (status, distribution, workload)
│   └── domains/
│       └── query/
│           ├── router.py           # Query routing logic
│           ├── executor.py         # Query execution & joins
│           └── coordinator.py      # Main coordinator with cache
└── docs/                           # Documentation & plan
```

## Troubleshooting

```bash
# Check service status
docker compose ps

# View logs for a specific service
docker compose logs dbms1

# Restart a service
docker compose restart redis

# Reset everything
docker compose down -v
docker compose up -d
uv run python src/cli/init_db.py
```

## Contributors

- Henrik Kvamme
- Rui Silveira
