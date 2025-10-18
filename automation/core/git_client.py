"""
Git Client Module
Centralized Git command execution with consistent error handling
"""
from typing import Optional, List, Dict, Tuple
import subprocess
from pathlib import Path
from datetime import datetime
import re


class GitError(Exception):
    """Git operation failed"""
    pass


class GitClient:
    """Centralized Git command execution with consistent settings"""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize Git client
        
        Args:
            repo_path: Path to repository. If None, uses current directory
        """
        self.repo_path = repo_path or Path.cwd()
        self.encoding = 'utf-8'
        self.error_handling = 'replace'
    
    def run(self, 
            args: List[str], 
            check: bool = True,
            capture: bool = True,
            input_text: Optional[str] = None) -> subprocess.CompletedProcess:
        """Execute git command with consistent settings
        
        Args:
            args: Git command arguments (without 'git' prefix)
            check: If True, raise exception on non-zero exit
            capture: If True, capture stdout/stderr
            input_text: Optional input text to send to command
            
        Returns:
            CompletedProcess instance
            
        Raises:
            GitError: If command fails and check=True
        """
        cmd = ['git'] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture,
                text=True,
                check=check,
                input=input_text,
                encoding=self.encoding,
                errors=self.error_handling
            )
            return result
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {' '.join(args)}\n{e.stderr}")
        except FileNotFoundError:
            raise GitError("Git is not installed or not in PATH")
    
    # ========== Repository Checks ==========
    
    def is_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            self.run(['rev-parse', '--is-inside-work-tree'], check=True)
            return True
        except GitError:
            return False
    
    def has_remote(self, remote_name: str = 'origin') -> bool:
        """Check if remote exists"""
        try:
            self.run(['remote', 'get-url', remote_name], check=True)
            return True
        except GitError:
            return False
    
    def is_clean(self) -> bool:
        """Check if working directory is clean"""
        status = self.status_porcelain()
        return not bool(status.strip())
    
    # ========== Status Operations ==========
    
    def status(self) -> str:
        """Get human-readable repository status"""
        return self.run(['status']).stdout
    
    def status_porcelain(self) -> str:
        """Get machine-readable status"""
        return self.run(['status', '--porcelain']).stdout
    
    def diff(self, cached: bool = False, files: Optional[List[str]] = None) -> str:
        """Get diff output
        
        Args:
            cached: If True, show staged changes
            files: Optional list of files to diff
        """
        args = ['diff']
        if cached:
            args.append('--cached')
        if files:
            args.extend(files)
        return self.run(args).stdout
    
    def diff_stat(self, cached: bool = False) -> Dict[str, int]:
        """Get diff statistics
        
        Returns:
            Dictionary with 'insertions', 'deletions', 'files_changed'
        """
        args = ['diff', '--stat']
        if cached:
            args.append('--cached')
        
        output = self.run(args).stdout
        
        stats = {'files_changed': 0, 'insertions': 0, 'deletions': 0}
        
        # Parse last line: "N files changed, M insertions(+), K deletions(-)"
        match = re.search(r'(\d+) file[s]? changed', output)
        if match:
            stats['files_changed'] = int(match.group(1))
        
        match = re.search(r'(\d+) insertion[s]?', output)
        if match:
            stats['insertions'] = int(match.group(1))
        
        match = re.search(r'(\d+) deletion[s]?', output)
        if match:
            stats['deletions'] = int(match.group(1))
        
        return stats
    
    # ========== Staging Operations ==========
    
    def add(self, files: Optional[List[str]] = None) -> bool:
        """Stage files
        
        Args:
            files: List of files to stage. If None, stages all changes
        """
        args = ['add']
        args.extend(files if files else ['.'])
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def reset(self, files: Optional[List[str]] = None) -> bool:
        """Unstage files
        
        Args:
            files: List of files to unstage. If None, unstages all
        """
        args = ['reset', 'HEAD']
        if files:
            args.extend(files)
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    # ========== Commit Operations ==========
    
    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """Create commit
        
        Args:
            message: Commit message
            allow_empty: Allow empty commits
        """
        args = ['commit', '-m', message]
        if allow_empty:
            args.append('--allow-empty')
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def amend(self, message: Optional[str] = None, no_edit: bool = False) -> bool:
        """Amend last commit
        
        Args:
            message: New commit message. If None, keeps existing
            no_edit: If True, don't change message
        """
        args = ['commit', '--amend']
        if message:
            args.extend(['-m', message])
        if no_edit:
            args.append('--no-edit')
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    # ========== Branch Operations ==========
    
    def current_branch(self) -> Optional[str]:
        """Get current branch name"""
        try:
            return self.run(['branch', '--show-current']).stdout.strip()
        except GitError:
            return None
    
    def list_branches(self, remote: bool = False) -> List[str]:
        """List branches
        
        Args:
            remote: If True, list remote branches
        """
        args = ['branch']
        if remote:
            args.append('-r')
        
        output = self.run(args).stdout
        branches = []
        for line in output.split('\n'):
            line = line.strip()
            if line:
                # Remove '* ' prefix for current branch
                branch = line.lstrip('* ').strip()
                branches.append(branch)
        return branches
    
    def create_branch(self, name: str, checkout: bool = True) -> bool:
        """Create new branch
        
        Args:
            name: Branch name
            checkout: If True, switch to new branch
        """
        args = ['checkout', '-b', name] if checkout else ['branch', name]
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def checkout(self, branch: str) -> bool:
        """Switch to branch"""
        try:
            self.run(['checkout', branch])
            return True
        except GitError:
            return False
    
    # ========== Remote Operations ==========
    
    def push(self, 
             remote: str = 'origin', 
             branch: Optional[str] = None,
             force: bool = False,
             set_upstream: bool = False) -> bool:
        """Push to remote
        
        Args:
            remote: Remote name
            branch: Branch name. If None, uses current branch
            force: Force push
            set_upstream: Set upstream tracking
        """
        args = ['push']
        if force:
            args.append('--force')
        if set_upstream:
            args.extend(['-u', remote, branch or self.current_branch()])
        else:
            args.append(remote)
            if branch:
                args.append(branch)
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def pull(self, rebase: bool = False) -> bool:
        """Pull from remote
        
        Args:
            rebase: Use rebase strategy
        """
        args = ['pull']
        if rebase:
            args.append('--rebase')
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def fetch(self, remote: str = 'origin', prune: bool = True) -> bool:
        """Fetch from remote
        
        Args:
            remote: Remote name
            prune: Remove deleted remote branches
        """
        args = ['fetch', remote]
        if prune:
            args.append('--prune')
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    def get_remote_url(self, remote: str = 'origin') -> Optional[str]:
        """Get remote URL"""
        try:
            return self.run(['remote', 'get-url', remote]).stdout.strip()
        except GitError:
            return None
    
    def set_remote_url(self, url: str, remote: str = 'origin') -> bool:
        """Set or update remote URL"""
        if self.has_remote(remote):
            args = ['remote', 'set-url', remote, url]
        else:
            args = ['remote', 'add', remote, url]
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    # ========== Log Operations ==========
    
    def log(self, 
            limit: int = 10, 
            format_str: str = '%H|%an|%ai|%s',
            file_path: Optional[str] = None) -> List[Dict[str, str]]:
        """Get commit log
        
        Args:
            limit: Maximum commits to retrieve
            format_str: Git log format string
            file_path: Optional file path to filter commits
        """
        args = ['log', f'-{limit}', f'--pretty=format:{format_str}']
        if file_path:
            args.extend(['--', file_path])
        
        try:
            result = self.run(args)
        except GitError:
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
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
    
    def show_commit(self, commit_hash: str, stat: bool = False) -> str:
        """Show commit details"""
        args = ['show', commit_hash]
        if stat:
            args.append('--stat')
        return self.run(args).stdout
    
    def get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in commit"""
        output = self.run(['show', '--name-only', '--pretty=format:', commit_hash]).stdout
        return [f.strip() for f in output.strip().split('\n') if f.strip()]
    
    # ========== History Operations ==========
    
    def reset_hard(self, commit_hash: str) -> bool:
        """Hard reset to commit (DESTRUCTIVE)"""
        try:
            self.run(['reset', '--hard', commit_hash])
            return True
        except GitError:
            return False
    
    def reset_soft(self, commit_hash: str) -> bool:
        """Soft reset to commit (keeps changes staged)"""
        try:
            self.run(['reset', '--soft', commit_hash])
            return True
        except GitError:
            return False
    
    def revert(self, commit_hash: str, no_commit: bool = False) -> bool:
        """Revert commit
        
        Args:
            commit_hash: Commit to revert
            no_commit: Don't create revert commit automatically
        """
        args = ['revert', commit_hash]
        if no_commit:
            args.append('--no-commit')
        try:
            self.run(args)
            return True
        except GitError:
            return False
    
    # ========== Utility Methods ==========
    
    def get_config(self, key: str, scope: str = 'local') -> Optional[str]:
        """Get git config value
        
        Args:
            key: Config key (e.g., 'user.name')
            scope: Config scope ('local', 'global', 'system')
        """
        try:
            return self.run(['config', f'--{scope}', key]).stdout.strip()
        except GitError:
            return None
    
    def set_config(self, key: str, value: str, scope: str = 'local') -> bool:
        """Set git config value"""
        try:
            self.run(['config', f'--{scope}', key, value])
            return True
        except GitError:
            return False
    
    def get_root_dir(self) -> Optional[Path]:
        """Get repository root directory"""
        try:
            root = self.run(['rev-parse', '--show-toplevel']).stdout.strip()
            return Path(root)
        except GitError:
            return None
    
    def get_git_dir(self) -> Optional[Path]:
        """Get .git directory path"""
        try:
            git_dir = self.run(['rev-parse', '--git-dir']).stdout.strip()
            return Path(git_dir)
        except GitError:
            return None
    
    def file_exists_in_commit(self, file_path: str, commit_hash: str = 'HEAD') -> bool:
        """Check if file exists in specific commit"""
        try:
            self.run(['cat-file', '-e', f'{commit_hash}:{file_path}'])
            return True
        except GitError:
            return False
    
    def get_file_content(self, file_path: str, commit_hash: str = 'HEAD') -> Optional[str]:
        """Get file content from specific commit"""
        try:
            return self.run(['show', f'{commit_hash}:{file_path}']).stdout
        except GitError:
            return None


# Convenience function for quick access
def get_git_client(repo_path: Optional[Path] = None) -> GitClient:
    """Get GitClient instance"""
    return GitClient(repo_path)


if __name__ == '__main__':
    # Demo GitClient functionality
    print("Demo: GitClient\n")
    
    client = GitClient()
    
    print("Repository Information:")
    print(f"  Is repo: {client.is_repo()}")
    print(f"  Current branch: {client.current_branch()}")
    print(f"  Is clean: {client.is_clean()}")
    print(f"  Root dir: {client.get_root_dir()}")
    
    if client.is_repo():
        print("\nRecent commits:")
        commits = client.log(limit=5)
        for commit in commits:
            print(f"  {commit['short_hash']} - {commit['message'][:50]}")
        
        print("\nRemote information:")
        remote_url = client.get_remote_url()
        print(f"  Origin URL: {remote_url}")
        
        print("\nDiff statistics:")
        stats = client.diff_stat()
        print(f"  Files changed: {stats['files_changed']}")
        print(f"  Insertions: {stats['insertions']}")
        print(f"  Deletions: {stats['deletions']}")