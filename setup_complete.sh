#!/bin/bash
# Complete system setup with hot-cold standby

set -e  # Exit on error

echo "==================================================================="
echo "Complete Distributed DBMS Setup"
echo "==================================================================="
echo ""

# Step 0: Reset databases (optional but recommended for clean state)
echo "[0/6] Resetting databases..."
docker compose down -v > /dev/null 2>&1 || true
docker compose up -d
echo "  Waiting for PostgreSQL to be ready..."
sleep 5

# Initialize fresh schemas
uv run python src/cli/init_db.py
echo ""

# Step 1: Generate test data
echo "[1/6] Generating test data..."
uv run python db-generation/generate_test_data.py
echo ""

# Step 2: Load data into DBMS1, DBMS1-STANDBY, and DBMS2
echo "[2/6] Loading data into all databases..."
uv run python src/cli/load_data.py bulk-load --sql-dir generated_data
echo ""

# Step 3: Populate Be-Read table (replicated on both DBMS)
echo "[3/6] Populating Be-Read table..."
uv run python src/cli/populate_beread.py
echo ""

# Step 4: Populate Popular-Rank table
echo "[4/6] Populating Popular-Rank table..."
uv run python src/cli/populate_popularrank.py
echo ""

# Step 5: Verify distribution
echo "[5/6] Verifying data distribution..."
echo ""
uv run python src/cli/monitor.py summary
echo ""

echo "==================================================================="
echo "✓ Complete setup finished!"
echo "==================================================================="
echo ""
echo "System is ready for testing. To test failover:"
echo "  1. Query: uv run python src/cli/query.py execute --sql \"SELECT * FROM \\\"user\\\" WHERE region='Beijing' LIMIT 5\""
echo "  2. Stop DBMS1: docker stop ddbs-group-project-dbms1-1"
echo "  3. Query again - should failover to standby"
echo "  4. Restart: docker start ddbs-group-project-dbms1-1"
echo ""
