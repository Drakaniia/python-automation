import pytest
import subprocess
from pathlib import Path
from automation.core import GitClient

@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary git repository"""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    
    # Initialize git
    subprocess.run(['git', 'init'], cwd=repo, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], 
                  cwd=repo, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], 
                  cwd=repo, check=True)
    
    # Create initial commit
    (repo / 'README.md').write_text('# Test')
    subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], 
                  cwd=repo, check=True)
    
    yield repo

def test_full_workflow(temp_repo):
    """Test complete git workflow"""
    client = GitClient(temp_repo)
    
    # Verify repo state
    assert client.is_repo()
    assert client.current_branch() == 'master' or client.current_branch() == 'main'
    
    # Create new file
    (temp_repo / 'test.txt').write_text('Hello')
    
    # Stage and commit
    assert client.add(['test.txt'])
    assert client.commit('Add test file')
    
    # Verify commit
    commits = client.log(limit=1)
    assert len(commits) == 1
    assert 'Add test file' in commits[0]['message']