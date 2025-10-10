"""
Project structure viewer
"""
import os
from pathlib import Path


class StructureViewer:
    """Displays project structure"""
    
    EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "node_modules", ".venv", "venv"}
    
    def __init__(self):
        self.cwd = Path.cwd()
        self.parent = self.cwd.parent
    
    def list_dir_contents(self, base: Path, indent: int = 0):
        """List files and folders inside a given directory."""
        try:
            entries = sorted(
                base.iterdir(), 
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
        except PermissionError:
            return
        
        for entry in entries:
            if entry.name in self.EXCLUDE_DIRS or entry.name.startswith('.'):
                continue
            
            prefix = "  " * indent
            
            if entry.is_dir():
                print(f"{prefix}📁 {entry.name}/")
            else:
                # Mark executable files with *
                star = "*" if os.access(entry, os.X_OK) else ""
                size = entry.stat().st_size
                size_str = self.format_size(size)
                print(f"{prefix}📄 {entry.name}{star} ({size_str})")
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def show(self):
        """Show parent folder and list the structure of the current project."""
        print(f"\n{'='*60}")
        print(f"📂 PARENT DIRECTORY: {self.parent.name}")
        print(f"{'='*60}\n")
        
        try:
            # List parent contents
            for item in sorted(
                self.parent.iterdir(), 
                key=lambda x: (not x.is_dir(), x.name.lower())
            ):
                if item.name in self.EXCLUDE_DIRS or item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    marker = "📂" if item != self.cwd else "📂 ⭐"
                    print(f"{marker} {item.name}/")
                    
                    # Expand the current project folder
                    if item == self.cwd:
                        self.list_dir_contents(item, indent=1)
                        print()
                else:
                    size = item.stat().st_size
                    size_str = self.format_size(size)
                    print(f"📄 {item.name} ({size_str})")
        except PermissionError as e:
            print(f"❌ Permission denied: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print(f"\n{'='*60}")
        print(f"Current Directory: {self.cwd}")
        print(f"{'='*60}")


if __name__ == "__main__":
    viewer = StructureViewer()
    viewer.show()