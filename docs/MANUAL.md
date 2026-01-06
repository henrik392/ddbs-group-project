# Distributed Database System - Operation Manual

**Version:** 1.0
**Authors:** Henrik Kvamme, Rui Silveira
**Last Updated:** December 2024

---

## Important Note

**All CLI commands require `PYTHONPATH=.` to be set.** Two options:
1. **Use Makefile (Recommended):** `make setup-10g`, `make query-shell`, etc.
2. **Manual commands:** Prepend `PYTHONPATH=.` to all `uv run python src/cli/...` commands

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
- Python 3.14 or higher
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

This installs all dependencies from `pyproject.toml` including: psycopg, redis, click, hdfs, fastapi, sqlalchemy, pydantic

**Step 3: Start Infrastructure**
```bash
docker compose up -d
```

This starts:
- PostgreSQL DBMS1 (port 5434) - Beijing data
- PostgreSQL DBMS2 (port 5433) - Hong Kong data
- PostgreSQL DBMS-STANDBY (port 5435) - Hot-cold standby
- Redis DC1 (port 6379) - Beijing cache
- Redis DC2 (port 6381) - Hong Kong cache
- Redis STANDBY (port 6380) - Shared standby cache
- HDFS NameNode (ports 9870, 9000) - Distributed file system
- HDFS DataNode (port 9864) - Data storage node

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
| DBMS-STANDBY | localhost | 5435 | ddbs1 | ddbs | ddbs |
| Redis DC1 | localhost | 6379 | - | - | ddbs_redis_secure_2024_dc1 |
| Redis DC2 | localhost | 6381 | - | - | ddbs_redis_secure_2024_dc2 |
| Redis STANDBY | localhost | 6380 | - | - | ddbs_redis_secure_2024_standby |
| HDFS NameNode | localhost | 9870/9000 | - | - | - |
| HDFS DataNode | localhost | 9864 | - | - | - |

**Connection Strings:**
```python
# DBMS Connections
DBMS1 = "postgresql://ddbs:ddbs@localhost:5434/ddbs1"
DBMS2 = "postgresql://ddbs:ddbs@localhost:5433/ddbs2"
DBMS_STANDBY = "postgresql://ddbs:ddbs@localhost:5435/ddbs1"

# Redis Connections (with authentication)
REDIS_DC1 = {"host": "localhost", "port": 6379, "password": "ddbs_redis_secure_2024_dc1"}
REDIS_DC2 = {"host": "localhost", "port": 6381, "password": "ddbs_redis_secure_2024_dc2"}
REDIS_STANDBY = {"host": "localhost", "port": 6380, "password": "ddbs_redis_secure_2024_standby"}

# HDFS Configuration
HDFS_NAMENODE = "http://localhost:9870"
HDFS_WEBHDFS = "http://localhost:9000"
```

### 2.2 Docker Compose Configuration

File: `docker-compose.yml`

- **Ports:** Can be changed if conflicts exist
- **Volumes:** dbms1, dbms2, dbms_standby, redis1, redis2, redis_standby, namenode, datanode1
- **Redis Auth:** Password configured in redis*.conf files

### 2.3 Cache Configuration

**Datacenter-Aware Caching:**
- **DC1 (Beijing):** redis1:6379 for DBMS1 queries
- **DC2 (Hong Kong):** redis2:6381 for DBMS2 queries
- **STANDBY:** redis-standby:6380 for failover

**TTL Settings:** Edit `CACHE_TTL = 60` in `src/config.py` (default: 60 seconds)

### 2.4 Failover Architecture

- **DBMS-STANDBY** (port 5435): Replica of DBMS1, auto-failover when DBMS1 unavailable
- **redis-standby** (port 6380): Backup cache for both DC1 and DC2, auto-failover when primary cache unavailable

---

## 3. Operation

### 3.1 Initial Setup

**IMPORTANT:** All CLI commands require `PYTHONPATH=.` to be set. Either:
1. Use Makefile commands (recommended): `make setup-10g`
2. Set PYTHONPATH manually: `PYTHONPATH=. uv run python src/cli/...`

**Complete workflow from scratch:**

