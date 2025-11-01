"""
automation/dev_mode/test_project.py
Run project tests (npm test, pytest, etc.)
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional, Any
from automation.dev_mode._base import DevModeCommand


class TestProjectCommand(DevModeCommand):
    """Command to run project tests"""
    
    label = "Run Tests (All Types)"
    description = "Run project tests using npm test, pytest, or other test runners"
    
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute test command"""
        if interactive:
            return self._interactive_run()
        else:
            return self._noninteractive_run(**kwargs)
    
    def _interactive_run(self):
        """Interactive test execution"""
        current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("🧪 RUN TESTS")
        print("="*70)
        print(f"📍 Current Directory: {current_dir}")
        print("="*70 + "\n")
        
        # Detect available test frameworks
        test_frameworks = self._detect_test_frameworks(current_dir)
        
        if not test_frameworks:
            print("❌ No test frameworks detected in this project")
            print("\n💡 Supported frameworks:")
            print("  • JavaScript/Node: Jest, Mocha, Vitest")
            print("  • Python: pytest, unittest")
            print("  • Other: Check package.json scripts")
            input("\nPress Enter to continue...")
            return
        
        # Show available test options
        print("Available Test Commands:")
        for i, (name, command, framework) in enumerate(test_frameworks, 1):
            print(f"  {i}. {name} ({framework})")
        print(f"  {len(test_frameworks) + 1}. Cancel")
        
        # Get user choice
        choice = input(f"\nYour choice (1-{len(test_frameworks) + 1}): ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(test_frameworks) + 1:
                print("\n❌ Operation cancelled")
                input("\nPress Enter to continue...")
                return
            
            if 1 <= choice_num <= len(test_frameworks):
                name, command, framework = test_frameworks[choice_num - 1]
                self._run_test_command(name, command, framework, current_dir)
            else:
                print("❌ Invalid choice")
                input("\nPress Enter to continue...")
        
        except ValueError:
            print("❌ Invalid input")
            input("\nPress Enter to continue...")
    
    def _noninteractive_run(
        self,
        framework: str = 'auto',
        args: Optional[str] = None
    ):
        """Non-interactive test execution"""
        current_dir = Path.cwd()
        
        test_frameworks = self._detect_test_frameworks(current_dir)
        if not test_frameworks:
            raise FileNotFoundError("No test frameworks detected")
        
        # Auto-select first available framework or match by name
        if framework == 'auto':
            name, command, fw = test_frameworks[0]
        else:
            matches = [t for t in test_frameworks if framework.lower() in t[2].lower()]
            if not matches:
                raise ValueError(f"Test framework '{framework}' not found")
            name, command, fw = matches[0]
        
        # Add custom args if provided
        if args:
            command = f"{command} {args}"
        
        self._run_test_command(name, command, fw, current_dir, attach=True)
    
    def _detect_test_frameworks(self, project_dir: Path) -> list:
        """
        Detect available test frameworks in the project
        
        Returns:
            List of tuples: (display_name, command, framework_type)
        """
        frameworks = []
        
        # Check for Node.js/JavaScript test frameworks
        package_json = project_dir / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                scripts = data.get('scripts', {})
                
                # Detect test scripts
                test_script_names = ['test', 'test:unit', 'test:integration', 'test:e2e']
                for script_name in test_script_names:
                    if script_name in scripts:
                        command = scripts[script_name]
                        
                        # Identify framework
                        if 'jest' in command.lower():
                            framework = 'Jest'
                        elif 'vitest' in command.lower():
                            framework = 'Vitest'
                        elif 'mocha' in command.lower():
                            framework = 'Mocha'
                        elif 'cypress' in command.lower():
                            framework = 'Cypress'
                        elif 'playwright' in command.lower():
                            framework = 'Playwright'
                        else:
                            framework = 'npm script'
                        
                        display_name = f"npm run {script_name}"
                        frameworks.append((display_name, command, framework))
            
            except (json.JSONDecodeError, Exception):
                pass
        
        # Check for Python test frameworks
        # pytest
        if (project_dir / 'pytest.ini').exists() or \
           (project_dir / 'pyproject.toml').exists() or \
           list(project_dir.glob('test_*.py')) or \
           list(project_dir.glob('tests/')):
            if self.validate_binary('pytest'):
                frameworks.append(('pytest', 'pytest', 'pytest'))
        
        # Python unittest
        if list(project_dir.glob('test*.py')):
            frameworks.append(('unittest', 'python -m unittest discover', 'unittest'))
        
        return frameworks
    
    def _run_test_command(
        self,
        name: str,
        command: str,
        framework: str,
        cwd: Path,
        attach: bool = True
    ):
        """Execute test command"""
        print(f"\n🚀 Running tests: {name}")
        print(f"   Framework: {framework}")
        print("="*70 + "\n")
        
        # Detect package manager for npm commands
        if command.startswith('npm ') or 'npm run' in name:
            pkg_manager = self._detect_package_manager(cwd)
            # Replace npm with detected package manager
            if pkg_manager != 'npm':
                command = command.replace('npm ', f'{pkg_manager} ')
                name = name.replace('npm ', f'{pkg_manager} ')
        
        print(f"   $ {command}")
        print(f"\n💡 Press Ctrl+C to stop the tests")
        print("="*70 + "\n")
        
        try:
            # Use shell=True on Windows for npm/yarn/pnpm commands
            use_shell = sys.platform == 'win32'
            
            if use_shell:
                # Windows: use shell mode with string command
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    shell=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                # Unix: use list command without shell
                cmd_list = command.split()
                process = subprocess.Popen(
                    cmd_list,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Stream output
            try:
                for line in process.stdout:
                    try:
                        print(line, end='')
                        sys.stdout.flush()
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        continue
            except KeyboardInterrupt:
                pass
            
            process.wait()
            
            if process.returncode == 0:
                print("\n\n✅ All tests passed!")
            elif process.returncode is None:
                print("\n\n⚠️  Tests were interrupted")
            else:
                print(f"\n\n❌ Tests failed with exit code {process.returncode}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        except FileNotFoundError as e:
            print(f"\n❌ Error: Command not found")
            print(f"💡 Make sure the test framework is installed")
        
        except Exception as e:
            print(f"\n❌ Error running tests: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to continue...")
    
    def _detect_package_manager(self, cwd: Path) -> str:
        """Detect which package manager to use"""
        if (cwd / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (cwd / 'yarn.lock').exists():
            return 'yarn'
        else:
            return 'npm'


# Export command instance
COMMAND = TestProjectCommand()