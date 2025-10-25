"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
UPDATED: Changelog is now auto-generated after successful push
"""
from pathlib import Path
from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_pull import GitPull
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.menu import Menu, MenuItem
from automation.core.git_client import get_git_client


class GitOperations:
    """Unified Git operations orchestrator with dynamic directory detection"""
    
    def __init__(self):
        # Don't cache components - create fresh for each operation
        pass
    
    def _get_current_path(self):
        """Get current working directory (updates dynamically)"""
        return Path.cwd()
    
    def _refresh_git_client(self):
        """Get fresh GitClient for current directory"""
        return get_git_client(working_dir=self._get_current_path())
    
    # ========== BASIC GIT OPERATIONS ==========
    
    def status(self):
        """Show git status"""
        status_handler = GitStatus()
        status_handler.show_status()
    
    def log(self):
        """Show git log"""
        log_handler = GitLog()
        log_handler.show_log(limit=10)
    
    def pull(self):
        """Pull from remote"""
        pull_handler = GitPull()
        pull_handler.pull()
    
    def push(self):
        """Add, commit, and push changes"""
        # Create fresh push handler for current directory
        push_handler = GitPush()
        push_handler.push()
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        initializer = GitInitializer()
        initializer.initialize_and_push()
    
    # ========== GIT RECOVERY ==========
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        log_handler = GitLog()
        recovery_handler = GitRecover()
        recovery_handler.show_recovery_menu(
            commit_history_func=log_handler.get_commit_history,
            commit_details_func=log_handler.get_commit_details,
            verify_commit_func=log_handler.verify_commit_exists
        )


class GitMenu(Menu):
    """Unified menu for all Git operations"""
    
    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("🔧 GitHub Operations")
    
    def setup_items(self):
        """Setup menu items with all Git operations"""
        self.items = [
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Log (Last 10 commits)", lambda: self.git_ops.log()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Push (Add, Commit & Push)", lambda: self.git_ops.push()),
            MenuItem("Initialize Git & Push to GitHub", lambda: self.git_ops.initialize_and_push()),
            MenuItem("Git Recovery (Revert to Previous Commit)", lambda: self.git_ops.show_recovery_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]