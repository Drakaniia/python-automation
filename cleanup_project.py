#!/usr/bin/env python3
"""
Project Cleanup Script
Removes unnecessary files and directories to simplify the project structure
"""
import os
import shutil
from pathlib import Path


def cleanup_project():
    """Remove unnecessary directories and files"""
    
    # Current directory
    base_dir = Path.cwd()
    
    # Directories to remove
    dirs_to_remove = [
        'htmlcov',           # Coverage HTML reports
        'scripts',           # Benchmark scripts
        '.benchmarks',       # Benchmark data
        '.pytest_cache',     # Pytest cache
        'docs',              # Documentation (keeping README.md)
    ]
    
    # Files to remove
    files_to_remove = [
        '.coverage',         # Coverage data file
        'run_test.bat',      # Windows test runner
        'run_all_test.sh',   # Shell test runner
        'COMMAND.md',        # Command documentation
        'RUN.md',            # Run documentation
        'FOLDER_STRUCTURE.MD',  # Folder structure doc
    ]
    
    print("🧹 Cleaning up project...")
    print("=" * 70)
    
    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = base_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed directory: {dir_name}/")
            except Exception as e:
                print(f"❌ Failed to remove {dir_name}/: {e}")
        else:
            print(f"⏭️  Skipped (not found): {dir_name}/")
    
    print()
    
    # Remove files
    for file_name in files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists() and file_path.is_file():
            try:
                file_path.unlink()
                print(f"✅ Removed file: {file_name}")
            except Exception as e:
                print(f"❌ Failed to remove {file_name}: {e}")
        else:
            print(f"⏭️  Skipped (not found): {file_name}")
    
    print()
    print("=" * 70)
    print("✨ Cleanup complete!")
    print()
    
    # Show what's left
    print("📁 Remaining project structure:")
    print()
    print("python-automation/")
    print("├── automation/          # Core package")
    print("│   ├── core/           # Git client & exceptions")
    print("│   ├── github/         # Git operations")
    print("│   ├── menu.py")
    print("│   ├── folder_navigator.py")
    print("│   └── structure_viewer.py")
    print("├── tests/              # Test suite")
    print("│   ├── conftest.py")
    print("│   ├── test_exceptions.py")
    print("│   ├── test_git_client.py")
    print("│   ├── test_git_push.py")
    print("│   ├── test_integration.py")
    print("│   └── test_performance.py")
    print("├── .gitignore")
    print("├── .commit_cache.json")
    print("├── CHANGELOG.md")
    print("├── LICENSE")
    print("├── main.py")
    print("├── README.md")
    print("├── requirements-test.txt")
    print("└── setup.sh")
    print()
    
    # Update .gitignore
    update_gitignore(base_dir)


def update_gitignore(base_dir):
    """Update .gitignore to ignore test artifacts"""
    gitignore_path = base_dir / '.gitignore'
    
    # Lines to ensure are in .gitignore
    essential_ignores = [
        "# Test artifacts",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".benchmarks/",
        "",
        "# Coverage reports",
        "*.cover",
        "coverage.xml",
        "",
    ]
    
    try:
        # Read existing content
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # Check if test artifacts section exists
        if "# Test artifacts" not in existing_content:
            print("📝 Updating .gitignore...")
            
            # Add essential ignores
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write("\n")
                for line in essential_ignores:
                    f.write(line + "\n")
            
            print("✅ Updated .gitignore with test artifact rules")
        else:
            print("✅ .gitignore already up to date")
    
    except Exception as e:
        print(f"⚠️  Could not update .gitignore: {e}")


def show_cleanup_summary():
    """Show summary of what will be removed"""
    print("\n📋 Cleanup Summary")
    print("=" * 70)
    print("\nThe following will be removed:")
    print("\n📁 Directories:")
    print("  • htmlcov/         - HTML coverage reports")
    print("  • scripts/         - Benchmark scripts")
    print("  • .benchmarks/     - Benchmark data")
    print("  • .pytest_cache/   - Pytest cache")
    print("  • docs/            - Documentation folder")
    print("\n📄 Files:")
    print("  • .coverage        - Coverage data")
    print("  • run_test.bat     - Windows test runner")
    print("  • run_all_test.sh  - Shell test runner")
    print("  • COMMAND.md       - Command docs")
    print("  • RUN.md           - Run docs")
    print("  • FOLDER_STRUCTURE.MD - Structure docs")
    print("\n✅ Keeping:")
    print("  • All source code (automation/)")
    print("  • Tests (tests/)")
    print("  • Main documentation (README.md)")
    print("  • License and changelog")
    print("  • Setup script (setup.sh)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    import sys
    
    print("🚀 Python Automation System - Cleanup Tool")
    print("=" * 70)
    
    # Show what will be removed
    show_cleanup_summary()
    
    # Confirm
    response = input("\n❓ Proceed with cleanup? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        cleanup_project()
        print("\n💡 Note: Run 'git add -A' and 'git commit' to save these changes")
        print("💡 Removed directories can still be regenerated by running tests")
    else:
        print("\n❌ Cleanup cancelled")
        sys.exit(0)