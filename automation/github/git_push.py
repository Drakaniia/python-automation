"""
Git Push Module
Handles push operations with improved error handling and logging
"""
from automation.core import get_git_client, get_logger, get_config, GitError

logger = get_logger()

class GitPush:
    """Handles git push and commit operations"""
    
    def __init__(self):
        self.git = get_git_client()
        self.config = get_config()
    
    def push(self):
        """Add, commit, and push changes to remote"""
        self._display_header()
        
        # Validate repository
        if not self._validate_repo():
            return
        
        # Get commit message
        commit_msg = self._get_commit_message()
        if not commit_msg:
            return
        
        # Execute push workflow
        try:
            self._stage_files()
            self._create_commit(commit_msg)
            self._push_to_remote()
            logger.success("Push completed successfully!")
        except GitError as e:
            logger.error(f"Push failed: {e}")
        finally:
            input("\nPress Enter to continue...")
    
    def _display_header(self):
        """Display operation header"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH")
        print("="*70 + "\n")
    
    def _validate_repo(self) -> bool:
        """Validate git repository"""
        if not self.git.is_repo():
            logger.error("Not a git repository. Initialize git first.")
            input("\nPress Enter to continue...")
            return False
        return True
    
    def _get_commit_message(self) -> str:
        """Get commit message from user"""
        max_length = self.config.get('limits.max_commit_message_length', 72)
        
        commit_msg = input("Enter commit message: ").strip()
        
        if not commit_msg:
            logger.error("Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return ""
        
        if len(commit_msg) > max_length:
            logger.warning(f"Message is long ({len(commit_msg)} chars). "
                         f"Consider keeping it under {max_length} chars.")
        
        return commit_msg
    
    def _stage_files(self):
        """Stage all changes"""
        logger.step("Staging files")
        
        if not self.git.add():
            raise GitError("Failed to stage files")
        
        logger.success("Files staged")
    
    def _create_commit(self, message: str):
        """Create commit with message"""
        logger.step("Creating commit")
        
        if not self.git.commit(message):
            raise GitError("Failed to create commit")
        
        logger.success(f"Commit created: {message[:50]}")
    
    def _push_to_remote(self):
        """Push to remote repository"""
        logger.step("Pushing to remote")
        
        remote = self.config.get('git.default_remote', 'origin')
        
        if not self.git.push(remote=remote):
            raise GitError("Failed to push to remote")
        
        logger.success(f"Pushed to {remote}")