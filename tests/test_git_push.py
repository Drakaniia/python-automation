"""
tests/test_git_push.py
Updated tests for enhanced GitPush with retry functionality
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from automation.github.git_push import GitPush, GitPushRetry, PushConfig, PushStrategy
from automation.core.exceptions import GitError, GitCommandError
import subprocess


@pytest.fixture
def mock_git_client():
    """Create mock GitClient"""
    with patch('automation.github.git_push.get_git_client') as mock:
        client = Mock()
        client.is_repo.return_value = True
        client.has_remote.return_value = True
        client.has_uncommitted_changes.return_value = True
        client.status.return_value = "M  file.txt\n"
        client.current_branch.return_value = "main"
        client.add.return_value = True
        client.commit.return_value = True
        
        # Mock _run_command to simulate successful push
        def mock_run_command(cmd, check=True, timeout=30):
            result = Mock()
            result.returncode = 0
            result.stdout = "Everything up-to-date"
            result.stderr = ""
            return result
        
        client._run_command = mock_run_command
        mock.return_value = client
        yield client


@pytest.fixture
def git_push(mock_git_client):
    """Create GitPush instance with mocked dependencies"""
    return GitPush()


@pytest.fixture
def git_push_retry(mock_git_client):
    """Create GitPushRetry instance"""
    return GitPushRetry()


class TestPushConfig:
    """Test push configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = PushConfig()
        
        assert config.max_retries == 3
        assert config.retry_delay == 2
        assert config.network_timeout == 30
        assert config.enable_auto_hooks_bypass is True
        assert config.enable_auto_upstream is True
    
    def test_strategies_count(self):
        """Test that all strategies are defined"""
        config = PushConfig()
        
        assert len(config.strategies) == 6
        assert config.strategies[0].name == "normal"
        assert config.strategies[-1].name == "force"
    
    def test_destructive_flags(self):
        """Test destructive strategies are marked"""
        config = PushConfig()
        
        # Force strategies should be destructive
        force_strategies = [s for s in config.strategies if 'force' in s.name]
        for strategy in force_strategies:
            assert strategy.is_destructive is True
            assert strategy.requires_confirmation is True


class TestPushStrategy:
    """Test push strategy class"""
    
    def test_strategy_creation(self):
        """Test creating a strategy"""
        strategy = PushStrategy(
            name="test",
            flags=["--test"],
            description="Test strategy",
            requires_confirmation=True,
            is_destructive=True
        )
        
        assert strategy.name == "test"
        assert strategy.flags == ["--test"]
        assert strategy.requires_confirmation is True
        assert strategy.is_destructive is True


