#!/bin/bash
# Setup script for hot-cold standby configuration

echo "==================================================================="
echo "Hot-Cold Standby Setup Script"
echo "==================================================================="
echo ""

# Step 1: Ensure standby container is running
echo "[1/4] Starting standby container..."
docker compose up -d dbms1-standby
echo "✓ Standby container started"
echo ""

# Step 2: Wait for PostgreSQL to be ready
echo "[2/4] Waiting for standby database to be ready..."
until docker compose exec -T dbms1-standby pg_isready -U ddbs > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 1
done
echo "✓ Standby database is ready"
echo ""

# Step 3: Initialize standby database
echo "[3/4] Initializing standby database schema..."
uv run python src/cli/init_db.py
echo "✓ Schema initialized"
echo ""

# Step 4: Load data into standby
echo "[4/4] Loading data into standby..."
uv run python src/cli/load_data.py bulk-load --sql-dir data/partitioned_data
echo ""

echo "==================================================================="
echo "✓ Standby setup complete!"
echo "==================================================================="
echo ""
echo "To test failover:"
echo "  1. Run a query: uv run python src/cli/query.py"
echo "  2. Stop primary: docker stop ddbs-group-project-dbms1-1"
echo "  3. Run query again - should failover to standby"
echo "  4. Restart primary: docker start ddbs-group-project-dbms1-1"
echo ""
