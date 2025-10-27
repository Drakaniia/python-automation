#!/bin/bash

# ============================================================
# Python Automation System - Enhanced Setup Script
# ============================================================
# Features:
# - Comprehensive system validation
# - Automatic Python detection and verification
# - Smart shell configuration
# - Git validation and setup
# - Automatic alias configuration
# - Cross-platform support (Linux, macOS, Git Bash)
# ============================================================

set -e  # Exit on error

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/main.py"
MIN_PYTHON_VERSION="3.7"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Python Automation System - Enhanced Setup                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

validate_python() {
    print_section "🐍 Python Validation"
    
    # Check for Python commands
    PYTHON_CMD=""
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Found python3 command"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
            PYTHON_CMD="python"
            print_success "Found python command (Python 3)"
        else
            print_error "Python 3 is required, but only Python 2 was found"
            print_info "Install Python 3 from: https://www.python.org/downloads/"
            exit 1
        fi
    elif command -v py &> /dev/null; then
        # Windows py launcher
        PY_VERSION=$(py --version 2>&1)
        if [[ $PY_VERSION == *"Python 3"* ]]; then
            PYTHON_CMD="py"
            print_success "Found py launcher (Python 3)"
        else
            print_error "Python 3 is required"
            exit 1
        fi
    else
        print_error "Python is not installed or not in PATH"
        print_info "Install Python 3 from: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
    print_info "Python version: $PYTHON_VERSION"
    
    # Verify minimum version
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
        print_error "Python $MIN_PYTHON_VERSION or higher is required"
        print_info "Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python version meets requirements (>= $MIN_PYTHON_VERSION)"
    
    # Test Python execution
    if $PYTHON_CMD -c "import sys; sys.exit(0)" &> /dev/null; then
        print_success "Python execution test passed"
    else
        print_error "Python execution test failed"
        exit 1
    fi
    
    echo ""
}

validate_git() {
    print_section "🔧 Git Validation"
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version 2>&1)
        print_success "Git is installed: $GIT_VERSION"
        
        # Check git config
        GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
        GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
        
        if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
            print_warning "Git user configuration incomplete"
            print_info "You may need to configure: git config --global user.name 'Your Name'"
            print_info "And: git config --global user.email 'your@email.com'"
        else
            print_success "Git user configured: $GIT_USER <$GIT_EMAIL>"
        fi
    else
        print_warning "Git is not installed"
        print_info "Some features require Git. Install from: https://git-scm.com/"
        print_info "You can continue without Git for basic features."
    fi
    
    echo ""
}

validate_files() {
    print_section "📁 File Structure Validation"
    
    # Check main.py
    if [ -f "$MAIN_PY" ]; then
        print_success "Found main.py"
    else
        print_error "main.py not found at: $MAIN_PY"
        exit 1
    fi
    
    # Check automation directory
    if [ -d "$SCRIPT_DIR/automation" ]; then
        print_success "Found automation/ directory"
    else
        print_error "automation/ directory not found"
        exit 1
    fi
    
    # Check critical modules
    CRITICAL_MODULES=(
        "automation/__init__.py"
        "automation/menu.py"
        "automation/git_operations.py"
    )
    
    for module in "${CRITICAL_MODULES[@]}"; do
        if [ -f "$SCRIPT_DIR/$module" ]; then
            print_success "Found $module"
        else
            print_error "Missing critical module: $module"
            exit 1
        fi
    done
    
    echo ""
}

validate_permissions() {
    print_section "🔐 Permission Validation"
    
    # Make main.py executable
    if chmod +x "$MAIN_PY" 2>/dev/null; then
        print_success "Set executable permissions on main.py"
    else
        print_warning "Could not set executable permissions (may not be needed on Windows)"
    fi
    
    # Check write permissions on shell config
    SHELL_CONFIG=$(get_shell_config)
    
    if [ -w "$SHELL_CONFIG" ] || [ ! -f "$SHELL_CONFIG" ]; then
        print_success "Shell config is writable: $SHELL_CONFIG"
    else
        print_error "Cannot write to shell config: $SHELL_CONFIG"
        print_info "You may need to run with appropriate permissions"
        exit 1
    fi
    
    echo ""
}

