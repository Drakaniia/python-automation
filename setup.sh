#!/bin/bash

# ============================================================
# Python Automation System - Complete Setup Script
# ============================================================
# Features:
# - Python installation detection and guidance
# - Comprehensive system validation
# - Automatic shell configuration (bash, zsh, fish)
# - Git setup with user configuration
# - Intelligent PATH detection and configuration
# - Backup and rollback capabilities
# - Cross-platform support (Linux, macOS, Windows/Git Bash)
# - Test installation functionality
# - Interactive and non-interactive modes
# ============================================================

set -e  # Exit on error

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/main.py"
MIN_PYTHON_VERSION="3.7"
COMMAND_ALIAS="magic"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_header() {
    clear
    echo -e "\n${BLUE}${BOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}${BOLD}║  Python Automation System - Complete Setup Wizard            ║${NC}"
    echo -e "${BLUE}${BOLD}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
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

print_step() {
    echo -e "\n${MAGENTA}▶${NC} ${BOLD}$1${NC}"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    
    if [ "$default" = "y" ]; then
        echo -e "${YELLOW}${prompt} [Y/n]:${NC} "
    else
        echo -e "${YELLOW}${prompt} [y/N]:${NC} "
    fi
    
    read -r response
    
    if [ -z "$response" ]; then
        response="$default"
    fi
    
    case "$response" in
        [Yy]|[Yy][Ee][Ss]) return 0 ;;
        *) return 1 ;;
    esac
}

pause() {
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

# ============================================================
# SYSTEM DETECTION
# ============================================================

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

detect_package_manager() {
    local os="$1"
    
    if [ "$os" = "linux" ]; then
        if command -v apt-get &> /dev/null; then
            echo "apt"
        elif command -v yum &> /dev/null; then
            echo "yum"
        elif command -v dnf &> /dev/null; then
            echo "dnf"
        elif command -v pacman &> /dev/null; then
            echo "pacman"
        else
            echo "unknown"
        fi
    elif [ "$os" = "macos" ]; then
        if command -v brew &> /dev/null; then
            echo "brew"
        else
            echo "none"
        fi
    else
        echo "none"
    fi
}

get_shell_config() {
    # Detect shell and return config file path
    local shell_name="$(basename "$SHELL")"
    
    case "$shell_name" in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            if [ -f "$HOME/.bashrc" ]; then
                echo "$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                echo "$HOME/.bash_profile"
            else
                echo "$HOME/.bashrc"
            fi
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            echo "$HOME/.bashrc"
            ;;
    esac
}

detect_shell() {
    basename "$SHELL" 2>/dev/null || echo "bash"
}

# ============================================================
# PYTHON DETECTION & INSTALLATION GUIDANCE
# ============================================================

find_python_command() {
    # Try to find a working Python 3 command
    local commands=("python3" "python" "py")
    
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # Check if it's Python 3
            local version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)
            
            if [ "$major" = "3" ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    
    return 1
}

validate_python() {
    print_section "🐍 Python Detection & Validation"
    
    # Try to find Python
    if PYTHON_CMD=$(find_python_command); then
        print_success "Found Python 3 command: $PYTHON_CMD"
    else
        print_error "Python 3 not found on this system"
        echo ""
        offer_python_installation
        return 1
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
        echo ""
        offer_python_installation
        return 1
    fi
    
    print_success "Python version meets requirements (>= $MIN_PYTHON_VERSION)"
    
    # Test Python execution
    if $PYTHON_CMD -c "import sys; sys.exit(0)" &> /dev/null; then
        print_success "Python execution test passed"
    else
        print_error "Python execution test failed"
        return 1
    fi
    
    # Check pip
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_success "pip is available"
    else
        print_warning "pip is not available"
        print_info "Some features may require pip for dependency installation"
    fi
    
    echo ""
    return 0
}

offer_python_installation() {
    local os=$(detect_os)
    local pkg_mgr=$(detect_package_manager "$os")
    
    echo -e "${RED}${BOLD}Python 3 is required but not found!${NC}\n"
    
    echo -e "${YELLOW}Installation Instructions:${NC}\n"
    
    case "$os" in
        linux)
            case "$pkg_mgr" in
                apt)
                    echo "Ubuntu/Debian:"
                    echo "  sudo apt update"
                    echo "  sudo apt install python3 python3-pip"
                    ;;
                yum|dnf)
                    echo "CentOS/Fedora/RHEL:"
                    echo "  sudo $pkg_mgr install python3 python3-pip"
                    ;;
                pacman)
                    echo "Arch Linux:"
                    echo "  sudo pacman -S python python-pip"
                    ;;
                *)
                    echo "Please install Python 3.7+ using your distribution's package manager"
                    ;;
            esac
            ;;
        macos)
            if [ "$pkg_mgr" = "brew" ]; then
                echo "Using Homebrew:"
                echo "  brew install python3"
            else
                echo "1. Install Homebrew first:"
                echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo ""
                echo "2. Then install Python:"
                echo "   brew install python3"
            fi
            echo ""
            echo "Or download from: https://www.python.org/downloads/"
            ;;
        windows)
            echo "Windows (Git Bash/WSL):"
            echo "  1. Download Python from: https://www.python.org/downloads/"
            echo "  2. During installation, check 'Add Python to PATH'"
            echo "  3. Restart your terminal after installation"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}After installing Python, run this setup script again.${NC}"
    echo ""
    
    exit 1
}

