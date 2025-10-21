"""
GitHub Module Package
Contains modular Git operation handlers
"""

from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.github.commit_summarizer import CommitSummarizer
from automation.github.git_hooks import GitHooksManager
from automation.github.git_visualizations import GitVisualizations

__all__ = [
    'GitStatus',
    'GitLog',
    'GitPush',
    'GitInitializer',
    'GitRecover',
    'CommitSummarizer',
    'GitHooksManager',
    'GitVisualizations'
]