"""
Menu System Module - Updated with Dev Mode
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

    # ANSI escape codes for cursor control
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    SAVE_CURSOR = '\033[s'
    RESTORE_CURSOR = '\033[u'

    def __init__(self, title):
        self.title = title
        self.items = []
        self._items_initialized = False
        self._menu_start_line = 0
        self.setup_items()
        self._items_initialized = True

    @abstractmethod
    def setup_items(self):
        """Setup menu items - must be implemented by subclasses"""
        pass

    def display(self, selected_idx=0, initial=True):
        """Display the menu - full refresh only on initial display"""
        if initial:
            self.clear_screen()
            print("=" * 70)
            print(f"  {self.title}")
            print("=" * 70)
            print(f"  📍 Current Directory: {Path.cwd()}")
            print("=" * 70)

            # Remember where menu items start (after header)
            self._menu_start_line = 5

            # Print all items
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
            print(f"\033[1;46m{full_line.ljust(70)}\033[0m")
        else:
            full_line = f"    {line_text}"
            print(full_line.ljust(70))

    def _update_item(self, index, item, is_selected):
        """Update a single menu item without clearing screen"""
        line_number = self._menu_start_line + index
        sys.stdout.write(f'\033[{line_number + 1};1H')
        sys.stdout.write('\033[2K')

        line_text = f"{index + 1}. {item.label}"

        if is_selected:
            full_line = f"  ► {line_text}"
            sys.stdout.write(f"\033[1;46m{full_line.ljust(70)}\033[0m")
        else:
            full_line = f"    {line_text}"
            sys.stdout.write(full_line.ljust(70))

        sys.stdout.flush()

    def get_choice_with_arrows(self):
        """Get user choice using arrow keys (if available)"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_navigation()
        else:
            return self._traditional_input()

    def _arrow_navigation(self):
        """Navigate with arrow keys - smooth updates only"""
        selected_idx = 0
        self.display(selected_idx, initial=True)
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()

        try:
            while True:
                try:
                    key = self._getch()

                    old_idx = selected_idx
                    new_idx = selected_idx
                    should_exit = False
                    should_select = False

                    if HAS_MSVCRT:
                        if key in ('\xe0', '\x00'):
                            arrow = self._getch()
                            if arrow == 'H':
                                new_idx = (selected_idx - 1) % len(self.items)
                            elif arrow == 'P':
                                new_idx = (selected_idx + 1) % len(self.items)
                        elif key == '\r':
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key == '\x03':
                            should_exit = True
                            selected_idx = len(self.items) - 1
                            should_select = True

                    else:
                        if key == '\x1b':
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':
                                    new_idx = (selected_idx - 1) % len(self.items)
                                elif arrow == 'B':
                                    new_idx = (selected_idx + 1) % len(self.items)
                        elif key in ['\r', '\n']:
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key in ['\x03', '\x04']:
                            should_exit = True
                            selected_idx = len(self.items) - 1
                            should_select = True

                    if new_idx != old_idx:
                        selected_idx = new_idx
                        self._update_item(old_idx, self.items[old_idx], is_selected=False)
                        self._update_item(new_idx, self.items[new_idx], is_selected=True)

                    if should_select:
                        sys.stdout.write(self.SHOW_CURSOR)
                        sys.stdout.flush()
                        return selected_idx + 1

                except KeyboardInterrupt:
                    sys.stdout.write(self.SHOW_CURSOR)
                    sys.stdout.flush()
                    print("\n\nExiting...")
                    return len(self.items)
                except Exception:
                    continue

        finally:
            sys.stdout.write(self.SHOW_CURSOR)
            sys.stdout.flush()

    def _traditional_input(self):
        """Traditional number input method"""
        self.display(0, initial=True)

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
        if HAS_MSVCRT:
            char = msvcrt.getch()
            try:
                return char.decode('utf-8')
            except:
                return chr(ord(char))
        elif HAS_TERMIOS:
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
            self.clear_screen()
            result = self.items[choice - 1].action()
            if result == "exit":
                break

    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')


class MainMenu(Menu):
    """Main menu for the automation system - Updated with Dev Mode"""

    def __init__(self):
        # Initialize dependencies ONCE before calling parent __init__
        self._git_menu = None
        self._structure_viewer = None
        self._folder_nav = None
        self._dev_mode_menu = None

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
        from automation.dev_mode import DevModeMenu

        # Create instances once and reuse them
        if self._git_menu is None:
            self._git_menu = GitMenu()
        if self._structure_viewer is None:
            self._structure_viewer = StructureViewer()
        if self._folder_nav is None:
            self._folder_nav = FolderNavigator()
        if self._dev_mode_menu is None:
            self._dev_mode_menu = DevModeMenu()

        # Create menu items with bound methods
        self.items = [
            MenuItem("GitHub Operations", self._run_git_operations),
            MenuItem("Show Project Structure", self._show_structure),
            MenuItem("Navigate Folders", self._navigate_folders),
            MenuItem("Dev Mode (Web Dev Automation)", self._run_dev_mode),
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
    
    def _run_dev_mode(self):
        """Run Dev Mode menu"""
        self._dev_mode_menu.run()
        return None
    
    def _exit_program(self):
        """Exit the program"""
        self.clear_screen()
        print("\n" + "="*70)
        print("  👋 Thanks for using Python Automation System!")
        print("  Made with ❤️  for developers")
        print("="*70 + "\n")
        return "exit"