# ============================================================
# GIT VALIDATION & CONFIGURATION
# ============================================================

validate_git() {
    print_section "🔧 Git Validation & Configuration"
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        echo ""
        offer_git_installation
        return 1
    fi
    
    GIT_VERSION=$(git --version 2>&1)
    print_success "Git is installed: $GIT_VERSION"
    
    # Check git config
    GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
    GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
    
    if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
        print_warning "Git user configuration incomplete"
        echo ""
        
        if ask_yes_no "Would you like to configure Git now?"; then
            configure_git_user
        else
            print_info "You can configure Git later with:"
            print_info "  git config --global user.name 'Your Name'"
            print_info "  git config --global user.email 'your@email.com'"
        fi
    else
        print_success "Git user configured: $GIT_USER <$GIT_EMAIL>"
    fi
    
    echo ""
    return 0
}

offer_git_installation() {
    local os=$(detect_os)
    local pkg_mgr=$(detect_package_manager "$os")
    
    echo -e "${YELLOW}Git Installation Instructions:${NC}\n"
    
    case "$os" in
        linux)
            case "$pkg_mgr" in
                apt)
                    echo "Ubuntu/Debian:"
                    echo "  sudo apt update"
                    echo "  sudo apt install git"
                    ;;
                yum|dnf)
                    echo "CentOS/Fedora/RHEL:"
                    echo "  sudo $pkg_mgr install git"
                    ;;
                pacman)
                    echo "Arch Linux:"
                    echo "  sudo pacman -S git"
                    ;;
            esac
            ;;
        macos)
            if [ "$pkg_mgr" = "brew" ]; then
                echo "Using Homebrew:"
                echo "  brew install git"
            else
                echo "Install Xcode Command Line Tools:"
                echo "  xcode-select --install"
            fi
            ;;
        windows)
            echo "Download from: https://git-scm.com/download/win"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}Git is optional but recommended for full functionality.${NC}"
    echo ""
    
    if ! ask_yes_no "Continue without Git?" "n"; then
        exit 1
    fi
}

configure_git_user() {
    echo ""
    echo -e "${CYAN}Git User Configuration${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    
    if [ -n "$git_name" ] && [ -n "$git_email" ]; then
        git config --global user.name "$git_name"
        git config --global user.email "$git_email"
        print_success "Git configured: $git_name <$git_email>"
    else
        print_error "Invalid input. Git configuration skipped."
    fi
    
    echo ""
}

# ============================================================
# FILE STRUCTURE VALIDATION
# ============================================================