class TestGitPushRetry:
    """Test GitPushRetry functionality"""
    
    def test_init(self, git_push_retry):
        """Test initialization"""
        assert git_push_retry.git is not None
        assert git_push_retry.config is not None
        assert git_push_retry.attempt_count == 0
    
    def test_pre_push_checks_success(self, git_push_retry, mock_git_client):
        """Test pre-push checks pass"""
        result = git_push_retry._pre_push_checks()
        
        assert result is True
        mock_git_client.is_repo.assert_called()
        mock_git_client.has_remote.assert_called()
    
    def test_pre_push_checks_failure(self, git_push_retry, mock_git_client, monkeypatch):
        """Test pre-push checks fail"""
        mock_git_client.is_repo.return_value = False
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        result = git_push_retry._pre_push_checks()
        
        assert result is False
    
    def test_has_changes_true(self, git_push_retry, mock_git_client):
        """Test detecting uncommitted changes"""
        mock_git_client.has_uncommitted_changes.return_value = True
        
        assert git_push_retry._has_changes() is True
    
    def test_has_changes_false(self, git_push_retry, mock_git_client):
        """Test no uncommitted changes"""
        mock_git_client.has_uncommitted_changes.return_value = False
        
        assert git_push_retry._has_changes() is False
    
    def test_stage_and_commit_success(self, git_push_retry, mock_git_client):
        """Test staging and committing"""
        result = git_push_retry._stage_and_commit("Test commit")
        
        assert result is True
        mock_git_client.add.assert_called_once()
        mock_git_client.commit.assert_called_once_with("Test commit")
    
    def test_stage_and_commit_failure(self, git_push_retry, mock_git_client):
        """Test staging fails"""
        mock_git_client.add.side_effect = GitError("Add failed")
        
        result = git_push_retry._stage_and_commit("Test commit")
        
        assert result is False
    
    def test_try_push_strategy_success(self, git_push_retry, mock_git_client):
        """Test successful push with strategy"""
        strategy = PushStrategy("normal", [], "Standard push")
        
        success, error = git_push_retry._try_push_strategy(strategy, "origin", "main")
        
        assert success is True
        assert error is None
    
    def test_try_push_strategy_failure(self, git_push_retry, mock_git_client):
        """Test failed push with strategy"""
        strategy = PushStrategy("normal", [], "Standard push")
        
        # Make _run_command raise an error
        def failing_run_command(cmd, check=True, timeout=30):
            raise GitCommandError(
                command=' '.join(cmd),
                return_code=1,
                stderr="pre-push hook declined"
            )
        
        mock_git_client._run_command = failing_run_command
        
        success, error = git_push_retry._try_push_strategy(strategy, "origin", "main")
        
        assert success is False
        assert error is not None
    
    def test_analyze_error_hook_failure(self, git_push_retry):
        """Test analyzing hook error"""
        error = GitCommandError("git push", 1, "pre-push hook declined")
        
        should_continue, wait_time = git_push_retry._analyze_error_and_decide(
            error, 1, PushStrategy("normal", [], "test")
        )
        
        assert should_continue is True
        assert wait_time == 0  # No wait for hook errors
    
    def test_analyze_error_network_failure(self, git_push_retry):
        """Test analyzing network error"""
        error = GitCommandError("git push", 1, "network timeout")
        
        should_continue, wait_time = git_push_retry._analyze_error_and_decide(
            error, 1, PushStrategy("normal", [], "test")
        )
        
        assert should_continue is True
        assert wait_time > 0  # Should have backoff
    
    def test_analyze_error_auth_failure(self, git_push_retry):
        """Test analyzing authentication error"""
        error = GitCommandError("git push", 1, "authentication failed")
        
        should_continue, wait_time = git_push_retry._analyze_error_and_decide(
            error, 1, PushStrategy("normal", [], "test")
        )
        
        assert should_continue is False  # Don't retry auth errors
    
    def test_confirm_destructive_operation_yes(self, git_push_retry, monkeypatch):
        """Test confirming destructive operation"""
        monkeypatch.setattr('builtins.input', lambda _: 'YES')
        
        strategy = PushStrategy("force", ["--force"], "Force push", 
                               requires_confirmation=True, is_destructive=True)
        
        result = git_push_retry._confirm_destructive_operation(strategy)
        
        assert result is True
    
    def test_confirm_destructive_operation_no(self, git_push_retry, monkeypatch):
        """Test declining destructive operation"""
        monkeypatch.setattr('builtins.input', lambda _: 'no')
        
        strategy = PushStrategy("force", ["--force"], "Force push",
                               requires_confirmation=True, is_destructive=True)
        
        result = git_push_retry._confirm_destructive_operation(strategy)
        
        assert result is False
    
    def test_extract_error_message(self, git_push_retry):
        """Test extracting clean error messages"""
        stderr = "! [rejected] main -> main (pre-push hook declined)\nerror: failed to push"
        
        message = git_push_retry._extract_error_message(stderr)
        
        assert "rejected" in message or "error" in message
        assert len(message) <= 100  # Should be truncated
    
    def test_push_with_retry_success(self, git_push_retry, mock_git_client, monkeypatch):
        """Test successful push with retry system"""
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        result = git_push_retry.push_with_retry(
            commit_message="Test commit",
            remote="origin",
            branch="main"
        )
        
        assert result is True
        assert git_push_retry.attempt_count >= 1


