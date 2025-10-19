"""
Menu System Module - Fixed Navigation
Removed buggy partial redraw - now does full clean refresh on navigation
"""
from abc import ABC, abstractmethod
import os
import sys
from pathlib import Path

# Try to import platform-specific modules
try:
    import tty
    import termios
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class MenuItem:
    """Represents a single menu item"""
    
    def __init__(self, label, action):
        self.label = label
        self.action = action
    
    def __repr__(self):
        return f"MenuItem(label='{self.label}')"


class Menu(ABC):
    """Abstract base class for all menus with smooth navigation"""
    
    def __init__(self, title):
        self.title = title
        self.items = []
        self._items_initialized = False
        self.setup_items()
        self._items_initialized = True
    
    @abstractmethod
    def setup_items(self):
        """Setup menu items - must be implemented by subclasses"""
        pass
    
    def display(self, selected_idx=0):
        """Display the complete menu with full screen refresh"""
        self.clear_screen()
        print("=" * 70)
        print(f"  {self.title}")
        print("=" * 70)
        print(f"  📍 Current Directory: {Path.cwd()}")
        print("=" * 70)
        
        # Print each item
        for i in range(len(self.items)):
            self._print_item(i, self.items[i], i == selected_idx)
        
        print("=" * 70)
        
        if HAS_TERMIOS or HAS_MSVCRT:
            print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
        else:
            print("\n  Type number and press Enter to select")
    
    def _print_item(self, index, item, is_selected):
        """Print a single menu item with correct formatting"""
        line_text = f"{index + 1}. {item.label}"
        
        if is_selected:
            full_line = f"  ► {line_text}"
            print(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            print(full_line)
    
    def get_choice_with_arrows(self):
        """Get user choice using arrow keys (if available)"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_navigation()
        else:
            return self._traditional_input()
    
    def _arrow_navigation(self):
        """Navigate with arrow keys - does full refresh on each navigation"""
        selected_idx = 0
        
        # Initial display
        self.display(selected_idx)
        
        while True:
            try:
                key = self._getch()
                
                old_idx = selected_idx
                
                if HAS_MSVCRT:  # Windows handling
                    if key in ('\xe0', '\x00'):
                        arrow = self._getch()
                        if arrow == 'H':  # Up arrow
                            selected_idx = (selected_idx - 1) % len(self.items)
                        elif arrow == 'P':  # Down arrow
                            selected_idx = (selected_idx + 1) % len(self.items)
                    elif key == '\r':  # Enter key
                        return selected_idx + 1
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(self.items):
                            return num
                    elif key == '\x03':  # Ctrl+C
                        print("\n\nExiting...")
                        return len(self.items)
                
                else:  # Unix/Linux/Mac handling
                    if key == '\x1b':  # ESC sequence
                        next_key = self._getch()
                        if next_key == '[':
                            arrow = self._getch()
                            if arrow == 'A':  # Up arrow
                                selected_idx = (selected_idx - 1) % len(self.items)
                            elif arrow == 'B':  # Down arrow
                                selected_idx = (selected_idx + 1) % len(self.items)
                    elif key in ['\r', '\n']:  # Enter key
                        return selected_idx + 1
                    elif key.isdigit():
                        num = int(key)
                        if 1 <= num <= len(self.items):
                            return num
                    elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                        print("\n\nExiting...")
                        return len(self.items)
                
                # If selection changed, redisplay entire menu
                if old_idx != selected_idx:
                    self.display(selected_idx)
                
            except Exception:
                continue
    
    def _traditional_input(self):
        """Traditional number input method"""
        self.display(0)
        
        while True:
            try:
                choice = input("\nEnter your choice: ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.items):
                    return choice_num
                print(f"Please enter a number between 1 and {len(self.items)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                return len(self.items)
    
    def _getch(self):
        """Get a single character from stdin"""
        if HAS_MSVCRT:  # Windows
            char = msvcrt.getch()
            try:
                return char.decode('utf-8')
            except:
                return chr(ord(char))
        elif HAS_TERMIOS:  # Unix/Linux/Mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch
        else:
            return input()
    
    def run(self):
        """Run the menu loop"""
        while True:
            choice = self.get_choice_with_arrows()
            
            # Execute the selected action
            result = self.items[choice - 1].action()
            
            if result == "exit":
                break
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')


class MainMenu(Menu):
    """Main menu for the automation system"""
    
    def __init__(self):
        # Initialize dependencies ONCE before calling parent __init__
        self._git_menu = None
        self._structure_viewer = None
        self._folder_nav = None
        
        super().__init__("🚀 Python Automation System - Main Menu")
    
    def setup_items(self):
        """Setup main menu items - called only once during initialization"""
        # Only create items if not already initialized
        if self.items:
            return
        
        # Import here to avoid circular imports
        from automation.git_operations import GitMenu
        from automation.structure_viewer import StructureViewer
        from automation.folder_navigator import FolderNavigator
        
        # Create instances once and reuse them
        if self._git_menu is None:
            self._git_menu = GitMenu()
        if self._structure_viewer is None:
            self._structure_viewer = StructureViewer()
        if self._folder_nav is None:
            self._folder_nav = FolderNavigator()
        
        # Create menu items with bound methods (not lambdas)
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Exit", self._exit_program)
        ]
    
    def _run_git_operations(self):
        """Run GitHub operations menu"""
        self._git_menu.run()
        return None
    
    def _show_structure(self):
        """Show project structure"""
        self._structure_viewer.show_structure()
        return None
    
    def _navigate_folders(self):
        """Navigate folders"""
        self._folder_nav.navigate()
        return None
    
    def _exit_program(self):
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  👋 Thanks for using Python Automation System!")
        print("  Made with ❤️  for developers")
        print("="*70 + "\n")
        return "exit"