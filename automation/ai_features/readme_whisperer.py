"""
README Whisperer Module
AI-powered README.md generator and updater
Analyzes codebase structure and generates comprehensive documentation
"""
import subprocess
from pathlib import Path
import json


class ReadmeWhisperer:
    """Generates and updates README.md files based on project analysis"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def generate_readme(self, target_dir=None):
        """
        Generate or update README.md for the target directory
        
        Args:
            target_dir: Path to target directory (default: current directory)
        """
        if target_dir:
            self.current_dir = Path(target_dir)
        else:
            self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("📝 README WHISPERER - AI-Powered Documentation Generator")
        print("="*70)
        print(f"\n📍 Target Directory: {self.current_dir}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}\n")
        
        # Step 1: Analyze project structure
        print("🔍 Analyzing project structure...")
        structure = self._analyze_structure()
        
        # Step 2: Get git information
        print("📊 Gathering git information...")
        git_info = self._get_git_info()
        
        # Step 3: Detect tech stack
        print("🔧 Detecting tech stack...")
        tech_stack = self._detect_tech_stack()
        
        # Step 4: Check for existing README
        existing_readme = self._read_existing_readme()
        
        # Step 5: Generate README content
        print("\n✍️  Generating README content...\n")
        readme_content = self._generate_content(
            structure, git_info, tech_stack, existing_readme
        )
        
        # Step 6: Preview and confirm
        print("="*70)
        print("📄 GENERATED README PREVIEW")
        print("="*70)
        print(readme_content[:500] + "...\n")
        
        choice = input("Do you want to save this README? (y/n): ").strip().lower()
        
        if choice == 'y':
            self._save_readme(readme_content)
            print("\n✅ README.md successfully generated!")
        else:
            print("\n❌ README generation cancelled.")
        
        input("\nPress Enter to continue...")
    
    def _analyze_structure(self):
        """Analyze directory structure and file types"""
        structure = {
            'files': [],
            'directories': [],
            'file_types': {},
            'total_files': 0
        }
        
        try:
            for item in self.current_dir.rglob('*'):
                # Skip common ignored directories
                if any(part in ['.git', '__pycache__', 'node_modules', 'venv', '.venv'] 
                       for part in item.parts):
                    continue
                
                if item.is_file():
                    structure['files'].append(item.relative_to(self.current_dir))
                    structure['total_files'] += 1
                    
                    # Track file extensions
                    ext = item.suffix.lower()
                    if ext:
                        structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                elif item.is_dir():
                    structure['directories'].append(item.relative_to(self.current_dir))
        except Exception as e:
            print(f"⚠️  Warning: {e}")
        
        return structure
    
    def _get_git_info(self):
        """Get git repository information"""
        git_info = {
            'is_repo': False,
            'recent_commits': [],
            'branch': None,
            'remote_url': None
        }
        
        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=self.current_dir
            )
            
            if result.returncode == 0:
                git_info['is_repo'] = True
                
                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir
                )
                git_info['branch'] = result.stdout.strip()
                
                # Get remote URL
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir
                )
                if result.returncode == 0:
                    git_info['remote_url'] = result.stdout.strip()
                
                # Get recent commits
                result = subprocess.run(
                    ["git", "log", "-5", "--pretty=format:%s"],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir
                )
                if result.returncode == 0:
                    git_info['recent_commits'] = result.stdout.strip().split('\n')
        except Exception:
            pass
        
        return git_info
    
    def _detect_tech_stack(self):
        """Detect technologies used in the project"""
        tech_stack = {
            'languages': [],
            'frameworks': [],
            'tools': []
        }
        
        # Check for common files and patterns
        indicators = {
            'requirements.txt': ('Python', 'pip'),
            'setup.py': ('Python', 'setuptools'),
            'package.json': ('JavaScript/Node.js', 'npm'),
            'Cargo.toml': ('Rust', 'cargo'),
            'go.mod': ('Go', 'go modules'),
            'pom.xml': ('Java', 'Maven'),
            'build.gradle': ('Java/Kotlin', 'Gradle'),
            'Gemfile': ('Ruby', 'Bundler'),
            'composer.json': ('PHP', 'Composer'),
            'Dockerfile': (None, 'Docker'),
            '.gitignore': (None, 'Git')
        }
        
        for filename, (lang, tool) in indicators.items():
            if (self.current_dir / filename).exists():
                if lang and lang not in tech_stack['languages']:
                    tech_stack['languages'].append(lang)
                if tool and tool not in tech_stack['tools']:
                    tech_stack['tools'].append(tool)
        
        # Detect frameworks from file extensions
        py_files = list(self.current_dir.glob('**/*.py'))
        if py_files:
            if 'Python' not in tech_stack['languages']:
                tech_stack['languages'].append('Python')
        
        js_files = list(self.current_dir.glob('**/*.js'))
        if js_files:
            if 'JavaScript' not in tech_stack['languages']:
                tech_stack['languages'].append('JavaScript')
        
        return tech_stack
    
    def _read_existing_readme(self):
        """Read existing README.md if it exists"""
        readme_path = self.current_dir / "README.md"
        
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return None
        return None
    
    def _generate_content(self, structure, git_info, tech_stack, existing_readme):
        """Generate README content based on analysis"""
        project_name = self.current_dir.name
        
        # Build README sections
        sections = []
        
        # Header with project name
        sections.append(f"# {project_name}")
        sections.append("")
        
        # Project summary
        if existing_readme and "## " in existing_readme:
            # Try to preserve existing description
            lines = existing_readme.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        sections.append(lines[i + 1].strip())
                        break
            else:
                sections.append(self._generate_summary(structure, tech_stack))
        else:
            sections.append(self._generate_summary(structure, tech_stack))
        
        sections.append("")
        
        # Tech Stack section
        if tech_stack['languages'] or tech_stack['tools']:
            sections.append("## 🛠️ Tech Stack")
            sections.append("")
            
            if tech_stack['languages']:
                sections.append("**Languages:**")
                for lang in tech_stack['languages']:
                    sections.append(f"- {lang}")
                sections.append("")
            
            if tech_stack['tools']:
                sections.append("**Tools & Frameworks:**")
                for tool in tech_stack['tools']:
                    sections.append(f"- {tool}")
                sections.append("")
        
        # Features section
        sections.append("## ✨ Features")
        sections.append("")
        sections.append(self._generate_features(structure))
        sections.append("")
        
        # Installation section
        sections.append("## 📦 Installation")
        sections.append("")
        sections.append(self._generate_installation(tech_stack))
        sections.append("")
        
        # Usage section
        sections.append("## 🚀 Usage")
        sections.append("")
        sections.append(self._generate_usage(structure))
        sections.append("")
        
        # Project structure
        if structure['directories']:
            sections.append("## 📁 Project Structure")
            sections.append("")
            sections.append("```")
            sections.append(f"{project_name}/")
            for dir_path in sorted(structure['directories'])[:10]:  # Limit to 10
                sections.append(f"├── {dir_path}/")
            sections.append("```")
            sections.append("")
        
        # Contributing section
        sections.append("## 🤝 Contributing")
        sections.append("")
        sections.append("Contributions are welcome! Please feel free to submit a Pull Request.")
        sections.append("")
        
        # License section
        if (self.current_dir / "LICENSE").exists():
            sections.append("## 📄 License")
            sections.append("")
            sections.append("See [LICENSE](LICENSE) for details.")
            sections.append("")
        
        return '\n'.join(sections)
    
    def _generate_summary(self, structure, tech_stack):
        """Generate project summary"""
        langs = ', '.join(tech_stack['languages']) if tech_stack['languages'] else 'Multiple languages'
        return f"A {langs} project with {structure['total_files']} files across {len(structure['directories'])} directories."
    
    def _generate_features(self, structure):
        """Generate features list based on structure"""
        features = []
        
        # Analyze file patterns
        has_tests = any('test' in str(f).lower() for f in structure['files'])
        has_docs = any('doc' in str(f).lower() for f in structure['files'])
        has_config = any(str(f).endswith(('.json', '.yaml', '.yml', '.toml')) for f in structure['files'])
        
        if has_tests:
            features.append("- ✅ Comprehensive test suite")
        if has_docs:
            features.append("- 📚 Documentation included")
        if has_config:
            features.append("- ⚙️ Configurable settings")
        
        if not features:
            features.append("- 🚀 Lightweight and efficient")
            features.append("- 🔧 Easy to use")
        
        return '\n'.join(features)
    
    def _generate_installation(self, tech_stack):
        """Generate installation instructions"""
        instructions = []
        
        if 'Python' in tech_stack['languages']:
            instructions.append("```bash")
            instructions.append("# Clone the repository")
            instructions.append("git clone <repository-url>")
            instructions.append("")
            instructions.append("# Install dependencies")
            if 'pip' in tech_stack['tools']:
                instructions.append("pip install -r requirements.txt")
            instructions.append("```")
        elif 'JavaScript/Node.js' in tech_stack['languages']:
            instructions.append("```bash")
            instructions.append("# Clone the repository")
            instructions.append("git clone <repository-url>")
            instructions.append("")
            instructions.append("# Install dependencies")
            instructions.append("npm install")
            instructions.append("```")
        else:
            instructions.append("```bash")
            instructions.append("git clone <repository-url>")
            instructions.append("cd " + self.current_dir.name)
            instructions.append("```")
        
        return '\n'.join(instructions)
    
    def _generate_usage(self, structure):
        """Generate usage instructions"""
        # Look for main entry points
        main_files = [f for f in structure['files'] 
                     if f.name in ['main.py', 'app.py', 'index.js', 'main.js', 'index.html']]
        
        if main_files:
            main_file = main_files[0]
            if main_file.suffix == '.py':
                return f"```bash\npython {main_file}\n```"
            elif main_file.suffix == '.js':
                return f"```bash\nnode {main_file}\n```"
        
        return "```bash\n# Add usage instructions here\n```"
    
    def _save_readme(self, content):
        """Save README.md to disk"""
        readme_path = self.current_dir / "README.md"
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ README.md saved to: {readme_path}")
        except Exception as e:
            print(f"❌ Error saving README: {e}")