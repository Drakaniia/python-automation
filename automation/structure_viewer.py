"""
automation/structure_viewer.py
Smart Project Structure Viewer - Focuses on Essential Files Only

Features:
- Respects .gitignore patterns
- Smart filtering of common unnecessary files
- Configurable depth limits
- Special handling for common project types (frontend, backend, etc.)
- Shows only crucial files (.env, config files, src/, etc.)
"""
import os
import re
from pathlib import Path
from typing import Set, List, Optional, Tuple


class StructureViewer:
    """Smart project structure viewer with intelligent filtering"""
    
    # Common directories to always exclude (even if not in .gitignore)
    ALWAYS_EXCLUDE_DIRS = {
        "__pycache__", ".git", ".pytest_cache", ".mypy_cache", ".tox",
        ".eggs", "*.egg-info", ".coverage", "htmlcov", ".benchmarks",
        ".venv", "venv", "env", "ENV", "virtualenv",
        "node_modules", ".next", ".nuxt", "out", "dist", "build",
        ".cache", ".parcel-cache", ".turbo", ".vercel",
        "vendor", "bower_components",
        ".idea", ".vscode", ".vs", ".DS_Store",
        "tmp", "temp", "logs", "*.log"
    }
    
    # Common files to exclude
    ALWAYS_EXCLUDE_FILES = {
        "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
        "*.class", "*.o", "*.obj",
        ".DS_Store", "Thumbs.db", "desktop.ini",
        "*.swp", "*.swo", "*~", ".*.swp",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "poetry.lock", "Pipfile.lock",
        "*.map", "*.min.js", "*.min.css",
        ".env.local", ".env.*.local"
    }
    
    # Files to ALWAYS show (even if normally excluded)
    ALWAYS_SHOW_FILES = {
        ".env", ".env.example", ".env.template",
        ".gitignore", ".dockerignore",
        "README.md", "README.txt", "LICENSE", "LICENSE.txt",
        "Dockerfile", "docker-compose.yml",
        ".prettierrc", ".eslintrc", ".eslintrc.js", ".eslintrc.json",
        "tsconfig.json", "jsconfig.json",
        "package.json", "setup.py", "pyproject.toml",
        "requirements.txt", "Pipfile", "Cargo.toml",
        ".gitattributes", ".editorconfig"
    }
    
    # Important directories to always explore
    IMPORTANT_DIRS = {
        "src", "app", "pages", "components", "lib", "utils",
        "api", "routes", "views", "controllers", "models",
        "public", "static", "assets",
        "config", "configs", "settings",
        "tests", "test", "__tests__",
        "docs", "documentation",
        "scripts", "bin"
    }
    
    # File patterns that indicate project type
    PROJECT_MARKERS = {
        "frontend": ["package.json", "next.config.js", "vite.config.js", "webpack.config.js"],
        "react": ["package.json", "src/App.tsx", "src/App.jsx"],
        "nextjs": ["next.config.js", "app/", "pages/"],
        "vue": ["vue.config.js", "nuxt.config.js"],
        "python": ["setup.py", "pyproject.toml", "requirements.txt"],
        "django": ["manage.py", "settings.py"],
        "flask": ["app.py", "wsgi.py"],
    }
    
    def __init__(self, max_depth: int = 4, max_files_per_dir: int = 50):
        """
        Initialize structure viewer
        
        Args:
            max_depth: Maximum directory depth to explore
            max_files_per_dir: Maximum files to show per directory
        """
        self.current_dir = Path.cwd()
        self.max_depth = max_depth
        self.max_files_per_dir = max_files_per_dir
        self.gitignore_patterns: Set[str] = set()
        self.project_type: Optional[str] = None
    
    def show_structure(self):
        """Display smart project structure"""
        # Update to current working directory
        self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("📁 SMART PROJECT STRUCTURE")
        print("="*70)
        print(f"\n📍 Current Directory: {self.current_dir.name}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}")
        
        # Detect project type
        self.project_type = self._detect_project_type()
        if self.project_type:
            print(f"🔍 Detected: {self.project_type.upper()} project")
        
        # Load .gitignore patterns
        self._load_gitignore()
        
        print("\n💡 Showing: Essential files and directories only")
        print(f"   Max depth: {self.max_depth} levels")
        print(f"   Filters: .gitignore + smart exclusions\n")
        
        # Generate the tree structure
        tree_lines = self._generate_smart_tree(self.current_dir)
        
        print("```")
        print(f"{self.current_dir.name}/")
        for line in tree_lines:
            print(line)
        print("```")
        
        # Show summary
        file_count, dir_count = self._count_items(self.current_dir)
        print(f"\n📊 Showing: {dir_count} directories, {file_count} files")
        print(f"   (Filtered from larger codebase)")
        print("="*70 + "\n")
        
        input("Press Enter to continue...")
    
    def _detect_project_type(self) -> Optional[str]:
        """Detect project type based on markers"""
        for project_type, markers in self.PROJECT_MARKERS.items():
            for marker in markers:
                marker_path = self.current_dir / marker
                if marker_path.exists():
                    return project_type
        return None
    
    def _load_gitignore(self):
        """Load and parse .gitignore patterns"""
        gitignore_path = self.current_dir / ".gitignore"
        
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Store pattern
                    self.gitignore_patterns.add(line)
        
        except Exception as e:
            print(f"⚠️  Could not read .gitignore: {e}")
    
    def _should_exclude_path(self, path: Path, is_dir: bool = False) -> bool:
        """
        Determine if a path should be excluded
        
        Args:
            path: Path to check
            is_dir: Whether the path is a directory
        
        Returns:
            True if path should be excluded
        """
        name = path.name
        relative_path = str(path.relative_to(self.current_dir))
        
        # Never exclude always-show files
        if name in self.ALWAYS_SHOW_FILES:
            return False
        
        # Always exclude certain patterns
        if is_dir:
            if name in self.ALWAYS_EXCLUDE_DIRS:
                return True
        else:
            # Check file patterns
            for pattern in self.ALWAYS_EXCLUDE_FILES:
                if self._matches_pattern(name, pattern):
                    return True
        
        # Check .gitignore patterns
        for pattern in self.gitignore_patterns:
            if self._matches_gitignore_pattern(relative_path, pattern, is_dir):
                return True
        
        return False
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if name matches a wildcard pattern"""
        # Simple wildcard matching
        pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
        return bool(re.match(f'^{pattern_regex}$', name))
    
    def _matches_gitignore_pattern(self, path: str, pattern: str, is_dir: bool) -> bool:
        """Check if path matches .gitignore pattern"""
        # Handle trailing slash (directory-only patterns)
        if pattern.endswith('/'):
            if not is_dir:
                return False
            pattern = pattern[:-1]
        
        # Handle leading slash (root-relative patterns)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Check exact match from root
            return path == pattern or path.startswith(pattern + '/')
        
        # Handle wildcards
        if '*' in pattern:
            pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
            return bool(re.search(pattern_regex, path))
        
        # Simple substring match
        path_parts = path.split('/')
        return pattern in path_parts or path.endswith('/' + pattern)
    
    def _is_important_dir(self, dir_path: Path) -> bool:
        """Check if directory is important and should be explored"""
        name = dir_path.name.lower()
        return name in self.IMPORTANT_DIRS
    
    def _is_config_or_doc_file(self, file_path: Path) -> bool:
        """Check if file is a configuration or documentation file"""
        name = file_path.name.lower()
        
        # Configuration files
        config_patterns = [
            '.config.', 'config.', '.rc', 'rc.',
            '.json', '.yaml', '.yml', '.toml', '.ini',
            '.conf', 'file', 'ignore'
        ]
        
        # Documentation files
        doc_patterns = [
            'readme', 'license', 'changelog', 'contributing',
            'authors', 'todo', 'makefile', 'dockerfile'
        ]
        
        name_lower = name.lower()
        
        # Check config patterns
        for pattern in config_patterns:
            if pattern in name_lower:
                return True
        
        # Check doc patterns
        for pattern in doc_patterns:
            if pattern in name_lower:
                return True
        
        # Check extensions
        important_extensions = {
            '.md', '.txt', '.rst', '.json', '.yaml', '.yml',
            '.toml', '.env', '.sh', '.bat', '.ps1'
        }
        
        return file_path.suffix.lower() in important_extensions
    
    def _generate_smart_tree(
        self,
        directory: Path,
        prefix: str = "",
        depth: int = 0
    ) -> List[str]:
        """
        Generate smart tree structure with intelligent filtering
        
        Args:
            directory: Directory to scan
            prefix: Prefix for tree lines
            depth: Current depth level
        
        Returns:
            List of tree lines
        """
        if depth >= self.max_depth:
            return []
        
        lines = []
        
        try:
            # Get all items
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            # Filter items
            filtered_items = []
            
            for item in items:
                is_dir = item.is_dir()
                
                # Check if should exclude
                if self._should_exclude_path(item, is_dir):
                    continue
                
                # For directories: include if important or has important content
                if is_dir:
                    if self._is_important_dir(item):
                        filtered_items.append(item)
                    elif depth < 2:  # Show some top-level dirs
                        filtered_items.append(item)
                else:
                    # For files: include if important or in important dir
                    if item.name in self.ALWAYS_SHOW_FILES:
                        filtered_items.append(item)
                    elif self._is_config_or_doc_file(item):
                        filtered_items.append(item)
                    elif depth <= 1:  # Show root-level files
                        filtered_items.append(item)
                    elif self._is_important_dir(directory):  # In important dir
                        filtered_items.append(item)
            
            # Limit items per directory
            if len(filtered_items) > self.max_files_per_dir:
                shown_items = filtered_items[:self.max_files_per_dir]
                hidden_count = len(filtered_items) - self.max_files_per_dir
            else:
                shown_items = filtered_items
                hidden_count = 0
            
            for i, item in enumerate(shown_items):
                is_last = (i == len(shown_items) - 1) and (hidden_count == 0)
                
                # Tree characters
                if is_last:
                    current_prefix = "└── "
                    next_prefix = "    "
                else:
                    current_prefix = "├── "
                    next_prefix = "│   "
                
                # Display name
                if item.is_dir():
                    display_name = f"{item.name}/"
                else:
                    # Add file size for files
                    try:
                        size = self._format_size(item.stat().st_size)
                        display_name = f"{item.name} ({size})"
                    except:
                        display_name = item.name
                
                lines.append(f"{prefix}{current_prefix}{display_name}")
                
                # Recurse into subdirectories
                if item.is_dir():
                    sublines = self._generate_smart_tree(
                        item,
                        prefix + next_prefix,
                        depth + 1
                    )
                    lines.extend(sublines)
            
            # Show hidden count if any
            if hidden_count > 0:
                lines.append(f"{prefix}└── ... and {hidden_count} more files")
        
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
        except Exception as e:
            lines.append(f"{prefix}[Error: {str(e)[:30]}]")
        
        return lines
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def _count_items(self, directory: Path) -> Tuple[int, int]:
        """
        Count files and directories (respecting filters)
        
        Returns:
            Tuple of (file_count, dir_count)
        """
        file_count = 0
        dir_count = 0
        
        try:
            for item in directory.rglob("*"):
                # Skip excluded paths
                if self._should_exclude_path(item, item.is_dir()):
                    continue
                
                # Check depth
                try:
                    depth = len(item.relative_to(directory).parts)
                    if depth > self.max_depth:
                        continue
                except ValueError:
                    continue
                
                if item.is_file():
                    # Only count if it would be shown
                    if (item.name in self.ALWAYS_SHOW_FILES or 
                        self._is_config_or_doc_file(item) or
                        self._is_important_dir(item.parent)):
                        file_count += 1
                elif item.is_dir():
                    if self._is_important_dir(item) or depth <= 2:
                        dir_count += 1
        
        except PermissionError:
            pass
        except Exception:
            pass
        
        return file_count, dir_count


# Standalone test
if __name__ == "__main__":
    print("Testing Smart Structure Viewer")
    print("="*70 + "\n")
    
    viewer = StructureViewer(max_depth=4, max_files_per_dir=30)
    viewer.show_structure()