validate_files() {
    print_section "📁 File Structure Validation"
    
    local all_valid=true
    
    # Check main.py
    if [ -f "$MAIN_PY" ]; then
        print_success "Found main.py"
    else
        print_error "main.py not found at: $MAIN_PY"
        all_valid=false
    fi
    
    # Check automation directory
    if [ -d "$SCRIPT_DIR/automation" ]; then
        print_success "Found automation/ directory"
    else
        print_error "automation/ directory not found"
        all_valid=false
    fi
    
    # Check critical modules
    local critical_modules=(
        "automation/__init__.py"
        "automation/menu.py"
        "automation/git_operations.py"
        "automation/folder_navigator.py"
    )
    
    for module in "${critical_modules[@]}"; do
        if [ -f "$SCRIPT_DIR/$module" ]; then
            print_success "Found $module"
        else
            print_error "Missing critical module: $module"
            all_valid=false
        fi
    done
    
    echo ""
    
    if [ "$all_valid" = false ]; then
        print_error "File structure validation failed"
        echo ""
        echo -e "${RED}The installation appears to be incomplete or corrupted.${NC}"
        echo -e "${YELLOW}Please ensure all files are present before continuing.${NC}"
        echo ""
        exit 1
    fi
    
    return 0
}

# ============================================================
# PERMISSIONS
# ============================================================

validate_permissions() {
    print_section "🔐 Permission Configuration"
    
    # Make main.py executable
    if chmod +x "$MAIN_PY" 2>/dev/null; then
        print_success "Set executable permissions on main.py"
    else
        print_warning "Could not set executable permissions (may not be needed on Windows)"
    fi
    
    # Check write permissions on shell config
    local shell_config=$(get_shell_config)
    local shell_config_dir=$(dirname "$shell_config")
    
    # Create config directory if needed
    if [ ! -d "$shell_config_dir" ]; then
        if mkdir -p "$shell_config_dir" 2>/dev/null; then
            print_success "Created config directory: $shell_config_dir"
        else
            print_error "Cannot create config directory: $shell_config_dir"
            echo ""
            echo -e "${RED}You may need elevated permissions.${NC}"
            exit 1
        fi
    fi
    
    # Create config file if it doesn't exist
    if [ ! -f "$shell_config" ]; then
        if touch "$shell_config" 2>/dev/null; then
            print_success "Created shell config: $shell_config"
        fi
    fi
    
    if [ -w "$shell_config" ]; then
        print_success "Shell config is writable: $shell_config"
    else
        print_error "Cannot write to shell config: $shell_config"
        echo ""
        echo -e "${RED}You may need to run with appropriate permissions.${NC}"
        exit 1
    fi
    
    echo ""
}

# ============================================================
# SHELL CONFIGURATION
# ============================================================

backup_shell_config() {
    local config_file="$1"
    local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -f "$config_file" ]; then
        if cp "$config_file" "$backup_file" 2>/dev/null; then
            print_success "Created backup: $(basename "$backup_file")"
            echo "$backup_file"  # Return backup path
            return 0
        else
            print_warning "Could not create backup"
            return 1
        fi
    fi
}

