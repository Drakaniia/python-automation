"""
Structured Logging System
Provides consistent logging with color support and file output
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for terminal output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[0;36m',      # Cyan
        'INFO': '\033[0;32m',       # Green
        'WARNING': '\033[1;33m',    # Yellow
        'ERROR': '\033[0;31m',      # Red
        'CRITICAL': '\033[1;35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self, fmt: str, use_colors: bool = True):
        super().__init__(fmt)
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        # Check if NO_COLOR env var is set
        if os.getenv('NO_COLOR'):
            return False
        
        # Check if stdout is a TTY
        if not hasattr(sys.stdout, 'isatty'):
            return False
        
        if not sys.stdout.isatty():
            return False
        
        # Windows color support
        if sys.platform == 'win32':
            try:
                import colorama
                colorama.init()
                return True
            except ImportError:
                return False
        
        return True
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        if self.use_colors and record.levelname in self.COLORS:
            # Color the level name
            levelname = record.levelname
            colored_levelname = (f"{self.COLORS[levelname]}"
                               f"{levelname}{self.RESET}")
            record.levelname = colored_levelname
        
        return super().format(record)


class MagicLogger:
    """Centralized logging for automation system"""
    
    def __init__(self, 
                 name: str = 'magic',
                 level: int = logging.INFO,
                 log_to_file: bool = True,
                 use_colors: bool = True):
        """Initialize logger
        
        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            use_colors: Enable colored output
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()  # Clear any existing handlers
        
        # Console handler
        self._setup_console_handler(use_colors)
        
        # File handler (optional)
        if log_to_file:
            self._setup_file_handler()
    
    def _setup_console_handler(self, use_colors: bool):
        """Setup console output handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Format: [LEVEL] - Message
        formatter = ColoredFormatter(
            '%(levelname)s - %(message)s',
            use_colors=use_colors
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file output handler"""
        try:
            log_dir = Path.home() / '.magic_logs'
            log_dir.mkdir(exist_ok=True)
            
            # Create log file with date
            log_file = log_dir / f'magic_{datetime.now():%Y%m%d}.log'
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Format: [2025-01-15 14:30:45] [LEVEL] [module] - Message
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
        except Exception as e:
            # If file logging fails, just continue without it
            self.logger.warning(f"Could not setup file logging: {e}")
    
    # Convenience methods
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def success(self, message: str):
        """Log success message (as INFO with custom prefix)"""
        self.logger.info(f"✅ {message}")
    
    def step(self, message: str):
        """Log processing step (as INFO with custom prefix)"""
        self.logger.info(f"📍 {message}")
    
    def set_level(self, level: int):
        """Change logging level"""
        self.logger.setLevel(level)


# Global logger instance
_logger: Optional[MagicLogger] = None


def get_logger() -> MagicLogger:
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        # Check if debug mode is enabled
        debug = os.getenv('MAGIC_DEBUG', '').lower() in ('1', 'true', 'yes')
        level = logging.DEBUG if debug else logging.INFO
        
        # Check if colors should be disabled
        use_colors = not os.getenv('MAGIC_NO_COLOR', '').lower() in ('1', 'true', 'yes')
        
        _logger = MagicLogger(level=level, use_colors=use_colors)
    return _logger


# Convenience functions for direct use
def debug(message: str):
    """Log debug message"""
    get_logger().debug(message)


def info(message: str):
    """Log info message"""
    get_logger().info(message)


def warning(message: str):
    """Log warning message"""
    get_logger().warning(message)


def error(message: str):
    """Log error message"""
    get_logger().error(message)


def critical(message: str):
    """Log critical message"""
    get_logger().critical(message)


def success(message: str):
    """Log success message"""
    get_logger().success(message)


def step(message: str):
    """Log processing step"""
    get_logger().step(message)


if __name__ == '__main__':
    # Demo logger functionality
    print("Demo: Structured Logging\n")
    
    logger = get_logger()
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.success("Operation completed successfully!")
    logger.step("Processing step 1 of 3")
    
    print("\nLog file location:")
    log_dir = Path.home() / '.magic_logs'
    print(f"  {log_dir}")
    
    if log_dir.exists():
        log_files = list(log_dir.glob('magic_*.log'))
        if log_files:
            print(f"\nRecent log files:")
            for log_file in sorted(log_files)[-3:]:
                print(f"  • {log_file.name}")