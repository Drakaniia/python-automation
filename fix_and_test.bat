@echo off
REM fix_and_test.bat
REM Automated setup and test script for Python Automation System (Windows)

setlocal enabledelayedexpansion

echo ================================================================
echo   Python Automation System - Setup and Test (Windows)
echo ================================================================
echo.

REM Check if we're in the right directory
if not exist "setup.py" (
    echo [ERROR] setup.py not found. Are you in the project root?
    pause
    exit /b 1
)

echo [OK] Found setup.py
echo.

REM Step 1: Create pytest.ini if it doesn't exist
echo Step 1: Checking required files
echo --------------------------------

if not exist "pytest.ini" (
    echo Creating pytest.ini...
    (
        echo [pytest]
        echo pythonpath = .
        echo testpaths = tests
        echo python_files = test_*.py
        echo python_classes = Test*
        echo python_functions = test_*
        echo addopts = 
        echo     -v
        echo     --tb=short
        echo     --strict-markers
        echo     -ra
    ) > pytest.ini
    echo [OK] Created pytest.ini
) else (
    echo [OK] pytest.ini exists
)
echo.

REM Step 2: Install package
echo Step 2: Installing package in development mode
echo ------------------------------------------------

pip install -e ".[test]" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Package installed successfully
) else (
    echo [WARN] Failed to install with test dependencies
    echo Installing without test dependencies...
    pip install -e . >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Package installed
        echo Installing test dependencies separately...
        pip install pytest pytest-cov pytest-mock >nul 2>&1
        echo [OK] Test dependencies installed
    ) else (
        echo [ERROR] Installation failed
        pause
        exit /b 1
    )
)
echo.

REM Step 3: Verify installation
echo Step 3: Verifying installation
echo --------------------------------

python -c "import automation" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] automation module is importable
) else (
    echo [ERROR] Cannot import automation module
    pause
    exit /b 1
)

python -c "from automation.core import GitClient" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] automation.core is importable
) else (
    echo [ERROR] Cannot import automation.core
    pause
    exit /b 1
)

python -c "from automation.dev_mode import DevModeMenu" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] automation.dev_mode is importable
) else (
    echo [ERROR] Cannot import automation.dev_mode
    pause
    exit /b 1
)
echo.

REM Step 4: Run tests
echo Step 4: Running dev_mode tests
echo --------------------------------
echo.

pytest tests/test_dev_mode/ -v --tb=short
if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================================================
    echo   ALL TESTS PASSED!
    echo ================================================================
    echo.
    
    REM Generate coverage report
    echo Generating coverage report...
    echo.
    pytest tests/test_dev_mode/ --cov=automation/dev_mode --cov-report=term-missing --cov-report=html -v
    
    echo.
    echo [OK] Coverage report generated!
    echo View HTML report: htmlcov\index.html
    echo.
) else (
    echo.
    echo ================================================================
    echo   SOME TESTS FAILED
    echo ================================================================
    echo.
    pause
    exit /b 1
)

REM Summary
echo ================================================================
echo   Setup Complete! You can now:
echo.
echo   * Run tests: pytest tests/test_dev_mode/ -v
echo   * Use magic: magic
echo   * View coverage: start htmlcov\index.html
echo ================================================================
echo.

pause