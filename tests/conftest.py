"""
tests/conftest.py
Pytest configuration and fixtures for comprehensive testing
"""
import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from automation.core.git_client import GitClient
from automation.core.exceptions import ExceptionHandler


@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def temp_git_repo(temp_dir):
    """Create temporary Git repository"""
    # Initialize git
    subprocess.run(['git', 'init'], cwd=temp_dir, check=True)
    subprocess.run(
        ['git', 'config', 'user.email', 'test@test.com'],
        cwd=temp_dir,
        check=True
    )
    subprocess.run(
        ['git', 'config', 'user.name', 'Test User'],
        cwd=temp_dir,
        check=True
    )
    
    # Create initial commit
    readme = temp_dir / 'README.md'
    readme.write_text('# Test Repository')
    
    subprocess.run(['git', 'add', '.'], cwd=temp_dir, check=True)
    subprocess.run(
        ['git', 'commit', '-m', 'Initial commit'],
        cwd=temp_dir,
        check=True
    )
    
    yield temp_dir


@pytest.fixture
def git_client(temp_git_repo):
    """Create GitClient instance for testing"""
    return GitClient(temp_git_repo)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing error conditions"""
    with patch('subprocess.run') as mock:
        yield mock
