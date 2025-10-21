"""
Folder Navigator Module - Complete Fix
Fixes back arrow in empty directories and navigation glitches
"""
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


class FolderNavigator:
    """Handles interactive folder navigation with arrow key support"""

    # ANSI escape codes
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_LINE = '\033[2K'
    CLEAR_SCREEN = '\033[2J\033[H'

    def __init__(self):
        self.current_path = Path.cwd()
        self.selected_idx = 0
        self.navigation_history = []

    def navigate(self):
        """Start the interactive navigation loop with arrow keys"""
        while True:
            subdirs = self._get_subdirectories()

            # Ensure selected index is within bounds
            if subdirs and self.selected_idx >= len(subdirs):
                self.selected_idx = max(0, len(subdirs) - 1)

            # Full display
            self._display_navigation(subdirs)

            # Handle user input
            action = self._get_user_input(subdirs)

            if action == "confirm":
                print(f"\n✅ Directory confirmed: {self.current_path}")
                print("⚠️  All operations will now work in this directory.\n")
                input("Press Enter to return to main menu...")
                break
            elif action == "back":
                self._go_back()
            elif action == "up":
                if subdirs:
                    self.selected_idx = (self.selected_idx - 1) % len(subdirs)
            elif action == "down":
                if subdirs:
                    self.selected_idx = (self.selected_idx + 1) % len(subdirs)
            elif action == "enter_dir":
                if subdirs:
                    self._enter_directory(subdirs[self.selected_idx])
            elif isinstance(action, int):
                if 1 <= action <= len(subdirs):
                    self.selected_idx = action - 1
                    self._enter_directory(subdirs[self.selected_idx])

    def _display_navigation(self, subdirs):
        """Display the navigation interface"""
        self._clear_screen()
        print("="*70)
        print("📂 FOLDER NAVIGATOR")
        print("="*70)
        print(f"📍 Current Location: {self.current_path}")
        print(f"📍 Absolute Path: {self.current_path.absolute()}")
        print("="*70)

        if not subdirs:
            print("\n📭 No subdirectories found in current location.")
            print("    Press ← to go back or Enter to confirm this directory.\n")
        else:
            print("\n📁 Available Directories:")
            print("-" * 70)
            for idx, subdir in enumerate(subdirs):
                self._print_directory_item(idx, subdir, idx == self.selected_idx)
            print("-" * 70)

        # Show navigation instructions
        print("\nNavigation:")
        if HAS_TERMIOS or HAS_MSVCRT:
            print("  • ↑/↓ arrows: Navigate through directories")
            print("  • → arrow or Number: Enter selected directory")
            print("  • ← arrow: Go back to parent directory")
            print("  • Enter: Confirm current directory and return to menu")
        else:
            print("  • Type number + Enter: Enter that directory")
            print("  • Type 'back': Go up one level")
            print("  • Type 'confirm': Confirm current directory")
        print("="*70)

    def _print_directory_item(self, idx, subdir, is_selected):
        """Print a single directory item with proper formatting"""
        line = f"{idx + 1}. {subdir.name}/"

        if is_selected:
            # Pad line to ensure full coverage
            line = f"  ► {line}".ljust(68)
            print(f"\033[1;46m{line}\033[0m")
        else:
            line = f"    {line}".ljust(68)
            print(line)

    def _get_user_input(self, subdirs):
        """Get user input with arrow key support"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_input(subdirs)
        else:
            return self._traditional_input(subdirs)

    def _arrow_input(self, subdirs):
        """Handle arrow key navigation with proper key handling"""
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
                                if subdirs:
                                    return "up"
                            elif arrow == 'P':  # Down arrow
                                if subdirs:
                                    return "down"
                            elif arrow == 'K':  # Left arrow
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return "back"
                            elif arrow == 'M':  # Right arrow
                                if subdirs:
                                    sys.stdout.write(self.SHOW_CURSOR)
                                    sys.stdout.flush()
                                    return "enter_dir"
                        elif key == '\r':  # Enter key
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return "confirm"
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(subdirs):
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return num
                        elif key in ['\x03', '\x1b']:  # Ctrl+C or ESC
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return "confirm"

                    else:  # Unix/Linux/Mac handling
                        if key == '\x1b':  # ESC sequence
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':  # Up arrow
                                    if subdirs:
                                        return "up"
                                elif arrow == 'B':  # Down arrow
                                    if subdirs:
                                        return "down"
                                elif arrow == 'D':  # Left arrow
                                    sys.stdout.write(self.SHOW_CURSOR)
                                    sys.stdout.flush()
                                    return "back"
                                elif arrow == 'C':  # Right arrow
                                    if subdirs:
                                        sys.stdout.write(self.SHOW_CURSOR)
                                        sys.stdout.flush()
                                        return "enter_dir"
                            else:
                                # ESC key pressed alone
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return "confirm"
                        elif key in ['\r', '\n']:  # Enter key
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return "confirm"
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(subdirs):
                                sys.stdout.write(self.SHOW_CURSOR)
                                sys.stdout.flush()
                                return num
                        elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                            sys.stdout.write(self.SHOW_CURSOR)
                            sys.stdout.flush()
                            return "confirm"
                except KeyboardInterrupt:
                    sys.stdout.write(self.SHOW_CURSOR)
                    sys.stdout.flush()
                    return "confirm"
                except Exception:
                    continue
        finally:
            sys.stdout.write(self.SHOW_CURSOR)
            sys.stdout.flush()

    def _traditional_input(self, subdirs):
        """Traditional text-based input"""
        choice = input("\nYour choice: ").strip().lower()

        if choice in ['confirm', 'exit', 'q', '']:
            return "confirm"
        elif choice in ['back', '..']:
            return "back"
        elif choice.isdigit():
            return int(choice)
        else:
            print("\n❌ Invalid input. Please try again.")
            input("\nPress Enter to continue...")
            return None

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

    def _get_subdirectories(self):
        """Get list of subdirectories in current path"""
        try:
            subdirs = [item for item in self.current_path.iterdir()
                      if item.is_dir() and not item.name.startswith('.')]
            return sorted(subdirs, key=lambda x: x.name.lower())
        except PermissionError:
            return []

    def _enter_directory(self, target_dir):
        """Enter a subdirectory"""
        try:
            self.navigation_history.append(self.current_path)
            self.current_path = target_dir
            os.chdir(self.current_path)
            self.selected_idx = 0
        except PermissionError:
            # Show error and wait for user acknowledgment
            self._clear_screen()
            print("\n" + "="*70)
            print(f"❌ Permission denied: {target_dir.name}")
            print("="*70 + "\n")
            input("Press Enter to continue...")
        except Exception as e:
            # Show error and wait for user acknowledgment
            self._clear_screen()
            print("\n" + "="*70)
            print(f"❌ Error: {e}")
            print("="*70 + "\n")
            input("Press Enter to continue...")

    def _go_back(self):
        """Go back to previous directory"""
        if self.navigation_history:
            self.current_path = self.navigation_history.pop()
            os.chdir(self.current_path)
            self.selected_idx = 0
        else:
            parent = self.current_path.parent
            if parent != self.current_path:
                self.current_path = parent
                os.chdir(self.current_path)
                self.selected_idx = 0

    def _clear_screen(self):
        """Clear the terminal screen completely"""
        # Use both methods for maximum compatibility
        sys.stdout.write(self.CLEAR_SCREEN)
        sys.stdout.flush()
        os.system('cls' if os.name == 'nt' else 'clear')


# Test the navigator
if __name__ == "__main__":
    print("Testing Folder Navigator...")
    print("This will start the navigation interface.")
    print("Press Enter to continue or Ctrl+C to cancel...")

    try:
        input()
        nav = FolderNavigator()
        nav.navigate()
        print(f"\nFinal directory: {nav.current_path}")
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")