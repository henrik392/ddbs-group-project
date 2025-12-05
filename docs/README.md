# Documentation

This directory contains all project documentation and the final report.

## Files

- **report.tex** - Main LaTeX report (submit this as PDF)
- **REPORT_TEMPLATE.md** - Markdown template (for reference)
- **MANUAL.md** - System deployment and usage manual
- **SCREENSHOT_GUIDE.md** - Guide for taking required screenshots
- **PLAN.md** - Project implementation plan
- **compile_report.sh** - Script to compile LaTeX to PDF

## Compiling the Report

### Prerequisites

Install LaTeX:
- **macOS:** `brew install --cask mactex`
- **Ubuntu:** `sudo apt-get install texlive-full`
- **Windows:** Download MiKTeX from https://miktex.org/

### Quick Compilation

```bash
cd docs
./compile_report.sh
```

This will generate `report.pdf` in the `docs/` directory.

### Manual Compilation

If the script doesn't work:

```bash
cd docs
pdflatex report.tex
pdflatex report.tex  # Run twice for references
pdflatex report.tex  # Run third time for table of contents
```

## Screenshots

**IMPORTANT:** Before compiling the final report, you need to take screenshots!

1. **Start the system:**
   ```bash
   docker compose up -d
   ```

2. **Follow the screenshot guide:**
   ```bash
   # See SCREENSHOT_GUIDE.md for detailed instructions
   cat SCREENSHOT_GUIDE.md
   ```

3. **Take 10 screenshots** and save them in `docs/screenshots/`:
   - `01_standby_status.png` - Hot standby system status
   - `02_failover_before.png` - Query before failover
   - `03_failover_during.png` - Automatic failover in action
   - `04_docker_ps.png` - Docker deployment
   - `05_distribution.png` - Data distribution
   - `06_summary.png` - System summary
   - `07_query_execution.png` - Query execution
   - `08_cache_hit.png` - Cache performance
   - `09_top5_articles.png` - Top-5 distributed join
   - `10_interactive_shell.png` - Interactive shell (optional)

4. **Quick screenshot session** (7 minutes):
   ```bash
   # Copy-paste commands from SCREENSHOT_GUIDE.md "Quick Screenshot Session"
   ```

## Report Structure

The LaTeX report includes:

1. **Title Page**
2. **Abstract** - Project summary and keywords
3. **Table of Contents**
4. **Introduction** - Background, motivation, objectives
5. **Related Work** - Existing solutions comparison
6. **Problem Definition** - Data model, fragmentation, requirements
7. **System Design** - Architecture, components, algorithms
8. **Evaluation** - Deployment, distribution, performance, failover
9. **Conclusion** - Achievements, learnings, future work
10. **References** - Academic citations
11. **Appendix** - Work distribution, system manual reference

## What Gets Full Marks

### Required Features (All Implemented ✓)

- [x] Horizontal fragmentation with business logic
- [x] Selective replication (science articles, Be-Read)
- [x] Distributed query processing with intelligent routing
- [x] Distributed join (Popular-Rank + Article)
- [x] Be-Read population from distributed Read table
- [x] Query result caching with Redis
- [x] Comprehensive monitoring tools
- [x] **Hot-cold standby with automatic failover** (Phase 6)

### Report Requirements

- [x] Clear problem definition
- [x] Architecture diagrams
- [x] Algorithm descriptions
- [x] Implementation details
- [x] **10 screenshots demonstrating functionality**
- [x] Performance evaluation
- [x] Work distribution

### Optional Advanced Features

You've already implemented the main optional feature:
- [x] **Phase 6: Hot-Cold Standby & Fault Tolerance**

Other optional features (not required for full marks):
- [ ] Phase 7: Dynamic DBMS expansion
- [ ] Advanced query optimization
- [ ] Real-time monitoring dashboard

## Submission Checklist

Before submitting:

1. [ ] All 10 screenshots taken and placed in `docs/screenshots/`
2. [ ] Report compiled to PDF: `./compile_report.sh`
3. [ ] Verify PDF includes all screenshots
4. [ ] Check page count (should be 20-30 pages)
5. [ ] Verify all figures have captions
6. [ ] Check references formatting
7. [ ] Review work distribution in Appendix A

## Troubleshooting

### Missing LaTeX Packages

If compilation fails with missing package errors:

**macOS/Linux:**
```bash
sudo tlmgr update --self
sudo tlmgr install <package-name>
```

**Windows (MiKTeX):**
Packages install automatically on first use.

### Screenshots Not Showing

1. Verify files exist: `ls -lh screenshots/`
2. Check filenames match exactly (case-sensitive)
3. Ensure PNG format (not JPG)
4. Re-compile: `./compile_report.sh`

### "File not found" Error

Make sure you're in the `docs/` directory:
```bash
cd docs
./compile_report.sh
```

## Tips for Academic Writing

1. **Be concise** - Technical writing should be clear and direct
2. **Use passive voice** - "The system was implemented" vs "We implemented"
3. **Cite properly** - All claims need references
4. **Explain algorithms** - Code snippets + textual description
5. **Quantify results** - "92% faster" not "much faster"
6. **Professional tone** - Formal academic language

## Questions?

See:
- `MANUAL.md` - System usage
- `SCREENSHOT_GUIDE.md` - Screenshot instructions
- `../README.md` - Project overview
- `../CLAUDE.md` - Development guide