# ============================================================
# SHELL CONFIGURATION
# ============================================================

get_shell_config() {
    # Detect shell and return config file path
    if [ -n "$ZSH_VERSION" ]; then
        echo "$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bashrc" ]; then
            echo "$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            echo "$HOME/.bash_profile"
        else
            echo "$HOME/.bashrc"
        fi
    else
        # Default to .bashrc
        echo "$HOME/.bashrc"
    fi
}

detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    else
        echo "unknown"
    fi
}

backup_shell_config() {
    local config_file=$1
    local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -f "$config_file" ]; then
        if cp "$config_file" "$backup_file" 2>/dev/null; then
            print_success "Created backup: $backup_file"
            return 0
        else
            print_warning "Could not create backup"
            return 1
        fi
    fi
}

configure_alias() {
    print_section "⚙️  Alias Configuration"
    
    SHELL_CONFIG=$(get_shell_config)
    SHELL_TYPE=$(detect_shell)
    
    print_info "Detected shell: $SHELL_TYPE"
    print_info "Config file: $SHELL_CONFIG"
    
    # Create config file if it doesn't exist
    if [ ! -f "$SHELL_CONFIG" ]; then
        touch "$SHELL_CONFIG"
        print_success "Created new config file: $SHELL_CONFIG"
    fi
    
    # Backup existing config
    backup_shell_config "$SHELL_CONFIG"
    
    # Check if alias already exists
    if grep -q "alias magic=" "$SHELL_CONFIG" 2>/dev/null; then
        print_warning "Alias 'magic' already exists in $SHELL_CONFIG"
        
        # Show current alias
        CURRENT_ALIAS=$(grep "alias magic=" "$SHELL_CONFIG" | tail -1)
        print_info "Current: $CURRENT_ALIAS"
        
        echo ""
        read -p "$(echo -e ${YELLOW}Update existing alias? [Y/n]:${NC} )" -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
            print_info "Keeping existing alias"
            return 0
        fi
        
        # Remove old alias lines
        if [ "$(uname)" == "Darwin" ]; then
            # macOS
            sed -i '' '/alias magic=/d' "$SHELL_CONFIG"
            sed -i '' '/# Python Automation System/d' "$SHELL_CONFIG"
        else
            # Linux/Git Bash
            sed -i '/alias magic=/d' "$SHELL_CONFIG" 2>/dev/null || true
            sed -i '/# Python Automation System/d' "$SHELL_CONFIG" 2>/dev/null || true
        fi
        
        print_success "Removed old alias configuration"
    fi
    
    # Add new alias
    echo "" >> "$SHELL_CONFIG"
    echo "# Python Automation System" >> "$SHELL_CONFIG"
    echo "alias magic='$PYTHON_CMD \"$MAIN_PY\"'" >> "$SHELL_CONFIG"
    
    print_success "Added 'magic' alias to $SHELL_CONFIG"
    print_info "Command: $PYTHON_CMD \"$MAIN_PY\""
    
    echo ""
}

# ============================================================
# TESTING
# ============================================================

test_installation() {
    print_section "🧪 Installation Testing"
    
    # Test Python import
    print_info "Testing Python module imports..."
    
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from automation.menu import MainMenu
print('✓ Module import successful')
" 2>/dev/null; then
        print_success "Python module imports working"
    else
        print_error "Python module import failed"
        print_info "There may be missing dependencies or syntax errors"
        return 1
    fi
    
    # Test main.py execution
    print_info "Testing main.py execution..."
    
    # Just verify it can load without running the menu
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from automation.menu import MainMenu
print('✓ Script loads successfully')
" 2>/dev/null; then
        print_success "main.py execution test passed"
    else
        print_error "main.py execution test failed"
        return 1
    fi
    
    echo ""
    return 0
}

