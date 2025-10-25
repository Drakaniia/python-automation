"""
tests/test_dev_mode/test_menu_routing.py
Test Dev Mode menu routing and command loading
"""
import pytest
from automation.dev_mode.dev_mode import DevModeMenu
from automation.dev_mode._base import DevModeCommand


class TestDevModeMenu:
    """Test Dev Mode menu functionality"""
    
    def test_menu_initialization(self):
        """Test menu initializes correctly"""
        menu = DevModeMenu()
        
        assert menu.title == "🌐 Dev Mode - Web Development Automation"
        assert len(menu.items) > 0
        assert len(menu.commands) == 5  # 5 command modules
    
    def test_all_commands_loaded(self):
        """Test all command modules are loaded"""
        menu = DevModeMenu()
        
        expected_labels = [
            "Create Frontend Project (React / Next.js / Vue)",
            "Run Project (Dev / Build)",
            "Install Dependencies (npm install)",
            "Format Code (Prettier)",
            "Docker Quick Commands"
        ]
        
        loaded_labels = [cmd.label for cmd in menu.commands]
        
        for expected in expected_labels:
            assert expected in loaded_labels
    
    def test_back_to_main_menu_option(self):
        """Test back option is present"""
        menu = DevModeMenu()
        
        # Last item should be "Back to Main Menu"
        assert menu.items[-1].label == "Back to Main Menu"
    
    def test_commands_implement_interface(self):
        """Test all commands implement DevModeCommand interface"""
        menu = DevModeMenu()
        
        for cmd in menu.commands:
            assert isinstance(cmd, DevModeCommand)
            assert hasattr(cmd, 'label')
            assert hasattr(cmd, 'description')
            assert hasattr(cmd, 'run')
            assert callable(cmd.run)
    
    def test_command_has_required_attributes(self):
        """Test commands have required attributes"""
        menu = DevModeMenu()
        
        for cmd in menu.commands:
            # Check label
            assert isinstance(cmd.label, str)
            assert len(cmd.label) > 0
            
            # Check description
            assert isinstance(cmd.description, str)
            assert len(cmd.description) > 0
    
    def test_menu_items_count(self):
        """Test correct number of menu items"""
        menu = DevModeMenu()
        
        # 5 commands + 1 back option = 6 items
        assert len(menu.items) == 6


class TestCommandAPI:
    """Test command API consistency"""
    
    def test_run_method_signature(self):
        """Test run method accepts required parameters"""
        from automation.dev_mode.create_frontend import COMMAND as create_frontend
        from automation.dev_mode.run_project import COMMAND as run_project
        from automation.dev_mode.install_deps import COMMAND as install_deps
        from automation.dev_mode.format_code import COMMAND as format_code
        from automation.dev_mode.docker_quick import COMMAND as docker_quick
        
        commands = [
            create_frontend,
            run_project,
            install_deps,
            format_code,
            docker_quick
        ]
        
        for cmd in commands:
            # Should accept interactive parameter
            import inspect
            sig = inspect.signature(cmd.run)
            params = list(sig.parameters.keys())
            
            assert 'interactive' in params
            assert 'kwargs' in params
    
    def test_validate_binary_method(self):
        """Test validate_binary helper method"""
        from automation.dev_mode.create_frontend import COMMAND
        
        # Test with a binary that should exist
        result = COMMAND.validate_binary('python')
        assert isinstance(result, bool)
    
    def test_show_missing_binary_error(self, capsys):
        """Test missing binary error display"""
        from automation.dev_mode.create_frontend import COMMAND
        
        COMMAND.show_missing_binary_error('test-binary', 'https://example.com')
        
        captured = capsys.readouterr()
        assert 'test-binary' in captured.out
        assert 'https://example.com' in captured.out


class TestModuleExports:
    """Test module exports"""
    
    def test_base_module_exports(self):
        """Test _base.py exports DevModeCommand"""
        from automation.dev_mode._base import DevModeCommand
        
        assert DevModeCommand is not None
    
    def test_each_module_exports_command(self):
        """Test each module exports COMMAND instance"""
        modules = [
            'automation.dev_mode.create_frontend',
            'automation.dev_mode.run_project',
            'automation.dev_mode.install_deps',
            'automation.dev_mode.format_code',
            'automation.dev_mode.docker_quick'
        ]
        
        for module_name in modules:
            module = __import__(module_name, fromlist=['COMMAND'])
            assert hasattr(module, 'COMMAND')
            assert isinstance(module.COMMAND, DevModeCommand)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])