# Project Delivery Checklist

Use this checklist to ensure all deliverables are complete and ready for submission.

---

## 📦 Deliverables (Required)

### 1. Report (30% of grade)
- [ ] Report completed based on `docs/REPORT_TEMPLATE.md`
- [ ] All sections filled out:
  - [ ] Abstract
  - [ ] Introduction (Background, Motivation, Objectives)
  - [ ] Existing Solutions
  - [ ] Problem Definition (Data Model, Fragmentation Strategy, Requirements)
  - [ ] Proposed Solution (Architecture, Components, Key Operations, CLI Tools)
  - [ ] Solution Evaluation (all 7 subsections with screenshots)
  - [ ] Conclusion (Achievements, Key Learnings, Future Work)
  - [ ] References (7 sources included)
  - [ ] Appendix A: Load Allocation (**REQUIRED - specify who did what**)
- [ ] 8 screenshots taken and inserted (see `docs/SCREENSHOT_GUIDE.md`)
- [ ] Report formatted properly (research paper style)
- [ ] Report exported to PDF
- [ ] File named: `DDBS_Project_Report_HenrikKvamme_RuiSilveira.pdf`

### 2. System Manual (30% of grade)
- [ ] Manual completed based on `docs/MANUAL.md`
- [ ] All sections filled out:
  - [ ] Installation instructions
  - [ ] Configuration details
  - [ ] Operation instructions
  - [ ] Monitoring guide
  - [ ] Troubleshooting section
- [ ] Commands tested and verified
- [ ] Screenshots/examples included where helpful
- [ ] Manual exported to PDF
- [ ] File named: `DDBS_Project_Manual_HenrikKvamme_RuiSilveira.pdf`

### 3. Demo Preparation (30% of grade)
- [ ] Demo script prepared (see below)
- [ ] System tested and working
- [ ] All features demostrated
- [ ] Talking points prepared
- [ ] Backup plan if something fails
- [ ] Demo time: 10-15 minutes

---

## 🖼️ Screenshots (8 Total)

All screenshots must be taken following `docs/SCREENSHOT_GUIDE.md`:

- [ ] 1. System Deployment (`make ps`) - Report Section 5.1
- [ ] 2. Data Distribution (`make verify-data`) - Report Section 5.2
- [ ] 3. Query Caching (first vs cached) - Report Section 5.3
- [ ] 4. Distributed Join (`make top5-daily`) - Report Section 5.4
- [ ] 5. System Monitoring (`make monitor`) - Report Section 5.5
- [ ] 6. Standby Status (`monitor.py status`) - Report Section 5.7
- [ ] 7. Normal Operation (query before failure) - Report Section 5.7
- [ ] 8. Failover Test (automatic failover) - Report Section 5.7

**Screenshot Requirements:**
- [ ] All screenshots are high quality PNG files
- [ ] Terminal font size is readable (14pt+)
- [ ] No line wrapping or truncation
- [ ] Files named correctly (01_*.png through 08_*.png)
- [ ] Screenshots inserted in report at correct locations
- [ ] Captions match the guide

---

## 💻 Code & Repository

### Code Quality
- [ ] Code formatted with `make format`
- [ ] Linting passed with `make lint-fix`
- [ ] No unnecessary print statements or debug code
- [ ] All imports working correctly
- [ ] PYTHONPATH correctly set in Makefile

### Repository Cleanliness
- [ ] Cache directories cleaned (`.ruff_cache`, `__pycache__`)
- [ ] No generated data files committed
- [ ] No `.DS_Store` or system files
- [ ] `.gitignore` comprehensive and up-to-date
- [ ] No unused scripts or files
- [ ] README.md up-to-date with Makefile commands

### Documentation
- [ ] `README.md` - Quick start and overview
- [ ] `CLAUDE.md` - Development commands
- [ ] `docs/MANUAL.md` - Operation manual
- [ ] `docs/REPORT_TEMPLATE.md` - Report content
- [ ] `docs/SCREENSHOT_GUIDE.md` - Screenshot instructions
- [ ] `docs/PLAN.md` - Project plan (historical)

---

## 🧪 Functional Testing

### Complete Setup Test
```bash
# Test one-command setup
make clean
make setup-10g
```

**Verify:**
- [ ] All containers start successfully
- [ ] Databases initialized correctly
- [ ] Data generated (10,000 users, 10,000 articles, 1M reads)
- [ ] Data loaded into DBMS1 and DBMS2 correctly
- [ ] Media uploaded to HDFS
- [ ] Be-Read table populated
- [ ] Popular-Rank table populated
- [ ] No errors in terminal output

### Query Testing
- [ ] `make query-shell` works
- [ ] Beijing user query routes to DBMS1
- [ ] Hong Kong user query routes to DBMS2
- [ ] All users query routes to both DBMS (parallel)
- [ ] Cache hit works (same query twice)
- [ ] `make top5-daily` shows 5 articles with details
- [ ] `make top5-weekly` works
- [ ] `make top5-monthly` works

### Monitoring Testing
- [ ] `make monitor` shows system summary
- [ ] `make verify-data` shows correct distribution
- [ ] `monitor.py status` shows all DBMS online
- [ ] `monitor.py distribution` shows fragmentation rules
- [ ] `monitor.py workload` shows cache statistics

### Failover Testing
- [ ] Stop DBMS1: `docker stop ddbs-group-project-dbms1-1`
- [ ] Beijing query fails over to DBMS1-STANDBY automatically
- [ ] Warning message appears
- [ ] Same results returned
- [ ] Restart DBMS1: `docker start ddbs-group-project-dbms1-1`

---

## 📝 Report Content Verification

