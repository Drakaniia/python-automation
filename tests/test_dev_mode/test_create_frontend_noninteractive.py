"""
tests/test_dev_mode/test_create_frontend_noninteractive.py
Test create_frontend module in non-interactive mode
"""
import pytest
from unittest.mock import Mock, patch, call
from automation.dev_mode.create_frontend import CreateFrontendCommand


@pytest.fixture
def create_frontend_cmd():
    """Create CreateFrontendCommand instance"""
    return CreateFrontendCommand()


class TestCreateFrontendNonInteractive:
    """Test create_frontend non-interactive mode"""
    
    def test_command_attributes(self, create_frontend_cmd):
        """Test command has required attributes"""
        assert create_frontend_cmd.label == "Create Frontend Project (React / Next.js / Vue)"
        assert len(create_frontend_cmd.description) > 0
    
    def test_invalid_project_name(self, create_frontend_cmd):
        """Test validation rejects invalid project names"""
        with pytest.raises(ValueError, match="Invalid project name"):
            create_frontend_cmd.run(
                interactive=False,
                framework='react',
                name='invalid name with spaces'
            )
    
    def test_empty_project_name(self, create_frontend_cmd):
        """Test validation rejects empty project name"""
        with pytest.raises(ValueError, match="Invalid project name"):
            create_frontend_cmd.run(
                interactive=False,
                framework='react',
                name=''
            )
    
    def test_unknown_framework(self, create_frontend_cmd):
        """Test validation rejects unknown framework"""
        with pytest.raises(ValueError, match="Unknown framework"):
            create_frontend_cmd.run(
                interactive=False,
                framework='unknown',
                name='test-project'
            )
    
    def test_valid_project_name(self, create_frontend_cmd):
        """Test valid project names pass validation"""
        valid_names = [
            'my-project',
            'my_project',
            'myproject123',
            'MyProject'
        ]
        
        for name in valid_names:
            assert create_frontend_cmd._is_valid_project_name(name)
    
    def test_invalid_project_name_validation(self, create_frontend_cmd):
        """Test invalid project names fail validation"""
        invalid_names = [
            'my project',
            'my@project',
            'my.project',
            'my/project'
        ]
        
        for name in invalid_names:
            assert not create_frontend_cmd._is_valid_project_name(name)
    
    @patch('subprocess.run')
    def test_react_command_building(self, mock_run, create_frontend_cmd):
        """Test React command is built correctly"""
        cmd = create_frontend_cmd._build_react_command(
            'test-project',
            typescript=True,
            pkg_manager='npm'
        )
        
        assert 'npx' in cmd
        assert 'create-react-app' in cmd
        assert 'test-project' in cmd
        assert '--template' in cmd
        assert 'typescript' in cmd
    
    def test_nextjs_command_building(self, create_frontend_cmd):
        """Test Next.js command is built correctly"""
        cmd = create_frontend_cmd._build_nextjs_command(
            'test-project',
            typescript=True,
            pkg_manager='npm'
        )
        
        assert 'npx' in cmd
        assert 'create-next-app@latest' in cmd
        assert 'test-project' in cmd
        assert '--typescript' in cmd
    
    def test_vue_command_building(self, create_frontend_cmd):
        """Test Vue command is built correctly"""
        cmd = create_frontend_cmd._build_vue_command(
            'test-project',
            typescript=True,
            pkg_manager='npm'
        )
        
        assert 'npm' in cmd
        assert 'init' in cmd
        assert 'vue@latest' in cmd
        assert 'test-project' in cmd


class TestCreateFrontendIntegration:
    """Integration tests for create_frontend"""
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_noninteractive_react_project(self, mock_exists, mock_run, create_frontend_cmd):
        """Test creating React project non-interactively"""
        # Setup mocks
        mock_exists.return_value = False  # Project doesn't exist
        mock_run.return_value = Mock(returncode=0)
        
        # Execute
        create_frontend_cmd.run(
            interactive=False,
            framework='react',
            name='test-react-app',
            typescript=False
        )
        
        # Verify subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert 'create-react-app' in ' '.join(call_args)
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_noninteractive_nextjs_project(self, mock_exists, mock_run, create_frontend_cmd):
        """Test creating Next.js project non-interactively"""
        mock_exists.return_value = False
        mock_run.return_value = Mock(returncode=0)
        
        create_frontend_cmd.run(
            interactive=False,
            framework='nextjs',
            name='test-next-app',
            typescript=True
        )
        
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert 'create-next-app' in ' '.join(call_args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])