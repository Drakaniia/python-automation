# ============================================================
# tests/test_exceptions.py
# ============================================================
"""Test exception handling system"""
import pytest
from automation.core.exceptions import (
    AutomationError,
    ErrorSeverity,
    GitError,
    GitCommandError,
    ExceptionHandler
)


class TestAutomationError:
    """Test base exception class"""
    
    def test_basic_error(self):
        """Test creating basic error"""
        error = AutomationError("Test error")
        assert str(error) == "Test error"
        assert error.severity == ErrorSeverity.ERROR
    
    def test_error_with_details(self):
        """Test error with details"""
        error = AutomationError(
            "Test error",
            details={"key": "value"}
        )
        assert error.details["key"] == "value"
    
    def test_error_with_suggestion(self):
        """Test error with suggestion"""
        error = AutomationError(
            "Test error",
            suggestion="Try this"
        )
        assert error.suggestion == "Try this"
    
    def test_error_display(self):
        """Test error display formatting"""
        error = AutomationError(
            "Test error",
            severity=ErrorSeverity.WARNING,
            details={"detail": "value"},
            suggestion="Fix it"
        )
        
        display = error.display()
        assert "WARNING" in display
        assert "Test error" in display
        assert "detail: value" in display
        assert "Fix it" in display


class TestGitCommandError:
    """Test Git command error"""
    
    def test_git_command_error(self):
        """Test creating Git command error"""
        error = GitCommandError(
            command="git push",
            return_code=1,
            stderr="remote not found"
        )
        
        assert "git push" in error.message
        assert error.details["return_code"] == 1
        assert "remote not found" in error.details["stderr"]
    
    def test_error_suggestions(self):
        """Test automatic suggestion generation"""
        test_cases = [
            ("not a git repository", "Initialize Git"),
            ("remote not found", "Configure remote"),
            ("permission denied", "permissions"),
            ("conflict", "merge conflicts"),
        ]
        
        for stderr, expected in test_cases:
            error = GitCommandError(
                command="git test",
                return_code=1,
                stderr=stderr
            )
            assert expected.lower() in error.suggestion.lower()


class TestExceptionHandler:
    """Test exception handler"""
    
    def test_safe_execute_success(self):
        """Test safe execution with success"""
        def success_func():
            return "result"
        
        result, error = ExceptionHandler.safe_execute(success_func)
        assert result == "result"
        assert error is None
    
    def test_safe_execute_error(self):
        """Test safe execution with error"""
        def error_func():
            raise ValueError("Test error")
        
        result, error = ExceptionHandler.safe_execute(error_func)
        assert result is None
        assert isinstance(error, AutomationError)

