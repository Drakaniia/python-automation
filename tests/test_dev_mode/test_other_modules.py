"""
tests/test_dev_mode/test_other_modules.py
Test other Dev Mode modules (run_project, install_deps, format_code, docker_quick)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json


class TestRunProject:
    """Test run_project module"""
    
    @pytest.fixture
    def run_project_cmd(self):
        from automation.dev_mode.run_project import RunProjectCommand
        return RunProjectCommand()
    
    def test_command_attributes(self, run_project_cmd):
        """Test command has required attributes"""
        assert run_project_cmd.label == "Run Project (Dev / Build)"
        assert len(run_project_cmd.description) > 0
    
    def test_detect_scripts(self, run_project_cmd, tmp_path):
        """Test script detection from package.json"""
        package_json = tmp_path / 'package.json'
        package_json.write_text(json.dumps({
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "test": "jest"
            }
        }))
        
        scripts = run_project_cmd._detect_scripts(package_json)
        
        assert 'dev' in scripts
        assert 'build' in scripts
        assert 'start' in scripts
        assert 'test' not in scripts  # Not a relevant script
    
    def test_detect_package_manager(self, run_project_cmd, tmp_path):
        """Test package manager detection"""
        # Test pnpm
        (tmp_path / 'pnpm-lock.yaml').touch()
        assert run_project_cmd._detect_package_manager(tmp_path) == 'pnpm'
        
        # Test yarn
        (tmp_path / 'pnpm-lock.yaml').unlink()
        (tmp_path / 'yarn.lock').touch()
        assert run_project_cmd._detect_package_manager(tmp_path) == 'yarn'
        
        # Test npm (default)
        (tmp_path / 'yarn.lock').unlink()
        assert run_project_cmd._detect_package_manager(tmp_path) == 'npm'
    
    @patch('pathlib.Path.cwd')
    def test_noninteractive_no_package_json(self, mock_cwd, run_project_cmd, tmp_path):
        """Test error when no package.json exists"""
        mock_cwd.return_value = tmp_path
        
        with pytest.raises(FileNotFoundError, match="No package.json"):
            run_project_cmd.run(interactive=False, mode='dev')
    
    @patch('pathlib.Path.cwd')
    def test_noninteractive_invalid_script(self, mock_cwd, run_project_cmd, tmp_path):
        """Test error when script doesn't exist"""
        mock_cwd.return_value = tmp_path
        
        package_json = tmp_path / 'package.json'
        package_json.write_text(json.dumps({"scripts": {"dev": "echo test"}}))
        
        with pytest.raises(ValueError, match="Script .* not found"):
            run_project_cmd.run(interactive=False, mode='nonexistent')


class TestInstallDeps:
    """Test install_deps module"""
    
    @pytest.fixture
    def install_deps_cmd(self):
        from automation.dev_mode.install_deps import InstallDepsCommand
        return InstallDepsCommand()
    
    def test_command_attributes(self, install_deps_cmd):
        """Test command has required attributes"""
        assert install_deps_cmd.label == "Install Dependencies (npm install)"
        assert len(install_deps_cmd.description) > 0
    
    def test_detect_package_manager(self, install_deps_cmd, tmp_path):
        """Test package manager detection from lock files"""
        # Change to tmp directory context
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Test pnpm
            (tmp_path / 'pnpm-lock.yaml').touch()
            assert install_deps_cmd._detect_package_manager() == 'pnpm'
            
            # Test yarn
            (tmp_path / 'pnpm-lock.yaml').unlink()
            (tmp_path / 'yarn.lock').touch()
            assert install_deps_cmd._detect_package_manager() == 'yarn'
            
            # Test npm
            (tmp_path / 'yarn.lock').unlink()
            (tmp_path / 'package-lock.json').touch()
            assert install_deps_cmd._detect_package_manager() == 'npm'
        finally:
            os.chdir(original_cwd)
    
    @patch('subprocess.run')
    def test_install_all_npm(self, mock_run, install_deps_cmd):
        """Test installing all dependencies with npm"""
        mock_run.return_value = Mock(returncode=0)
        
        install_deps_cmd._install_all('npm', interactive=False)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ['npm', 'install']
    
    @patch('subprocess.run')
    def test_install_package_dev(self, mock_run, install_deps_cmd):
        """Test installing package as dev dependency"""
        mock_run.return_value = Mock(returncode=0)
        
        install_deps_cmd._install_package('npm', 'eslint', dev=True, interactive=False)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'npm' in call_args
        assert 'install' in call_args
        assert '--save-dev' in call_args
        assert 'eslint' in call_args


