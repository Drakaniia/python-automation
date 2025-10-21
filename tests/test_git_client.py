

# ============================================================
# tests/test_git_client.py
# ============================================================
"""Test GitClient functionality"""
import pytest
from automation.core.git_client import GitClient
from automation.core.exceptions import (
    NotGitRepositoryError,
    GitCommandError,
    NoRemoteError
)


class TestGitClientBasics:
    """Test basic Git client functionality"""
    
    def test_is_repo_true(self, git_client):
        """Test repository detection - positive"""
        assert git_client.is_repo() is True
    
    def test_is_repo_false(self, temp_dir):
        """Test repository detection - negative"""
        client = GitClient(temp_dir)
        assert client.is_repo() is False
    
    def test_ensure_repo_success(self, git_client):
        """Test ensure_repo with valid repo"""
        git_client.ensure_repo()  # Should not raise
    
    def test_ensure_repo_failure(self, temp_dir):
        """Test ensure_repo with non-repo"""
        client = GitClient(temp_dir)
        with pytest.raises(NotGitRepositoryError):
            client.ensure_repo()
    
    def test_current_branch(self, git_client):
        """Test getting current branch"""
        branch = git_client.current_branch()
        assert branch in ['main', 'master']


class TestGitClientStatus:
    """Test status operations"""
    
    def test_status_clean(self, git_client):
        """Test status on clean repository"""
        status = git_client.status()
        assert 'working tree clean' in status.lower()
    
    def test_status_with_changes(self, git_client, temp_git_repo):
        """Test status with uncommitted changes"""
        # Create new file
        (temp_git_repo / 'new_file.txt').write_text('content')
        
        status = git_client.status()
        assert 'new_file.txt' in status
    
    def test_status_porcelain(self, git_client, temp_git_repo):
        """Test machine-readable status"""
        # Create new file
        (temp_git_repo / 'new_file.txt').write_text('content')
        
        status = git_client.status(porcelain=True)
        assert '?? new_file.txt' in status
    
    def test_has_uncommitted_changes_false(self, git_client):
        """Test has_uncommitted_changes - clean"""
        assert git_client.has_uncommitted_changes() is False
    
    def test_has_uncommitted_changes_true(self, git_client, temp_git_repo):
        """Test has_uncommitted_changes - dirty"""
        (temp_git_repo / 'new_file.txt').write_text('content')
        assert git_client.has_uncommitted_changes() is True


class TestGitClientCommits:
    """Test commit operations"""
    
    def test_add_all(self, git_client, temp_git_repo):
        """Test staging all files"""
        (temp_git_repo / 'file1.txt').write_text('content1')
        (temp_git_repo / 'file2.txt').write_text('content2')
        
        result = git_client.add()
        assert result is True
    
    def test_add_specific_files(self, git_client, temp_git_repo):
        """Test staging specific files"""
        (temp_git_repo / 'file1.txt').write_text('content1')
        (temp_git_repo / 'file2.txt').write_text('content2')
        
        result = git_client.add(['file1.txt'])
        assert result is True
    
    def test_commit_success(self, git_client, temp_git_repo):
        """Test successful commit"""
        (temp_git_repo / 'file.txt').write_text('content')
        git_client.add()
        
        result = git_client.commit('Test commit')
        assert result is True
    
    def test_commit_empty_message(self, git_client):
        """Test commit with empty message"""
        from automation.core.exceptions import GitError
        
        with pytest.raises(GitError, match="empty"):
            git_client.commit('')
    
    def test_commit_amend(self, git_client, temp_git_repo):
        """Test amending previous commit"""
        (temp_git_repo / 'file.txt').write_text('content')
        git_client.add()
        git_client.commit('Original message')
        
        # Amend
        (temp_git_repo / 'file.txt').write_text('updated')
        git_client.add()
        result = git_client.commit('Amended message', amend=True)
        
        assert result is True


class TestGitClientLog:
    """Test log operations"""
    
    def test_log_single_commit(self, git_client):
        """Test getting commit history"""
        commits = git_client.log(limit=1)
        
        assert len(commits) == 1
        assert 'hash' in commits[0]
        assert 'author' in commits[0]
        assert 'message' in commits[0]
    
    def test_log_multiple_commits(self, git_client, temp_git_repo):
        """Test getting multiple commits"""
        # Create additional commits
        for i in range(3):
            (temp_git_repo / f'file{i}.txt').write_text(f'content{i}')
            git_client.add()
            git_client.commit(f'Commit {i}')
        
        commits = git_client.log(limit=5)
        assert len(commits) >= 3


class TestGitClientRemotes:
    """Test remote operations"""
    
    def test_has_remote_false(self, git_client):
        """Test has_remote when no remote exists"""
        assert git_client.has_remote() is False
    
    def test_get_remote_url_none(self, git_client):
        """Test get_remote_url with no remote"""
        assert git_client.get_remote_url() is None
    
    def test_add_remote(self, git_client):
        """Test adding remote"""
        result = git_client.add_remote('origin', 'https://github.com/test/repo.git')
        assert result is True
        assert git_client.has_remote('origin') is True
    
    def test_push_no_remote(self, git_client):
        """Test push without remote configured"""
        with pytest.raises(NoRemoteError):
            git_client.push()


class TestGitClientInit:
    """Test repository initialization"""
    
    def test_init_new_repo(self, temp_dir):
        """Test initializing new repository"""
        client = GitClient(temp_dir)
        result = client.init()
        
        assert result is True
        assert client.is_repo() is True
    
    def test_init_existing_repo(self, git_client):
        """Test init on existing repository"""
        from automation.core.exceptions import GitError
        
        with pytest.raises(GitError, match="Already"):
            git_client.init()


class TestGitClientReset:
    """Test reset operations"""
    
    def test_reset_soft(self, git_client, temp_git_repo):
        """Test soft reset"""
        # Create second commit
        (temp_git_repo / 'file.txt').write_text('content')
        git_client.add()
        git_client.commit('Second commit')
        
        # Get first commit hash
        commits = git_client.log(limit=2)
        first_commit = commits[1]['hash']
        
        # Reset
        result = git_client.reset(first_commit, mode='soft')
        assert result is True
    
    def test_reset_invalid_mode(self, git_client):
        """Test reset with invalid mode"""
        from automation.core.exceptions import GitError
        
        with pytest.raises(GitError, match="Invalid"):
            git_client.reset('HEAD', mode='invalid')


class TestGitClientErrors:
    """Test error handling"""
    
    def test_command_timeout(self, git_client, mock_subprocess):
        """Test command timeout handling"""
        import subprocess
        from automation.core.exceptions import GitError
        
        mock_subprocess.side_effect = subprocess.TimeoutExpired('git', 1)
        
        with pytest.raises(GitError, match="timed out"):
            git_client._run_command(['git', 'status'], timeout=1)
    
    def test_git_not_installed(self, mock_subprocess):
        """Test Git not installed error"""
        from automation.core.exceptions import GitNotInstalledError
        
        mock_subprocess.side_effect = FileNotFoundError()
        
        with pytest.raises(GitNotInstalledError):
            client = GitClient()
            client._run_command(['git', 'status'])