class TestGitPushBasic:
    """Test basic GitPush functionality"""
    
    def test_init(self, git_push):
        """Test GitPush initialization"""
        assert git_push.git is not None
        assert git_push.push_retry is not None
    
    def test_has_changes(self, git_push, mock_git_client):
        """Test checking for changes"""
        mock_git_client.has_uncommitted_changes.return_value = True
        
        assert git_push._has_changes() is True
    
    def test_show_changes_summary(self, git_push, mock_git_client):
        """Test showing changes summary"""
        mock_git_client.status.return_value = "M  file.txt\n?? new.txt\nD  old.txt"
        
        # Should not raise
        git_push._show_changes_summary()
    
    def test_get_commit_message_valid(self, git_push, monkeypatch):
        """Test getting valid commit message"""
        monkeypatch.setattr('builtins.input', lambda _: 'Valid commit message')
        
        message = git_push._get_commit_message()
        
        assert message == 'Valid commit message'
    
    def test_get_commit_message_empty(self, git_push, monkeypatch):
        """Test getting empty commit message"""
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        message = git_push._get_commit_message()
        
        assert message is None
    
    def test_get_commit_message_too_short(self, git_push, monkeypatch):
        """Test commit message too short"""
        inputs = iter(['ab', 'n'])  # Short message, then decline retry
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        message = git_push._get_commit_message()
        
        assert message is None


class TestGitPushIntegration:
    """Integration tests for push workflow"""
    
    def test_push_success_flow(self, git_push, mock_git_client, monkeypatch):
        """Test complete successful push flow"""
        # Mock inputs
        inputs = iter(['Test commit message', ''])  # Commit message, then Enter
        monkeypatch.setattr('builtins.input', lambda _: next(inputs, ''))
        
        # Mock has changes
        mock_git_client.has_uncommitted_changes.return_value = True
        
        # Execute - should complete without errors
        git_push.push(dry_run=False)
        
        # Verify add and commit were called
        assert mock_git_client.add.called
        assert mock_git_client.commit.called
    
    def test_push_no_changes(self, git_push, mock_git_client, monkeypatch):
        """Test push with no changes"""
        monkeypatch.setattr('builtins.input', lambda _: '')
        mock_git_client.has_uncommitted_changes.return_value = False
        
        # Should return early
        git_push.push()
        
        # Should not call add/commit
        mock_git_client.add.assert_not_called()
        mock_git_client.commit.assert_not_called()
    
    def test_push_dry_run(self, git_push, mock_git_client, monkeypatch):
        """Test dry run mode"""
        monkeypatch.setattr('builtins.input', lambda _: 'Test commit')
        mock_git_client.has_uncommitted_changes.return_value = True
        
        git_push.push(dry_run=True)
        
        # Should not execute actual push
        mock_git_client.add.assert_not_called()
    
    def test_push_not_a_repo(self, git_push, mock_git_client, monkeypatch):
        """Test push in non-git directory"""
        mock_git_client.is_repo.return_value = False
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        # Should handle gracefully
        git_push.push()
        
        mock_git_client.add.assert_not_called()


class TestErrorRecovery:
    """Test error recovery scenarios"""
    
    def test_recover_from_hook_failure(self, git_push_retry, mock_git_client, monkeypatch):
        """Test recovering from hook failure"""
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        attempt = [0]
        
        def mock_run_with_hook_failure(cmd, check=True, timeout=30):
            attempt[0] += 1
            if attempt[0] == 1:
                # First attempt fails with hook
                raise GitCommandError("git push", 1, "pre-push hook declined")
            else:
                # Second attempt succeeds
                result = Mock()
                result.returncode = 0
                result.stdout = "Success"
                return result
        
        mock_git_client._run_command = mock_run_with_hook_failure
        
        result = git_push_retry.push_with_retry(
            commit_message="Test",
            remote="origin",
            branch="main"
        )
        
        # Should succeed on retry
        assert result is True
        assert attempt[0] >= 2  # At least 2 attempts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])