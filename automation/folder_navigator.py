"""
Folder Navigator Module
Interactive directory navigation system with persistent working directory
"""
import os
from pathlib import Path
from automation.menu import Menu, MenuItem


class FolderNavigator:
    """Handles interactive folder navigation"""
    
    def __init__(self):
        # Use the current working directory (don't reset it)
        self.current_path = Path.cwd()
    
    def navigate(self):
        """Start the interactive navigation loop"""
        while True:
            self._clear_screen()
            print("="*70)
            print("📂 FOLDER NAVIGATOR")
            print("="*70)
            print(f"\n📍 Current Location: {self.current_path}")
            print(f"📍 Absolute Path: {self.current_path.absolute()}\n")
            
            # Get subdirectories
            subdirs = self._get_subdirectories()
            
            if not subdirs:
                print("📭 No subdirectories found in current location.\n")
            else:
                print("📁 Available Directories:")
                print("-" * 70)
                for idx, subdir in enumerate(subdirs, 1):
                    print(f"  {idx}. {subdir.name}/")
                print("-" * 70 + "\n")
            
            # Show options
            print("Navigation Options:")
            print("  • Enter number to navigate into directory")
            print("  • Type 'back' or '..' to go up one level")
            print("  • Type 'home' to go to home directory")
            print("  • Type 'exit' or 'q' to return to main menu\n")
            
            choice = input("Your choice: ").strip().lower()
            
            # Handle exit - DON'T change directory back, stay where we are
            if choice in ['exit', 'q']:
                # Keep the current directory - this is the fix!
                print(f"\n✅ Staying in: {self.current_path}")
                print("⚠️  All operations will now work in this directory.\n")
                input("Press Enter to return to main menu...")
                break
            
            # Handle going back
            elif choice in ['back', '..']:
                self._go_up()
            
            # Handle home directory
            elif choice == 'home':
                self.current_path = Path.home()
                os.chdir(self.current_path)
                print(f"\n✅ Navigated to home directory: {self.current_path}")
                input("\nPress Enter to continue...")
            
            # Handle numeric input
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(subdirs):
                    self._enter_directory(subdirs[idx - 1])
                else:
                    print(f"\n❌ Invalid choice. Please enter a number between 1 and {len(subdirs)}")
                    input("\nPress Enter to continue...")
            
            else:
                print("\n❌ Invalid input. Please try again.")
                input("\nPress Enter to continue...")
    
    def _get_subdirectories(self):
        """Get list of subdirectories in current path"""
        try:
            subdirs = [item for item in self.current_path.iterdir() 
                      if item.is_dir() and not item.name.startswith('.')]
            return sorted(subdirs, key=lambda x: x.name.lower())
        except PermissionError:
            print("❌ Permission denied to read this directory")
            return []
    
    def _enter_directory(self, target_dir):
        """Enter a subdirectory"""
        try:
            self.current_path = target_dir
            os.chdir(self.current_path)
            print(f"\n✅ Entered: {target_dir.name}/")
            input("\nPress Enter to continue...")
        except PermissionError:
            print(f"\n❌ Permission denied: {target_dir.name}")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def _go_up(self):
        """Go up one directory level"""
        parent = self.current_path.parent
        if parent != self.current_path:  # Check if we can go up
            self.current_path = parent
            os.chdir(self.current_path)
            print(f"\n✅ Moved up to: {self.current_path}")
        else:
            print("\n⚠️  Already at root directory")
        input("\nPress Enter to continue...")
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')


class FolderNavigatorMenu(Menu):
    """Menu for folder navigation"""
    
    def __init__(self):
        self.navigator = FolderNavigator()
        super().__init__("Folder Navigator")
    
    def setup_items(self):
        """Setup menu items"""
        self.items = [
            MenuItem("Start Navigation", lambda: self.navigator.navigate()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]