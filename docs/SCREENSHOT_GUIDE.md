# Screenshot Guide for Report

## Screenshots Needed (10 total)

### Hot-Cold Standby & Fault Tolerance

#### 1. Standby System Status
**Command:**
```bash
uv run python src/cli/monitor.py status
```

**What it shows:**
- DBMS1 (Primary) status
- DBMS1-STANDBY (Hot standby) status
- DBMS2 status
- All three database instances online

**Where to use:** Section 5.6 "Fault Tolerance - Hot-Cold Standby"

**Caption:** "System status showing primary DBMS1 and hot standby DBMS1-STANDBY both online"

---

#### 2. Failover Test - Before Failure
**Command:**
```bash
# First query - DBMS1 is online
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache
```

**What it shows:** Normal query execution on primary DBMS1

**Where to use:** Section 5.6 "Fault Tolerance - Failover Demonstration"

**Caption:** "Query execution on primary DBMS1 under normal operation"

---

#### 3. Failover Test - During Failure
**Commands:**
```bash
# Stop primary DBMS1
docker stop ddbs-group-project-dbms1-1

# Same query - should automatically failover
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache
```

**What it shows:**
- Warning message: "⚠ DBMS1 failed, trying standby DBMS1-STANDBY"
- Same data retrieved from standby
- Zero downtime

**Where to use:** Section 5.6 "Fault Tolerance - Automatic Failover"

**Caption:** "Automatic failover to DBMS1-STANDBY when primary DBMS1 fails"

---

### Regular Operations

#### 4. System Deployment
**Command:**
```bash
docker compose ps
```

**What it shows:** All services running (dbms1, dbms1-standby, dbms2, redis, minio)

**Where to use:** Section 5.1 "System Deployment"

**Caption:** "System deployment showing all distributed components operational including hot standby"

---

#### 5. Data Distribution
**Command:**
```bash
uv run python src/cli/monitor.py distribution
```

**What it shows:**
- Fragmentation rules
- Actual row counts per DBMS
- Table sizes

**Where to use:** Section 5.2 "Data Distribution"

**Caption:** "Data distribution across DBMS1 and DBMS2 showing correct horizontal fragmentation"

---

#### 6. System Summary
**Command:**
```bash
uv run python src/cli/monitor.py summary
```

**What it shows:**
- DBMS status (both online)
- Total row counts
- Cache hit rate

**Where to use:** Section 5.5 "Monitoring Capabilities"

**Caption:** "System monitoring summary showing operational status and data metrics"

---

#### 7. Query Execution
**Command:**
```bash
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" LIMIT 10"
```

**What it shows:** Query results from distributed database

**Where to use:** Section 5.3 "Query Performance"

**Caption:** "Distributed query execution merging results from both DBMS"

---

#### 8. Cache Performance
**Two screenshots - run same query twice:**

**First run:**
```bash
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"
```

**Second run (same query):**
```bash
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"
```

**What it shows:**
- First: Normal execution
- Second: Cache hit message

**Where to use:** Section 5.3 "Query Performance" (cache demonstration)

**Caption:** "Query cache demonstration: first execution vs. cached execution"

---

#### 9. Top-5 Popular Articles (Distributed Join)
**Command:**
```bash
uv run python src/cli/query.py top5 --granularity daily
```

**What it shows:**
- Top-5 articles with complete details
- Article title, category, abstract
- Image/video paths

**Where to use:** Section 5.4 "Distributed Join"

**Caption:** "Top-5 daily popular articles with distributed join across DBMS"

---

#### 10. Interactive Query Shell (Optional but good)
**Command:**
```bash
uv run python src/cli/query.py execute -i
```

**Then type a few queries in the shell**

**What it shows:** Interactive session with multiple queries

**Where to use:** Section 5.3 "Query Performance"

**Caption:** "Interactive query shell for ad-hoc distributed queries"

---

## How to Take Screenshots

### macOS:
- **Full screen:** Cmd + Shift + 3
- **Selection:** Cmd + Shift + 4
- **Window:** Cmd + Shift + 4, then press Space, click window

### Windows:
- **Full screen:** Windows + PrtScn
- **Snipping Tool:** Windows + Shift + S

### Linux:
- **GNOME:** PrtScn or Shift + PrtScn
- **KDE:** Spectacle (built-in)

## Screenshot Tips

1. **Clear terminal history** before taking screenshots:
   ```bash
   clear
   ```

2. **Use full commands** (not aliases) so they're clear

3. **Crop** to show only relevant terminal output

4. **Readable font size** - 14pt or larger

5. **Consistent terminal theme** - light or dark (dark looks more professional)

6. **Save as PNG** for best quality

7. **Name files clearly:**
   - `01_standby_status.png`
   - `02_failover_before.png`
   - `03_failover_during.png`
   - `04_docker_ps.png`
   - `05_distribution.png`
   - `06_summary.png`
   - `07_query_execution.png`
   - `08_cache_hit.png`
   - `09_top5_articles.png`
   - `10_interactive_shell.png`

## Directory Structure

Save screenshots in:
```
docs/
├── screenshots/
│   ├── 01_standby_status.png
│   ├── 02_failover_before.png
│   ├── 03_failover_during.png
│   ├── 04_docker_ps.png
│   ├── 05_distribution.png
│   ├── 06_summary.png
│   ├── 07_query_execution.png
│   ├── 08_cache_hit.png
│   ├── 09_top5_articles.png
│   └── 10_interactive_shell.png
├── REPORT_TEMPLATE.md
├── MANUAL.md
└── ...
```

## Inserting Screenshots in Report

If converting to PDF/Word, use markdown image syntax:

```markdown
![Caption text](screenshots/01_docker_ps.png)
```

Or in LaTeX:

```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{screenshots/01_docker_ps.png}
\caption{System deployment showing all distributed components operational}
\end{figure}
```

## Quick Screenshot Session (7 minutes)

Run these commands in order and screenshot each:

```bash
# HOT-COLD STANDBY DEMONSTRATION

# 1. Standby system status (all three DBMS)
clear && uv run python src/cli/monitor.py status

# 2. Failover test - before failure (normal operation)
clear && uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache

# 3. Failover test - during failure
docker stop ddbs-group-project-dbms1-1
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache

# IMPORTANT: Restart DBMS1 before continuing
docker start ddbs-group-project-dbms1-1
sleep 3

# REGULAR OPERATIONS

# 4. System deployment
clear && docker compose ps

# 5. Data distribution
clear && uv run python src/cli/monitor.py distribution

# 6. System summary
clear && uv run python src/cli/monitor.py summary

# 7. Query execution
clear && uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" LIMIT 10"

# 8. Cache (first run)
clear && uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# 9. Cache (second run - same query)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# 10. Top-5 articles
clear && uv run python src/cli/query.py top5 --granularity daily
```

## Done!

You should now have all screenshots needed for a complete report that demonstrates:
- ✅ Hot-cold standby fault tolerance
- ✅ Automatic failover mechanism
- ✅ System deployment with standby
- ✅ Data partitioning
- ✅ Query execution
- ✅ Cache performance
- ✅ Distributed joins
- ✅ Monitoring capabilities
