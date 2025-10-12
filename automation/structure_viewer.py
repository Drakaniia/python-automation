"""
Project Structure Viewer Module
Displays the current directory structure in an AI-readable format
"""
import os
from pathlib import Path


class StructureViewer:
    """Handles project structure visualization"""
    
    # Directories to exclude from the tree
    EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env"}
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def show_structure(self):
        """Display current directory structure in AI-readable format"""
        # Update to current working directory
        self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("📁 PROJECT STRUCTURE (AI-Readable Format)")
        print("="*70)
        print(f"\n📍 Current Directory: {self.current_dir}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}\n")
        
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
    
    def _generate_tree(self, directory, prefix="", is_last=True):
        """Generate tree structure recursively"""
        lines = []
        
        try:
            # Get all items and sort them (directories first, then files)
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            # Filter out excluded directories
            items = [item for item in items if item.name not in self.EXCLUDE_DIRS]
            
            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)
                
                # Determine the tree characters
                if is_last_item:
                    current_prefix = "└── "
                    next_prefix = "    "
                else:
                    current_prefix = "├── "
                    next_prefix = "│   "
                
                # Add file/directory indicator
                if item.is_dir():
                    display_name = f"{item.name}/"
                else:
                    # Add file size for files
                    size = self._format_size(item.stat().st_size)
                    display_name = f"{item.name} ({size})"
                
                lines.append(f"{prefix}{current_prefix}{display_name}")
                
                # Recurse into subdirectories
                if item.is_dir():
                    sublines = self._generate_tree(item, prefix + next_prefix, is_last_item)
                    lines.extend(sublines)
        
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
        
        return lines
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def _count_items(self, directory):
        """Count files and directories recursively"""
        file_count = 0
        dir_count = 0
        
        try:
            for item in directory.rglob("*"):
                # Skip excluded directories
                if any(excluded in item.parts for excluded in self.EXCLUDE_DIRS):
                    continue
                
                if item.is_file():
                    file_count += 1
                elif item.is_dir():
                    dir_count += 1
        except PermissionError:
            pass
        
        return file_count, dir_count