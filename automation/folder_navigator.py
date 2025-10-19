"""
Folder Navigator Module with Robust Navigation
Fixed text corruption with proper line clearing and padding
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
    
    def __init__(self):
        self.current_path = Path.cwd()
        self.selected_idx = 0
        self.navigation_history = []
    
    def navigate(self):
        """Start the interactive navigation loop with arrow keys"""
        while True:
            subdirs = self._get_subdirectories()
            
            # Ensure selected index is within bounds
            if self.selected_idx >= len(subdirs):
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
            print("    Press Enter to confirm this directory.\n")
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
            print(f"  \033[1;46m{line}\033[0m")
        else:
            line = f"    {line}".ljust(68)
            print(f"  {line}")
    
    def _redraw_directory_item(self, subdirs, idx, is_selected):
        """Redraw a single directory item at its position"""
        if idx < 0 or idx >= len(subdirs):
            return
        
        # Calculate line position (8 header lines + index)
        line_num = 8 + idx
        
        # Move to line, clear it, and rewrite
        print(f'\033[{line_num};1H{self.CLEAR_LINE}', end='', flush=True)
        
        subdir = subdirs[idx]
        line = f"{idx + 1}. {subdir.name}/"
        
        if is_selected:
            line = f"  ► {line}".ljust(68)
            print(f"  \033[1;46m{line}\033[0m", end='', flush=True)
        else:
            line = f"    {line}".ljust(68)
            print(f"  {line}", end='', flush=True)
    
    def _get_user_input(self, subdirs):
        """Get user input with arrow key support"""
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_input(subdirs)
        else:
            return self._traditional_input(subdirs)
    
    def _arrow_input(self, subdirs):
        """Handle arrow key navigation with smooth updates"""
        if not subdirs:
            # No subdirectories, wait for Enter
            while True:
                key = self._getch()
                if HAS_MSVCRT:
                    if key == '\r':
                        return "confirm"
                    elif key == '\x03':
                        return "confirm"
                else:
                    if key in ['\r', '\n']:
                        return "confirm"
                    elif key in ['\x03', '\x04']:
                        return "confirm"
        
        # Hide cursor during navigation
        print(self.HIDE_CURSOR, end='', flush=True)
        
        try:
            while True:
                try:
                    key = self._getch()
                    
                    if HAS_MSVCRT:  # Windows handling
                        if key in ('\xe0', '\x00'):
                            arrow = self._getch()
                            if arrow == 'H':  # Up arrow
                                old_idx = self.selected_idx
                                self.selected_idx = (self.selected_idx - 1) % len(subdirs)
                                self._redraw_directory_item(subdirs, old_idx, False)
                                self._redraw_directory_item(subdirs, self.selected_idx, True)
                            elif arrow == 'P':  # Down arrow
                                old_idx = self.selected_idx
                                self.selected_idx = (self.selected_idx + 1) % len(subdirs)
                                self._redraw_directory_item(subdirs, old_idx, False)
                                self._redraw_directory_item(subdirs, self.selected_idx, True)
                            elif arrow == 'K':  # Left arrow
                                print(self.SHOW_CURSOR, end='', flush=True)
                                return "back"
                            elif arrow == 'M':  # Right arrow
                                print(self.SHOW_CURSOR, end='', flush=True)
                                return "enter_dir"
                        elif key == '\r':  # Enter key
                            print(self.SHOW_CURSOR, end='', flush=True)
                            return "confirm"
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(subdirs):
                                print(self.SHOW_CURSOR, end='', flush=True)
                                return num
                        elif key in ['\x03', '\x1b']:  # Ctrl+C or ESC
                            print(self.SHOW_CURSOR, end='', flush=True)
                            return "confirm"
                    
                    else:  # Unix/Linux/Mac handling
                        if key == '\x1b':  # ESC sequence
                            next_key = self._getch()
                            if next_key == '[':
                                arrow = self._getch()
                                if arrow == 'A':  # Up arrow
                                    old_idx = self.selected_idx
                                    self.selected_idx = (self.selected_idx - 1) % len(subdirs)
                                    self._redraw_directory_item(subdirs, old_idx, False)
                                    self._redraw_directory_item(subdirs, self.selected_idx, True)
                                elif arrow == 'B':  # Down arrow
                                    old_idx = self.selected_idx
                                    self.selected_idx = (self.selected_idx + 1) % len(subdirs)
                                    self._redraw_directory_item(subdirs, old_idx, False)
                                    self._redraw_directory_item(subdirs, self.selected_idx, True)
                                elif arrow == 'D':  # Left arrow
                                    print(self.SHOW_CURSOR, end='', flush=True)
                                    return "back"
                                elif arrow == 'C':  # Right arrow
                                    print(self.SHOW_CURSOR, end='', flush=True)
                                    return "enter_dir"
                            else:
                                # ESC key pressed alone
                                print(self.SHOW_CURSOR, end='', flush=True)
                                return "confirm"
                        elif key in ['\r', '\n']:  # Enter key
                            print(self.SHOW_CURSOR, end='', flush=True)
                            return "confirm"
                        elif key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(subdirs):
                                print(self.SHOW_CURSOR, end='', flush=True)
                                return num
                        elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                            print(self.SHOW_CURSOR, end='', flush=True)
                            return "confirm"
                except Exception:
                    continue
        finally:
            print(self.SHOW_CURSOR, end='', flush=True)
    
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
            if not (HAS_TERMIOS or HAS_MSVCRT):
                print(f"\n❌ Permission denied: {target_dir.name}")
                input("\nPress Enter to continue...")
        except Exception as e:
            if not (HAS_TERMIOS or HAS_MSVCRT):
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
    
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
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')