class TestFormatCode:
    """Test format_code module"""
    
    @pytest.fixture
    def format_code_cmd(self):
        from automation.dev_mode.format_code import FormatCodeCommand
        return FormatCodeCommand()
    
    def test_command_attributes(self, format_code_cmd):
        """Test command has required attributes"""
        assert format_code_cmd.label == "Format Code (Prettier)"
        assert len(format_code_cmd.description) > 0
    
    def test_check_prettier_config(self, format_code_cmd, tmp_path):
        """Test Prettier config detection"""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # No config initially
            assert not format_code_cmd._check_prettier_config()
            
            # Create .prettierrc
            (tmp_path / '.prettierrc').touch()
            assert format_code_cmd._check_prettier_config()
        finally:
            os.chdir(original_cwd)
    
    def test_is_formattable(self, format_code_cmd):
        """Test file type checking"""
        formattable = [
            'test.js',
            'test.jsx',
            'test.ts',
            'test.tsx',
            'test.json',
            'test.css',
            'test.html'
        ]
        
        for file in formattable:
            assert format_code_cmd._is_formattable(file)
        
        # Non-formattable
        assert not format_code_cmd._is_formattable('test.py')
        assert not format_code_cmd._is_formattable('test.txt')
    
    @patch('subprocess.run')
    def test_format_path(self, mock_run, format_code_cmd):
        """Test formatting specific path"""
        mock_run.return_value = Mock(returncode=0)
        
        format_code_cmd._format_path('src/', interactive=False)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'npx' in call_args
        assert 'prettier' in call_args
        assert '--write' in call_args
        assert 'src/' in call_args


class TestDockerQuick:
    """Test docker_quick module"""
    
    @pytest.fixture
    def docker_cmd(self):
        from automation.dev_mode.docker_quick import DockerQuickCommand
        return DockerQuickCommand()
    
    def test_command_attributes(self, docker_cmd):
        """Test command has required attributes"""
        assert docker_cmd.label == "Docker Quick Commands"
        assert len(docker_cmd.description) > 0
    
    @patch('subprocess.run')
    def test_is_docker_running_true(self, mock_run, docker_cmd):
        """Test Docker daemon detection - running"""
        mock_run.return_value = Mock(returncode=0)
        
        assert docker_cmd._is_docker_running() is True
        mock_run.assert_called_once()
        assert 'docker' in mock_run.call_args[0][0]
        assert 'info' in mock_run.call_args[0][0]
    
    @patch('subprocess.run')
    def test_is_docker_running_false(self, mock_run, docker_cmd):
        """Test Docker daemon detection - not running"""
        mock_run.return_value = Mock(returncode=1)
        
        assert docker_cmd._is_docker_running() is False
    
    @patch('subprocess.run')
    def test_list_containers(self, mock_run, docker_cmd):
        """Test listing containers"""
        mock_run.return_value = Mock(returncode=0)
        
        docker_cmd._list_containers(interactive=False, all_containers=False)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ['docker', 'ps']
    
    @patch('subprocess.run')
    def test_list_all_containers(self, mock_run, docker_cmd):
        """Test listing all containers including stopped"""
        mock_run.return_value = Mock(returncode=0)
        
        docker_cmd._list_containers(interactive=False, all_containers=True)
        
        call_args = mock_run.call_args[0][0]
        assert call_args == ['docker', 'ps', '-a']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])