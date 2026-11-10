#!/bin/bash
# EventSphere Startup Script
# Team 19 - CSE-B

# Ensure script runs from project root directory regardless of where it is invoked from
cd "$(dirname "$0")"

echo "=================================================="
echo " Starting EventSphere Full-Stack Application...  "
echo "=================================================="

# Check Python version
python3 --version

# Run backend test suite first
echo "Running backend automated verification tests..."
python3 backend/tests/test_api.py

if [ $? -ne 0 ]; then
    echo "Tests failed! Aborting startup."
    exit 1
fi

echo "All tests passed successfully!"
echo "Launching EventSphere on http://127.0.0.1:5050..."
python3 run.py
