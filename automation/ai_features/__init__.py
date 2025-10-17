"""
AI Features Package
Contains AI-powered automation modules for documentation and changelog generation
"""

from automation.ai_features.readme_whisperer import ReadmeWhisperer
from automation.ai_features.commit_summarizer import CommitSummarizer

__all__ = [
    'ReadmeWhisperer',
    'CommitSummarizer'
]