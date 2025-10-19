"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
"""
from pathlib import Path
from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_pull import GitPull
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.menu import Menu, MenuItem


class GitOperations:
    """Unified Git operations orchestrator"""
    
    def __init__(self):
        self.current_path = Path.cwd()
        
        # Initialize all modular components
        self.status_handler = GitStatus()
        self.log_handler = GitLog()
        self.pull_handler = GitPull()
        self.push_handler = GitPush()
        self.initializer = GitInitializer()
        self.recovery_handler = GitRecover()
    
    # ========== BASIC GIT OPERATIONS ==========
    
    def status(self):
        """Show git status"""
        self.status_handler.show_status()
    
    def log(self):
        """Show git log"""
        self.log_handler.show_log(limit=10)
    
    def pull(self):
        """Pull from remote"""
        self.pull_handler.pull()
    
    def push(self):
        """Add, commit, and push changes"""
        self.push_handler.push()
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        self.initializer.initialize_and_push()
    
    # ========== GIT RECOVERY ==========
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        self.recovery_handler.show_recovery_menu(
            commit_history_func=self.log_handler.get_commit_history,
            commit_details_func=self.log_handler.get_commit_details,
            verify_commit_func=self.log_handler.verify_commit_exists
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