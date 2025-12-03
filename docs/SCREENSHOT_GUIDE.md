# Screenshot Guide for Report

## Screenshots Needed (7 total)

### 1. System Deployment
**Command:**
```bash
docker compose ps
```

**What it shows:** All services running (dbms1, dbms2, redis, minio)

**Where to use:** Section 5.1 "System Deployment"

**Caption:** "System deployment showing all distributed components operational"

---

### 2. Data Distribution
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

### 3. System Summary
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

### 4. Query Execution
**Command:**
```bash
uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" LIMIT 10"
```

**What it shows:** Query results from distributed database

**Where to use:** Section 5.3 "Query Performance"

**Caption:** "Distributed query execution merging results from both DBMS"

---

### 5. Cache Performance
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

### 6. Top-5 Popular Articles (Distributed Join)
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

### 7. Interactive Query Shell (Optional but good)
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
   - `01_docker_ps.png`
   - `02_distribution.png`
   - `03_summary.png`
   - `04_query_execution.png`
   - `05_cache_hit.png`
   - `06_top5_articles.png`
   - `07_interactive_shell.png`

## Directory Structure

Save screenshots in:
```
docs/
├── screenshots/
│   ├── 01_docker_ps.png
│   ├── 02_distribution.png
│   ├── 03_summary.png
│   ├── 04_query_execution.png
│   ├── 05_cache_hit.png
│   ├── 06_top5_articles.png
│   └── 07_interactive_shell.png
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

## Quick Screenshot Session (5 minutes)

Run these commands in order and screenshot each:

```bash
# 1. System deployment
docker compose ps

# 2. Data distribution
clear && uv run python src/cli/monitor.py distribution

# 3. System summary
clear && uv run python src/cli/monitor.py summary

# 4. Query execution
clear && uv run python src/cli/query.py execute --sql "SELECT uid, name, region FROM \"user\" LIMIT 10"

# 5. Cache (first run)
clear && uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# 6. Cache (second run - same query)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 5"

# 7. Top-5 articles
clear && uv run python src/cli/query.py top5 --granularity daily
```

## Done!

You should now have all screenshots needed for a complete report that demonstrates:
- ✅ System deployment
- ✅ Data partitioning
- ✅ Query execution
- ✅ Cache performance
- ✅ Distributed joins
- ✅ Monitoring capabilities
