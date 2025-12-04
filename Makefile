.PHONY: help setup down clean reset deps format lint lint-fix logs ps
.PHONY: init-db generate-data-10g generate-data-50g generate-data-100g
.PHONY: load-data upload-media populate-beread populate-popularrank populate-all
.PHONY: verify-data verify-beread verify-popularrank monitor
.PHONY: setup-complete setup-10g setup-50g setup-100g
.PHONY: query-shell query-examples top5-daily top5-weekly top5-monthly

.DEFAULT_GOAL := help

##@ Infrastructure Management

setup:  ## Start all infrastructure (PostgreSQL, Redis, HDFS)
	@echo "Starting infrastructure..."
	docker compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "✓ Infrastructure started"

down:  ## Stop all infrastructure
	@echo "Stopping infrastructure..."
	docker compose down
	@echo "✓ Infrastructure stopped"

clean:  ## Stop and remove all data volumes
	@echo "Cleaning all data..."
	docker compose down -v
	@echo "✓ All data removed"

reset: clean setup  ## Clean restart with fresh databases
	@echo "✓ System reset complete"

##@ Database Initialization

init-db:  ## Initialize database schemas on all DBMS
	@echo "Initializing database schemas..."
	uv run python src/cli/init_db.py

##@ Data Generation

generate-data-10g:  ## Generate 10G dataset with real media
	@echo "Generating 10G dataset..."
	uv run python db-generation/generate_production_data.py --scale 10G

generate-data-50g:  ## Generate 50G dataset with real media
	@echo "Generating 50G dataset..."
	uv run python db-generation/generate_production_data.py --scale 50G

generate-data-100g:  ## Generate 100G dataset with real media
	@echo "Generating 100G dataset..."
	uv run python db-generation/generate_production_data.py --scale 100G

##@ Data Loading

load-data:  ## Load partitioned SQL into databases
	@echo "Loading data into databases..."
	uv run python src/cli/load_data.py bulk-load --sql-dir generated_data

upload-media:  ## Upload article media to HDFS
	@echo "Checking HDFS availability..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
		if curl -s http://localhost:9870 > /dev/null 2>&1; then \
			echo "✓ HDFS is ready"; \
			break; \
		fi; \
		echo "Waiting for HDFS... ($$timeout seconds remaining)"; \
		sleep 2; \
		timeout=$$((timeout - 2)); \
	done
	@echo "Uploading media files to HDFS..."
	uv run python src/cli/load_data.py upload-media --mock-dir production_articles

##@ Data Population

populate-beread:  ## Populate Be-Read table from Read data
	@echo "Populating Be-Read table..."
	uv run python src/cli/populate_beread.py

populate-popularrank:  ## Populate Popular-Rank table from Be-Read
	@echo "Populating Popular-Rank table..."
	uv run python src/cli/populate_popularrank.py

populate-all: populate-beread populate-popularrank  ## Populate all aggregate tables
	@echo "✓ All aggregate tables populated"

##@ Verification

verify-data:  ## Verify data distribution across DBMS
	@echo "Verifying data distribution..."
	uv run python src/cli/load_data.py verify

verify-beread:  ## Verify Be-Read table population
	@echo "Verifying Be-Read table..."
	uv run python src/cli/populate_beread.py verify

verify-popularrank:  ## Verify Popular-Rank table population
	@echo "Verifying Popular-Rank table..."
	uv run python src/cli/populate_popularrank.py verify

monitor:  ## Show system status summary
	uv run python src/cli/monitor.py summary

##@ Complete Workflows

setup-complete: setup init-db generate-data-10g load-data upload-media populate-all monitor  ## Full setup with 10G data
	@echo ""
	@echo "============================================"
	@echo "✓ Complete setup finished!"
	@echo "============================================"
	@echo ""
	@echo "Try these commands:"
	@echo "  make query-shell    # Start interactive query shell"
	@echo "  make top5-daily     # View top-5 daily articles"
	@echo "  make monitor        # Check system status"

setup-10g: reset init-db generate-data-10g load-data upload-media populate-all verify-data  ## Complete 10G setup from scratch
	@echo ""
	@echo "============================================"
	@echo "✓ 10G dataset setup complete!"
	@echo "============================================"

setup-50g: reset init-db generate-data-50g load-data upload-media populate-all verify-data  ## Complete 50G setup from scratch
	@echo ""
	@echo "============================================"
	@echo "✓ 50G dataset setup complete!"
	@echo "============================================"

setup-100g: reset init-db generate-data-100g load-data upload-media populate-all verify-data  ## Complete 100G setup from scratch
	@echo ""
	@echo "============================================"
	@echo "✓ 100G dataset setup complete!"
	@echo "============================================"

##@ Query & Monitoring

query-shell:  ## Start interactive query shell
	@echo "Starting interactive query shell..."
	@echo "Type 'help' for commands, 'exit' to quit"
	@echo ""
	uv run python src/cli/query.py execute --interactive

query-examples:  ## Show example queries
	uv run python src/cli/query.py examples

top5-daily:  ## Query top-5 daily articles
	@echo "Top-5 daily popular articles:"
	@echo ""
	uv run python src/cli/query.py top5 --granularity daily

top5-weekly:  ## Query top-5 weekly articles
	@echo "Top-5 weekly popular articles:"
	@echo ""
	uv run python src/cli/query.py top5 --granularity weekly

top5-monthly:  ## Query top-5 monthly articles
	@echo "Top-5 monthly popular articles:"
	@echo ""
	uv run python src/cli/query.py top5 --granularity monthly

##@ Development

deps:  ## Install dependencies
	@echo "Installing dependencies..."
	uv sync
	@echo "✓ Dependencies installed"

format:  ## Format code with ruff
	@echo "Formatting code..."
	uv run ruff format .
	@echo "✓ Code formatted"

lint:  ## Lint code with ruff
	@echo "Linting code..."
	uv run ruff check .

lint-fix:  ## Auto-fix linting issues
	@echo "Fixing linting issues..."
	uv run ruff check --fix .
	@echo "✓ Linting issues fixed"

##@ Docker Helpers

logs:  ## Show docker compose logs (follow mode)
	docker compose logs -f

ps:  ## Show running containers
	docker compose ps

##@ Help

help:  ## Display this help message
	@echo ""
	@echo "DDBS Group Project - Distributed Database System"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "Quick Start Examples:"
	@echo "  make setup-10g      # Complete setup with 10G dataset"
	@echo "  make query-shell    # Start interactive query interface"
	@echo "  make monitor        # Check system status"
	@echo ""