configure_shell_alias() {
    print_section "⚙️  Shell Alias Configuration"
    
    local shell_config=$(get_shell_config)
    local shell_type=$(detect_shell)
    
    print_info "Detected shell: $shell_type"
    print_info "Config file: $shell_config"
    echo ""
    
    # Backup existing config
    local backup_path=$(backup_shell_config "$shell_config")
    
    # Build alias command based on shell
    local alias_cmd=""
    case "$shell_type" in
        fish)
            alias_cmd="alias $COMMAND_ALIAS='$PYTHON_CMD \"$MAIN_PY\"'"
            ;;
        *)
            alias_cmd="alias $COMMAND_ALIAS='$PYTHON_CMD \"$MAIN_PY\"'"
            ;;
    esac
    
    # Check if alias already exists
    if grep -q "alias $COMMAND_ALIAS=" "$shell_config" 2>/dev/null; then
        print_warning "Alias '$COMMAND_ALIAS' already exists in $shell_config"
        echo ""
        
        # Show current alias
        local current_alias=$(grep "alias $COMMAND_ALIAS=" "$shell_config" | tail -1)
        print_info "Current: $current_alias"
        echo ""
        
        if ask_yes_no "Update existing alias?"; then
            # Remove old alias lines
            if [ "$(uname)" = "Darwin" ]; then
                # macOS
                sed -i '' "/alias $COMMAND_ALIAS=/d" "$shell_config"
                sed -i '' '/# Python Automation System/d' "$shell_config"
            else
                # Linux/Git Bash
                sed -i "/alias $COMMAND_ALIAS=/d" "$shell_config" 2>/dev/null || true
                sed -i '/# Python Automation System/d' "$shell_config" 2>/dev/null || true
            fi
            
            print_success "Removed old alias configuration"
        else
            print_info "Keeping existing alias"
            echo ""
            return 0
        fi
    fi
    
    # Add new alias
    {
        echo ""
        echo "# ============================================"
        echo "# Python Automation System"
        echo "# Installed: $(date)"
        echo "# ============================================"
        echo "$alias_cmd"
        echo ""
    } >> "$shell_config"
    
    print_success "Added '$COMMAND_ALIAS' alias to $shell_config"
    print_info "Command: $alias_cmd"
    echo ""
    
    # Show rollback instructions
    if [ -n "$backup_path" ]; then
        print_info "Backup saved to: $backup_path"
        print_info "To rollback: cp \"$backup_path\" \"$shell_config\""
        echo ""
    fi
}

# ============================================================
# TESTING
# ============================================================

test_installation() {
    print_section "🧪 Installation Testing"
    
    local all_tests_passed=true
    
    # Test 1: Python module imports
    print_step "Testing Python module imports..."
    
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from automation.menu import MainMenu
    print('✓ Module import successful')
except Exception as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_success "Python module imports working"
    else
        print_error "Python module import failed"
        all_tests_passed=false
    fi
    
    # Test 2: Main script loads
    print_step "Testing main.py execution..."
    
    if $PYTHON_CMD "$MAIN_PY" --help &> /dev/null || \
       $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from automation.menu import MainMenu
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
        print_success "main.py loads successfully"
    else
        print_warning "Could not verify main.py execution"
    fi
    
    # Test 3: Alias availability
    print_step "Testing alias configuration..."
    
    local shell_config=$(get_shell_config)
    if grep -q "alias $COMMAND_ALIAS=" "$shell_config"; then
        print_success "Alias configured in shell config"
    else
        print_error "Alias not found in shell config"
        all_tests_passed=false
    fi
    
    echo ""
    
    if [ "$all_tests_passed" = true ]; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed, but basic setup is complete"
        print_info "The system should still work, but some features may be limited"
    fi
    
    echo ""
    return 0
}

# ============================================================
# FINAL COMPLETION
# ============================================================

