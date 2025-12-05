# Distributed Database System for News Article Management

**Authors:** Henrik Kvamme, Rui Silveira
**Course:** Distributed Database Systems
**Institution:** Tsinghua University

---

## Abstract

This project implements a distributed database management system for a news article platform using horizontal fragmentation and replication across multiple database nodes. The system manages both structured data (5 relational tables) and unstructured data (text, images, video) using PostgreSQL for structured data, Redis for caching, and MinIO for unstructured file storage. We implement a coordinator-based architecture that handles query routing, distributed joins, and result merging while maintaining ACID properties. The system successfully demonstrates data partitioning, replication, distributed query processing, and comprehensive monitoring capabilities. Performance evaluation shows effective load distribution and query caching with hit rates exceeding 15%.

**Keywords:** Distributed databases, horizontal fragmentation, query coordination, replication, caching

---

## 1. Introduction

### 1.1 Problem Background and Motivation

Modern news platforms handle massive amounts of data distributed across geographic regions and require high availability, scalability, and performance. Traditional centralized database systems face limitations in:

- **Scalability:** Single-node systems cannot handle growing data volumes
- **Availability:** Single point of failure affects entire system
- **Performance:** Geographic distribution causes high latency
- **Data Locality:** Users access data from different regions

Distributed database systems address these challenges by partitioning data across multiple nodes, replicating critical data, and processing queries in parallel.

### 1.2 Objectives

This project aims to implement a distributed database system that:

1. Manages structured data (User, Article, Read, Be-Read, Popular-Rank tables) and unstructured data (text, images, videos)
2. Implements horizontal fragmentation based on business logic (region, category, temporal granularity)
3. Handles replication for high availability
4. Provides efficient distributed query processing with caching
5. Monitors system health and workload

---

## 2. Existing Solutions

### 2.1 Distributed Database Technologies

**MongoDB Sharding:**
- Horizontal scaling through sharding
- Automatic data distribution
- Built-in replication
- Limitation: Document-oriented, not relational

**MySQL Cluster:**
- Synchronous replication
- Shared-nothing architecture
- Limitation: Complex configuration, limited flexibility

**PostgreSQL with Citus:**
- Distributed PostgreSQL
- Horizontal scaling
- SQL compatibility
- Limitation: Requires Citus extension

**Apache Cassandra:**
- Wide-column store
- Tunable consistency
- Limitation: Not ACID-compliant

### 2.2 Our Approach

We chose a **custom coordinator-based architecture** with:
- PostgreSQL for ACID compliance and relational model
- Redis for high-performance caching
- MinIO for scalable object storage
- Python-based coordinator for query routing

This provides full control over fragmentation rules, simpler deployment, and better understanding of distributed database concepts.

---

## 3. Problem Definition

### 3.1 Data Model

**Structured Tables (5):**

1. **User** (13 attributes): User profiles and preferences
2. **Article** (12 attributes): Article metadata and content references
3. **Read** (9 attributes): User reading history
4. **Be-Read** (11 attributes): Article popularity statistics
5. **Popular-Rank** (4 attributes): Temporal rankings (daily/weekly/monthly)

**Unstructured Data:**
- Article text files
- Images (1-5 per article)
- Videos (5% of articles)

### 3.2 Fragmentation Strategy

**Horizontal Fragmentation Rules:**

| Table | Fragmentation Attribute | Distribution |
|-------|------------------------|--------------|
| User | region | Beijing → DBMS1, Hong Kong → DBMS2 |
| Article | category | science → DBMS1 & DBMS2 (replicated), technology → DBMS2 |
| Read | Co-located with User | Beijing reads → DBMS1, Hong Kong reads → DBMS2 |
| Be-Read | category (replicated) | science → both DBMS, technology → DBMS2 |
| Popular-Rank | temporalGranularity | daily → DBMS1, weekly/monthly → DBMS2 |

### 3.3 Requirements

1. **Data Loading:** Bulk load with automatic partitioning
2. **Query Processing:**
   - Query users/articles with conditions
   - Populate Be-Read from Read table
   - Top-5 popular articles with details (distributed join)
3. **Monitoring:** DBMS status, data distribution, workload

---

## 4. Proposed Solution

### 4.1 System Architecture

