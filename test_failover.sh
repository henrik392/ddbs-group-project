#!/bin/bash
# Test hot-cold standby failover

echo "==================================================================="
echo "Hot-Cold Standby Failover Test"
echo "==================================================================="
echo ""

TEST_QUERY="SELECT uid, name, region FROM \"user\" WHERE region='Beijing' LIMIT 3"

# Test 1: Query with DBMS1 online
echo "[Test 1] Querying with DBMS1 online..."
echo "Query: $TEST_QUERY"
echo ""
uv run python src/cli/query.py execute --sql "$TEST_QUERY" --no-cache
echo ""
echo "-------------------------------------------------------------------"
echo ""

# Test 2: Stop DBMS1 and query again
echo "[Test 2] Stopping DBMS1 and testing failover..."
echo "Stopping container: ddbs-group-project-dbms1-1"
docker stop ddbs-group-project-dbms1-1
echo ""
echo "Query: $TEST_QUERY"
echo ""
uv run python src/cli/query.py execute --sql "$TEST_QUERY" --no-cache
echo ""
echo "-------------------------------------------------------------------"
echo ""

# Test 3: Restart DBMS1
echo "[Test 3] Restarting DBMS1..."
docker start ddbs-group-project-dbms1-1
echo ""
echo "Waiting for DBMS1 to be ready..."
sleep 3
echo ""

echo "Query: $TEST_QUERY"
echo ""
uv run python src/cli/query.py execute --sql "$TEST_QUERY" --no-cache
echo ""
echo "-------------------------------------------------------------------"
echo ""

echo "==================================================================="
echo "Failover Test Complete"
echo "==================================================================="
echo ""
echo "Expected results:"
echo "  Test 1: Should query DBMS1 successfully"
echo "  Test 2: Should show '⚠ DBMS1 failed, trying standby DBMS1-STANDBY'"
echo "          and return the same data from standby"
echo "  Test 3: Should query DBMS1 successfully again"
echo ""