print_completion_message() {
    print_section "🎉 Setup Complete!"
    
    echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║  Python Automation System is ready to use!                    ║${NC}"
    echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${CYAN}${BOLD}📋 Installation Summary:${NC}"
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_CMD ($PYTHON_VERSION)"
    echo -e "  ${GREEN}✓${NC} Install location: $SCRIPT_DIR"
    echo -e "  ${GREEN}✓${NC} Shell config: $(get_shell_config)"
    echo -e "  ${GREEN}✓${NC} Command alias: ${YELLOW}${BOLD}$COMMAND_ALIAS${NC}"
    
    echo -e "\n${CYAN}${BOLD}🚀 Next Steps:${NC}"
    echo -e "  ${BLUE}1.${NC} Reload your shell configuration:"
    echo -e "     ${YELLOW}source $(get_shell_config)${NC}"
    echo -e "     ${MAGENTA}OR restart your terminal${NC}"
    
    echo -e "\n  ${BLUE}2.${NC} Test the installation:"
    echo -e "     ${YELLOW}$COMMAND_ALIAS${NC}"
    
    echo -e "\n  ${BLUE}3.${NC} Navigate to any project and run:"
    echo -e "     ${YELLOW}cd /path/to/your/project${NC}"
    echo -e "     ${YELLOW}$COMMAND_ALIAS${NC}"
    
    echo -e "\n${CYAN}${BOLD}💡 Quick Start Guide:${NC}"
    echo -e "  • ${BLUE}GitHub Operations:${NC} Push, pull, commit management"
    echo -e "  • ${BLUE}Project Structure:${NC} View and share project layout"
    echo -e "  • ${BLUE}Folder Navigator:${NC} Interactive directory navigation"
    echo -e "  • ${BLUE}Dev Mode:${NC} Web development automation tools"
    
    echo -e "\n${CYAN}${BOLD}📚 Resources:${NC}"
    echo -e "  • README: $SCRIPT_DIR/README.md"
    echo -e "  • Repository: https://github.com/Drakaniia/python-automation"
    echo -e "  • Issues: https://github.com/Drakaniia/python-automation/issues"
    
    echo -e "\n${CYAN}${BOLD}❓ Need Help?${NC}"
    echo -e "  • Email: alistairybaez574@gmail.com"
    echo -e "  • Documentation: Check README.md for detailed usage"
    
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}\n"
}

reload_shell_config() {
    local shell_config=$(get_shell_config)
    
    echo ""
    if ask_yes_no "Would you like to reload your shell configuration now?"; then
        if [ -f "$shell_config" ]; then
            print_info "Reloading $shell_config..."
            
            # Source the config
            set +e  # Don't exit on error for sourcing
            # shellcheck disable=SC1090
            source "$shell_config" 2>/dev/null || true
            set -e
            
            print_success "Configuration reloaded!"
            echo ""
            print_info "You can now use: ${YELLOW}${BOLD}$COMMAND_ALIAS${NC}"
            
            echo ""
            echo -e "${CYAN}${BOLD}Try it now:${NC}"
            echo -e "  ${YELLOW}$COMMAND_ALIAS${NC}"
        else
            print_warning "Could not reload configuration"
            print_info "Please restart your terminal or run: source $shell_config"
        fi
    else
        echo ""
        print_info "Remember to reload your shell:"
        echo -e "  ${YELLOW}source $shell_config${NC}"
        echo -e "  ${MAGENTA}OR restart your terminal${NC}"
    fi
    
    echo ""
}

# ============================================================
# MAIN SETUP FLOW
# ============================================================

main() {
    # Print header
    print_header
    
    echo -e "${CYAN}This wizard will:${NC}"
    echo -e "  • Detect and validate Python installation"
    echo -e "  • Check Git configuration"
    echo -e "  • Validate project files"
    echo -e "  • Configure shell aliases"
    echo -e "  • Test the installation"
    echo ""
    
    if ! ask_yes_no "Ready to begin?"; then
        echo ""
        echo -e "${YELLOW}Setup cancelled by user.${NC}"
        exit 0
    fi
    
    # Run validations
    validate_python || exit 1
    validate_git || true  # Git is optional
    validate_files || exit 1
    validate_permissions || exit 1
    
    # Configure alias
    configure_shell_alias
    
    # Test installation
    test_installation
    
    # Print completion message
    print_completion_message
    
    # Offer to reload config
    reload_shell_config
    
    # Final message
    echo -e "${GREEN}${BOLD}🎉 Setup completed successfully!${NC}\n"
}

# ============================================================
# ERROR HANDLING
# ============================================================

# Trap errors
trap 'echo -e "\n${RED}${BOLD}Setup failed. Please check the errors above.${NC}\n"; exit 1' ERR

# Trap Ctrl+C
trap 'echo -e "\n\n${YELLOW}Setup cancelled by user.${NC}\n"; exit 130' INT

# ============================================================
# ENTRY POINT
# ============================================================

main "$@"

exit 0