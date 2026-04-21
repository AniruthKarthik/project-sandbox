SHELL := /bin/bash

# Configuration
INGEST_DIR := $(CURDIR)/ingest
BFF_DIR := $(CURDIR)/bff
CLIENT_DIR := $(CURDIR)/client
VENV := $(INGEST_DIR)/env
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn
PYTEST := $(VENV)/bin/pytest

.PHONY: all install test clean start stop ingest bff client install-ingest install-bff install-client test-ingest test-bff test-client

all: install test

install: install-ingest install-bff install-client

install-ingest:
	@echo "Installing ingest dependencies..."
	@if [ ! -d "$(VENV)" ]; then python3 -m venv $(VENV); fi
	$(PIP) install --upgrade pip
	$(PIP) install -r $(INGEST_DIR)/requirements.txt

install-bff:
	@echo "Installing bff dependencies..."
	cd $(BFF_DIR) && npm install

install-client:
	@echo "Installing client dependencies..."
	cd $(CLIENT_DIR) && npm install

test: test-ingest test-bff test-client

test-ingest:
	@echo "Running ingest tests..."
	cd $(INGEST_DIR) && $(PYTEST)

test-bff:
	@echo "Running bff tests..."
	cd $(BFF_DIR) && npm test

test-client:
	@echo "Running client tests (lint/typecheck)..."
	cd $(CLIENT_DIR) && npm test

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf $(BFF_DIR)/node_modules
	rm -rf $(CLIENT_DIR)/node_modules
	rm -rf $(CLIENT_DIR)/dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

stop:
	@echo "Stopping any existing services on ports 8000, 3000, 5173-5175..."
	@pids=$$(lsof -i :8000 -i :3000 -i :5173-5175 -t 2>/dev/null | sort -u); \
	if [ -n "$$pids" ]; then \
		echo "Killing processes: $$pids"; \
		kill $$pids 2>/dev/null || true; \
		sleep 1; \
		kill -9 $$pids 2>/dev/null || true; \
	else \
		echo "No services found on these ports."; \
	fi

start: stop
	@echo "Starting all services..."
	@set -m; \
	pids=""; \
	cleanup() { \
		trap - INT TERM EXIT; \
		echo -e "\nShutting down services..."; \
		if [ -n "$$pids" ]; then \
			kill $$pids 2>/dev/null || true; \
		fi; \
		sleep 1; \
		pids_to_kill=$$(lsof -i :8000 -i :3000 -i :5173-5175 -t 2>/dev/null | sort -u); \
		if [ -n "$$pids_to_kill" ]; then \
			kill -9 $$pids_to_kill 2>/dev/null || true; \
		fi; \
		echo "All services stopped and ports freed."; \
		exit 0; \
	}; \
	trap cleanup INT TERM EXIT; \
	(cd $(INGEST_DIR) && exec $(UVICORN) main:app --reload --host 0.0.0.0 --port 8000) & \
	pids="$$pids $$!"; \
	(cd $(BFF_DIR) && exec npm run dev) & \
	pids="$$pids $$!"; \
	(cd $(CLIENT_DIR) && exec npm run dev -- --host 0.0.0.0) & \
	pids="$$pids $$!"; \
	echo "Waiting for services to start..."; \
	sleep 5; \
	if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:5173 >/dev/null 2>&1 || true; \
	elif command -v open >/dev/null 2>&1; then \
		open http://localhost:5173 >/dev/null 2>&1 || true; \
	fi; \
	wait

ingest:
	cd $(INGEST_DIR) && $(UVICORN) main:app --reload --host 0.0.0.0 --port 8000

bff:
	cd $(BFF_DIR) && npm run dev

client:
	cd $(CLIENT_DIR) && npm run dev -- --host 0.0.0.0
