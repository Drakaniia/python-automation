@echo off
REM Run all tests for Python Automation System (Windows)

echo ========================================
echo Running All Tests
echo ========================================
echo.

REM Set Python path
set PYTHONPATH=%CD%

REM Check if pytest is installed
py -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo Installing test dependencies...
    py -m pip install pytest pytest-cov pytest-mock pytest-benchmark
)

REM Run tests
echo Running test suite...
echo.

py -m pytest tests/ -v --cov=automation --cov-report=html --cov-report=term --tb=short

REM Check exit code
if errorlevel 1 (
    echo.
    echo ========================================
    echo Some tests failed!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo All tests passed!
    echo Coverage report: htmlcov\index.html
    echo ========================================
)

pause