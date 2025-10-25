#!/bin/bash
# fix_and_test.sh
# Automated setup and test script for Python Automation System

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Python Automation System - Setup & Test                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    print_error "setup.py not found. Are you in the project root?"
    exit 1
fi

print_status "Found setup.py"

# Step 1: Create necessary files if they don't exist
echo -e "\n${YELLOW}Step 1: Checking required files${NC}"

if [ ! -f "pytest.ini" ]; then
    print_info "Creating pytest.ini..."
    cat > pytest.ini << 'EOF'
[pytest]
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    -ra
EOF
    print_status "Created pytest.ini"
else
    print_status "pytest.ini exists"
fi

# Step 2: Install package in development mode
echo -e "\n${YELLOW}Step 2: Installing package in development mode${NC}"

if pip install -e ".[test]" > /dev/null 2>&1; then
    print_status "Package installed successfully"
else
    print_error "Failed to install package"
    print_info "Trying without test dependencies..."
    if pip install -e . > /dev/null 2>&1; then
        print_status "Package installed (without test dependencies)"
        print_info "Installing test dependencies separately..."
        pip install pytest pytest-cov pytest-mock > /dev/null 2>&1
        print_status "Test dependencies installed"
    else
        print_error "Installation failed. Please check errors above."
        exit 1
    fi
fi

# Step 3: Verify installation
echo -e "\n${YELLOW}Step 3: Verifying installation${NC}"

if python -c "import automation" 2>/dev/null; then
    print_status "automation module is importable"
else
    print_error "Cannot import automation module"
    exit 1
fi

if python -c "from automation.core import GitClient" 2>/dev/null; then
    print_status "automation.core is importable"
else
    print_error "Cannot import automation.core"
    exit 1
fi

if python -c "from automation.dev_mode import DevModeMenu" 2>/dev/null; then
    print_status "automation.dev_mode is importable"
else
    print_error "Cannot import automation.dev_mode"
    exit 1
fi

# Step 4: Run tests
echo -e "\n${YELLOW}Step 4: Running dev_mode tests${NC}\n"

if pytest tests/test_dev_mode/ -v --tb=short; then
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED!                                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}\n"
    
    # Run coverage report
    echo -e "${YELLOW}Generating coverage report...${NC}\n"
    pytest tests/test_dev_mode/ --cov=automation/dev_mode --cov-report=term-missing --cov-report=html -v
    
    echo -e "\n${GREEN}Coverage report generated!${NC}"
    echo -e "${BLUE}View HTML report: htmlcov/index.html${NC}\n"
else
    echo -e "\n${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED                                       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}\n"
    exit 1
fi

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Setup Complete! You can now:                              ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║  • Run tests: pytest tests/test_dev_mode/ -v              ║${NC}"
echo -e "${BLUE}║  • Use magic: magic                                        ║${NC}"
echo -e "${BLUE}║  • View coverage: open htmlcov/index.html                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"