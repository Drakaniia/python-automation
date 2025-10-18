"""
Configuration Management System
Centralized configuration with user customization support
"""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import os


class Config:
    """Central configuration management for automation system"""
    
    DEFAULT_CONFIG = {
        'git': {
            'default_branch': 'main',
            'auto_changelog': True,
            'commit_template': '{emoji} {action} {scope}: {description}',
            'push_with_lease': False,  # Safer than force push
            'auto_stage_all': True,
        },
        'ui': {
            'enable_colors': True,
            'enable_emojis': True,
            'menu_style': 'arrows',  # 'arrows' or 'numbers'
            'clear_screen': True,
            'show_hints': True,
        },
        'paths': {
            'exclude_dirs': [
                '__pycache__', '.git', 'node_modules', 
                'venv', '.venv', 'env', 'dist', 'build',
                '.pytest_cache', '.coverage'
            ],
            'exclude_files': [
                '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
                'Thumbs.db', '*.swp', '*.log'
            ]
        },
        'limits': {
            'commit_history': 50,
            'log_display': 10,
            'max_commit_message_length': 72,
        },
        'ai': {
            'enable_smart_commits': True,
            'analyze_diff_lines': 500,  # Limit diff analysis for performance
            'suggest_scope': True,
            'suggest_emoji': True,
        },
        'debug': {
            'verbose': False,
            'log_git_commands': False,
            'show_stack_traces': False,
        }
    }
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration
        
        Args:
            config_file: Path to custom config file. If None, uses ~/.magic_config.json
        """
        if config_file is None:
            self.config_file = Path.home() / '.magic_config.json'
        else:
            self.config_file = Path(config_file)
        
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return self._merge_configs(self.DEFAULT_CONFIG, user_config)
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Invalid config file: {e}")
                print(f"   Using default configuration")
            except Exception as e:
                print(f"⚠️  Warning: Could not load config: {e}")
        
        return self._deep_copy(self.DEFAULT_CONFIG)
    
    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy configuration dictionary"""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        return obj
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge configurations
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = self._deep_copy(base)
        
        for key, value in override.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = self._deep_copy(value)
        
        return result
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        # MAGIC_DEBUG=1 enables debug mode
        if os.getenv('MAGIC_DEBUG', '').lower() in ('1', 'true', 'yes'):
            self.config['debug']['verbose'] = True
            self.config['debug']['show_stack_traces'] = True
        
        # MAGIC_NO_COLOR=1 disables colors
        if os.getenv('MAGIC_NO_COLOR', '').lower() in ('1', 'true', 'yes'):
            self.config['ui']['enable_colors'] = False
        
        # MAGIC_NO_EMOJI=1 disables emojis
        if os.getenv('MAGIC_NO_EMOJI', '').lower() in ('1', 'true', 'yes'):
            self.config['ui']['enable_emojis'] = False
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'git.default_branch')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config.get('git.default_branch')
            'main'
            >>> config.get('ui.enable_colors')
            True
            >>> config.get('nonexistent.key', 'fallback')
            'fallback'
        """
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, path: str, value: Any):
        """Set configuration value using dot notation
        
        Args:
            path: Dot-separated path (e.g., 'git.default_branch')
            value: Value to set
            
        Examples:
            >>> config.set('git.default_branch', 'develop')
            >>> config.set('ui.enable_colors', False)
        """
        keys = path.split('.')
        target = self.config
        
        # Navigate to parent dictionary
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set the value
        target[keys[-1]] = value
    
    def save(self, backup: bool = True):
        """Save current configuration to file
        
        Args:
            backup: If True, create backup of existing config
        """
        try:
            # Create backup if requested
            if backup and self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.bak')
                import shutil
                shutil.copy2(self.config_file, backup_file)
            
            # Save configuration
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✅ Configuration saved to: {self.config_file}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def reset(self):
        """Reset configuration to defaults"""
        self.config = self._deep_copy(self.DEFAULT_CONFIG)
        print("✅ Configuration reset to defaults")
    
    def show(self):
        """Display current configuration"""
        print("\n" + "="*70)
        print("⚙️  CURRENT CONFIGURATION")
        print("="*70 + "\n")
        
        def print_section(data: Dict, indent: int = 0):
            for key, value in data.items():
                prefix = "  " * indent
                if isinstance(value, dict):
                    print(f"{prefix}📁 {key}:")
                    print_section(value, indent + 1)
                else:
                    print(f"{prefix}  • {key}: {value}")
        
        print_section(self.config)
        print("\n" + "="*70)
        print(f"📍 Config file: {self.config_file}")
        print("="*70 + "\n")
    
    def export_template(self, output_file: Optional[Path] = None):
        """Export configuration template with comments
        
        Args:
            output_file: Output file path. If None, prints to console
        """
        template = {
            "_comment": "Magic Automation System Configuration",
            "_docs": "Edit this file to customize behavior",
            **self.DEFAULT_CONFIG
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            print(f"✅ Template exported to: {output_file}")
        else:
            print(json.dumps(template, indent=2))


# Global configuration instance
_config = None

def get_config() -> Config:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


# Convenience functions
def get(path: str, default: Any = None) -> Any:
    """Get configuration value (shorthand)"""
    return get_config().get(path, default)


def set_value(path: str, value: Any):
    """Set configuration value (shorthand)"""
    get_config().set(path, value)


def is_debug() -> bool:
    """Check if debug mode is enabled"""
    return get('debug.verbose', False)


def is_colors_enabled() -> bool:
    """Check if colors are enabled"""
    return get('ui.enable_colors', True)


def is_emojis_enabled() -> bool:
    """Check if emojis are enabled"""
    return get('ui.enable_emojis', True)


if __name__ == '__main__':
    # Demo configuration system
    config = Config()
    
    print("Demo: Configuration System\n")
    
    # Show current config
    config.show()
    
    # Get values
    print("\n📊 Getting values:")
    print(f"  Default branch: {config.get('git.default_branch')}")
    print(f"  Enable colors: {config.get('ui.enable_colors')}")
    print(f"  Commit history limit: {config.get('limits.commit_history')}")
    
    # Set values
    print("\n✏️  Setting values:")
    config.set('git.default_branch', 'develop')
    print(f"  New default branch: {config.get('git.default_branch')}")
    
    # Export template
    print("\n📄 Exporting template:")
    config.export_template(Path('config_template.json'))