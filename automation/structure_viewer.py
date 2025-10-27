"""
automation/structure_viewer.py
Intelligent Project Structure Viewer - Shows ALL Important Code

Features:
- Shows ALL directories with actual source code
- Respects .gitignore patterns
- Hides only true build artifacts, cache, and dependencies
- Shows hidden files only if they're important (.env, .gitignore)
- Works across all languages (Python, JavaScript, etc.)
"""
import os
import re
from pathlib import Path
from typing import Set, List, Optional, Tuple


class StructureViewer:
    """Intelligent project structure viewer"""
    
    # ONLY exclude true build artifacts and dependencies
    EXCLUDE_DIRS = {
        # Python
        "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
        ".eggs", "*.egg-info", ".coverage", "htmlcov",
        ".venv", "venv", "env", "ENV", "virtualenv",
        
        # JavaScript/Node
        "node_modules", ".next/cache", ".next/server", "out",
        ".nuxt", ".cache", ".parcel-cache", ".turbo",
        "bower_components",
        
        # Build outputs (ONLY generated files)
        "dist", "build", ".build", "target/debug", "target/release",
        
        # Version control and IDE (hidden)
        ".git", ".svn", ".hg",
        
        # OS files
        ".DS_Store", "Thumbs.db"
    }
    
    # Exclude ONLY generated files
    EXCLUDE_FILES = {
        # Compiled
        "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
        "*.class", "*.o", "*.obj",
        
        # Lock files
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "poetry.lock", "Pipfile.lock",
        
        # Minified/compiled assets
        "*.min.js", "*.min.css", "*.map",
        
        # OS
        ".DS_Store", "Thumbs.db", "desktop.ini",
        "*.swp", "*.swo", "*~"
    }
    
    # ALWAYS show these important files
    ALWAYS_SHOW = {
        ".env", ".env.example", ".env.template", ".env.development",
        ".gitignore", ".dockerignore", ".gitattributes",
        "README.md", "README.txt", "LICENSE", "CHANGELOG.md",
        "Dockerfile", "docker-compose.yml",
        ".prettierrc", ".prettierrc.json", ".prettierignore",
        ".eslintrc", ".eslintrc.js", ".eslintrc.json",
        "tsconfig.json", "jsconfig.json",
        "package.json", "setup.py", "pyproject.toml",
        "requirements.txt", "Cargo.toml", "go.mod",
        "Makefile", ".editorconfig"
    }
    
    # Source code extensions (if a directory has these, it's important)
    SOURCE_EXTENSIONS = {
        # Python
        '.py', '.pyx', '.pxd',
        # JavaScript/TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
        # Vue/React/Svelte
        '.vue', '.svelte',
        # Web
        '.html', '.css', '.scss', '.sass', '.less',
        # Config that might be in folders
        '.json', '.yaml', '.yml', '.toml', '.ini',
        # Other languages
        '.java', '.kt', '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
        '.rb', '.php', '.swift', '.m', '.mm',
        # Scripts
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        # Data/Templates
        '.sql', '.graphql', '.prisma', '.proto',
        '.md', '.rst', '.txt'
    }
    
    def __init__(self, max_depth: int = 5, max_files_per_dir: int = 100):
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
    
    def show_structure(self):
        """Display intelligent project structure"""
        self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("📁 PROJECT STRUCTURE")
        print("="*70)
        print(f"\n📍 Current Directory: {self.current_dir.name}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}")
        
        # Load .gitignore patterns
        self._load_gitignore()
        
        print("\n💡 Showing: All source code and important files")
        print(f"   Hiding: Build artifacts, dependencies, cache")
        print(f"   Max depth: {self.max_depth} levels\n")
        
        # Generate the tree structure
        tree_lines = self._generate_tree(self.current_dir)
        
        print("```")
        print(f"{self.current_dir.name}/")
        for line in tree_lines:
            print(line)
        print("```")
        
        # Show summary
        file_count, dir_count = self._count_items(self.current_dir)
        print(f"\n📊 Summary: {dir_count} directories, {file_count} files")
        print("="*70 + "\n")
        
        input("Press Enter to continue...")
    
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
        
        except Exception:
            pass
    
    def _should_exclude(self, path: Path, is_dir: bool = False) -> bool:
        """
        Determine if path should be excluded
        
        Strategy:
        1. NEVER exclude if it's an ALWAYS_SHOW file
        2. NEVER exclude if directory contains source code
        3. ONLY exclude if it's in EXCLUDE_DIRS/FILES or .gitignore
        4. For hidden files (starting with .), exclude unless important
        
        Args:
            path: Path to check
            is_dir: Whether it's a directory
        
        Returns:
            True if should be excluded
        """
        name = path.name
        
        # Rule 1: Never exclude always-show files
        if name in self.ALWAYS_SHOW:
            return False
        
        # Rule 2: Hidden files - only show if important
        if name.startswith('.') and name not in self.ALWAYS_SHOW:
            # Allow hidden directories that might contain code
            if is_dir:
                # Check if it has source code inside
                if self._has_source_code(path):
                    return False
            # Exclude other hidden files
            return True
        
        # Rule 3: Check explicit exclude lists
        if is_dir:
            if name in self.EXCLUDE_DIRS:
                return True
        else:
            for pattern in self.EXCLUDE_FILES:
                if self._matches_pattern(name, pattern):
                    return True
        
        # Rule 4: Check .gitignore
        try:
            relative_path = str(path.relative_to(self.current_dir))
            for pattern in self.gitignore_patterns:
                if self._matches_gitignore(relative_path, pattern, is_dir):
                    # But still show if it's a directory with source code
                    if is_dir and self._has_source_code(path):
                        return False
                    return True
        except ValueError:
            pass
        
        return False
    
    def _has_source_code(self, directory: Path) -> bool:
        """
        Check if directory contains actual source code files
        
        Args:
            directory: Directory to check
        
        Returns:
            True if contains source files
        """
        try:
            # Quick check: look at immediate children
            for item in directory.iterdir():
                if item.is_file():
                    # Check if it's a source file
                    if item.suffix in self.SOURCE_EXTENSIONS:
                        return True
                    # Check if it's an important file
                    if item.name in self.ALWAYS_SHOW:
                        return True
                elif item.is_dir():
                    # Recursively check subdirectories (but limit depth)
                    if not item.name.startswith('.'):
                        if self._has_source_code_shallow(item):
                            return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _has_source_code_shallow(self, directory: Path, depth: int = 0) -> bool:
        """Shallow recursive check for source code (max 2 levels deep)"""
        if depth > 1:
            return False
        
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix in self.SOURCE_EXTENSIONS:
                    return True
                elif item.is_dir() and not item.name.startswith('.'):
                    if self._has_source_code_shallow(item, depth + 1):
                        return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if name matches wildcard pattern"""
        pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
        return bool(re.match(f'^{pattern_regex}$', name))
    
    def _matches_gitignore(self, path: str, pattern: str, is_dir: bool) -> bool:
        """Check if path matches .gitignore pattern"""
        # Handle trailing slash (directory-only patterns)
        if pattern.endswith('/'):
            if not is_dir:
                return False
            pattern = pattern[:-1]
        
        # Handle leading slash (root-relative patterns)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            return path == pattern or path.startswith(pattern + '/')
        
        # Handle wildcards
        if '*' in pattern:
            pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
            return bool(re.search(pattern_regex, path))
        
        # Simple substring match
        path_parts = path.split('/')
        return pattern in path_parts or path.endswith('/' + pattern)
    
    def _generate_tree(
        self,
        directory: Path,
        prefix: str = "",
        depth: int = 0
    ) -> List[str]:
        """
        Generate tree structure
        
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
            items = sorted(
                directory.iterdir(),
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            
            # Filter out excluded items
            filtered_items = []
            for item in items:
                if not self._should_exclude(item, item.is_dir()):
                    filtered_items.append(item)
            
            # Limit items if too many
            if len(filtered_items) > self.max_files_per_dir:
                shown_items = filtered_items[:self.max_files_per_dir]
                hidden_count = len(filtered_items) - self.max_files_per_dir
            else:
                shown_items = filtered_items
                hidden_count = 0
            
            # Generate lines for each item
            for i, item in enumerate(shown_items):
                is_last = (i == len(shown_items) - 1) and (hidden_count == 0)
                
                # Tree characters
                if is_last:
                    current_prefix = "└── "
                    next_prefix = "    "
                else:
                    current_prefix = "├── "
                    next_prefix = "│   "
                
                # Display name with size for files
                if item.is_dir():
                    display_name = f"{item.name}/"
                else:
                    try:
                        size = self._format_size(item.stat().st_size)
                        display_name = f"{item.name} ({size})"
                    except:
                        display_name = item.name
                
                lines.append(f"{prefix}{current_prefix}{display_name}")
                
                # Recurse into subdirectories
                if item.is_dir():
                    sublines = self._generate_tree(
                        item,
                        prefix + next_prefix,
                        depth + 1
                    )
                    lines.extend(sublines)
            
            # Show hidden count if any
            if hidden_count > 0:
                lines.append(f"{prefix}└── ... and {hidden_count} more items")
        
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
        Count files and directories recursively
        
        Returns:
            Tuple of (file_count, dir_count)
        """
        file_count = 0
        dir_count = 0
        
        def count_recursive(path: Path, depth: int):
            nonlocal file_count, dir_count
            
            if depth > self.max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if self._should_exclude(item, item.is_dir()):
                        continue
                    
                    if item.is_file():
                        file_count += 1
                    elif item.is_dir():
                        dir_count += 1
                        count_recursive(item, depth + 1)
            except (PermissionError, OSError):
                pass
        
        count_recursive(directory, 0)
        return file_count, dir_count


# Test
if __name__ == "__main__":
    viewer = StructureViewer(max_depth=5)
    viewer.show_structure()