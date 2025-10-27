"""
automation/menu.py
Responsive Menu System with Adaptive Viewport Handling
FIXED: Terminal viewport adaptation, smooth arrow navigation, dynamic resizing
"""
from abc import ABC, abstractmethod
import os
import sys
import shutil
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


class TerminalInfo:
    """Handle terminal size and viewport information"""
    
    @staticmethod
    def get_size():
        """Get current terminal size (columns, lines)"""
        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.columns, size.lines
        except Exception:
            return 80, 24
    
    @staticmethod
    def is_small_viewport():
        """Check if terminal viewport is small"""
        cols, lines = TerminalInfo.get_size()
        return lines < 20 or cols < 70
    
    @staticmethod
    def get_available_lines():
        """Get number of lines available for menu items"""
        _, lines = TerminalInfo.get_size()
        # Reserve space for header (5) + footer (3) + padding
        return max(5, lines - 8)


class MenuItem:
    """Represents a single menu item"""

    def __init__(self, label, action):
        self.label = label
        self.action = action

    def __repr__(self):
        return f"MenuItem(label='{self.label}')"


class Menu(ABC):
    """
    Abstract base class for all menus with responsive viewport adaptation
    
    Features:
    - Automatic terminal size detection
    - Smooth scrolling for small viewports
    - Optimized redraw for large menus
    - Arrow key navigation with proper cursor positioning
    """

    # ANSI escape codes for cursor control
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_SCREEN = '\033[2J\033[H'
    CLEAR_LINE = '\033[2K'
    MOVE_UP = '\033[1A'

    def __init__(self, title):
        self.title = title
        self.items = []
        self._items_initialized = False
        self._scroll_offset = 0  # For scrolling in small viewports
        self.setup_items()
        self._items_initialized = True

    @abstractmethod
    def setup_items(self):
        """Setup menu items - must be implemented by subclasses"""
        pass

    def display(self, selected_idx=0, initial=True, force_full_redraw=False):
        """
        Display the menu with responsive viewport handling
        
        Args:
            selected_idx: Currently selected item index
            initial: Whether this is the initial display
            force_full_redraw: Force complete screen refresh
        """
        cols, lines = TerminalInfo.get_size()
        available_lines = TerminalInfo.get_available_lines()
        is_small = TerminalInfo.is_small_viewport()
        
        # Adjust scroll offset to keep selected item visible
        if len(self.items) > available_lines:
            # Calculate scroll position
            if selected_idx < self._scroll_offset:
                self._scroll_offset = selected_idx
            elif selected_idx >= self._scroll_offset + available_lines:
                self._scroll_offset = selected_idx - available_lines + 1
        else:
            self._scroll_offset = 0
        
        if initial or force_full_redraw:
            self._display_full(selected_idx, cols, lines, available_lines, is_small)
        else:
            # Only update the changed items for smooth navigation
            self._update_visible_items(selected_idx, available_lines)

    def _display_full(self, selected_idx, cols, lines, available_lines, is_small):
        """Full screen refresh with responsive layout"""
        self.clear_screen()
        
        # Adjust separator width for terminal size
        sep_width = min(70, cols - 2)
        
        # Header
        print("=" * sep_width)
        
        # Truncate title if needed
        title_display = self.title[:cols-4] if len(self.title) > cols-4 else self.title
        print(f"  {title_display}")
        
        print("=" * sep_width)
        
        # Current directory info (truncate for small viewports)
        current_dir = str(Path.cwd())
        if len(current_dir) > cols - 25:
            # Show last part of path
            current_dir = "..." + current_dir[-(cols-28):]
        
        print(f"  📍 Current Directory: {current_dir}")
        print("=" * sep_width)
        
        # Calculate visible range
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(self.items))
        
        # Show scroll indicator at top if needed
        if self._scroll_offset > 0:
            scroll_info = f"  ↑ {self._scroll_offset} more above..."
            print(scroll_info[:cols-2])
        
        # Display visible menu items
        for i in range(visible_start, visible_end):
            self._print_item(i, self.items[i], i == selected_idx, cols)
        
        # Show scroll indicator at bottom if needed
        if visible_end < len(self.items):
            remaining = len(self.items) - visible_end
            scroll_info = f"  ↓ {remaining} more below..."
            print(scroll_info[:cols-2])
        
        print("=" * sep_width)
        
        # Footer - adapt instructions based on viewport and capabilities
        if is_small:
            if HAS_TERMIOS or HAS_MSVCRT:
                print("\n  ↑/↓: Navigate | Enter: Select")
            else:
                print("\n  Type number + Enter")
        else:
            if HAS_TERMIOS or HAS_MSVCRT:
                print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
            else:
                print("\n  Type number and press Enter to select")

    def _update_visible_items(self, selected_idx, available_lines):
        """
        Update only the visible menu items for smooth navigation
        
        This is much faster than full redraw and prevents flickering
        """
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(self.items))
        cols, _ = TerminalInfo.get_size()
        
        # Calculate cursor position for updates
        # Header is 5 lines, scroll indicator adds 1 if present
        base_line = 5
        if self._scroll_offset > 0:
            base_line += 1
        
        # Update each visible item
        for i in range(visible_start, visible_end):
            line_number = base_line + (i - visible_start)
            
            # Move cursor to the line
            sys.stdout.write(f'\033[{line_number + 1};1H')
            sys.stdout.write(self.CLEAR_LINE)
            
            # Redraw the item
            self._print_item_inline(i, self.items[i], i == selected_idx, cols)
        
        sys.stdout.flush()

    def _print_item(self, index, item, is_selected, cols):
        """Print a single menu item with proper formatting"""
        line_text = f"{index + 1}. {item.label}"
        
        # Truncate if too long for terminal
        max_text_width = cols - 6  # Leave space for prefix and padding
        if len(line_text) > max_text_width:
            line_text = line_text[:max_text_width-3] + "..."
        
        if is_selected:
            full_line = f"  ► {line_text}"
            # Pad to full width for consistent highlight
            full_line = full_line.ljust(min(70, cols - 2))
            print(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            print(full_line)

    def _print_item_inline(self, index, item, is_selected, cols):
        """Print item inline (without newline) for updates"""
        line_text = f"{index + 1}. {item.label}"
        
        max_text_width = cols - 6
        if len(line_text) > max_text_width:
            line_text = line_text[:max_text_width-3] + "..."
        
        if is_selected:
            full_line = f"  ► {line_text}"
            full_line = full_line.ljust(min(70, cols - 2))
            sys.stdout.write(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            sys.stdout.write(full_line)

    def get_choice_with_arrows(self):
        """Get user choice using arrow keys (if available)"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_navigation()
        else:
            return self._traditional_input()

    def _arrow_navigation(self):
        """
        Navigate with arrow keys - optimized for responsiveness
        
        Improvements:
        - Smooth scrolling in small viewports
        - Minimal redraws for large menus
        - Proper cursor positioning
        - Terminal resize detection
        """
        selected_idx = 0
        last_terminal_size = TerminalInfo.get_size()
        
        # Initial display
        self.display(selected_idx, initial=True)
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()

        try:
            while True:
                try:
                    # Check for terminal resize
                    current_size = TerminalInfo.get_size()
                    if current_size != last_terminal_size:
                        last_terminal_size = current_size
                        self.display(selected_idx, initial=True, force_full_redraw=True)
                    
                    key = self._getch()

                    old_idx = selected_idx
                    new_idx = selected_idx
                    should_exit = False
                    should_select = False

                    if HAS_MSVCRT:  # Windows
                        if key in ('\xe0', '\x00'):
                            arrow = self._getch()
                            if arrow == 'H':  # Up
                                new_idx = (selected_idx - 1) % len(self.items)
                            elif arrow == 'P':  # Down
                                new_idx = (selected_idx + 1) % len(self.items)
                        elif key == '\r':  # Enter
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key == '\x03':  # Ctrl+C
                            should_exit = True
                            selected_idx = len(self.items) - 1
                            should_select = True

                    else:  # Unix/Linux/Mac
                        if key == '\x1b':  # ESC sequence
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':  # Up
                                    new_idx = (selected_idx - 1) % len(self.items)
                                elif arrow == 'B':  # Down
                                    new_idx = (selected_idx + 1) % len(self.items)
                        elif key in ['\r', '\n']:  # Enter
                            should_select = True
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(self.items):
                                should_exit = True
                                selected_idx = num - 1
                                should_select = True
                        elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                            should_exit = True
                            selected_idx = len(self.items) - 1
                            should_select = True

                    # Update selection if changed
                    if new_idx != old_idx:
                        selected_idx = new_idx
                        
                        # Check if we need full redraw (scrolling) or just update
                        available_lines = TerminalInfo.get_available_lines()
                        needs_scroll = (
                            len(self.items) > available_lines and
                            (selected_idx < self._scroll_offset or 
                             selected_idx >= self._scroll_offset + available_lines)
                        )
                        
                        if needs_scroll:
                            # Full redraw for scrolling
                            self.display(selected_idx, initial=False, force_full_redraw=True)
                        else:
                            # Just update the two affected items
                            self._update_visible_items(selected_idx, available_lines)

                    if should_select:
                        sys.stdout.write(self.SHOW_CURSOR)
                        sys.stdout.flush()
                        return selected_idx + 1

                except KeyboardInterrupt:
                    sys.stdout.write(self.SHOW_CURSOR)
                    sys.stdout.flush()
                    print("\n\nExiting...")
                    return len(self.items)
                except Exception as e:
                    # Log error but continue
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