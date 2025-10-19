"""
Git Push Module
Handles push operations with simple user input for commit messages
"""
import subprocess
from pathlib import Path


class GitPush:
    """Handles git push and commit operations"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def push(self):
        """Add, commit, and push changes to remote"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH")
        print("="*70 + "\n")
        
        # Check if it's a git repository
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        # Check if there are changes
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        # Stage changes
        print("📦 Staging all changes...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        print("✅ Files staged\n")
        
        # Get commit message from user
        commit_message = input("Enter commit message: ").strip()
        
        if not commit_message:
            print("\n❌ Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Commit
        print(f"\n💾 Creating commit...")
        if not self._run_command(["git", "commit", "-m", commit_message]):
            input("\nPress Enter to continue...")
            return
        print("✅ Commit created\n")
        
        # Push
        print("📡 Pushing to remote...")
        if self._run_command(["git", "push"]):
            print("\n✅ Successfully pushed!")
        else:
            print("\n❌ Push failed. Check your remote configuration and network connection.")
        
        input("\nPress Enter to continue...")
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command):
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False