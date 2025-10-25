"""
automation/dev_mode/format_code.py
Format code using Prettier
"""
import subprocess
import json
from pathlib import Path
from typing import Optional
from automation.dev_mode._base import DevModeCommand


class FormatCodeCommand(DevModeCommand):
    """Command to format code with Prettier"""
    
    label = "Format Code (Prettier)"
    description = "Format code using Prettier"
    
    def run(self, interactive: bool = True, **kwargs) -> any:
        """Execute code formatting"""
        if interactive:
            return self._interactive_format()
        else:
            return self._noninteractive_format(**kwargs)
    
    def _interactive_format(self):
        """Interactive code formatting"""
        print("\n" + "="*70)
        print("✨ FORMAT CODE WITH PRETTIER")
        print("="*70 + "\n")
        
        # Check if Prettier is configured
        has_prettier = self._check_prettier_config()
        
        if has_prettier:
            print("✅ Prettier configuration detected")
        else:
            print("⚠️  No Prettier configuration found")
            print("💡 Will use default Prettier settings")
        
        # Formatting options
        print("\nFormatting Options:")
        print("  1. Format entire project")
        print("  2. Format specific path")
        print("  3. Format staged files only (git)")
        print("  4. Cancel")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == '1':
            self._format_all()
        elif choice == '2':
            path = input("\nPath to format (e.g., src/): ").strip()
            if path:
                self._format_path(path)
            else:
                print("❌ Path cannot be empty")
        elif choice == '3':
            self._format_staged()
        elif choice == '4':
            print("\n❌ Operation cancelled")
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _noninteractive_format(
        self,
        path: str = '.',
        staged: bool = False
    ):
        """Non-interactive code formatting"""
        if staged:
            self._format_staged(interactive=False)
        else:
            self._format_path(path, interactive=False)
    
    def _check_prettier_config(self) -> bool:
        """Check if Prettier is configured"""
        cwd = Path.cwd()
        
        # Check for config files
        config_files = [
            '.prettierrc',
            '.prettierrc.json',
            '.prettierrc.js',
            '.prettierrc.yaml',
            '.prettierrc.yml',
            'prettier.config.js'
        ]
        
        for config_file in config_files:
            if (cwd / config_file).exists():
                return True
        
        # Check package.json for prettier config
        package_json = cwd / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'prettier' in data:
                        return True
            except:
                pass
        
        return False
    
    def _format_all(self, interactive: bool = True):
        """Format entire project"""
        print("\n🔨 Formatting entire project...")
        print("="*70 + "\n")
        
        cmd = ['npx', 'prettier', '--write', '.']
        
        print(f"$ {' '.join(cmd)}\n")
        
        self._run_prettier(cmd, interactive)
    
    def _format_path(self, path: str, interactive: bool = True):
        """Format specific path"""
        print(f"\n🔨 Formatting: {path}")
        print("="*70 + "\n")
        
        cmd = ['npx', 'prettier', '--write', path]
        
        print(f"$ {' '.join(cmd)}\n")
        
        self._run_prettier(cmd, interactive)
    
    def _format_staged(self, interactive: bool = True):
        """Format staged files only"""
        print("\n🔨 Formatting staged files...")
        print("="*70 + "\n")
        
        # Check if git repo
        if not (Path.cwd() / '.git').exists():
            msg = "❌ Not a git repository"
            if interactive:
                print(msg)
                return
            else:
                raise FileNotFoundError(msg)
        
        # Get staged files
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = result.stdout.strip().split('\n')
            staged_files = [f for f in staged_files if f]
            
            if not staged_files:
                msg = "ℹ️  No staged files to format"
                if interactive:
                    print(msg)
                    return
                else:
                    print(msg)
                    return
            
            print(f"Found {len(staged_files)} staged file(s):")
            for f in staged_files[:10]:  # Show first 10
                print(f"  • {f}")
            if len(staged_files) > 10:
                print(f"  ... and {len(staged_files) - 10} more")
            print()
            
            # Format each file
            for file in staged_files:
                # Only format supported file types
                if self._is_formattable(file):
                    cmd = ['npx', 'prettier', '--write', file]
                    subprocess.run(cmd, check=False, capture_output=True)
            
            print("✅ Staged files formatted!")
            print("💡 Don't forget to stage the formatted changes:")
            print("   git add .")
        
        except subprocess.CalledProcessError as e:
            msg = f"❌ Error getting staged files: {e}"
            if interactive:
                print(msg)
            else:
                raise RuntimeError(msg)
    
    def _run_prettier(self, cmd: list, interactive: bool = True):
        """Run Prettier command"""
        try:
            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                check=True,
                capture_output=not interactive
            )
            
            print("\n✅ Code formatted successfully!")
        
        except subprocess.CalledProcessError as e:
            if interactive:
                print(f"\n❌ Formatting failed with exit code {e.returncode}")
                print("💡 Make sure Prettier is installed:")
                print("   npm install --save-dev prettier")
            else:
                raise
        except Exception as e:
            if interactive:
                print(f"\n❌ Error: {e}")
            else:
                raise
    
    def _is_formattable(self, filepath: str) -> bool:
        """Check if file type is formattable by Prettier"""
        formattable_extensions = {
            '.js', '.jsx', '.ts', '.tsx',
            '.json', '.css', '.scss', '.less',
            '.html', '.md', '.yaml', '.yml'
        }
        
        return Path(filepath).suffix in formattable_extensions


# Export command instance
COMMAND = FormatCodeCommand()