### Section 5: Solution Evaluation

**5.1 System Deployment:**
- [ ] Screenshot shows all services running
- [ ] Caption explains what is shown
- [ ] Text discusses deployment success

**5.2 Data Distribution:**
- [ ] Screenshot shows fragmentation verification
- [ ] Correct counts mentioned (Beijing vs Hong Kong)
- [ ] Text confirms fragmentation rules work

**5.3 Query Performance:**
- [ ] Screenshot shows cache hit
- [ ] Response time comparison mentioned
- [ ] Cache hit rate documented

**5.4 Distributed Join:**
- [ ] Screenshot shows top-5 articles
- [ ] All article details visible
- [ ] Text explains join process

**5.5 Monitoring:**
- [ ] Screenshot shows system summary
- [ ] All monitoring capabilities covered
- [ ] Text explains monitoring value

**5.6 Functional Requirements:**
- [ ] Table shows all requirements met
- [ ] All checkmarks (✓) correct

**5.7 Hot/Cold Standby:**
- [ ] Screenshot shows all 3 DBMS online
- [ ] Screenshot shows normal operation
- [ ] Screenshot shows failover working
- [ ] Text explains failover process
- [ ] Benefits documented

### Section 6: Conclusion
- [ ] Achievements list includes hot/cold standby
- [ ] Key learnings are meaningful
- [ ] Future work makes sense (not already implemented features)

### Appendix A: Load Allocation
- [ ] **Henrik Kvamme contributions listed with percentage**
- [ ] **Rui Silveira contributions listed with percentage**
- [ ] **Percentages add up to 100%**
- [ ] **Collaboration noted**
- [ ] **THIS IS MANDATORY - DO NOT SKIP**

---

## 🎤 Demo Script

**Duration:** 10-15 minutes

### 1. Introduction (1 min)
"We've implemented a distributed database system for a news article platform with horizontal fragmentation, replication, and fault tolerance."

### 2. System Deployment (2 min)
```bash
make ps
```
- Show all containers running
- Explain architecture: 2 DBMS + standby, Redis, HDFS

### 3. Data Distribution (2 min)
```bash
make verify-data
```
- Explain fragmentation rules
- Show Beijing vs Hong Kong distribution
- Show science article replication

### 4. Query Processing (3 min)
```bash
make query-shell
# Type: SELECT * FROM "user" WHERE region='Beijing' LIMIT 5
# Type: SELECT * FROM "user" LIMIT 10
# Run same query twice to show cache
```
- Show single DBMS routing
- Show parallel query with merge
- Show cache hit

### 5. Distributed Join (2 min)
```bash
make top5-daily
```
- Explain popular ranking
- Show article details fetched from both DBMS
- Point out distributed join

### 6. Monitoring (2 min)
```bash
make monitor
```
- Show system health
- Show cache hit rate
- Show data distribution

### 7. Failover Demo (3 min)
```bash
# Query Beijing users (works)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache

# Stop DBMS1
docker stop ddbs-group-project-dbms1-1

# Query again (auto-fails over)
uv run python src/cli/query.py execute --sql "SELECT * FROM \"user\" WHERE region='Beijing' LIMIT 3" --no-cache

# Restart
docker start ddbs-group-project-dbms1-1
```
- Explain hot standby
- Show automatic failover
- Zero downtime

### 8. Conclusion (1 min)
"The system successfully demonstrates distributed database concepts with production-ready features including fault tolerance."

---

## 📊 Grading Breakdown

| Component | Percentage | Checklist Items Complete |
|-----------|------------|--------------------------|
| Report    | 30%        | ___/15 |
| Manual    | 30%        | ___/7  |
| Demo      | 30%        | ___/8  |
| **Total** | **90%**    | ___/30 |

**Note:** The optional advanced features were specified as +10% bonus:
- ✅ Hot/Cold Standby (implemented)
- ❌ DBMS Expansion (not implemented)
- ❌ DBMS Dropping (not implemented)
- ❌ Data Migration (not implemented)

---

## 🚀 Final Submission Steps

1. **Generate PDFs:**
   ```bash
   # From docs/
   # Convert REPORT_TEMPLATE.md to PDF (use pandoc, markdown-pdf, or similar)
   # Convert MANUAL.md to PDF
   ```

2. **Create submission folder:**
   ```
   DDBS_Project_HenrikKvamme_RuiSilveira/
   ├── DDBS_Project_Report.pdf
   ├── DDBS_Project_Manual.pdf
   ├── screenshots/
   │   ├── 01_system_deployment.png
   │   ├── 02_data_distribution.png
   │   ├── ... (all 8 screenshots)
   ├── source_code/
   │   └── (entire git repository as zip)
   └── README.txt (submission notes)
   ```

3. **Test everything one more time:**
   ```bash
   make clean
   make setup-10g
   # Run through demo script
   ```

4. **Submit via course platform**
   - Upload before deadline
   - Verify file sizes (PDFs should be < 20MB)
   - Keep backup copy

---

## ✅ Pre-Submission Final Checks

- [ ] All checkboxes in this document completed
- [ ] Report reviewed by both team members
- [ ] Manual tested by someone who hasn't used the system
- [ ] Demo rehearsed at least once
- [ ] Load allocation clearly specified in report
- [ ] All PDFs generated and checked
- [ ] Submission folder ready
- [ ] Backup copy saved
- [ ] Submitted before deadline

---

## 📞 Emergency Contacts

If something goes wrong:
- Check `docs/MANUAL.md` Troubleshooting section
- Run `make clean && make setup-10g`
- Check Docker logs: `make logs`
- Verify services: `make ps`

---

**Good luck with your submission! 🎓**
