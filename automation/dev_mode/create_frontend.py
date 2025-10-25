"""
automation/dev_mode/create_frontend.py
Create new frontend projects (React, Next.js, Vue)
"""
import subprocess
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from automation.dev_mode._base import DevModeCommand


class CreateFrontendCommand(DevModeCommand):
    """Command to create new frontend projects"""
    
    label = "Create Frontend Project (React / Next.js / Vue)"
    description = "Scaffold a new frontend project using modern frameworks"
    
    FRAMEWORKS = {
        '1': {'name': 'React', 'command': 'create-react-app'},
        '2': {'name': 'Next.js', 'command': 'create-next-app'},
        '3': {'name': 'Vue', 'command': 'create-vue'}
    }
    
    PACKAGE_MANAGERS = {
        '1': 'npm',
        '2': 'pnpm',
        '3': 'yarn'
    }
    
    CSS_FRAMEWORKS = {
        '1': {'name': 'None', 'flag': None},
        '2': {'name': 'Tailwind CSS', 'flag': '--tailwind'},
        '3': {'name': 'Bootstrap', 'flag': None}  # Manual setup
    }
    
    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute frontend project creation"""
        if interactive:
            return self._interactive_create()
        else:
            return self._noninteractive_create(**kwargs)
    
    def _interactive_create(self):
        """Interactive project creation flow"""
        print("\n" + "="*70)
        print("🚀 CREATE FRONTEND PROJECT")
        print("="*70 + "\n")
        
        # Check if Node.js/npm is installed
        if not self.validate_binary('node'):
            self.show_missing_binary_error(
                'node',
                'https://nodejs.org/'
            )
            input("\nPress Enter to continue...")
            return
        
        # 1. Select framework
        framework_choice = self._prompt_framework()
        if not framework_choice:
            return
        
        framework_info = self.FRAMEWORKS[framework_choice]
        
        # 2. Get project name
        project_name = self._prompt_project_name()
        if not project_name:
            return
        
        # 3. Select package manager
        pkg_manager = self._prompt_package_manager()
        
        # 4. TypeScript?
        use_typescript = self._prompt_yes_no("Use TypeScript?", default='y')
        
        # 5. CSS Framework
        css_choice = self._prompt_css_framework()
        css_info = self.CSS_FRAMEWORKS[css_choice]
        
        # 6. Target directory
        target_dir = self._prompt_directory()
        
        # 7. Initialize Git?
        init_git = self._prompt_yes_no("Initialize Git repository?", default='y')
        
        # Show summary
        print("\n" + "="*70)
        print("📋 PROJECT SUMMARY")
        print("="*70)
        print(f"Framework:        {framework_info['name']}")
        print(f"Project Name:     {project_name}")
        print(f"Package Manager:  {pkg_manager}")
        print(f"TypeScript:       {'Yes' if use_typescript else 'No'}")
        print(f"CSS Framework:    {css_info['name']}")
        print(f"Target Directory: {target_dir}")
        print(f"Initialize Git:   {'Yes' if init_git else 'No'}")
        print("="*70 + "\n")
        
        confirm = self._prompt_yes_no("Proceed with creation?", default='y')
        if not confirm:
            print("\n❌ Project creation cancelled")
            input("\nPress Enter to continue...")
            return
        
        # Create project
        self._create_project(
            framework=framework_info,
            project_name=project_name,
            pkg_manager=pkg_manager,
            use_typescript=use_typescript,
            css_framework=css_info,
            target_dir=target_dir,
            init_git=init_git
        )
        
        input("\nPress Enter to continue...")
    
    def _noninteractive_create(
        self,
        framework: str,
        name: str,
        package_manager: str = 'npm',
        typescript: bool = False,
        css: str = 'none',
        directory: str = '.',
        init_git: bool = False
    ):
        """Non-interactive project creation"""
        # Validate inputs
        if not name or not self._is_valid_project_name(name):
            raise ValueError(f"Invalid project name: {name}")
        
        framework_map = {
            'react': self.FRAMEWORKS['1'],
            'next': self.FRAMEWORKS['2'],
            'nextjs': self.FRAMEWORKS['2'],
            'vue': self.FRAMEWORKS['3']
        }
        
        framework_info = framework_map.get(framework.lower())
        if not framework_info:
            raise ValueError(f"Unknown framework: {framework}")
        
        css_info = self.CSS_FRAMEWORKS['1']  # Default to none
        
        self._create_project(
            framework=framework_info,
            project_name=name,
            pkg_manager=package_manager,
            use_typescript=typescript,
            css_framework=css_info,
            target_dir=directory,
            init_git=init_git
        )
    
    def _create_project(
        self,
        framework: Dict,
        project_name: str,
        pkg_manager: str,
        use_typescript: bool,
        css_framework: Dict,
        target_dir: str,
        init_git: bool
    ):
        """Execute project creation"""
        print("\n🔨 Creating project...\n")
        
        target_path = Path(target_dir).resolve()
        project_path = target_path / project_name
        
        # Check if directory already exists
        if project_path.exists():
            print(f"❌ ERROR: Directory '{project_name}' already exists")
            return
        
        try:
            # Build command based on framework
            if framework['name'] == 'React':
                cmd = self._build_react_command(
                    project_name, use_typescript, pkg_manager
                )
            elif framework['name'] == 'Next.js':
                cmd = self._build_nextjs_command(
                    project_name, use_typescript, pkg_manager
                )
            elif framework['name'] == 'Vue':
                cmd = self._build_vue_command(
                    project_name, use_typescript, pkg_manager
                )
            
            # Execute creation command
            print(f"$ {' '.join(cmd)}\n")
            result = subprocess.run(
                cmd,
                cwd=target_path,
                check=True,
                capture_output=False
            )
            
            print(f"\n✅ Project '{project_name}' created successfully!")
            
            # Initialize Git if requested
            if init_git:
                self._initialize_git(project_path)
            
            # Show next steps
            self._show_next_steps(project_name, pkg_manager)
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to create project: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _build_react_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-react-app command"""
        cmd = ['npx', 'create-react-app', name]
        if typescript:
            cmd.append('--template')
            cmd.append('typescript')
        if pkg_manager != 'npm':
            cmd.extend(['--use-' + pkg_manager])
        return cmd
    
    def _build_nextjs_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-next-app command"""
        cmd = ['npx', 'create-next-app@latest', name]
        if typescript:
            cmd.append('--typescript')
        else:
            cmd.append('--js')
        cmd.append('--no-git')  # We'll handle git separately
        if pkg_manager != 'npm':
            cmd.extend(['--use-' + pkg_manager])
        return cmd
    
    def _build_vue_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-vue command"""
        cmd = ['npm', 'init', 'vue@latest', name, '--', '--default']
        if typescript:
            cmd.append('--typescript')
        return cmd
    
    def _initialize_git(self, project_path: Path):
        """Initialize Git repository"""
        print("\n📦 Initializing Git repository...")
        try:
            subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit'],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            print("✅ Git repository initialized")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to initialize Git repository")
    
    def _show_next_steps(self, project_name: str, pkg_manager: str):
        """Display next steps"""
        print("\n" + "="*70)
        print("🎉 NEXT STEPS")
        print("="*70)
        print(f"\n1. Navigate to your project:")
        print(f"   cd {project_name}")
        print(f"\n2. Start the development server:")
        print(f"   {pkg_manager} run dev")
        print(f"\n3. Open your browser to:")
        print(f"   http://localhost:3000")
        print("\n" + "="*70)
    
    def _prompt_framework(self) -> Optional[str]:
        """Prompt user to select framework"""
        print("Select Framework:")
        for key, value in self.FRAMEWORKS.items():
            print(f"  {key}. {value['name']}")
        
        choice = input("\nYour choice (1-3): ").strip()
        if choice not in self.FRAMEWORKS:
            print("❌ Invalid choice")
            input("\nPress Enter to continue...")
            return None
        return choice
    
    def _prompt_project_name(self) -> Optional[str]:
        """Prompt for project name"""
        while True:
            name = input("\nProject name: ").strip()
            if not name:
                print("❌ Project name cannot be empty")
                continue
            
            if not self._is_valid_project_name(name):
                print("❌ Invalid project name. Use letters, numbers, hyphens, underscores")
                continue
            
            return name
    
    def _prompt_package_manager(self) -> str:
        """Prompt for package manager"""
        print("\nPackage Manager:")
        for key, value in self.PACKAGE_MANAGERS.items():
            print(f"  {key}. {value}")
        
        choice = input("\nYour choice (1-3, default: npm): ").strip() or '1'
        return self.PACKAGE_MANAGERS.get(choice, 'npm')
    
    def _prompt_css_framework(self) -> str:
        """Prompt for CSS framework"""
        print("\nCSS Framework:")
        for key, value in self.CSS_FRAMEWORKS.items():
            print(f"  {key}. {value['name']}")
        
        choice = input("\nYour choice (1-3, default: None): ").strip() or '1'
        return choice if choice in self.CSS_FRAMEWORKS else '1'
    
    def _prompt_directory(self) -> str:
        """Prompt for target directory"""
        directory = input("\nTarget directory (default: current): ").strip()
        return directory if directory else '.'
    
    def _prompt_yes_no(self, question: str, default: str = 'y') -> bool:
        """Prompt yes/no question"""
        default_text = "Y/n" if default == 'y' else "y/N"
        response = input(f"\n{question} [{default_text}]: ").strip().lower()
        
        if not response:
            return default == 'y'
        
        return response in ['y', 'yes']
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name"""
        # Allow letters, numbers, hyphens, underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))


# Export command instance
COMMAND = CreateFrontendCommand()