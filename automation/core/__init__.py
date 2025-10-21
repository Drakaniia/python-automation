"""
automation/core/__init__.py
Core Git operations and utilities
"""

from automation.core.git_client import GitClient, get_git_client
from automation.core.exceptions import (
    AutomationError,
    GitError,
    GitCommandError,
    NotGitRepositoryError,
    NoRemoteError,
    GitNotInstalledError,
    UncommittedChangesError,
    ErrorSeverity,
    ExceptionHandler,
    handle_errors
)

__all__ = [
    'GitClient',
    'get_git_client',
    'AutomationError',
    'GitError',
    'GitCommandError',
    'NotGitRepositoryError',
    'NoRemoteError',
    'GitNotInstalledError',
    'UncommittedChangesError',
    'ErrorSeverity',
    'ExceptionHandler',
    'handle_errors'
]