```bash
# 1. Start services
docker compose up -d
# OR: make setup

# 2. Initialize database schemas
PYTHONPATH=. uv run python src/cli/init_db.py
# OR: make init-db

# 3. Generate production data (10G/50G/100G)
PYTHONPATH=. uv run python db-generation/generate_production_data.py --scale 10G
# OR: make generate-data-10g

# 4. Load partitioned SQL into databases
PYTHONPATH=. uv run python src/cli/load_data.py bulk-load --sql-dir generated_data
# OR: make load-data

# 5. Upload media files to HDFS
PYTHONPATH=. uv run python src/cli/load_data.py upload-media --mock-dir production_articles
# OR: make upload-media

# 6. Populate Be-Read table
PYTHONPATH=. uv run python src/cli/populate_beread.py
# OR: make populate-beread

# 7. Populate Popular-Rank table
PYTHONPATH=. uv run python src/cli/populate_popularrank.py
# OR: make populate-popularrank

# 8. Verify system
PYTHONPATH=. uv run python src/cli/monitor.py summary
# OR: make monitor
```

**Recommended: Use Makefile for all operations:**
```bash
make setup-10g    # Complete setup with 10G dataset
make query-shell  # Interactive queries
make monitor      # System status
```

### 3.2 Query Operations

#### 3.2.1 Interactive Query Shell

```bash
PYTHONPATH=. uv run python src/cli/query.py execute --interactive
# OR: make query-shell
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
PYTHONPATH=. uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"
```

**Options:**
- `--sql <query>` - SQL query to execute (required)
- `--no-cache` - Disable cache for this query

#### 3.2.3 Top-5 Popular Articles

```bash
# Daily top-5
PYTHONPATH=. uv run python src/cli/query.py top5 --granularity daily
# OR: make top5-daily

# Weekly top-5
PYTHONPATH=. uv run python src/cli/query.py top5 -g weekly
# OR: make top5-weekly

# Monthly top-5
PYTHONPATH=. uv run python src/cli/query.py top5 -g monthly
# OR: make top5-monthly
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
PYTHONPATH=. uv run python src/cli/query.py examples
# OR: make query-examples
```

### 3.3 Data Management

#### 3.3.1 Reload Data

```bash
# Using Makefile (recommended)
make clean
make setup-10g

# Or manually with PYTHONPATH
docker compose down -v
docker compose up -d
PYTHONPATH=. uv run python src/cli/init_db.py
PYTHONPATH=. uv run python db-generation/generate_production_data.py --scale 10G
PYTHONPATH=. uv run python src/cli/load_data.py bulk-load --sql-dir generated_data
PYTHONPATH=. uv run python src/cli/load_data.py upload-media --mock-dir production_articles
PYTHONPATH=. uv run python src/cli/populate_beread.py
PYTHONPATH=. uv run python src/cli/populate_popularrank.py
```

#### 3.3.2 Verify Data Distribution

```bash
PYTHONPATH=. uv run python src/cli/load_data.py verify
# OR: make verify-data
```

#### 3.3.3 Verify Be-Read Population

```bash
PYTHONPATH=. uv run python src/cli/populate_beread.py verify
# OR: make verify-beread
```

#### 3.3.4 Verify Popular-Rank

```bash
PYTHONPATH=. uv run python src/cli/populate_popularrank.py verify
# OR: make verify-popularrank
```

---

## 4. Monitoring

### 4.1 System Summary

```bash
PYTHONPATH=. uv run python src/cli/monitor.py summary
# OR: make monitor
```

Shows: DBMS status, data counts, cache status

### 4.2 DBMS Status

```bash
PYTHONPATH=. uv run python src/cli/monitor.py status
```

Shows: Connection status, PostgreSQL version, database size, Redis stats

### 4.3 Data Distribution

```bash
PYTHONPATH=. uv run python src/cli/monitor.py distribution
```

Shows: Fragmentation rules, row counts per DBMS, replication status

### 4.4 Workload Statistics

```bash
PYTHONPATH=. uv run python src/cli/monitor.py workload
```

