import pytest
from unittest.mock import Mock, patch
from automation.github.git_push import GitPush
from automation.core import GitError

@pytest.fixture
def mock_git_client():
    """Create mock GitClient"""
    with patch('automation.github.git_push.get_git_client') as mock:
        client = Mock()
        client.is_repo.return_value = True
        client.add.return_value = True
        client.commit.return_value = True
        client.push.return_value = True
        mock.return_value = client
        yield client

@pytest.fixture
def git_push(mock_git_client):
    """Create GitPush instance with mocked dependencies"""
    return GitPush()

def test_push_success(git_push, mock_git_client, monkeypatch):
    """Test successful push operation"""
    # Mock user input
    monkeypatch.setattr('builtins.input', lambda _: 'Test commit')
    
    # Execute
    git_push.push()
    
    # Verify
    mock_git_client.add.assert_called_once()
    mock_git_client.commit.assert_called_once_with('Test commit')
    mock_git_client.push.assert_called_once()

def test_push_not_a_repo(git_push, mock_git_client, monkeypatch):
    """Test push in non-git directory"""
    mock_git_client.is_repo.return_value = False
    monkeypatch.setattr('builtins.input', lambda _: '')
    
    # Should return early without error
    git_push.push()
    
    mock_git_client.add.assert_not_called()

def test_push_empty_message(git_push, mock_git_client, monkeypatch):
    """Test push with empty commit message"""
    monkeypatch.setattr('builtins.input', lambda _: '')
    
    git_push.push()
    
    mock_git_client.commit.assert_not_called()

def test_push_git_error(git_push, mock_git_client, monkeypatch):
    """Test push when git command fails"""
    monkeypatch.setattr('builtins.input', lambda _: 'Test commit')
    mock_git_client.push.side_effect = GitError("Network error")
    
    # Should handle error gracefully
    git_push.push()
    
    mock_git_client.add.assert_called_once()