"""
automation/dev_mode/_base.py
Base interface for Dev Mode command modules
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class DevModeCommand(ABC):
    """Abstract base class for Dev Mode commands"""
    
    label: str  # Short label shown in menu
    description: str  # Detailed help text
    
    @abstractmethod
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """
        Execute the command
        
        Args:
            interactive: If True, prompt user for input. If False, use kwargs.
            **kwargs: Non-interactive mode parameters
        
        Returns:
            Result of command execution (implementation-specific)
        
        Raises:
            Exception: In non-interactive mode for validation/execution errors
        """
        raise NotImplementedError
    
    def validate_binary(self, binary_name: str) -> bool:
        """
        Check if a required binary exists in PATH
        
        Args:
            binary_name: Name of binary to check
        
        Returns:
            True if binary exists, False otherwise
        """
        import shutil
        return shutil.which(binary_name) is not None
    
    def show_missing_binary_error(self, binary_name: str, install_url: str):
        """
        Display friendly error when binary is missing
        
        Args:
            binary_name: Name of missing binary
            install_url: URL where user can install it
        """
        print(f"\n{'='*70}")
        print(f"ERROR: \"{binary_name}\" not found in PATH")
        print(f"{'='*70}")
        print(f"\n💡 Install {binary_name}:")
        print(f"   {install_url}")
        print(f"\n{'='*70}\n")