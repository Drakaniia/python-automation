"""
automation/github/git_push.py
Refactored Git push operations with comprehensive error handling and progress
"""
from pathlib import Path
from typing import Optional
import sys

from automation.core.git_client import get_git_client
from automation.core.exceptions import (
    ExceptionHandler,
    GitError,
    UncommittedChangesError,
    handle_errors
)


class ProgressIndicator:
    """Simple progress indicator for operations"""
    
    SPINNERS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str):
        self.message = message
        self.index = 0
        self.active = False
    
    def start(self):
        """Start showing progress"""
        self.active = True
        self._update()
    
    def _update(self):
        """Update spinner"""
        if self.active:
            spinner = self.SPINNERS[self.index % len(self.SPINNERS)]
            sys.stdout.write(f'\r{spinner} {self.message}...')
            sys.stdout.flush()
            self.index += 1
    
    def stop(self, success: bool = True):
        """Stop progress and show result"""
        self.active = False
        icon = "✅" if success else "❌"
        sys.stdout.write(f'\r{icon} {self.message}\n')
        sys.stdout.flush()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)
        return False


class GitPush:
    """
    Handles git push operations with comprehensive error handling
    
    Features:
    - Progress indicators for long operations
    - Automatic error detection and suggestions
    - Pre-push validation
    - Dry-run support
    """
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.git = get_git_client()
    
    @handle_errors()
    def push(self, dry_run: bool = False):
        """
        Add, commit, and push changes to remote
        
        Args:
            dry_run: Show what would be done without executing
        """
        print("\n" + "="*70)
        print("⬆️  GIT PUSH")
        print("="*70 + "\n")
        
        # Pre-flight checks
        if not self._pre_push_checks():
            input("\nPress Enter to continue...")
            return
        
        # Check for changes
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        # Show what will be pushed
        self._show_changes_summary()
        
        if dry_run:
            print("\n🏃 DRY RUN - No changes will be made")
            input("\nPress Enter to continue...")
            return
        
        # Get commit message
        commit_message = self._get_commit_message()
        if not commit_message:
            print("\n❌ Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        # Execute push workflow
        try:
            self._execute_push(commit_message)
        except Exception as e:
            ExceptionHandler.handle(e)
            input("\nPress Enter to continue...")
    
    def _pre_push_checks(self) -> bool:
        """Run pre-push validation checks"""
        print("🔍 Running pre-push checks...\n")
        
        checks = [
            ("Git repository", self.git.is_repo),
            ("Remote configured", lambda: self.git.has_remote('origin')),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                all_passed = False
        
        print()
        
        if not all_passed:
            print("⚠️  Pre-push checks failed. Please fix issues above.")
            
            if not self.git.is_repo():
                print("\n💡 Initialize Git with: 'Initialize Git & Push to GitHub'")
            elif not self.git.has_remote('origin'):
                print("\n💡 Configure remote with: 'Initialize Git & Push to GitHub'")
        
        return all_passed
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            return self.git.has_uncommitted_changes()
        except Exception as e:
            ExceptionHandler.handle(e)
            return False
    
    def _show_changes_summary(self):
        """Display summary of changes to be committed"""
        print("📊 Changes to be committed:\n")
        
        try:
            status = self.git.status(porcelain=True)
            
            if not status:
                print("  (none)")
                return
            
            # Parse and categorize changes
            new_files = []
            modified_files = []
            deleted_files = []
            
            for line in status.split('\n'):
                if not line.strip():
                    continue
                
                status_code = line[:2]
                filename = line[3:].strip()
                
                if '??' in status_code:
                    new_files.append(filename)
                elif 'M' in status_code or 'A' in status_code:
                    modified_files.append(filename)
                elif 'D' in status_code:
                    deleted_files.append(filename)
            
            if new_files:
                print(f"  ➕ New files: {len(new_files)}")
                for f in new_files[:5]:
                    print(f"     • {f}")
                if len(new_files) > 5:
                    print(f"     ... and {len(new_files) - 5} more")
            
            if modified_files:
                print(f"  📝 Modified: {len(modified_files)}")
                for f in modified_files[:5]:
                    print(f"     • {f}")
                if len(modified_files) > 5:
                    print(f"     ... and {len(modified_files) - 5} more")
            
            if deleted_files:
                print(f"  ➖ Deleted: {len(deleted_files)}")
                for f in deleted_files[:5]:
                    print(f"     • {f}")
                if len(deleted_files) > 5:
                    print(f"     ... and {len(deleted_files) - 5} more")
            
            print()
        
        except Exception as e:
            print(f"  ⚠️  Could not get change summary: {e}\n")
    
    def _get_commit_message(self) -> Optional[str]:
        """Get commit message from user"""
        print("📝 Enter commit message:")
        print("   (Tip: Use format like '🐛 Fix: issue description')\n")
        
        message = input("Commit message: ").strip()
        
        if not message:
            return None
        
        # Validate message
        if len(message) < 3:
            print("\n⚠️  Commit message too short (minimum 3 characters)")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return self._get_commit_message()
            return None
        
        return message
    
    def _execute_push(self, commit_message: str):
        """Execute the push workflow with progress indicators"""
        
        # Stage changes
        with ProgressIndicator("Staging changes"):
            self.git.add()
        
        # Commit
        with ProgressIndicator("Creating commit"):
            self.git.commit(commit_message)
        
        # Push
        print()  # New line before push output
        try:
            with ProgressIndicator("Pushing to remote"):
                # Check if upstream is set
                try:
                    self.git.push()
                except GitError as e:
                    if "no upstream" in str(e).lower():
                        print("\n⚠️  No upstream branch set. Setting upstream...")
                        self.git.push(set_upstream=True)
                    else:
                        raise
        except Exception as e:
            print(f"\n❌ Push failed: {e}")
            print("\n💡 Possible solutions:")
            print("  • Check your internet connection")
            print("  • Verify remote repository exists")
            print("  • Pull latest changes: git pull")
            raise
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Changes pushed to remote")
        print("="*70)
        
        # Show latest commit
        try:
            commits = self.git.log(limit=1)
            if commits:
                commit = commits[0]
                print(f"\n📝 Latest commit:")
                print(f"   {commit['hash'][:8]} - {commit['message']}")
                print(f"   by {commit['author']}")
        except Exception:
            pass
        
        print()
    
    @handle_errors()
    def force_push(self):
        """Force push with safety confirmation"""
        print("\n" + "="*70)
        print("⚠️  FORCE PUSH")
        print("="*70 + "\n")
        
        print("🔥 WARNING: Force push will overwrite remote history!")
        print("This is a destructive operation and cannot be undone.\n")
        
        # Show what will be affected
        try:
            branch = self.git.current_branch()
            print(f"Branch: {branch}")
            print(f"Remote: origin/{branch}\n")
        except Exception as e:
            print(f"⚠️  Could not get branch info: {e}\n")
        
        # Triple confirmation
        print("Type 'FORCE PUSH' (exact, case-sensitive) to confirm:")
        confirm = input("> ").strip()
        
        if confirm != "FORCE PUSH":
            print("\n❌ Operation cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Execute force push
        try:
            with ProgressIndicator("Force pushing"):
                self.git.push(force=True)
            
            print("\n✅ Force push completed")
        except Exception as e:
            ExceptionHandler.handle(e)
        
        input("\nPress Enter to continue...")
    
    @handle_errors()
    def push_tags(self):
        """Push tags to remote"""
        print("\n" + "="*70)
        print("🏷️  PUSH TAGS")
        print("="*70 + "\n")
        
        if not self.git.is_repo():
            print("❌ Not a git repository")
            input("\nPress Enter to continue...")
            return
        
        try:
            with ProgressIndicator("Pushing tags"):
                self.git._run_command(['git', 'push', '--tags'], check=True)
            
            print("✅ Tags pushed successfully")
        except Exception as e:
            ExceptionHandler.handle(e)
        
        input("\nPress Enter to continue...")


# Backward compatibility
def push():
    """Legacy function for backward compatibility"""
    pusher = GitPush()
    pusher.push()


if __name__ == "__main__":
    # Test the module
    print("Testing GitPush module\n")
    pusher = GitPush()
    pusher.push(dry_run=True)