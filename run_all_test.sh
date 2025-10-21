#!/bin/bash

# Run All Tests Script
# Comprehensive test runner for Python Automation System

echo "=================================="
echo "Running All Tests"
echo "=================================="
echo ""

# Set PYTHONPATH to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if pytest is installed
if ! python -m pytest --version &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install pytest pytest-cov pytest-mock pytest-benchmark
fi

# Run all tests with coverage
echo "🧪 Running test suite..."
echo ""

python -m pytest tests/ \
    -v \
    --cov=automation \
    --cov-report=html \
    --cov-report=term \
    --tb=short \
    --maxfail=5 \
    -p no:warnings

# Capture exit code
EXIT_CODE=$?

echo ""
echo "=================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report: htmlcov/index.html"
else
    echo "❌ Some tests failed (exit code: $EXIT_CODE)"
fi
echo "=================================="

exit $EXIT_CODE