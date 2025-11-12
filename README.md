# Distributed Database System

A distributed database management system implementing horizontal fragmentation, replication, and distributed query processing for a news article platform.

## Architecture

**Federated Database with Coordinator Pattern**
```
┌──────────────────────────────────────────┐
│        Coordinator (Python)              │
│  • Query parsing & routing               │
│  • Query splitting & result merging      │
│  • Transaction coordination              │
└──────────┬───────────────────────────────┘
           │
    ┌──────┴───────┐
    ↓              ↓
┌─────────┐    ┌─────────┐
│ DBMS1   │    │ DBMS2   │
│(Beijing)│    │(HongKong)│
│PostgreSQL    │PostgreSQL│
│ :5432   │    │ :5433   │
└────┬────┘    └────┬────┘
     │              │
     └──────┬───────┘
            ↓
     ┌─────────────┐
     │ Redis Cache │
     │   :6379     │
     └─────────────┘
            ↓
     ┌─────────────┐
     │    MinIO    │
     │ :9000/9001  │
     └─────────────┘
```

**Data Distribution:**
- **User**: Beijing → DBMS1, HongKong → DBMS2
- **Article**: science → DBMS1 & DBMS2, technology → DBMS2
- **Read**: Co-located with User table
- **Be-Read**: Replicated across DBMS1 and DBMS2
- **Popular-Rank**: daily → DBMS1, weekly/monthly → DBMS2

## Prerequisites

- Python 3.14
- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose

## Quick Start

### 1. Clone and Install
```bash
git clone <repo-url>
cd distributed-database-system
uv sync
```

### 2. Start Infrastructure
```bash
# Start all services (PostgreSQL × 2, Redis, MinIO)
docker compose up -d

# Check services are running
docker compose ps

# View logs
docker compose logs -f
```

### 3. Initialize Databases
```bash
# Wait for databases to be ready, then create schemas
uv run python -m src.init_db
```

### 4. Load Data
```bash
# Bulk load with automatic partitioning and replication
uv run python -m src.loader.bulk_load --data-dir ./data

# Populate Be-Read table from Read table
uv run python -m src.loader.populate_beread
```

### 5. Run Queries
```bash
# Interactive query shell
uv run python -m src.query.shell

# Or execute specific query
uv run python -m src.query.execute --query "SELECT * FROM User WHERE region='Beijing'"
```

### 6. Monitor
```bash
# Start monitoring dashboard
uv run python -m src.monitor.dashboard

# Access at http://localhost:8080
```

## Docker Management
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# View service logs
docker compose logs -f [service_name]

# Restart a specific service
docker compose restart dbms1

# Access PostgreSQL shell
docker compose exec dbms1 psql -U postgres -d dbms1
docker compose exec dbms2 psql -U postgres -d dbms2

# Access Redis CLI
docker compose exec redis redis-cli

# Access MinIO console
# http://localhost:9001 (minioadmin/minioadmin)
```

## Development
```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run tests
uv run pytest

# Type check
uv run mypy src/
```

## Project Structure
```
.
├── docker-compose.yml       # Infrastructure definition
├── config.json             # DBMS connection config
├── src/
│   ├── coordinator.py       # Query routing & coordination
│   ├── dbms/
│   │   ├── connection.py    # DBMS connection managers
│   │   └── manager.py       # DBMS node management
│   ├── loader/
│   │   ├── bulk_load.py     # Bulk data loading
│   │   └── partitioner.py   # Data partitioning logic
│   ├── query/
│   │   ├── parser.py        # Query parsing
│   │   ├── router.py        # Query routing
│   │   ├── executor.py      # Distributed query execution
│   │   └── aggregator.py    # Result merging
│   ├── cache/
│   │   └── redis_cache.py   # Redis cache layer
│   ├── monitor/
│   │   └── dashboard.py     # DBMS monitoring
│   └── init_db.py           # Database initialization
├── tests/
├── data/                    # Sample data files
├── pyproject.toml
└── README.md
```

## Core Operations

### 1. Bulk Load
```bash
uv run python -m src.loader.bulk_load --data-dir ./data
```

### 2. Populate Be-Read
```bash
uv run python -m src.loader.populate_beread
```

### 3. Distributed Queries
```python
# Single DBMS query
"SELECT * FROM User WHERE region='Beijing'"  # → DBMS1 only

# Multi-DBMS query with merge
"SELECT * FROM Article WHERE category='science'"  # → DBMS1 + DBMS2

# Distributed join
"SELECT u.name, a.title FROM User u 
 JOIN Read r ON u.uid = r.uid 
 JOIN Article a ON r.aid = a.aid"
```

### 4. Top-5 Popular Articles
```python
"SELECT * FROM PopularArticles WHERE granularity='daily' LIMIT 5"
```

## Query Splitting Example

**Query:** "Get all science articles read by Beijing users"
```python
# Coordinator splits into:
1. Query DBMS1: SELECT uid FROM User WHERE region='Beijing'
2. Query DBMS1+DBMS2: SELECT * FROM Article WHERE category='science'
3. Query DBMS1: SELECT * FROM Read WHERE uid IN (...)
4. Merge results locally in coordinator
5. Cache result in Redis (5 min TTL)
```

## Cache Strategy

- **Popular articles**: 10 min TTL
- **User profiles**: 5 min TTL
- **Query results**: 1 min TTL
- **Be-Read aggregations**: 30 sec TTL

## Troubleshooting
```bash
# Check if services are healthy
docker compose ps

# View detailed logs
docker compose logs dbms1
docker compose logs dbms2
docker compose logs redis

# Reset everything
docker compose down -v
docker compose up -d
uv run python -m src.init_db
```

## Run containers
1) `docker compose up -d`
2) `docker compose exec -T dbms1 sh -lc 'psql -U ddbs -d ddbs1 -v ON_ERROR_STOP=1 -f -' < sql/schema.sql`
   `docker compose exec -T dbms2 sh -lc 'psql -U ddbs -d ddbs2 -v ON_ERROR_STOP=1 -f -' < sql/schema.sql`
3) `uv run -- uvicorn services.api.app.main:app --reload` → GET /health

## Contributors

- [Your Name] - Project Lead
- [Teammate Name] - Team Member

## License

MIT License