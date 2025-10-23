#!/usr/bin/env python3
"""
Disable Git Hooks Script
Removes or disables problematic Git hooks
"""
import os
from pathlib import Path
import shutil


def disable_git_hooks():
    """Disable all Git hooks by renaming them"""
    git_dir = Path.cwd() / '.git'
    
    if not git_dir.exists():
        print("❌ Not a git repository")
        return False
    
    hooks_dir = git_dir / 'hooks'
    
    if not hooks_dir.exists():
        print("ℹ️  No hooks directory found")
        return True
    
    # Find all hook files
    hook_files = [f for f in hooks_dir.iterdir() 
                  if f.is_file() and not f.name.endswith('.disabled')]
    
    if not hook_files:
        print("ℹ️  No active hooks found")
        return True
    
    print(f"Found {len(hook_files)} hook(s):\n")
    
    for hook_file in hook_files:
        print(f"  • {hook_file.name}")
    
    print("\nOptions:")
    print("  1. Disable all hooks (rename to .disabled)")
    print("  2. Delete all hooks")
    print("  3. Disable only pre-push hook")
    print("  4. Cancel")
    
    choice = input("\nYour choice (1-4): ").strip()
    
    if choice == '1':
        # Rename all hooks
        for hook_file in hook_files:
            new_name = hook_file.with_suffix('.disabled')
            hook_file.rename(new_name)
            print(f"✅ Disabled: {hook_file.name}")
        print("\n✅ All hooks disabled!")
        
    elif choice == '2':
        # Delete all hooks
        confirm = input("⚠️  Delete ALL hooks? Type 'YES' to confirm: ").strip()
        if confirm == 'YES':
            for hook_file in hook_files:
                hook_file.unlink()
                print(f"✅ Deleted: {hook_file.name}")
            print("\n✅ All hooks deleted!")
        else:
            print("❌ Cancelled")
            
    elif choice == '3':
        # Disable only pre-push
        pre_push = hooks_dir / 'pre-push'
        if pre_push.exists():
            pre_push.rename(hooks_dir / 'pre-push.disabled')
            print("✅ Disabled pre-push hook")
        else:
            print("ℹ️  No pre-push hook found")
            
    elif choice == '4':
        print("❌ Cancelled")
        return False
    else:
        print("❌ Invalid choice")
        return False
    
    return True


def show_hook_status():
    """Show current hook status"""
    git_dir = Path.cwd() / '.git'
    hooks_dir = git_dir / 'hooks'
    
    if not hooks_dir.exists():
        print("No hooks directory")
        return
    
    active = [f.name for f in hooks_dir.iterdir() 
              if f.is_file() and not f.name.endswith('.disabled')]
    disabled = [f.name for f in hooks_dir.iterdir() 
                if f.name.endswith('.disabled')]
    
    print("\n" + "="*50)
    print("GIT HOOKS STATUS")
    print("="*50)
    
    if active:
        print("\n✅ Active Hooks:")
        for hook in active:
            print(f"  • {hook}")
    else:
        print("\n✅ No active hooks")
    
    if disabled:
        print("\n⏸️  Disabled Hooks:")
        for hook in disabled:
            print(f"  • {hook}")
    
    print("="*50 + "\n")


if __name__ == '__main__':
    print("="*50)
    print("Git Hooks Manager")
    print("="*50 + "\n")
    
    show_hook_status()
    
    print("What would you like to do?")
    print("  1. Disable/Delete hooks")
    print("  2. Just show status (done above)")
    print("  3. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        disable_git_hooks()
        print()
        show_hook_status()
    elif choice == '2':
        pass  # Already shown
    else:
        print("Exiting...")