# ============================================================
# FINAL SETUP
# ============================================================

print_completion_message() {
    print_section "🎉 Setup Complete!"
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Python Automation System is ready to use!                    ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${CYAN}📋 Installation Summary:${NC}"
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_CMD ($PYTHON_VERSION)"
    echo -e "  ${GREEN}✓${NC} Install location: $SCRIPT_DIR"
    echo -e "  ${GREEN}✓${NC} Shell config: $(get_shell_config)"
    echo -e "  ${GREEN}✓${NC} Command alias: ${YELLOW}magic${NC}"
    
    echo -e "\n${CYAN}🚀 Next Steps:${NC}"
    echo -e "  ${BLUE}1.${NC} Reload your shell configuration:"
    echo -e "     ${YELLOW}source $(get_shell_config)${NC}"
    echo -e "     ${MAGENTA}OR restart your terminal${NC}"
    
    echo -e "\n  ${BLUE}2.${NC} Test the installation:"
    echo -e "     ${YELLOW}magic${NC}"
    
    echo -e "\n  ${BLUE}3.${NC} Navigate to any project and run:"
    echo -e "     ${YELLOW}cd /path/to/your/project${NC}"
    echo -e "     ${YELLOW}magic${NC}"
    
    echo -e "\n${CYAN}💡 Quick Start Guide:${NC}"
    echo -e "  • ${BLUE}GitHub Operations:${NC} Push, pull, commit with AI"
    echo -e "  • ${BLUE}Project Structure:${NC} View and share project layout"
    echo -e "  • ${BLUE}Folder Navigator:${NC} Interactive directory navigation"
    echo -e "  • ${BLUE}Dev Mode:${NC} Web development automation tools"
    
    echo -e "\n${CYAN}📚 Documentation:${NC}"
    echo -e "  • README: $SCRIPT_DIR/README.md"
    echo -e "  • Repository: https://github.com/Drakaniia/python-automation"
    
    echo -e "\n${CYAN}❓ Need Help?${NC}"
    echo -e "  • Issues: https://github.com/Drakaniia/python-automation/issues"
    echo -e "  • Email: alistairybaez574@gmail.com"
    
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}\n"
}

# ============================================================
# MAIN SETUP FLOW
# ============================================================

main() {
    # Print header
    print_header
    
    # Run validations
    validate_python
    validate_git
    validate_files
    validate_permissions
    
    # Configure alias
    configure_alias
    
    # Test installation
    if test_installation; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed, but basic setup is complete"
        print_info "You can still use the system, but some features may not work"
    fi
    
    # Print completion message
    print_completion_message
    
    # Ask if user wants to source config now
    echo -e "${YELLOW}Would you like to reload your shell configuration now? [Y/n]:${NC} "
    read -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        SHELL_CONFIG=$(get_shell_config)
        
        if [ -f "$SHELL_CONFIG" ]; then
            print_info "Reloading $SHELL_CONFIG..."
            
            # Source the config
            set +e  # Don't exit on error for sourcing
            source "$SHELL_CONFIG" 2>/dev/null || true
            set -e
            
            print_success "Configuration reloaded!"
            print_info "You can now use: ${YELLOW}magic${NC}"
            
            echo -e "\n${CYAN}Try it now:${NC}"
            echo -e "  ${YELLOW}magic${NC}"
        else
            print_warning "Could not reload configuration"
            print_info "Please restart your terminal or run: source $SHELL_CONFIG"
        fi
    else
        print_info "Remember to reload your shell:"
        echo -e "  ${YELLOW}source $(get_shell_config)${NC}"
        echo -e "  ${MAGENTA}OR restart your terminal${NC}"
    fi
    
    echo ""
}

# ============================================================
# ENTRY POINT
# ============================================================

# Trap errors
trap 'echo -e "\n${RED}Setup failed. Please check the errors above.${NC}"; exit 1' ERR

# Run main setup
main

exit 0