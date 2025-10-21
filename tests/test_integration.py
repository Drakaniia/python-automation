# ============================================================
# tests/test_integration.py
# ============================================================
"""Integration tests for full workflows"""
import pytest
from automation.core.git_client import GitClient


class TestFullWorkflow:
    """Test complete Git workflow"""
    
    def test_init_add_commit_workflow(self, temp_dir):
        """Test full workflow: init -> add -> commit"""
        client = GitClient(temp_dir)
        
        # Initialize
        client.init()
        assert client.is_repo()
        
        # Configure git
        import subprocess
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], 
                      cwd=temp_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], 
                      cwd=temp_dir, check=True)
        
        # Create file
        (temp_dir / 'README.md').write_text('# Test')
        
        # Add and commit
        client.add()
        client.commit('Initial commit')
        
        # Verify
        commits = client.log(limit=1)
        assert len(commits) == 1
        assert 'Initial commit' in commits[0]['message']
    
    def test_multi_commit_workflow(self, git_client, temp_git_repo):
        """Test multiple commits workflow"""
        # Create multiple commits
        for i in range(3):
            file_path = temp_git_repo / f'file{i}.txt'
            file_path.write_text(f'Content {i}')
            
            git_client.add([file_path.name])
            git_client.commit(f'Add file {i}')
        
        # Verify history
        commits = git_client.log(limit=5)
        assert len(commits) >= 3
        
        # Verify we can access specific commits
        assert any('Add file 0' in c['message'] for c in commits)


class TestErrorRecovery:
    """Test error recovery scenarios"""
    
    def test_recover_from_failed_push(self, git_client):
        """Test recovering from failed push"""
        from automation.core.exceptions import NoRemoteError
        
        # Try to push without remote
        with pytest.raises(NoRemoteError):
            git_client.push()
        
        # Add remote and retry
        git_client.add_remote('origin', 'https://github.com/test/repo.git')
        assert git_client.has_remote()
        
        # Now has_remote check should pass
        # (actual push would fail without valid repo, but that's expected)

