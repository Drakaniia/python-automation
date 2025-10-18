"""
Core utilities for automation system
"""
from automation.core.config import Config, get_config, get, set_value
from automation.core.git_client import GitClient, GitError, get_git_client
from automation.core.logger import (
    MagicLogger, get_logger, 
    debug, info, warning, error, success, step
)

__all__ = [
    'Config', 'get_config', 'get', 'set_value',
    'GitClient', 'GitError', 'get_git_client',
    'MagicLogger', 'get_logger',
    'debug', 'info', 'warning', 'error', 'success', 'step'
]