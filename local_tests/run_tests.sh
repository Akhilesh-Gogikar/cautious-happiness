#!/bin/bash
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Using Dockerized Playwright Runner..."

# 1. Start Infrastructure (in background or ensure running)
echo "Starting Docker services..."
cd ..
# Remove orphaned containers to avoid conflicts, rebuild test runner
docker compose up -d db redis backend frontend
# Build the test runner image explicitly to update changes
docker compose build test-runner

# 2. Wait for Backend/Fronted to be ready
echo "Waiting for services to be ready..."
sleep 20

# 3. Run Tests inside Docker
echo "Running tests in container..."
docker compose run --rm test-runner

# Clean up?
# docker compose down
