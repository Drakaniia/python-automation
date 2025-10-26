"""
automation/dev_mode/run_project.py
Run project development server or build
FIXED: Windows compatibility and encoding issues
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from automation.dev_mode._base import DevModeCommand


class RunProjectCommand(DevModeCommand):
    """Command to run project dev server or build"""
    
    label = "Run Project (Dev / Build)"
    description = "Start development server or build production bundle"
    
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute project run command"""
        if interactive:
            return self._interactive_run()
        else:
            return self._noninteractive_run(**kwargs)
    
    def _interactive_run(self):
        """Interactive project run flow"""
        # Always use current directory
        current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("▶️  RUN PROJECT")
        print("="*70)
        print(f"📍 Current Directory: {current_dir}")
        print("="*70 + "\n")
        
        # Check for package.json
        package_json = current_dir / 'package.json'
        if not package_json.exists():
            print("❌ No package.json found in current directory")
            print("💡 Navigate to a Node.js project directory first")
            input("\nPress Enter to continue...")
            return
        
        # Detect project type and available scripts
        scripts = self._detect_scripts(package_json)
        if not scripts:
            print("❌ No dev or build scripts found in package.json")
            input("\nPress Enter to continue...")
            return
        
        # Show available scripts
        print("Available Scripts:")
        for i, (name, command) in enumerate(scripts.items(), 1):
            print(f"  {i}. {name}: {command}")
        print(f"  {len(scripts) + 1}. Cancel")
        
        # Get user choice
        choice = input(f"\nYour choice (1-{len(scripts) + 1}): ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(scripts) + 1:
                print("\n❌ Operation cancelled")
                input("\nPress Enter to continue...")
                return
            
            if 1 <= choice_num <= len(scripts):
                script_name = list(scripts.keys())[choice_num - 1]
                self._run_script(script_name, current_dir)
            else:
                print("❌ Invalid choice")
                input("\nPress Enter to continue...")
        
        except ValueError:
            print("❌ Invalid input")
            input("\nPress Enter to continue...")
    
    def _noninteractive_run(
        self,
        mode: str = 'dev',
        manager: str = 'npm',
        attach: bool = True
    ):
        """Non-interactive project run"""
        current_dir = Path.cwd()
        package_json = current_dir / 'package.json'
        
        if not package_json.exists():
            raise FileNotFoundError("No package.json found in current directory")
        
        scripts = self._detect_scripts(package_json)
        if mode not in scripts:
            raise ValueError(f"Script '{mode}' not found in package.json")
        
        self._run_script(mode, current_dir, attach=attach)
    
    def _detect_scripts(self, package_json: Path) -> Dict[str, str]:
        """Detect available npm scripts"""
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scripts = data.get('scripts', {})
            
            # Filter for common dev/build scripts
            relevant_scripts = {}
            for script_name, script_cmd in scripts.items():
                if script_name in ['dev', 'start', 'build', 'serve', 'preview']:
                    relevant_scripts[script_name] = script_cmd
            
            return relevant_scripts
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Error reading package.json: {e}")
            return {}
    
    def _run_script(self, script_name: str, cwd: Path, attach: bool = True):
        """Execute npm script with proper encoding handling"""
        print(f"\n🚀 Running script: {script_name}")
        print("="*70 + "\n")
        
        # Detect package manager
        pkg_manager = self._detect_package_manager(cwd)
        
        # Build command
        cmd = [pkg_manager, 'run', script_name]
        
        print(f"$ {' '.join(cmd)}")
        print(f"\n💡 Press Ctrl+C to stop the server")
        print("="*70 + "\n")
        
        try:
            # Use shell=True on Windows for npm/yarn/pnpm commands
            use_shell = sys.platform == 'win32'
            
            if use_shell:
                # Windows: use shell mode with string command and proper encoding
                cmd_str = ' '.join(cmd)
                process = subprocess.Popen(
                    cmd_str,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    shell=True,
                    encoding='utf-8',
                    errors='replace'  # Replace invalid characters instead of crashing
                )
            else:
                # Unix: use list command without shell
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'  # Replace invalid characters instead of crashing
                )
            
            # Stream output with robust error handling
            try:
                for line in process.stdout:
                    try:
                        # Print each line, handling any remaining encoding issues
                        print(line, end='')
                        sys.stdout.flush()
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        # Skip lines that can't be decoded/encoded
                        continue
            except KeyboardInterrupt:
                # User pressed Ctrl+C
                pass
            
            process.wait()
            
            if process.returncode == 0:
                print("\n\n✅ Script completed successfully")
            elif process.returncode is None:
                print("\n\n⚠️  Script was interrupted")
            else:
                print(f"\n\n⚠️  Script exited with code {process.returncode}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user")
            # Try to terminate gracefully
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        except FileNotFoundError:
            print(f"\n❌ Error: '{pkg_manager}' not found in PATH")
            print(f"💡 Make sure {pkg_manager} is installed and in your PATH")
        
        except Exception as e:
            print(f"\n❌ Error running script: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to continue...")
    
    def _detect_package_manager(self, cwd: Path) -> str:
        """Detect which package manager to use"""
        # Check for lock files
        if (cwd / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (cwd / 'yarn.lock').exists():
            return 'yarn'
        else:
            return 'npm'


# Export command instance
COMMAND = RunProjectCommand()