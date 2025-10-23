"""
automation/core/git_client.py
Unified Git client for all Git operations
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from automation.core.exceptions import (
    GitError,
    GitCommandError,
    NotGitRepositoryError,
    NoRemoteError,
    GitNotInstalledError,
    UncommittedChangesError
)


class GitClient:
    """
    Unified Git client providing clean interface to Git operations
    
    Features:
    - Automatic error handling and user-friendly messages
    - Type-safe return values
    - Consistent API across all operations
    - Proper encoding handling
    """
    
    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize Git client
        
        Args:
            working_dir: Working directory (defaults to current directory)
        """
        self.working_dir = working_dir or Path.cwd()
        self._verify_git_installed()
    
    # ========== Repository Checks ==========
    
    def is_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = self._run_command(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def ensure_repo(self) -> None:
        """Ensure we're in a Git repository, raise if not"""
        if not self.is_repo():
            raise NotGitRepositoryError(str(self.working_dir))
    
    # ========== Status Operations ==========
    
    def status(self, porcelain: bool = False) -> str:
        """
        Get repository status
        
        Args:
            porcelain: Return machine-readable format
        """
        self.ensure_repo()
        
        cmd = ['git', 'status']
        if porcelain:
            cmd.append('--porcelain')
        
        result = self._run_command(cmd, check=True)
        return result.stdout.strip()

    def has_uncommitted_changes(self) -> bool:
        """
        Check if there are uncommitted changes or untracked files
        
        This includes:
        - Modified tracked files
        - Deleted tracked files
        - Staged changes
        - Untracked files (new files not yet added)
        """
        try:
            status = self.status(porcelain=True)
            # Any non-empty output from git status --porcelain means there are changes
            # This includes both tracked changes AND untracked files (??)
            return bool(status and status.strip())
        except Exception:
            return False

    # ========== Add/Stage Operations ==========
    
    def add(self, files: Optional[List[str]] = None) -> bool:
        """
        Stage files for commit
        
        Args:
            files: Specific files to add (None = add all)
        """
        self.ensure_repo()
        
        cmd = ['git', 'add']
        if files:
            cmd.extend(files)
        else:
            cmd.append('.')
        
        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise
    
    # ========== Commit Operations ==========
    
    def commit(self, message: str, amend: bool = False) -> bool:
        """
        Create commit
        
        Args:
            message: Commit message
            amend: Amend previous commit
        """
        self.ensure_repo()
        
        if not message or not message.strip():
            raise GitError("Commit message cannot be empty")
        
        cmd = ['git', 'commit', '-m', message]
        if amend:
            cmd.append('--amend')
        
        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise
    
    # ========== Log Operations ==========
    
    def log(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get commit history
        
        Args:
            limit: Maximum number of commits to return
        """
        self.ensure_repo()
        
        result = self._run_command([
            'git', 'log',
            f'-{limit}',
            '--pretty=format:%H|%an|%ai|%s'
        ], check=True)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|', 3)
            if len(parts) == 4:
                commit_hash, author, date, message = parts
                
                commits.append({
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'author': author,
                    'date': date,
                    'message': message
                })
        
        return commits
    
    # ========== Branch Operations ==========
    
    def current_branch(self) -> str:
        """Get current branch name"""
        self.ensure_repo()
        
        result = self._run_command(
            ['git', 'branch', '--show-current'],
            check=True
        )
        return result.stdout.strip()
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create new branch
        
        Args:
            branch_name: Name of new branch
            checkout: Switch to new branch
        """
        self.ensure_repo()
        
        cmd = ['git', 'branch', branch_name]
        self._run_command(cmd, check=True)
        
        if checkout:
            self._run_command(['git', 'checkout', branch_name], check=True)
        
        return True
    
    # ========== Remote Operations ==========
    
    def has_remote(self, remote_name: str = 'origin') -> bool:
        """Check if remote exists"""
        try:
            result = self._run_command(
                ['git', 'remote', 'get-url', remote_name],
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_remote_url(self, remote_name: str = 'origin') -> Optional[str]:
        """Get remote URL"""
        try:
            result = self._run_command(
                ['git', 'remote', 'get-url', remote_name],
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def add_remote(self, remote_name: str, url: str) -> bool:
        """Add remote repository"""
        self.ensure_repo()
        
        self._run_command(
            ['git', 'remote', 'add', remote_name, url],
            check=True
        )
        return True
    
    def set_remote_url(self, remote_name: str, url: str) -> bool:
        """Update remote URL"""
        self.ensure_repo()
        
        self._run_command(
            ['git', 'remote', 'set-url', remote_name, url],
            check=True
        )
        return True
    
    # ========== Push/Pull Operations ==========
    
    def push(
        self,
        remote: str = 'origin',
        branch: Optional[str] = None,
        set_upstream: bool = False,
        force: bool = False
    ) -> bool:
        """
        Push commits to remote
        
        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            set_upstream: Set upstream tracking
            force: Force push
        """
        self.ensure_repo()
        
        if not self.has_remote(remote):
            raise NoRemoteError(remote)
        
        cmd = ['git', 'push']
        
        if set_upstream:
            cmd.append('--set-upstream')
        if force:
            cmd.append('--force')
        
        cmd.append(remote)
        
        if branch:
            cmd.append(branch)
        elif set_upstream:
            # Need explicit branch for set-upstream
            cmd.append(self.current_branch())
        
        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError as e:
            # Check for common issues
            if "no upstream" in e.stderr.lower():
                raise GitError(
                    "No upstream branch set",
                    suggestion="Use set_upstream=True to set upstream"
                )
            raise
    
    def pull(
        self,
        remote: str = 'origin',
        branch: Optional[str] = None,
        rebase: bool = False
    ) -> bool:
        """
        Pull changes from remote
        
        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            rebase: Use rebase instead of merge
        """
        self.ensure_repo()
        
        cmd = ['git', 'pull']
        
        if rebase:
            cmd.append('--rebase')
        
        cmd.append(remote)
        
        if branch:
            cmd.append(branch)
        
        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise
    
    # ========== Reset Operations ==========
    
    def reset(
        self,
        commit: str,
        mode: str = 'mixed'
    ) -> bool:
        """
        Reset to specific commit
        
        Args:
            commit: Commit hash or reference
            mode: Reset mode (soft, mixed, hard)
        """
        self.ensure_repo()
        
        valid_modes = ['soft', 'mixed', 'hard']
        if mode not in valid_modes:
            raise GitError(f"Invalid reset mode: {mode}")
        
        cmd = ['git', 'reset', f'--{mode}', commit]
        
        try:
            self._run_command(cmd, check=True)
            return True
        except GitCommandError:
            raise
    
    # ========== Init Operations ==========
    
    def init(self) -> bool:
        """Initialize new Git repository"""
        if self.is_repo():
            raise GitError("Already a Git repository")
        
        self._run_command(['git', 'init'], check=True)
        return True
    
    # ========== Internal Helpers ==========
    
    def _verify_git_installed(self) -> None:
        """Verify Git is installed"""
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=True,
                timeout=5
            )
        except FileNotFoundError:
            raise GitNotInstalledError()
        except subprocess.TimeoutExpired:
            raise GitError("Git command timed out during verification")
    
    def _run_command(
        self,
        cmd: List[str],
        check: bool = False,
        timeout: int = 30
    ) -> subprocess.CompletedProcess:
        """
        Run Git command with proper error handling
        
        Args:
            cmd: Command to run
            check: Raise on non-zero return code
            timeout: Command timeout in seconds
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            
            if check and result.returncode != 0:
                raise GitCommandError(
                    command=' '.join(cmd),
                    return_code=result.returncode,
                    stderr=result.stderr
                )
            
            return result
        
        except subprocess.TimeoutExpired:
            raise GitError(
                f"Command timed out after {timeout}s: {' '.join(cmd)}",
                suggestion="Check for hung processes or network issues"
            )
        except FileNotFoundError:
            raise GitNotInstalledError()
        except Exception as e:
            raise GitError(
                f"Command failed: {' '.join(cmd)}",
                details={"error": str(e)}
            )


# Singleton instance
_git_client: Optional[GitClient] = None


def get_git_client(working_dir: Optional[Path] = None) -> GitClient:
    """
    Get or create GitClient singleton
    
    Args:
        working_dir: Working directory (creates new instance if different)
    """
    global _git_client
    
    if _git_client is None or (working_dir and working_dir != _git_client.working_dir):
        _git_client = GitClient(working_dir)
    
    return _git_client