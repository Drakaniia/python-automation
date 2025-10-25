"""
GitHub Module Package
Contains modular Git operation handlers
UPDATED: Now exports ChangelogGenerator instead of CommitSummarizer
"""

from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.github.changelog_generator import ChangelogGenerator

__all__ = [
    'GitStatus',
    'GitLog',
    'GitPush',
    'GitInitializer',
    'GitRecover',
    'ChangelogGenerator',
]