```
┌──────────────────────────────────────────┐
│        Coordinator (Python)              │
│  • Query parsing & routing               │
│  • Query execution & result merging      │
│  • Cache management (Redis)              │
└──────────┬───────────────────────────────┘
           │
    ┌──────┴───────┐
    ↓              ↓
┌─────────┐    ┌─────────┐
│ DBMS1   │    │ DBMS2   │
│(Beijing)│    │(HongKong)│
│PostgreSQL    │PostgreSQL│
│ :5434   │    │ :5433   │
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

### 4.2 Components

#### 4.2.1 Database Layer (PostgreSQL)

Two PostgreSQL instances:
- **DBMS1** (port 5434): Beijing region data
- **DBMS2** (port 5433): Hong Kong region data + replicated science articles

Schema includes proper indexes:
- `idx_user_region` on User(region)
- `idx_article_category` on Article(category)
- `idx_user_uid` for joins

#### 4.2.2 Cache Layer (Redis)

Query result caching:
- Key: MD5 hash of SQL query
- TTL: 60 seconds
- Stores JSON serialized results
- Hit rate tracking

#### 4.2.3 Storage Layer (MinIO)

Object storage for unstructured data:
- Article text files
- Images (JPEG/PNG)
- Videos (FLV format)

#### 4.2.4 Coordinator Layer

**Query Router** (`src/domains/query/router.py`):
- Parses SQL to identify table and conditions
- Applies fragmentation rules
- Determines routing strategy (single/parallel)

**Query Executor** (`src/domains/query/executor.py`):
- Executes queries on target DBMS
- Handles three strategies:
  - **Single:** Query one DBMS
  - **Parallel:** Query multiple DBMS, merge results
  - **Join:** Distributed join (Popular-Rank + Article)

**Query Coordinator** (`src/domains/query/coordinator.py`):
- Cache lookup (Redis)
- Routes query (via Router)
- Executes query (via Executor)
- Caches results

### 4.3 Key Operations

#### 4.3.1 Data Loading

```python
# Automatic partitioning during generation
if user.region == "Beijing":
    dbms1_users.append(user)
else:
    dbms2_users.append(user)
```

#### 4.3.2 Be-Read Population

```python
# Aggregate reads from both DBMS
reads_dbms1 = fetch_reads(DBMS1)
reads_dbms2 = fetch_reads(DBMS2)
aggregated = group_by_article(reads_dbms1 + reads_dbms2)

# Insert with replication rules
for article in aggregated:
    if article.category == "science":
        insert(DBMS1, article)
        insert(DBMS2, article)  # Replicate
    else:
        insert(DBMS2, article)
```

#### 4.3.3 Distributed Join (Top-5 Popular Articles)

```python
# Step 1: Fetch ranking from appropriate DBMS
ranking = query(rank_dbms, "SELECT articleAidList FROM popular_rank WHERE temporalGranularity='daily'")

# Step 2: Extract article IDs
aids = ranking[0]['articleaidlist'].split(',')

# Step 3: Fetch article details from both DBMS
articles_dbms1 = query(DBMS1, f"SELECT * FROM article WHERE aid IN ({aids})")
articles_dbms2 = query(DBMS2, f"SELECT * FROM article WHERE aid IN ({aids})")

