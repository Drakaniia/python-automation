"""
automation/github/git_push.py
Enhanced Git push with comprehensive retry strategies and automatic error recovery
"""
from pathlib import Path
from typing import Optional, List, Tuple
import sys
import time
import re
import subprocess

from automation.core.git_client import get_git_client
from automation.core.exceptions import (
    ExceptionHandler,
    GitError,
    GitCommandError,
    UncommittedChangesError,
    handle_errors
)


class PushStrategy:
    """Represents a push strategy with specific flags"""
    
    def __init__(
        self,
        name: str,
        flags: List[str],
        description: str,
        requires_confirmation: bool = False,
        is_destructive: bool = False
    ):
        self.name = name
        self.flags = flags
        self.description = description
        self.requires_confirmation = requires_confirmation
        self.is_destructive = is_destructive
    
    def __repr__(self):
        return f"PushStrategy({self.name})"


class PushConfig:
    """Configuration for push retry behavior"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.network_timeout = 30  # seconds
        self.enable_auto_hooks_bypass = True
        self.enable_auto_upstream = True
        self.enable_force_push = True  # Allow force push with confirmation
        self.exponential_backoff = True
        
        # Define progressive strategies
        self.strategies = [
            PushStrategy(
                "normal",
                [],
                "Standard push",
                requires_confirmation=False
            ),
            PushStrategy(
                "set-upstream",
                ["--set-upstream"],
                "Push and set upstream tracking",
                requires_confirmation=False
            ),
            PushStrategy(
                "no-verify",
                ["--no-verify"],
                "Skip pre-push hooks",
                requires_confirmation=False
            ),
            PushStrategy(
                "no-verify-upstream",
                ["--no-verify", "--set-upstream"],
                "Skip hooks and set upstream",
                requires_confirmation=False
            ),
            PushStrategy(
                "force-with-lease",
                ["--force-with-lease", "--no-verify"],
                "Force push (safer - checks remote state)",
                requires_confirmation=True,
                is_destructive=True
            ),
            PushStrategy(
                "force",
                ["--force", "--no-verify"],
                "Force push (destructive - overwrites remote)",
                requires_confirmation=True,
                is_destructive=True
            ),
        ]


class ProgressIndicator:
    """Enhanced progress indicator with status"""
    
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
    
    def stop(self, success: bool = True, message: Optional[str] = None):
        """Stop progress and show result"""
        self.active = False
        icon = "✅" if success else "❌"
        final_msg = message or self.message
        sys.stdout.write(f'\r{icon} {final_msg}\n')
        sys.stdout.flush()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop(success=exc_type is None)
        return False


class GitPushRetry:
    """
    Enhanced Git push with automatic retry and error recovery
    
    Features:
    - Progressive retry strategies (normal → upstream → no-verify → force)
    - Automatic hook bypass detection
    - Smart force push with user confirmation
    - Network retry with exponential backoff
    - Comprehensive error analysis
    - User-friendly progress indicators
    """
    
    def __init__(self, config: Optional[PushConfig] = None):
        self.current_dir = Path.cwd()
        self.git = get_git_client()
        self.config = config or PushConfig()
        self.attempt_count = 0
    
    @handle_errors()
    def push_with_retry(
        self,
        commit_message: Optional[str] = None,
        remote: str = 'origin',
        branch: Optional[str] = None
    ) -> bool:
        """
        Execute push with comprehensive retry strategies
        
        Args:
            commit_message: Commit message (if staging changes)
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)
        
        Returns:
            True if push succeeded, False otherwise
        """
        print("\n" + "="*70)
        print("⬆️  ENHANCED GIT PUSH WITH RETRY")
        print("="*70 + "\n")
        
        # Pre-flight checks
        if not self._pre_push_checks():
            return False
        
        # Get current branch if not specified
        if not branch:
            try:
                branch = self.git.current_branch()
            except Exception as e:
                print(f"❌ Could not determine current branch: {e}")
                return False
        
        # Stage and commit if there are changes
        if commit_message and self._has_changes():
            if not self._stage_and_commit(commit_message):
                return False
        
        # Execute push with progressive strategies
        return self._execute_push_with_strategies(remote, branch)
    
    def _execute_push_with_strategies(self, remote: str, branch: str) -> bool:
        """
        Try push with progressive strategies until success
        """
        print(f"📤 Pushing to {remote}/{branch}")
        print(f"🔄 Max attempts: {len(self.config.strategies)}\n")
        
        last_error = None
        
        for idx, strategy in enumerate(self.config.strategies, 1):
            self.attempt_count = idx
            
            print(f"{'─'*70}")
            print(f"🔹 Attempt {idx}/{len(self.config.strategies)}: {strategy.name}")
            print(f"   Description: {strategy.description}")
            print(f"{'─'*70}\n")
            
            # Check if confirmation needed
            if strategy.requires_confirmation:
                if not self._confirm_destructive_operation(strategy):
                    print("❌ Operation cancelled by user\n")
                    continue
            
            # Try the strategy
            success, error = self._try_push_strategy(strategy, remote, branch)
            
            if success:
                print(f"\n{'='*70}")
                print(f"✅ SUCCESS on attempt {idx} using: {strategy.name}")
                print(f"{'='*70}\n")
                self._show_push_summary()
                return True
            
            last_error = error
            
            # Analyze error and decide next step
            should_continue, wait_time = self._analyze_error_and_decide(
                error, idx, strategy
            )
            
            if not should_continue:
                break
            
            if wait_time > 0 and idx < len(self.config.strategies):
                print(f"\n⏳ Waiting {wait_time}s before next attempt...")
                time.sleep(wait_time)
                print()
        
        # All strategies failed
        print(f"\n{'='*70}")
        print("❌ PUSH FAILED - All retry strategies exhausted")
        print(f"{'='*70}\n")
        self._show_failure_guidance(last_error)
        return False
    
    def _try_push_strategy(
        self,
        strategy: PushStrategy,
        remote: str,
        branch: str
    ) -> Tuple[bool, Optional[Exception]]:
        """
        Try a specific push strategy
        
        Returns:
            (success: bool, error: Optional[Exception])
        """
        try:
            # Build git push command
            cmd = ['git', 'push']
            cmd.extend(strategy.flags)
            cmd.extend([remote, branch])
            
            # Show command being executed
            print(f"   $ {' '.join(cmd)}")
            
            # Execute with progress indicator
            with ProgressIndicator(f"Pushing with {strategy.name}"):
                result = self.git._run_command(
                    cmd,
                    check=True,
                    timeout=self.config.network_timeout
                )
            
            print(f"   ✅ Push successful!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            
            return True, None
        
        except GitCommandError as e:
            print(f"   ❌ Failed: {self._extract_error_message(e.stderr)}")
            return False, e
        
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
            return False, e
    
    def _analyze_error_and_decide(
        self,
        error: Optional[Exception],
        attempt: int,
        strategy: PushStrategy
    ) -> Tuple[bool, int]:
        """
        Analyze error and decide whether to continue
        
        Returns:
            (should_continue: bool, wait_seconds: int)
        """
        if not error:
            return False, 0
        
        error_msg = str(error).lower()
        
        # Detect error types
        is_hook_error = any(x in error_msg for x in [
            'pre-push hook', 'hook', 'test', 'failed'
        ])
        
        is_diverged = any(x in error_msg for x in [
            'diverged', 'non-fast-forward', 'rejected'
        ])
        
        is_network = any(x in error_msg for x in [
            'network', 'timeout', 'connection', 'could not resolve'
        ])
        
        is_no_upstream = any(x in error_msg for x in [
            'no upstream', 'no tracking', 'upstream branch'
        ])
        
        is_auth = any(x in error_msg for x in [
            'authentication', 'permission denied', 'credentials'
        ])
        
        # Log error analysis
        print(f"\n   🔍 Error Analysis:")
        if is_hook_error:
            print(f"      • Pre-push hooks blocking push")
            print(f"      → Next: Retry with --no-verify")
        
        if is_diverged:
            print(f"      • Remote branch has diverged")
            print(f"      → Next: Force push with confirmation")
        
        if is_network:
            print(f"      • Network/connection issue")
            print(f"      → Next: Retry with backoff")
        
        if is_no_upstream:
            print(f"      • Upstream branch not set")
            print(f"      → Next: Retry with --set-upstream")
        
        if is_auth:
            print(f"      • Authentication failure")
            print(f"      → Action: Check credentials")
            return False, 0  # Don't retry auth errors
        
        # Calculate wait time
        wait_time = 0
        if is_network and self.config.exponential_backoff:
            # Exponential backoff for network errors
            wait_time = min(2 ** attempt, 8)  # Max 8 seconds
        elif is_network:
            wait_time = self.config.retry_delay
        
        # Continue if not the last attempt
        should_continue = attempt < len(self.config.strategies)
        
        return should_continue, wait_time
    
    def _confirm_destructive_operation(self, strategy: PushStrategy) -> bool:
        """
        Get user confirmation for destructive operations
        """
        print(f"\n⚠️  WARNING: {strategy.name.upper()} is a destructive operation!")
        print(f"   This will overwrite remote history.")
        print(f"   Description: {strategy.description}\n")
        
        # Show what will be overwritten
        try:
            self._show_divergence_info()
        except Exception:
            pass
        
        print("\n❓ Do you want to proceed?")
        print("   Type 'YES' (all caps) to confirm:")
        
        confirmation = input("   > ").strip()
        
        return confirmation == "YES"
    
    def _show_divergence_info(self):
        """Show information about diverged commits"""
        try:
            result = self.git._run_command(
                ['git', 'log', 'origin/HEAD..HEAD', '--oneline'],
                check=False
            )
            
            if result.stdout.strip():
                print("   📊 Local commits that will overwrite remote:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"      • {line}")
        except Exception:
            pass
    
    def _pre_push_checks(self) -> bool:
        """Run pre-push validation checks"""
        print("🔍 Pre-push validation...\n")
        
        checks = [
            ("Git repository", self.git.is_repo),
            ("Remote configured", lambda: self.git.has_remote('origin')),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: {e}")
                all_passed = False
        
        print()
        
        if not all_passed:
            print("⚠️  Pre-push checks failed\n")
            print("💡 Suggestions:")
            
            if not self.git.is_repo():
                print("   • Initialize Git: magic → Initialize Git & Push to GitHub")
            
            if not self.git.has_remote('origin'):
                print("   • Configure remote: git remote add origin <url>")
            
            print()
            input("Press Enter to continue...")
        
        return all_passed
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            return self.git.has_uncommitted_changes()
        except Exception:
            return False
    
    def _stage_and_commit(self, message: str) -> bool:
        """Stage and commit changes"""
        try:
            print("📝 Staging changes...")
            self.git.add()
            print("✅ Changes staged\n")
            
            print(f"💾 Creating commit: '{message}'")
            self.git.commit(message)
            print("✅ Commit created\n")
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to stage/commit: {e}\n")
            return False
    
    def _show_push_summary(self):
        """Show summary after successful push"""
        try:
            commits = self.git.log(limit=1)
            if commits:
                commit = commits[0]
                print("📝 Latest commit:")
                print(f"   {commit['short_hash']} - {commit['message']}")
                print(f"   by {commit['author']}")
                print()
        except Exception:
            pass
    
    def _show_failure_guidance(self, last_error: Optional[Exception]):
        """Show guidance when all strategies fail"""
        print("🔧 Manual intervention required\n")
        
        if last_error:
            error_msg = str(last_error).lower()
            
            if 'network' in error_msg or 'timeout' in error_msg:
                print("📡 Network Issues Detected:")
                print("   • Check internet connection")
                print("   • Verify firewall settings")
                print("   • Try: ping github.com")
                print("   • Try later when network is stable\n")
            
            elif 'authentication' in error_msg or 'permission' in error_msg:
                print("🔐 Authentication Issues Detected:")
                print("   • Verify SSH keys: ssh -T git@github.com")
                print("   • Or use HTTPS with token")
                print("   • Check repository permissions\n")
            
            elif 'repository' in error_msg or 'not found' in error_msg:
                print("📁 Repository Issues Detected:")
                print("   • Verify remote URL: git remote -v")
                print("   • Check if repo exists on GitHub")
                print("   • Create repo first if needed\n")
            
            elif 'large' in error_msg or 'size' in error_msg:
                print("📦 Large File Issues Detected:")
                print("   • Consider using Git LFS")
                print("   • Or split into smaller commits")
                print("   • Check .gitignore for large files\n")
        
        print("💡 Fallback Commands:")
        print("   # View full error details")
        print("   $ git push origin HEAD -v\n")
        print("   # Force push (destructive!)")
        print("   $ git push origin HEAD --force\n")
        print("   # Pull and merge first")
        print("   $ git pull origin HEAD --rebase\n")
        
        input("Press Enter to continue...")
    
    def _extract_error_message(self, stderr: str) -> str:
        """Extract clean error message from stderr"""
        if not stderr:
            return "Unknown error"
        
        # Take first meaningful line
        lines = [l.strip() for l in stderr.split('\n') if l.strip()]
        
        # Find error lines (starting with ! or error:)
        error_lines = [l for l in lines if l.startswith('!') or 'error' in l.lower()]
        
        if error_lines:
            return error_lines[0][:100]  # Truncate long messages
        
        return lines[0][:100] if lines else "Unknown error"


class GitPush:
    """
    Backward-compatible GitPush class with enhanced retry
    """
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.git = get_git_client()
        self.push_retry = GitPushRetry()
    
    @handle_errors()
    def push(self, dry_run: bool = False):
        """
        Add, commit, and push changes with automatic retry
        
        Args:
            dry_run: Show what would be done without executing
        """
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (With Auto-Retry)")
        print("="*70 + "\n")
        
        # Check for changes
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        # Show changes summary
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
        
        # Execute push with retry
        success = self.push_retry.push_with_retry(commit_message=commit_message)
        
        if success:
            print("🎉 Push completed successfully!")
        else:
            print("⚠️  Push failed after all retry attempts")
        
        input("\nPress Enter to continue...")
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            return self.git.has_uncommitted_changes()
        except Exception:
            return False
    
    def _show_changes_summary(self):
        """Display summary of changes"""
        print("📊 Changes to be committed:\n")
        
        try:
            status = self.git.status(porcelain=True)
            
            if not status:
                print("  (none)")
                return
            
            # Count changes
            new_files = len([l for l in status.split('\n') if l.startswith('??')])
            modified = len([l for l in status.split('\n') if 'M' in l[:2]])
            deleted = len([l for l in status.split('\n') if 'D' in l[:2]])
            
            if new_files:
                print(f"  ➕ New files: {new_files}")
            if modified:
                print(f"  📝 Modified: {modified}")
            if deleted:
                print(f"  ➖ Deleted: {deleted}")
            
            print()
        
        except Exception as e:
            print(f"  ⚠️  Could not get summary: {e}\n")
    
    def _get_commit_message(self) -> Optional[str]:
        """Get commit message from user"""
        print("📝 Enter commit message:")
        print("   (Tip: Use format like '🐛 Fix: issue description')\n")
        
        message = input("Commit message: ").strip()
        
        if not message:
            return None
        
        if len(message) < 3:
            print("\n⚠️  Commit message too short (minimum 3 characters)")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return self._get_commit_message()
            return None
        
        return message


# Backward compatibility
def push():
    """Legacy function"""
    pusher = GitPush()
    pusher.push()


if __name__ == "__main__":
    print("🧪 Testing Enhanced Git Push\n")
    
    # Demo configuration
    config = PushConfig()
    print("Configuration:")
    print(f"  • Max retries: {config.max_retries}")
    print(f"  • Retry delay: {config.retry_delay}s")
    print(f"  • Strategies: {len(config.strategies)}")
    print("\nStrategies:")
    for i, s in enumerate(config.strategies, 1):
        print(f"  {i}. {s.name}: {s.description}")
    
    print("\n" + "="*70)
    print("Ready to use! Import and call:")
    print("  from automation.github.git_push import GitPush")
    print("  pusher = GitPush()")
    print("  pusher.push()")