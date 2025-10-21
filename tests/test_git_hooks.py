"""
tests/test_git_hooks.py
Tests for Git hooks manager - Windows compatible version
"""
import pytest
import sys
from pathlib import Path
from automation.github.git_hooks import GitHooksManager


class TestGitHooksManager:
    """Test Git hooks management functionality"""
    
    def test_is_git_repo_true(self, temp_git_repo):
        """Test repository detection"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        assert manager.is_git_repo() is True
    
    def test_is_git_repo_false(self, temp_dir):
        """Test non-repository detection"""
        manager = GitHooksManager()
        manager.repo_path = temp_dir
        
        assert manager.is_git_repo() is False
    
    def test_install_hook_pre_commit(self, temp_git_repo, monkeypatch):
        """Test installing pre-commit hook"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        # Mock user input to skip prompts
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        result = manager.install_hook('pre-commit')
        
        hook_path = manager.hooks_dir / 'pre-commit'
        assert hook_path.exists()
        
        # Check executable on Unix-like systems only
        # Windows doesn't use Unix-style executable bits
        if sys.platform != 'win32':
            assert hook_path.stat().st_mode & 0o111  # Check executable
    
    def test_install_hook_pre_push(self, temp_git_repo, monkeypatch):
        """Test installing pre-push hook"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        result = manager.install_hook('pre-push')
        
        hook_path = manager.hooks_dir / 'pre-push'
        assert hook_path.exists()
    
    def test_install_unknown_hook(self, temp_git_repo, monkeypatch):
        """Test installing unknown hook type"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        monkeypatch.setattr('builtins.input', lambda _: '')
        
        result = manager.install_hook('unknown-hook')
        assert result is False
    
    def test_hook_overwrite_protection(self, temp_git_repo, monkeypatch):
        """Test that existing hooks are protected"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        # Install hook first time
        inputs = iter([''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        manager.install_hook('pre-commit')
        
        # Try to install again with 'n' response
        inputs = iter(['n', ''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = manager.install_hook('pre-commit')
        
        assert result is False
    
    def test_list_hooks(self, temp_git_repo, monkeypatch, capsys):
        """Test listing installed hooks"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        # Install a hook first
        monkeypatch.setattr('builtins.input', lambda _: '')
        manager.install_hook('pre-commit')
        
        # List hooks
        manager.list_hooks()
        
        captured = capsys.readouterr()
        assert 'pre-commit' in captured.out
    
    def test_hook_templates_exist(self):
        """Test that all hook templates are defined"""
        manager = GitHooksManager()
        
        expected_hooks = [
            'pre-commit',
            'pre-push',
            'commit-msg',
            'post-commit',
            'post-merge'
        ]
        
        for hook in expected_hooks:
            assert hook in manager.HOOK_TEMPLATES
            assert manager.HOOK_TEMPLATES[hook].startswith('#!/bin/sh')
    
    def test_install_all_hooks(self, temp_git_repo, monkeypatch):
        """Test installing all hooks at once"""
        manager = GitHooksManager()
        manager.repo_path = temp_git_repo
        manager.hooks_dir = temp_git_repo / '.git' / 'hooks'
        
        # Mock user confirmation
        inputs = iter(['y', ''])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        manager.install_all_hooks()
        
        # Check that hooks were created
        for hook_name in manager.HOOK_TEMPLATES.keys():
            hook_path = manager.hooks_dir / hook_name
            assert hook_path.exists()