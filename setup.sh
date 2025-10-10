#!/bin/bash

# Setup script for Python Automation System
# This script creates the alias 'magic' to run the automation tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/main.py"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Python Automation System Setup       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Detect Python command
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓${NC} Found python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo -e "${GREEN}✓${NC} Found python (Python 3)"
    else
        echo -e "${RED}✗${NC} Python 3 is required but not found"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Python is not installed or not in PATH"
    echo -e "${YELLOW}Please install Python 3 and add it to your PATH${NC}"
    exit 1
fi

# Make main.py executable
chmod +x "$MAIN_PY" 2>/dev/null
echo -e "${GREEN}✓${NC} Made main.py executable"

# Determine shell config file
if [ -n "$BASH_VERSION" ]; then
    if [ -f ~/.bashrc ]; then
        SHELL_CONFIG=~/.bashrc
    elif [ -f ~/.bash_profile ]; then
        SHELL_CONFIG=~/.bash_profile
    else
        SHELL_CONFIG=~/.bashrc
    fi
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG=~/.zshrc
else
    SHELL_CONFIG=~/.bashrc
fi

# Check if alias already exists
if grep -q "alias magic=" "$SHELL_CONFIG" 2>/dev/null; then
    echo -e "${YELLOW}!${NC} Alias 'magic' already exists in $SHELL_CONFIG"
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Setup cancelled.${NC}"
        exit 0
    fi
    # Remove old alias
    sed -i '/alias magic=/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '' '/alias magic=/d' "$SHELL_CONFIG"
fi

# Add alias to shell config
echo "" >> "$SHELL_CONFIG"
echo "# Python Automation System" >> "$SHELL_CONFIG"
echo "alias magic='$PYTHON_CMD $MAIN_PY'" >> "$SHELL_CONFIG"

echo -e "${GREEN}✓${NC} Added 'magic' alias to $SHELL_CONFIG"
echo -e "${BLUE}Using command:${NC} $PYTHON_CMD"

# Source the config file
echo -e "\n${BLUE}To activate the alias, run:${NC}"
echo -e "  ${YELLOW}source $SHELL_CONFIG${NC}"
echo -e "\n${BLUE}Or restart your terminal.${NC}"

echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Setup Complete!                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo -e "\n${BLUE}Usage:${NC} Type ${YELLOW}magic${NC} anywhere to launch the automation system\n"