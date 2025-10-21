"""
Git Hooks Manager Module
Manages Git hooks for automation and quality control
"""
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import stat


class GitHooksManager:
    """Manages Git hooks installation and configuration"""
    
    # Pre-defined hook templates
    HOOK_TEMPLATES = {
        'pre-commit': """#!/bin/sh
# Pre-commit hook for code quality checks

echo "🔍 Running pre-commit checks..."

# Check for Python syntax errors
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$')
if [ -n "$python_files" ]; then
    echo "  ✓ Checking Python syntax..."
    for file in $python_files; do
        python -m py_compile "$file" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  ❌ Syntax error in $file"
            exit 1
        fi
    done
    echo "  ✓ Python syntax OK"
fi

# Check for TODO/FIXME in staged files
todos=$(git diff --cached | grep -E '^\\+.*\\b(TODO|FIXME)\\b')
if [ -n "$todos" ]; then
    echo "  ⚠️  Warning: Found TODO/FIXME in staged changes"
    echo "$todos"
fi

# Check for debug statements
debug=$(git diff --cached | grep -E '^\\+.*\\b(print\\(|console\\.log|debugger)\\b')
if [ -n "$debug" ]; then
    echo "  ⚠️  Warning: Found debug statements in staged changes"
    echo "$debug"
fi

echo "  ✅ Pre-commit checks passed!"
exit 0
""",
        
        'pre-push': """#!/bin/sh
# Pre-push hook for final validation

echo "🚀 Running pre-push checks..."

# Check if on main/master branch
current_branch=$(git symbolic-ref --short HEAD)
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "  ⚠️  Pushing to $current_branch branch"
    read -p "  Are you sure? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "  ❌ Push cancelled"
        exit 1
    fi
fi

# Run tests if they exist
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    echo "  🧪 Running tests..."
    pytest -q 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  ⚠️  Tests failed - continue anyway? (y/n): "
        read confirm
        if [ "$confirm" != "y" ]; then
            exit 1
        fi
    fi
fi

echo "  ✅ Pre-push checks passed!"
exit 0
""",
        
        'commit-msg': """#!/bin/sh
# Commit message hook for enforcing conventions

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check minimum length
if [ ${#commit_msg} -lt 10 ]; then
    echo "❌ Commit message too short (minimum 10 characters)"
    exit 1
fi

# Check for issue references (optional)
# if ! echo "$commit_msg" | grep -qE '#[0-9]+|JIRA-[0-9]+'; then
#     echo "⚠️  No issue reference found in commit message"
# fi

echo "✅ Commit message validated"
exit 0
""",
        
        'post-commit': """#!/bin/sh
# Post-commit hook for logging and notifications

echo "📝 Commit created: $(git log -1 --pretty=format:'%h - %s')"

# Optional: Log commits to file
# echo "$(date): $(git log -1 --pretty=format:'%h - %s')" >> .git/commit_log.txt

exit 0
""",
        
        'post-merge': """#!/bin/sh
# Post-merge hook for dependency updates

echo "🔄 Post-merge: Checking for updates..."

# Check if requirements changed
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q 'requirements.txt'; then
    echo "  📦 requirements.txt changed - consider running: pip install -r requirements.txt"
fi

# Check if package.json changed
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q 'package.json'; then
    echo "  📦 package.json changed - consider running: npm install"
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
    
    def show_hooks_menu(self):
        """Display hooks management interface"""
        print("\n" + "="*70)
        print("🪝 GIT HOOKS MANAGER")
        print("="*70 + "\n")
        
        if not self.is_git_repo():
            print("❌ Not a Git repository")
            input("\nPress Enter to continue...")
            return
        
        while True:
            print("\n📋 Available Operations:")
            print("  1. List installed hooks")
            print("  2. Install pre-commit hook")
            print("  3. Install pre-push hook")
            print("  4. Install commit-msg hook")
            print("  5. Install post-commit hook")
            print("  6. Install post-merge hook")
            print("  7. Install all hooks")
            print("  8. Create custom hook")
            print("  9. Remove hook")
            print("  10. Back to menu\n")
            
            choice = input("Your choice: ").strip()
            
            if choice == '1':
                self.list_hooks()
            elif choice == '2':
                self.install_hook('pre-commit')
            elif choice == '3':
                self.install_hook('pre-push')
            elif choice == '4':
                self.install_hook('commit-msg')
            elif choice == '5':
                self.install_hook('post-commit')
            elif choice == '6':
                self.install_hook('post-merge')
            elif choice == '7':
                self.install_all_hooks()
            elif choice == '8':
                self.create_custom_hook()
            elif choice == '9':
                self.remove_hook()
            elif choice == '10':
                break
            else:
                print("\n❌ Invalid choice")
    
    def list_hooks(self):
        """List all installed hooks"""
        print("\n" + "="*70)
        print("📜 INSTALLED HOOKS")
        print("="*70 + "\n")
        
        if not self.hooks_dir.exists():
            print("No hooks directory found")
            input("\nPress Enter to continue...")
            return
        
        hooks_found = False
        for hook_file in self.hooks_dir.iterdir():
            if hook_file.is_file() and not hook_file.name.endswith('.sample'):
                hooks_found = True
                executable = hook_file.stat().st_mode & stat.S_IXUSR
                status = "✅ Executable" if executable else "⚠️  Not executable"
                print(f"  🪝 {hook_file.name:<20} {status}")
                
                # Show first few lines
                try:
                    with open(hook_file, 'r') as f:
                        lines = f.readlines()[:3]
                        for line in lines:
                            if line.strip() and not line.startswith('#!'):
                                print(f"     → {line.strip()}")
                except Exception:
                    pass
                print()
        
        if not hooks_found:
            print("  No hooks installed")
        
        input("\nPress Enter to continue...")
    
    def install_hook(self, hook_name: str) -> bool:
        """Install a specific hook"""
        print(f"\n🔧 Installing {hook_name} hook...")
        
        if hook_name not in self.HOOK_TEMPLATES:
            print(f"❌ Unknown hook: {hook_name}")
            input("\nPress Enter to continue...")
            return False
        
        hook_path = self.hooks_dir / hook_name
        
        # Check if hook exists
        if hook_path.exists():
            print(f"⚠️  Hook already exists: {hook_name}")
            overwrite = input("Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("❌ Installation cancelled")
                input("\nPress Enter to continue...")
                return False
        
        # Create hooks directory if needed
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Write hook content
        try:
            with open(hook_path, 'w', newline='\n') as f:
                f.write(self.HOOK_TEMPLATES[hook_name])
            
            # Make executable
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            print(f"✅ Successfully installed {hook_name} hook")
            print(f"   Location: {hook_path}")
            
        except Exception as e:
            print(f"❌ Error installing hook: {e}")
            input("\nPress Enter to continue...")
            return False
        
        input("\nPress Enter to continue...")
        return True
    
    def install_all_hooks(self):
        """Install all available hooks"""
        print("\n🔧 Installing all hooks...\n")
        
        confirm = input("Install all standard hooks? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Installation cancelled")
            input("\nPress Enter to continue...")
            return
        
        installed = []
        failed = []
        
        for hook_name in self.HOOK_TEMPLATES.keys():
            hook_path = self.hooks_dir / hook_name
            
            try:
                self.hooks_dir.mkdir(parents=True, exist_ok=True)
                
                with open(hook_path, 'w', newline='\n') as f:
                    f.write(self.HOOK_TEMPLATES[hook_name])
                
                hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                
                installed.append(hook_name)
                print(f"  ✅ Installed {hook_name}")
            
            except Exception as e:
                failed.append(hook_name)
                print(f"  ❌ Failed to install {hook_name}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Installed: {len(installed)}")
        print(f"  ❌ Failed: {len(failed)}")
        
        input("\nPress Enter to continue...")
    
    def create_custom_hook(self):
        """Create a custom hook"""
        print("\n" + "="*70)
        print("🎨 CREATE CUSTOM HOOK")
        print("="*70 + "\n")
        
        print("Available hook types:")
        print("  • applypatch-msg")
        print("  • pre-applypatch")
        print("  • post-applypatch")
        print("  • pre-commit")
        print("  • prepare-commit-msg")
        print("  • commit-msg")
        print("  • post-commit")
        print("  • pre-rebase")
        print("  • post-checkout")
        print("  • post-merge")
        print("  • pre-push")
        print("  • pre-receive")
        print("  • update")
        print("  • post-receive")
        print("  • post-update")
        print("  • push-to-checkout")
        print("  • pre-auto-gc")
        print("  • post-rewrite\n")
        
        hook_name = input("Enter hook name: ").strip()
        if not hook_name:
            print("❌ Hook name cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        print("\nEnter hook script (end with empty line):")
        print("#!/bin/sh")
        
        lines = ["#!/bin/sh\n"]
        while True:
            line = input()
            if not line:
                break
            lines.append(line + '\n')
        
        if len(lines) <= 1:
            print("❌ Hook content cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        hook_path = self.hooks_dir / hook_name
        
        try:
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            
            with open(hook_path, 'w', newline='\n') as f:
                f.writelines(lines)
            
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            
            print(f"\n✅ Successfully created {hook_name} hook")
            print(f"   Location: {hook_path}")
        
        except Exception as e:
            print(f"❌ Error creating hook: {e}")
        
        input("\nPress Enter to continue...")
    
    def remove_hook(self):
        """Remove an installed hook"""
        print("\n" + "="*70)
        print("🗑️  REMOVE HOOK")
        print("="*70 + "\n")
        
        # List installed hooks
        hooks = [h.name for h in self.hooks_dir.iterdir() 
                if h.is_file() and not h.name.endswith('.sample')]
        
        if not hooks:
            print("No hooks installed")
            input("\nPress Enter to continue...")
            return
        
        print("Installed hooks:")
        for i, hook in enumerate(hooks, 1):
            print(f"  {i}. {hook}")
        
        choice = input("\nEnter hook number to remove (or 'cancel'): ").strip()
        
        if choice.lower() == 'cancel':
            print("❌ Cancelled")
            input("\nPress Enter to continue...")
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(hooks):
                hook_name = hooks[idx]
                hook_path = self.hooks_dir / hook_name
                
                confirm = input(f"Remove {hook_name}? (y/n): ").strip().lower()
                if confirm == 'y':
                    hook_path.unlink()
                    print(f"✅ Removed {hook_name}")
                else:
                    print("❌ Cancelled")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_hook(self, hook_name: str):
        """Test a hook execution"""
        hook_path = self.hooks_dir / hook_name
        
        if not hook_path.exists():
            print(f"❌ Hook not found: {hook_name}")
            return False
        
        print(f"🧪 Testing {hook_name}...")
        
        try:
            result = subprocess.run(
                [str(hook_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            if result.stderr:
                print(f"Errors:\n{result.stderr}")
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"❌ Error testing hook: {e}")
            return False