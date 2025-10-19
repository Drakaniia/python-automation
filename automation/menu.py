"""
Menu System Module - Complete Fix for Navigation Issues
Prevents duplication and ensures smooth, stable navigation
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
    
    # ANSI escape codes
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_LINE = '\033[2K'
    
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
        """Display the complete menu"""
        self.clear_screen()
        self._print_menu(selected_idx)
    
    def _print_menu(self, selected_idx):
        """Print the entire menu with proper formatting"""
        print("=" * 70)
        print(f"  {self.title}")
        print("=" * 70)
        print(f"  📍 Current Directory: {Path.cwd()}")
        print("=" * 70)
        
        # Print each item exactly once
        for i in range(len(self.items)):
            self._print_item(i, self.items[i], i == selected_idx)
        
        print("=" * 70)
        
        if HAS_TERMIOS or HAS_MSVCRT:
            print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
        else:
            print("\n  Type number and press Enter to select")
    
    def _print_item(self, index, item, is_selected):
        """Print a single menu item with correct formatting"""
        # Create the base line
        line_text = f"{index + 1}. {item.label}"
        
        if is_selected:
            # Selected item with arrow and highlight
            full_line = f"  ► {line_text}"
            # Pad to exactly 68 characters
            full_line = full_line.ljust(68)
            print(f"\033[1;46m{full_line}\033[0m")
        else:
            # Unselected item
            full_line = f"    {line_text}"
            # Pad to exactly 68 characters
            full_line = full_line.ljust(68)
            print(full_line)
    
    def _redraw_item(self, index, is_selected):
        """Redraw a single menu item at its position without affecting others"""
        if index < 0 or index >= len(self.items):
            return
        
        # Calculate absolute line position
        # Header: line 1-5 (separator, title, separator, directory, separator)
        # Menu items start at line 6
        line_num = 6 + index
        
        # Move cursor to line and clear it
        sys.stdout.write(f'\033[{line_num};1H{self.CLEAR_LINE}')
        sys.stdout.flush()
        
        # Get the item
        item = self.items[index]
        line_text = f"{index + 1}. {item.label}"
        
        if is_selected:
            full_line = f"  ► {line_text}"
            full_line = full_line.ljust(68)
            sys.stdout.write(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            full_line = full_line.ljust(68)
            sys.stdout.write(full_line)
        
        sys.stdout.flush()
    
    def get_choice_with_arrows(self):
        """Get user choice using arrow keys (if available)"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_navigation()
        else:
            return self._traditional_input()
    
    def _arrow_navigation(self):
        """Navigate with arrow keys - robust version"""
        selected_idx = 0
        
        # Initial full display
        self.display(selected_idx)
        
        # Hide cursor during navigation
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()
        
        try:
            while True:
                try:
                    key = self._getch()
                    
                    if HAS_MSVCRT:  # Windows handling
                        if key in ('\xe0', '\x00'):
                            arrow = self._getch()
                            if arrow == 'H':  # Up arrow
                                old_idx = selected_idx
                                selected_idx = (selected_idx - 1) % len(self.items)
                                if old_idx != selected_idx:
                                    self._redraw_item(old_idx, False)
                                    self._redraw_item(selected_idx, True)
                            elif arrow == 'P':  # Down arrow
                                old_idx = selected_idx
                                selected_idx = (selected_idx + 1) % len(self.items)
                                if old_idx != selected_idx:
                                    self._redraw_item(old_idx, False)
                                    self._redraw_item(selected_idx, True)
                        elif key == '\r':  # Enter key
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return selected_idx + 1
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return num
                        elif key == '\x03':  # Ctrl+C
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            print("\n\nExiting...")
                            return len(self.items)
                    
                    else:  # Unix/Linux/Mac handling
                        if key == '\x1b':  # ESC sequence
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':  # Up arrow
                                    old_idx = selected_idx
                                    selected_idx = (selected_idx - 1) % len(self.items)
                                    if old_idx != selected_idx:
                                        self._redraw_item(old_idx, False)
                                        self._redraw_item(selected_idx, True)
                                elif arrow == 'B':  # Down arrow
                                    old_idx = selected_idx
                                    selected_idx = (selected_idx + 1) % len(self.items)
                                    if old_idx != selected_idx:
                                        self._redraw_item(old_idx, False)
                                        self._redraw_item(selected_idx, True)
                        elif key in ['\r', '\n']:  # Enter key
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return selected_idx + 1
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return num
                        elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            print("\n\nExiting...")
                            return len(self.items)
                except Exception:
                    continue
        finally:
            # Always restore cursor visibility
            sys.stdout.write(self.SHOW_CURSOR)
            sys.stdout.flush()
    
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
            
            # Show cursor before executing action
            sys.stdout.write(self.SHOW_CURSOR)
            sys.stdout.flush()
            
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


# Debug utility to verify menu structure
def debug_menu_items(menu):
    """Print menu items for debugging"""
    print(f"\n🔍 Debug: {menu.title}")
    print(f"   Total items: {len(menu.items)}")
    for i, item in enumerate(menu.items):
        print(f"   [{i+1}] {item.label}")
    print()


if __name__ == "__main__":
    # Test the menu system
    print("Testing Menu System...")
    menu = MainMenu()
    debug_menu_items(menu)
    
    print("Menu items verified. Press Ctrl+C to exit test.")
    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")