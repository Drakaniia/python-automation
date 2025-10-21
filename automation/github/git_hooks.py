"""
Git Hooks Manager Module - Windows Compatible
Manages Git hooks for automation and quality control
Fixed encoding issues for Windows
"""
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import stat
import sys


class GitHooksManager:
    """Manages Git hooks installation and configuration"""
    
    # Pre-defined hook templates
    HOOK_TEMPLATES = {
        'pre-commit': """#!/bin/sh
# Pre-commit hook for code quality checks

echo "Running pre-commit checks..."

# Check for Python syntax errors
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$')
if [ -n "$python_files" ]; then
    echo "  Checking Python syntax..."
    for file in $python_files; do
        python -m py_compile "$file" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  Syntax error in $file"
            exit 1
        fi
    done
    echo "  Python syntax OK"
fi

# Check for TODO/FIXME in staged files
todos=$(git diff --cached | grep -E '^\\+.*\\b(TODO|FIXME)\\b')
if [ -n "$todos" ]; then
    echo "  Warning: Found TODO/FIXME in staged changes"
    echo "$todos"
fi

# Check for debug statements
debug=$(git diff --cached | grep -E '^\\+.*\\b(print\\(|console\\.log|debugger)\\b')
if [ -n "$debug" ]; then
    echo "  Warning: Found debug statements in staged changes"
    echo "$debug"
fi

echo "  Pre-commit checks passed!"
exit 0
""",
        
        'pre-push': """#!/bin/sh
# Pre-push hook for final validation

echo "Running pre-push checks..."

# Check if on main/master branch
current_branch=$(git symbolic-ref --short HEAD)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "  Pushing to $current_branch branch"
    read -p "  Are you sure? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "  Push cancelled"
        exit 1
    fi
fi

# Run tests if they exist
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    echo "  Running tests..."
    pytest -q 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  Tests failed - continue anyway? (y/n): "
        read confirm
        if [ "$confirm" != "y" ]; then
            exit 1
        fi
    fi
fi

echo "  Pre-push checks passed!"
exit 0
""",
        
        'commit-msg': """#!/bin/sh
# Commit message hook for enforcing conventions

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check minimum length
if [ ${#commit_msg} -lt 10 ]; then
    echo "Commit message too short (minimum 10 characters)"
    exit 1
fi

echo "Commit message validated"
exit 0
""",
        
        'post-commit': """#!/bin/sh
# Post-commit hook for logging and notifications

echo "Commit created: $(git log -1 --pretty=format:'%h - %s')"

# Optional: Log commits to file
# echo "$(date): $(git log -1 --pretty=format:'%h - %s')" >> .git/commit_log.txt

exit 0
""",
        
        'post-merge': """#!/bin/sh
# Post-merge hook for dependency updates

echo "Post-merge: Checking for updates..."

# Check if requirements changed
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q 'requirements.txt'; then
    echo "  requirements.txt changed - consider running: pip install -r requirements.txt"
fi

# Check if package.json changed
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q 'package.json'; then
    echo "  package.json changed - consider running: npm install"
fi

exit 0
"""
    }
    
    def __init__(self):
        self.repo_path = Path.cwd()
        self.hooks_dir = self.repo_path / '.git' / 'hooks'
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        return (self.repo_path / '.git').exists()
    
    def install_hook(self, hook_name: str) -> bool:
        """Install a specific hook with proper encoding"""
        try:
            # Use ASCII-only messages for Windows compatibility
            print(f"\nInstalling {hook_name} hook...")
            
            if hook_name not in self.HOOK_TEMPLATES:
                print(f"Unknown hook: {hook_name}")
                return False
            
            hook_path = self.hooks_dir / hook_name
            
            # Check if hook exists
            if hook_path.exists():
                print(f"Hook already exists: {hook_name}")
                overwrite = input("Overwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    print("Installation cancelled")
                    return False
            
            # Create hooks directory if needed
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            
            # Write hook content with UTF-8 encoding and LF line endings
            hook_content = self.HOOK_TEMPLATES[hook_name]
            
            # Write with explicit encoding and newline handling
            with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(hook_content)
            
            # Make executable (works on Unix, ignored on Windows)
            try:
                current_mode = hook_path.stat().st_mode
                hook_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except (OSError, NotImplementedError):
                # Windows or filesystem doesn't support chmod
                pass
            
            print(f"Successfully installed {hook_name} hook")
            print(f"   Location: {hook_path}")
            return True
            
        except Exception as e:
            # Use ASCII characters only in error messages for Windows
            print(f"Error installing hook: {e}")
            return False
    
    def install_all_hooks(self):
        """Install all available hooks"""
        print("\nInstalling all hooks...\n")
        
        confirm = input("Install all standard hooks? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Installation cancelled")
            return
        
        installed = []
        failed = []
        
        for hook_name in self.HOOK_TEMPLATES.keys():
            try:
                hook_path = self.hooks_dir / hook_name
                self.hooks_dir.mkdir(parents=True, exist_ok=True)
                
                with open(hook_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(self.HOOK_TEMPLATES[hook_name])
                
                try:
                    current_mode = hook_path.stat().st_mode
                    hook_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                except (OSError, NotImplementedError):
                    pass
                
                installed.append(hook_name)
                print(f"  Installed {hook_name}")
            
            except Exception as e:
                failed.append(hook_name)
                print(f"  Failed to install {hook_name}: {e}")
        
        print(f"\nSummary:")
        print(f"  Installed: {len(installed)}")
        print(f"  Failed: {len(failed)}")
    
    def list_hooks(self):
        """List all installed hooks"""
        print("\n" + "="*70)
        print("INSTALLED HOOKS")
        print("="*70 + "\n")
        
        if not self.hooks_dir.exists():
            print("No hooks directory found")
            return
        
        hooks_found = False
        for hook_file in self.hooks_dir.iterdir():
            if hook_file.is_file() and not hook_file.name.endswith('.sample'):
                hooks_found = True
                
                # Check if executable (works on Unix, may not work on Windows)
                try:
                    executable = hook_file.stat().st_mode & stat.S_IXUSR
                    status = "Executable" if executable else "Not executable"
                except (OSError, AttributeError):
                    status = "Status unknown"
                
                print(f"  {hook_file.name:<20} {status}")
                
                # Show first few lines
                try:
                    with open(hook_file, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()[:3]
                        for line in lines:
                            if line.strip() and not line.startswith('#!'):
                                print(f"     -> {line.strip()}")
                except Exception:
                    pass
                print()
        
        if not hooks_found:
            print("  No hooks installed")
    
    def show_hooks_menu(self):
        """Display hooks management interface - simplified for testing"""
        print("\n" + "="*70)
        print("GIT HOOKS MANAGER")
        print("="*70 + "\n")
        
        if not self.is_git_repo():
            print("Not a Git repository")
            return
        
        # Simplified menu without emojis for Windows compatibility
        print("\nAvailable Operations:")
        print("  1. List installed hooks")
        print("  2. Install pre-commit hook")
        print("  3. Install pre-push hook")
        print("  4. Install all hooks")
        print("  5. Back to menu\n")