# Step 4: Merge and maintain order
articles = merge_in_order(articles_dbms1 + articles_dbms2, aids)
```

### 4.4 CLI Tools

**Data Management:**
- `init_db.py` - Initialize database schemas
- `load_data.py` - Bulk load with partitioning
- `populate_beread.py` - Populate Be-Read table
- `populate_popularrank.py` - Generate rankings

**Query Interface:**
- `query.py execute` - Execute queries
- `query.py top5` - Top-5 popular articles
- `query.py examples` - Show example queries

**Monitoring:**
- `monitor.py summary` - System overview
- `monitor.py status` - DBMS health
- `monitor.py distribution` - Data distribution
- `monitor.py workload` - Query statistics

---

## 5. Solution Evaluation

### 5.1 System Deployment

[SCREENSHOT: docker compose ps showing all services running]

The system successfully deploys with:
- 2 PostgreSQL instances (DBMS1, DBMS2)
- 1 Redis instance
- 1 MinIO instance

### 5.2 Data Distribution

[SCREENSHOT: monitor.py distribution output]

**Verification:**
- User table: 70 rows in DBMS1 (Beijing), 30 rows in DBMS2 (Hong Kong)
- Article table: 25 science articles in both DBMS (replicated), 25 technology articles in DBMS2 only
- Read table: Co-located with User (353 in DBMS1, 147 in DBMS2)
- Be-Read table: Properly replicated (25 in DBMS1, 50 in DBMS2)
- Popular-Rank: 1 daily in DBMS1, 2 weekly/monthly in DBMS2

**Result:** Fragmentation rules correctly implemented ✓

### 5.3 Query Performance

[SCREENSHOT: query execution with cache hit]

**Test Queries:**

1. **Single DBMS Query (Beijing users):**
   - Routed to DBMS1 only
   - Response time: ~50ms

2. **Distributed Query (All users):**
   - Parallel execution on both DBMS
   - Results merged correctly
   - Response time: ~80ms

3. **Cached Query:**
   - First execution: ~60ms
   - Second execution: ~5ms (cache hit)
   - **Cache hit rate: 16.67%**

### 5.4 Distributed Join

[SCREENSHOT: top5 daily output with article details]

**Top-5 Daily Popular Articles Query:**
- Fetches ranking from DBMS1 (daily granularity)
- Queries article details from both DBMS
- Merges results maintaining ranking order
- Returns complete article information (title, category, abstract, text, image, video)

**Result:** Distributed join successful ✓

### 5.5 Monitoring Capabilities

[SCREENSHOT: monitor.py summary]

**Status Monitoring:**
- DBMS connection status (ONLINE/OFFLINE)
- Database sizes (DBMS1: 7996 kB, DBMS2: 7972 kB)
- Active connections
- Redis memory usage

**Data Monitoring:**
- Row counts per table per DBMS
- Total data volume
- Distribution verification

**Workload Monitoring:**
- Cached queries count
- Cache hit/miss rate
- Query TTL tracking

**Result:** All monitoring requirements met ✓

### 5.6 Functional Requirements

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| Bulk loading with partitioning | `load_data.py` | ✓ |
| Query users/articles | `query.py execute` | ✓ |
| Populate Be-Read | `populate_beread.py` | ✓ |
| Top-5 popular articles | `query.py top5` with distributed join | ✓ |
| Monitoring | `monitor.py` (4 commands) | ✓ |
| Data replication | Science articles, Be-Read replicated | ✓ |
| Cache | Redis with 60s TTL, hit rate tracking | ✓ |

### 5.7 Advanced Features: Hot/Cold Standby

[SCREENSHOT: monitor.py status showing DBMS1, DBMS1-STANDBY, and DBMS2 all online]

**Implementation:**
The system implements hot/cold standby for DBMS1 to provide fault tolerance for Beijing region data.

**Architecture:**
- **DBMS1** (Primary, port 5434): Active Beijing region database
- **DBMS1-STANDBY** (Standby, port 5435): Hot standby replica with identical data
- Automatic failover when primary becomes unavailable

[SCREENSHOT: Failover test - query before failure on DBMS1]

**Failover Test - Normal Operation:**
- Query executed on primary DBMS1
- Response time: ~50ms
- Status: PRIMARY ACTIVE

[SCREENSHOT: Failover test - during failure showing automatic failover to standby]

**Failover Test - During Failure:**
1. Stop primary DBMS1: `docker stop ddbs-group-project-dbms1-1`
2. Execute same query automatically routes to DBMS1-STANDBY
3. Warning message: "⚠ DBMS1 failed, trying standby DBMS1-STANDBY"
4. Query succeeds with identical results
5. Zero downtime for Beijing users

**Benefits:**
- High availability for Beijing region data (User, Read, science Article, daily Popular-Rank)
- Automatic failover without manual intervention
- Data consistency maintained through identical schema and data
- Transparent to application layer

**Result:** Fault tolerance successfully implemented ✓

---

## 6. Conclusion

### 6.1 Achievements

This project successfully implements a distributed database system with:

1. **Horizontal fragmentation** based on business logic (region, category, temporal granularity)
2. **Replication** for high availability (science articles, Be-Read table)
3. **Distributed query processing** with intelligent routing and result merging
4. **Query caching** using Redis (60s TTL, 16.67% hit rate)
5. **Distributed joins** for complex queries (Popular-Rank + Article)
6. **Comprehensive monitoring** of DBMS status, data distribution, and workload
7. **Hot/cold standby** with automatic failover for fault tolerance

The system demonstrates fundamental distributed database concepts while maintaining simplicity and practicality, and successfully implements one optional advanced feature (hot/cold standby) for enhanced reliability.

### 6.2 Key Learnings

- Fragmentation strategy significantly impacts query performance
- Caching reduces database load and improves response time
- Coordinator pattern provides flexibility in query routing
- Monitoring is essential for distributed system management
- Proper indexing is critical for join performance

### 6.3 Future Work

**Performance Optimization:**
- Implement query result pagination for large datasets
- Add connection pooling for better resource management
- Optimize distributed join algorithms

**High Availability:**
- Enhanced health monitoring with predictive failure detection
- Multi-region standby replicas (Hong Kong standby for DBMS2)
- Automatic recovery and data reconciliation after failure

**Scalability:**
- Support for dynamic DBMS node addition/removal
- Automatic data rebalancing
- Horizontal scaling of coordinator layer

**Advanced Features:**
- Distributed transactions with 2PC
- Query optimization and cost-based routing
- Real-time monitoring dashboard
- Support for more complex joins (User + Read + Article)

---

## 7. References

1. Özsu, M. T., & Valduriez, P. (2020). *Principles of distributed database systems* (4th ed.). Springer.

2. PostgreSQL Global Development Group. (2024). PostgreSQL 16 Documentation. https://www.postgresql.org/docs/16/

3. Redis Labs. (2024). Redis Documentation. https://redis.io/documentation

4. MinIO, Inc. (2024). MinIO Object Storage. https://min.io/docs/

5. Docker, Inc. (2024). Docker Documentation. https://docs.docker.com/

6. Garcia-Molina, H., Ullman, J. D., & Widom, J. (2008). *Database systems: The complete book* (2nd ed.). Pearson.

7. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). *Database system concepts* (7th ed.). McGraw-Hill.

---

## Appendix A: Load Allocation

**Henrik Kvamme (Lead):**
- System architecture design (40%)
- Query coordinator implementation (router, executor, coordinator)
- Distributed join implementation
- Project documentation and report writing
- Total: 60%

**Rui Silveira:**
- Data loading and partitioning implementation
- Be-Read and Popular-Rank population logic
- Monitoring system implementation
- Testing and verification
- Total: 40%

Both members collaborated on system design, debugging, and final integration.
