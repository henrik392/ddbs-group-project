# Distributed Database System - Operation Manual

**Version:** 1.0
**Authors:** Henrik Kvamme, Rui Silveira
**Last Updated:** December 2024

---

## Table of Contents

1. [Installation](#1-installation)
2. [Configuration](#2-configuration)
3. [Operation](#3-operation)
4. [Monitoring](#4-monitoring)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Installation

### 1.1 Prerequisites

**Required Software:**
- Docker Desktop 4.0+ (includes Docker Compose)
- Python 3.11 or higher
- uv package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Git

**System Requirements:**
- 8GB RAM minimum
- 10GB free disk space
- macOS, Linux, or Windows with WSL2

### 1.2 Installation Steps

**Step 1: Clone Repository**
```bash
git clone <repository-url>
cd ddbs-group-project
```

**Step 2: Install Python Dependencies**
```bash
uv sync
```

This installs:
- `psycopg` (PostgreSQL driver)
- `redis` (Redis client)
- `click` (CLI framework)
- Other dependencies from `pyproject.toml`

**Step 3: Start Infrastructure**
```bash
docker compose up -d
```

This starts:
- PostgreSQL DBMS1 (port 5434)
- PostgreSQL DBMS2 (port 5433)
- Redis (port 6379)
- MinIO (ports 9000, 9001)

**Step 4: Verify Installation**
```bash
docker compose ps
```

Expected output: All services should show status "Up"

---

## 2. Configuration

### 2.1 Database Configuration

**Connection Parameters:**

| Service | Host | Port | Database | User | Password |
|---------|------|------|----------|------|----------|
| DBMS1 | localhost | 5434 | ddbs1 | ddbs | ddbs |
| DBMS2 | localhost | 5433 | ddbs2 | ddbs | ddbs |
| Redis | localhost | 6379 | - | - | - |
| MinIO | localhost | 9000 | - | minioadmin | minioadmin |

**Connection Strings:**
```python
DBMS1 = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
DBMS2 = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"
```

### 2.2 Docker Compose Configuration

File: `docker-compose.yml`

Key configuration options:
- **Ports:** Can be changed if conflicts exist
- **Volumes:** Data persists in Docker volumes (dbms1_data, dbms2_data, redis_data, minio_data)
- **Environment:** Database credentials and MinIO settings

### 2.3 Cache Configuration

**Redis TTL Settings:**

File: `src/domains/query/coordinator.py`
```python
# Query cache TTL (default: 60 seconds)
r.setex(cache_key, 60, json.dumps(results))
```

To modify TTL, edit the value (60) in `coordinator.py`.

---

## 3. Operation

### 3.1 Initial Setup

**Complete workflow from scratch:**

```bash
# 1. Start services
docker compose up -d

# 2. Initialize database schemas
uv run python src/cli/init_db.py

# 3. Generate test data
uv run python db-generation/generate_test_data.py

# 4. Load data with partitioning
uv run python src/cli/load_data.py bulk-load

# 5. Populate Be-Read table
uv run python src/cli/populate_beread.py

# 6. Populate Popular-Rank table
uv run python src/cli/populate_popularrank.py

# 7. Verify system
uv run python src/cli/monitor.py summary
```

### 3.2 Query Operations

#### 3.2.1 Interactive Query Shell

```bash
uv run python src/cli/query.py execute --interactive
```

**Commands in shell:**
- Type SQL query and press Enter
- `clear cache` - Clear all cached queries
- `exit` or `quit` - Exit shell

**Example session:**
```sql
SQL> SELECT * FROM "user" WHERE region='Beijing' LIMIT 3
✓ Routing: single on DBMS1
✓ Retrieved 3 rows

Returned 3 rows:
1. {'uid': 'u0', 'name': 'Alice', ...}
...

SQL> exit
```

#### 3.2.2 Single Query Execution

```bash
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"
```

**Options:**
- `--sql <query>` - SQL query to execute (required)
- `--no-cache` - Disable cache for this query

#### 3.2.3 Top-5 Popular Articles

```bash
# Daily top-5
uv run python src/cli/query.py top5 --granularity daily

# Weekly top-5
uv run python src/cli/query.py top5 -g weekly

# Monthly top-5
uv run python src/cli/query.py top5 -g monthly
```

**Output format:**
```
Top-5 daily popular articles:

1. Article 6: title6
   Category: technology
   Abstract: abstract of article 6...
   Text: Available
   Image: articles/article6/image_a6_0.jpg
...
```

#### 3.2.4 Example Queries

```bash
uv run python src/cli/query.py examples
```

Shows all example queries with descriptions.

### 3.3 Data Management

#### 3.3.1 Reload Data

```bash
# Clean database
docker compose down -v

# Start fresh
docker compose up -d
uv run python src/cli/init_db.py
uv run python src/cli/load_data.py bulk-load
uv run python src/cli/populate_beread.py
uv run python src/cli/populate_popularrank.py
```

#### 3.3.2 Verify Data Distribution

```bash
uv run python src/cli/load_data.py verify
```

Shows row counts per DBMS:
```
Data distribution verification:
DBMS1: 70 users, 25 articles, 353 reads
DBMS2: 30 users, 50 articles, 147 reads
```

#### 3.3.3 Verify Be-Read Population

```bash
uv run python src/cli/populate_beread.py verify
```

#### 3.3.4 Verify Popular-Rank

```bash
uv run python src/cli/populate_popularrank.py verify
```

---

## 4. Monitoring

### 4.1 System Summary

```bash
uv run python src/cli/monitor.py summary
```

**Shows:**
- DBMS status (ONLINE/OFFLINE)
- Total data counts per table
- Cache status and hit rate

**Use case:** Quick health check

### 4.2 DBMS Status

```bash
uv run python src/cli/monitor.py status
```

**Shows:**
- Connection status for each DBMS
- PostgreSQL version
- Database size
- Active connections
- Redis version and memory usage

**Use case:** Detailed health monitoring

### 4.3 Data Distribution

```bash
uv run python src/cli/monitor.py distribution
```

**Shows:**
- Fragmentation rules for all tables
- Actual row counts per DBMS
- Table sizes
- Replication verification

**Use case:** Verify data partitioning and replication

### 4.4 Workload Statistics

```bash
uv run python src/cli/monitor.py workload
```

**Shows:**
- Number of cached queries
- Cache hit/miss rate
- Recent queries with TTL
- Total Redis statistics

**Use case:** Performance monitoring and cache efficiency

---

## 5. Troubleshooting

### 5.1 Services Won't Start

**Problem:** `docker compose up -d` fails

**Solutions:**
1. Check if ports are already in use:
   ```bash
   lsof -i :5433
   lsof -i :5434
   lsof -i :6379
   ```
2. Stop conflicting services or change ports in `docker-compose.yml`
3. Ensure Docker Desktop is running
4. Check Docker logs:
   ```bash
   docker compose logs
   ```

### 5.2 Database Connection Errors

**Problem:** "Connection refused" errors

**Solutions:**
1. Verify services are running:
   ```bash
   docker compose ps
   ```
2. Wait 10-15 seconds after starting (PostgreSQL initialization)
3. Check database is ready:
   ```bash
   docker compose exec dbms1 psql -U ddbs -d ddbs1 -c "SELECT 1"
   ```
4. Restart services:
   ```bash
   docker compose restart
   ```

### 5.3 No Data Returned from Queries

**Problem:** Queries return empty results

**Solutions:**
1. Verify data is loaded:
   ```bash
   uv run python src/cli/monitor.py distribution
   ```
2. If empty, reload data:
   ```bash
   uv run python src/cli/load_data.py bulk-load
   ```
3. Check table names use double quotes:
   ```sql
   SELECT * FROM "user"  -- Correct
   SELECT * FROM user    -- May fail
   ```

### 5.4 Cache Not Working

**Problem:** Cache hits always 0

**Solutions:**
1. Verify Redis is running:
   ```bash
   docker compose ps redis
   ```
2. Check Redis connection:
   ```bash
   docker compose exec redis redis-cli ping
   ```
   Expected: `PONG`
3. Clear old cache:
   ```bash
   docker compose exec redis redis-cli FLUSHALL
   ```

### 5.5 Import Errors in Python

**Problem:** `ModuleNotFoundError`

**Solutions:**
1. Ensure dependencies are installed:
   ```bash
   uv sync
   ```
2. Use `uv run` prefix:
   ```bash
   uv run python src/cli/query.py execute -i
   ```

### 5.6 Permission Denied Errors

**Problem:** Cannot access Docker volumes

**Solutions:**
1. On Linux, add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```
   Then logout and login
2. Run with sudo (not recommended):
   ```bash
   sudo docker compose up -d
   ```

### 5.7 Port Already in Use

**Problem:** "Port is already allocated"

**Solutions:**
1. Find process using port:
   ```bash
   # macOS/Linux
   lsof -i :5434

   # Windows
   netstat -ano | findstr :5434
   ```
2. Kill process or change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5435:5432"  # Change 5434 to 5435
   ```

### 5.8 Disk Space Issues

**Problem:** "No space left on device"

**Solutions:**
1. Check Docker disk usage:
   ```bash
   docker system df
   ```
2. Clean unused Docker resources:
   ```bash
   docker system prune -a
   ```
3. Remove old volumes (CAUTION: loses data):
   ```bash
   docker compose down -v
   ```

---

## Appendix A: Database Schema

**Tables:**

1. **user** (13 attributes)
   - Primary key: `id`
   - Unique: `uid`
   - Indexed: `region`, `uid`

2. **article** (12 attributes)
   - Primary key: `id`
   - Unique: `aid`
   - Indexed: `category`, `aid`

3. **user_read** (9 attributes)
   - Primary key: `id`
   - Indexed: `uid`, `aid`

4. **be_read** (11 attributes)
   - Primary key: `id`
   - Unique: `aid`
   - Indexed: `aid`

5. **popular_rank** (4 attributes)
   - Primary key: `id`
   - Indexed: `temporalGranularity`

Full schema: See `sql/schema.sql`

---

## Appendix B: CLI Command Reference

### Data Management
```bash
# Initialize databases
uv run python src/cli/init_db.py

# Load data
uv run python src/cli/load_data.py bulk-load
uv run python src/cli/load_data.py verify

# Populate Be-Read
uv run python src/cli/populate_beread.py
uv run python src/cli/populate_beread.py verify

# Populate Popular-Rank
uv run python src/cli/populate_popularrank.py
uv run python src/cli/populate_popularrank.py verify
```

### Query Operations
```bash
# Interactive shell
uv run python src/cli/query.py execute --interactive

# Single query
uv run python src/cli/query.py execute --sql "QUERY"

# Top-5 articles
uv run python src/cli/query.py top5 -g {daily|weekly|monthly}

# Show examples
uv run python src/cli/query.py examples
```

### Monitoring
```bash
# System summary
uv run python src/cli/monitor.py summary

# DBMS status
uv run python src/cli/monitor.py status

# Data distribution
uv run python src/cli/monitor.py distribution

# Workload statistics
uv run python src/cli/monitor.py workload
```

### Docker Operations
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Clean restart (removes data)
docker compose down -v
docker compose up -d

# View logs
docker compose logs -f

# Access PostgreSQL
docker compose exec dbms1 psql -U ddbs -d ddbs1
docker compose exec dbms2 psql -U ddbs -d ddbs2

# Access Redis
docker compose exec redis redis-cli
```

---

## Appendix C: Fragmentation Rules Quick Reference

| Table | Attribute | DBMS1 | DBMS2 |
|-------|-----------|-------|-------|
| User | region | Beijing | Hong Kong |
| Article | category | science (replicated) | science + technology |
| Read | (co-located) | Beijing users' reads | Hong Kong users' reads |
| Be-Read | category | science (replicated) | science + technology |
| Popular-Rank | temporalGranularity | daily | weekly, monthly |

---

## Support

For issues or questions:
1. Check troubleshooting section (Section 5)
2. Review README.md for quick reference
3. Examine logs: `docker compose logs`
4. Contact: [Your contact information]

---

**End of Manual**
