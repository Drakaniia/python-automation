"""
automation/dev_mode/format_code.py
Simple Prettier setup - installs once and configures format-on-save
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional
from automation.dev_mode._base import DevModeCommand


class FormatCodeCommand(DevModeCommand):
    """Command to setup Prettier with format-on-save"""
    
    label = "Setup Prettier (Format on Save)"
    description = "Install and configure Prettier for auto-formatting"
    
    def run(self, interactive: bool = True, **kwargs) -> any:
        """Execute Prettier setup"""
        if interactive:
            return self._interactive_setup()
        else:
            return self._noninteractive_setup(**kwargs)
    
    def _interactive_setup(self):
        """Interactive Prettier setup"""
        current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("✨ PRETTIER SETUP (Format on Save)")
        print("="*70 + "\n")
        
        # Check if package.json exists
        package_json = current_dir / 'package.json'
        if not package_json.exists():
            print("⚠️  No package.json found")
            create = input("Create package.json? (y/n): ").strip().lower()
            if create == 'y':
                if not self._init_package_json(current_dir):
                    input("\nPress Enter to continue...")
                    return
                print()
            else:
                print("\n❌ Operation cancelled - package.json is required")
                input("\nPress Enter to continue...")
                return
        
        # Check if Prettier is already installed
        prettier_installed = self._check_prettier_installed(current_dir)
        
        if prettier_installed:
            print("✅ Prettier is already installed\n")
        else:
            print("⚠️  Prettier is not installed yet\n")
            print("🔨 Installing Prettier...")
            print("="*70 + "\n")
            
            if not self._install_prettier_with_progress(current_dir):
                print("\n❌ Failed to install Prettier")
                input("\nPress Enter to continue...")
                return
            
            print("\n✅ Prettier installed successfully!\n")
        
        # Create/update configuration files
        print("🔧 Setting up configuration files...\n")
        
        # 1. Create .prettierrc if it doesn't exist
        if not self._check_prettier_config(current_dir):
            self._create_prettier_config(current_dir)
            print("✅ Created .prettierrc")
        else:
            print("✅ .prettierrc already exists")
        
        # 2. Create .prettierignore
        self._create_prettier_ignore(current_dir)
        print("✅ Created/Updated .prettierignore")
        
        # 3. Create/Update VSCode settings for format-on-save
        self._create_vscode_settings(current_dir)
        print("✅ Created/Updated .vscode/settings.json (Workspace Settings)")
        
        # 4. Add format script to package.json
        self._add_format_script(current_dir)
        print("✅ Added format script to package.json")
        
        print("\n" + "="*70)
        print("🎉 PRETTIER SETUP COMPLETE!")
        print("="*70)
        print("\n📝 What was configured:")
        print("  • Prettier installed as dev dependency")
        print("  • .prettierrc configuration file")
        print("  • .prettierignore (excludes node_modules, etc.)")
        print("  • .vscode/settings.json (Workspace Settings) ✅")
        print("  • npm run format script added")
        
        print("\n✅ Workspace Settings Automatically Configured:")
        print("     The following settings were written to .vscode/settings.json:")
        print('     {')
        print('       "editor.formatOnSave": true,')
        print('       "editor.formatOnPaste": true,')
        print('       "editor.formatOnType": true,')
        print('       "editor.defaultFormatter": "esbenp.prettier-vscode"')
        print('     }')
        
        print("\n💡 How to use:")
        print("  • Auto-format: Just press Ctrl+S (save) in VSCode")
        print("  • Manual format: npm run format")
        print("  • Format file: Right-click → Format Document")
        
        print("\n⚠️  FINAL STEPS (One-Time Setup):")
        print("="*70)
        print("\n1️⃣  Install Prettier VSCode Extension (REQUIRED):")
        print("     • Press Ctrl+Shift+X (Extensions)")
        print("     • Search: 'Prettier - Code formatter'")
        print("     • Click Install (by Prettier)")
        
        print("\n2️⃣  Restart VSCode:")
        print("     • Close VSCode completely")
        print("     • Reopen your project")
        
        print("\n3️⃣  Test it:")
        print("     • Open any .js, .jsx, .ts, or .tsx file")
        print("     • Write messy code (wrong indentation)")
        print("     • Press Ctrl+S")
        print("     • Watch it auto-format! ✨")
        
        print("\n📂 Files Created:")
        print(f"     • {current_dir / '.vscode' / 'settings.json'}")
        print(f"     • {current_dir / '.vscode' / 'SETTINGS_INFO.md'}")
        print(f"     • {current_dir / '.prettierrc'}")
        print(f"     • {current_dir / '.prettierignore'}")
        
        print("\n🔧 Troubleshooting:")
        print("     • Settings not working? Check if Prettier extension is installed")
        print("     • Right-click file → Format Document With... → Choose Prettier")
        print("     • View settings: Ctrl+Shift+P → 'Open Workspace Settings (JSON)'")
        print("="*70 + "\n")
        
        input("Press Enter to continue...")
    
    def _noninteractive_setup(self, auto_install: bool = True):
        """Non-interactive setup"""
        current_dir = Path.cwd()
        
        if auto_install and not self._check_prettier_installed(current_dir):
            if not self._install_prettier_with_progress(current_dir):
                raise RuntimeError("Failed to install Prettier")
        
        self._create_prettier_config(current_dir)
        self._create_prettier_ignore(current_dir)
        self._create_vscode_settings(current_dir)
        self._add_format_script(current_dir)
    
    def _check_prettier_installed(self, project_dir: Path) -> bool:
        """Check if Prettier is installed locally"""
        package_json = project_dir / 'package.json'
        
        if not package_json.exists():
            return False
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check devDependencies and dependencies
            dev_deps = data.get('devDependencies', {})
            deps = data.get('dependencies', {})
            
            return 'prettier' in dev_deps or 'prettier' in deps
        
        except Exception:
            return False
    
    def _install_prettier_with_progress(self, project_dir: Path) -> bool:
        """Install Prettier with progress indication"""
        # Detect package manager
        pkg_manager = self._detect_package_manager(project_dir)
        
        # Build install command
        if pkg_manager == 'npm':
            cmd = ['npm', 'install', '--save-dev', 'prettier']
        elif pkg_manager == 'yarn':
            cmd = ['yarn', 'add', '--dev', 'prettier']
        elif pkg_manager == 'pnpm':
            cmd = ['pnpm', 'add', '--save-dev', 'prettier']
        else:
            cmd = ['npm', 'install', '--save-dev', 'prettier']
        
        print(f"$ {' '.join(cmd)}")
        
        try:
            use_shell = sys.platform == 'win32'
            
            # Show live output
            if use_shell:
                process = subprocess.Popen(
                    ' '.join(cmd),
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    shell=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Stream output
            for line in process.stdout:
                print(line, end='')
                sys.stdout.flush()
            
            process.wait()
            return process.returncode == 0
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False
    
    def _init_package_json(self, project_dir: Path) -> bool:
        """Initialize package.json"""
        print("📦 Creating package.json...\n")
        
        try:
            use_shell = sys.platform == 'win32'
            
            result = subprocess.run(
                ['npm', 'init', '-y'] if not use_shell else 'npm init -y',
                cwd=project_dir,
                check=True,
                capture_output=True,
                shell=use_shell,
                encoding='utf-8',
                errors='replace'
            )
            
            print("✅ package.json created")
            return True
        
        except subprocess.CalledProcessError:
            print("❌ Failed to create package.json")
            return False
    
    def _detect_package_manager(self, project_dir: Path) -> str:
        """Detect package manager from lock files"""
        if (project_dir / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (project_dir / 'yarn.lock').exists():
            return 'yarn'
        elif (project_dir / 'package-lock.json').exists():
            return 'npm'
        else:
            return 'npm'
    
    def _check_prettier_config(self, project_dir: Path) -> bool:
        """Check if Prettier config exists"""
        config_files = [
            '.prettierrc',
            '.prettierrc.json',
            '.prettierrc.js',
            '.prettierrc.yaml',
            '.prettierrc.yml',
            'prettier.config.js'
        ]
        
        return any((project_dir / config).exists() for config in config_files)
    
    def _create_prettier_config(self, project_dir: Path):
        """Create default .prettierrc configuration"""
        config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False,
            "arrowParens": "avoid",
            "endOfLine": "auto"
        }
        
        config_file = project_dir / '.prettierrc'
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not create .prettierrc: {e}")
    
    def _create_prettier_ignore(self, project_dir: Path):
        """Create .prettierignore file"""
        ignore_patterns = [
            "# Ignore build outputs",
            "node_modules/",
            "dist/",
            "build/",
            ".next/",
            "out/",
            "",
            "# Ignore cache",
            ".cache/",
            ".parcel-cache/",
            "",
            "# Ignore package manager files",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "",
            "# Ignore git",
            ".git/",
            "",
            "# Ignore Python",
            "__pycache__/",
            "*.pyc",
            ".venv/",
            "venv/",
            "",
            "# Ignore environment files",
            ".env",
            ".env.*",
        ]
        
        ignore_file = project_dir / '.prettierignore'
        
        try:
            with open(ignore_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ignore_patterns))
        except Exception as e:
            print(f"⚠️  Could not create .prettierignore: {e}")
    
    def _create_vscode_settings(self, project_dir: Path):
        """Create or update .vscode/settings.json for format-on-save (Workspace Settings)"""
        vscode_dir = project_dir / '.vscode'
        settings_file = vscode_dir / 'settings.json'
        
        # Create .vscode directory if it doesn't exist
        vscode_dir.mkdir(exist_ok=True)
        
        # Settings to add - Enhanced for proper format-on-save
        # This is the WORKSPACE settings.json that VSCode uses
        prettier_settings = {
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "editor.formatOnType": True,
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "[javascript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[javascriptreact]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[typescript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[typescriptreact]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[json]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[html]": {
                "editor.defaultFormatter": "vscode.html-language-features"
            },
            "[css]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[scss]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[vue]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[markdown]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            }
        }
        
        try:
            # Read existing settings if file exists
            existing_settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:  # Only parse if file has content
                            existing_settings = json.loads(content)
                except json.JSONDecodeError:
                    # If file is corrupted, start fresh
                    existing_settings = {}
                except Exception:
                    existing_settings = {}
            
            # Merge settings (prettier settings take precedence)
            existing_settings.update(prettier_settings)
            
            # Write back with nice formatting
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4)
            
            # Also create a backup comment file for user reference
            readme_file = vscode_dir / 'SETTINGS_INFO.md'
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write("# VSCode Workspace Settings\n\n")
                f.write("This folder contains workspace-specific settings for VSCode.\n\n")
                f.write("## settings.json\n")
                f.write("Automatically configured by Python Automation System.\n\n")
                f.write("These settings enable:\n")
                f.write("- Format on Save (Ctrl+S)\n")
                f.write("- Format on Paste\n")
                f.write("- Format on Type\n")
                f.write("- Prettier as default formatter\n\n")
                f.write("To view these settings in VSCode:\n")
                f.write("1. Press Ctrl+Shift+P\n")
                f.write("2. Type: 'Preferences: Open Workspace Settings (JSON)'\n")
                f.write("3. You'll see this settings.json file\n")
        
        except Exception as e:
            print(f"⚠️  Could not create VSCode settings: {e}")
    
    def _add_format_script(self, project_dir: Path):
        """Add format script to package.json"""
        package_json = project_dir / 'package.json'
        
        if not package_json.exists():
            return
        
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add scripts section if it doesn't exist
            if 'scripts' not in data:
                data['scripts'] = {}
            
            # Add format script
            data['scripts']['format'] = 'prettier --write .'
            data['scripts']['format:check'] = 'prettier --check .'
            
            # Write back
            with open(package_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"⚠️  Could not update package.json: {e}")


# Export command instance
COMMAND = FormatCodeCommand()