Shows: Cached queries, cache hit rate, Redis statistics

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
   PYTHONPATH=. uv run python src/cli/monitor.py distribution
   # OR: make monitor
   ```
2. If empty, reload data:
   ```bash
   make setup-10g
   ```
3. Check table names use double quotes:
   ```sql
   SELECT * FROM "user"  -- Correct
   SELECT * FROM user    -- May fail
   ```

### 5.4 Cache Not Working

**Problem:** Cache hits always 0

**Solutions:**
1. Verify Redis running: `docker compose ps redis1 redis2 redis-standby`
2. Test connection: `docker compose exec redis1 redis-cli -a ddbs_redis_secure_2024_dc1 ping`
3. Clear cache: `docker compose exec redis1 redis-cli -a ddbs_redis_secure_2024_dc1 FLUSHALL`

**Note:** Replace `redis1` with `redis2` or `redis-standby` and use corresponding password as needed.

### 5.5 Import Errors in Python

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solutions:**
1. Use Makefile commands (recommended):
   ```bash
   make query-shell
   ```
2. Or prepend `PYTHONPATH=.` to manual commands:
   ```bash
   PYTHONPATH=. uv run python src/cli/query.py execute -i
   ```
3. Ensure dependencies installed:
   ```bash
   uv sync
   # OR: make deps
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

### 5.9 HDFS Connection Issues

**Problem:** Cannot access HDFS or upload files

**Solutions:**
1. Check services: `docker compose ps namenode datanode1`
2. Open web UI: http://localhost:9870
3. Check health: `docker compose exec namenode hdfs dfsadmin -report`
4. Restart: `docker compose restart namenode datanode1` (wait 30-60s for DataNode)

### 5.10 Redis Authentication Failures

**Problem:** "NOAUTH Authentication required"

**Solutions:**
1. Always use `-a` flag: `docker compose exec redis1 redis-cli -a ddbs_redis_secure_2024_dc1`
2. Check passwords in `redis*.conf` files match `src/config.py`

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

**Note:** All commands require `PYTHONPATH=.` or use Makefile (recommended).

### Data Management
```bash
# Using Makefile (recommended)
make init-db
make generate-data-10g
make load-data
make upload-media
make populate-all
make verify-data

# Or with PYTHONPATH manually
PYTHONPATH=. uv run python src/cli/init_db.py
PYTHONPATH=. uv run python db-generation/generate_production_data.py --scale 10G
PYTHONPATH=. uv run python src/cli/load_data.py bulk-load --sql-dir generated_data
PYTHONPATH=. uv run python src/cli/load_data.py upload-media --mock-dir production_articles
PYTHONPATH=. uv run python src/cli/load_data.py verify
PYTHONPATH=. uv run python src/cli/populate_beread.py
PYTHONPATH=. uv run python src/cli/populate_beread.py verify
PYTHONPATH=. uv run python src/cli/populate_popularrank.py
PYTHONPATH=. uv run python src/cli/populate_popularrank.py verify
```

### Query Operations
```bash
# Using Makefile
make query-shell
make top5-daily
make top5-weekly
make query-examples

# Or with PYTHONPATH
PYTHONPATH=. uv run python src/cli/query.py execute --interactive
PYTHONPATH=. uv run python src/cli/query.py execute --sql "QUERY"
PYTHONPATH=. uv run python src/cli/query.py top5 -g {daily|weekly|monthly}
PYTHONPATH=. uv run python src/cli/query.py examples
```

### Monitoring
```bash
# Using Makefile
make monitor

# Or with PYTHONPATH
PYTHONPATH=. uv run python src/cli/monitor.py summary
PYTHONPATH=. uv run python src/cli/monitor.py status
PYTHONPATH=. uv run python src/cli/monitor.py distribution
PYTHONPATH=. uv run python src/cli/monitor.py workload
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
docker compose exec dbms-standby psql -U ddbs -d ddbs1

# Access Redis (requires authentication)
docker compose exec redis1 redis-cli -a ddbs_redis_secure_2024_dc1
docker compose exec redis2 redis-cli -a ddbs_redis_secure_2024_dc2
docker compose exec redis-standby redis-cli -a ddbs_redis_secure_2024_standby

# Access HDFS Web UI
# http://localhost:9870 - NameNode interface for file browsing and monitoring
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
