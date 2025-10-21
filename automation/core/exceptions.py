"""
automation/core/exceptions.py
Exception hierarchy and error handling utilities
"""
from enum import Enum
from typing import Optional, Dict, Any, Tuple, Callable
import functools
import traceback


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AutomationError(Exception):
    """Base exception for all automation errors"""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.details = details or {}
        self.suggestion = suggestion
    
    def display(self) -> str:
        """Format error for display"""
        lines = [
            f"\n{'='*70}",
            f"{self.severity.value}: {self.message}",
            f"{'='*70}"
        ]
        
        if self.details:
            lines.append("\nDetails:")
            for key, value in self.details.items():
                lines.append(f"  {key}: {value}")
        
        if self.suggestion:
            lines.append(f"\n💡 Suggestion: {self.suggestion}")
        
        lines.append(f"{'='*70}\n")
        
        return '\n'.join(lines)


class GitError(AutomationError):
    """Base class for Git-related errors"""
    pass


class GitCommandError(GitError):
    """Error executing Git command"""
    
    def __init__(self, command: str, return_code: int, stderr: str = ""):
        self.command = command
        self.return_code = return_code
        self.stderr = stderr
        
        message = f"Git command failed: {command}"
        details = {
            "command": command,
            "return_code": return_code,
            "stderr": stderr
        }
        
        # Generate helpful suggestions
        suggestion = self._generate_suggestion(stderr)
        
        super().__init__(message, details=details, suggestion=suggestion)
    
    def _generate_suggestion(self, stderr: str) -> str:
        """Generate helpful suggestion based on error"""
        stderr_lower = stderr.lower()
        
        if "not a git repository" in stderr_lower:
            return "Initialize Git with: git init"
        elif "remote" in stderr_lower and "not found" in stderr_lower:
            return "Configure remote with: git remote add origin <url>"
        elif "permission denied" in stderr_lower:
            return "Check file permissions or SSH keys"
        elif "conflict" in stderr_lower:
            return "Resolve merge conflicts before continuing"
        elif "up to date" in stderr_lower or "up-to-date" in stderr_lower:
            return "Nothing to push - repository is up to date"
        elif "no upstream" in stderr_lower or "no tracking" in stderr_lower:
            return "Set upstream with: git push --set-upstream origin <branch>"
        else:
            return "Check git status and try again"


class NotGitRepositoryError(GitError):
    """Not in a Git repository"""
    
    def __init__(self, path: str = "."):
        super().__init__(
            f"Not a Git repository: {path}",
            suggestion="Initialize repository with: git init"
        )


class NoRemoteError(GitError):
    """No remote configured"""
    
    def __init__(self, remote_name: str = "origin"):
        super().__init__(
            f"No remote '{remote_name}' configured",
            suggestion=f"Add remote with: git remote add {remote_name} <url>"
        )


class GitNotInstalledError(GitError):
    """Git is not installed or not in PATH"""
    
    def __init__(self):
        super().__init__(
            "Git is not installed or not found in PATH",
            severity=ErrorSeverity.CRITICAL,
            suggestion="Install Git from: https://git-scm.com/downloads"
        )


class UncommittedChangesError(GitError):
    """Uncommitted changes prevent operation"""
    
    def __init__(self, operation: str):
        super().__init__(
            f"Cannot {operation}: uncommitted changes exist",
            suggestion="Commit or stash changes before continuing"
        )


class ExceptionHandler:
    """Centralized exception handling"""
    
    @staticmethod
    def handle(error: Exception, exit_on_critical: bool = False) -> None:
        """Handle and display exception"""
        if isinstance(error, AutomationError):
            print(error.display())
            
            if exit_on_critical and error.severity == ErrorSeverity.CRITICAL:
                import sys
                sys.exit(1)
        else:
            # Wrap unexpected errors
            wrapped = AutomationError(
                str(error),
                severity=ErrorSeverity.ERROR,
                details={"type": type(error).__name__},
                suggestion="Check logs for details"
            )
            print(wrapped.display())
            
            # Print traceback for unexpected errors
            if isinstance(error, Exception):
                traceback.print_exc()
    
    @staticmethod
    def safe_execute(func: Callable, *args, **kwargs) -> Tuple[Any, Optional[AutomationError]]:
        """Execute function safely and return (result, error)"""
        try:
            result = func(*args, **kwargs)
            return result, None
        except AutomationError as e:
            return None, e
        except Exception as e:
            wrapped = AutomationError(
                str(e),
                details={"type": type(e).__name__}
            )
            return None, wrapped


def handle_errors(exit_on_critical: bool = False):
    """Decorator for automatic error handling"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AutomationError as e:
                ExceptionHandler.handle(e, exit_on_critical)
            except Exception as e:
                ExceptionHandler.handle(e, exit_on_critical)
        return wrapper
    return decorator