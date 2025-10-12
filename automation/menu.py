"""
Menu System Module
Defines base menu classes and main menu
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


class Menu(ABC):
    """Abstract base class for all menus"""
    
    def __init__(self, title):
        self.title = title
        self.items = []
        self.setup_items()
    
    @abstractmethod
    def setup_items(self):
        """Setup menu items - must be implemented by subclasses"""
        pass
    
    def display(self, selected_idx=0):
        """Display the menu with highlighting"""
        self.clear_screen()
        print("=" * 70)
        print(f"  {self.title}")
        print("=" * 70)
        print(f"  📍 Current Directory: {Path.cwd()}")
        print("=" * 70)
        
        for i, item in enumerate(self.items):
            if i == selected_idx:
                # Highlighted option (ANSI codes for cyan background and bold)
                print(f"  \033[1;46m► {i + 1}. {item.label}\033[0m")
            else:
                print(f"    {i + 1}. {item.label}")
        print("=" * 70)
        
        # Show appropriate instructions based on platform
        if HAS_TERMIOS or HAS_MSVCRT:
            print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
        else:
            print("\n  Type number and press Enter to select")
    
    def get_choice_with_arrows(self):
        """Get user choice using arrow keys (if available)"""
        # If arrow key support is available, use it
        if HAS_MSVCRT or HAS_TERMIOS:
            return self._arrow_navigation()
        else:
            # Fallback to traditional input
            return self._traditional_input()
    
    def _arrow_navigation(self):
        """Navigate with arrow keys"""
        selected_idx = 0
        
        while True:
            self.display(selected_idx)
            
            try:
                # Read key input
                key = self._getch()
                
                if HAS_MSVCRT:  # Windows handling
                    # Check for special keys (arrow keys return 224 or 0 prefix)
                    if key in ('\xe0', '\x00'):
                        arrow = self._getch()  # Get the actual arrow key code
                        if arrow == 'H':  # Up arrow
                            selected_idx = (selected_idx - 1) % len(self.items)
                        elif arrow == 'P':  # Down arrow
                            selected_idx = (selected_idx + 1) % len(self.items)
                    elif key == '\r':  # Enter key
                        return selected_idx + 1
                    elif key.isdigit():  # Direct number input
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
                    elif key.isdigit():  # Direct number input
                        num = int(key)
                        if 1 <= num <= len(self.items):
                            return num
                    elif key in ['\x03', '\x04']:  # Ctrl+C or Ctrl+D
                        print("\n\nExiting...")
                        return len(self.items)
            except Exception as e:
                # Debug: uncomment to see errors
                # print(f"\nDebug error: {e}")
                continue
    
    def _traditional_input(self):
        """Traditional number input method"""
        self.display(0)  # Display without highlighting
        
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
            # Decode bytes to string
            try:
                return char.decode('utf-8')
            except:
                # Return raw byte value for special keys
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
        super().__init__("🚀 Python Automation System - Main Menu")
    
    def setup_items(self):
        """Setup main menu items"""
        from automation.git_manager import GitMenu
        from automation.git_initializer import GitInitMenu
        from automation.git_recovery import GitRecoveryMenu
        from automation.structure_viewer import StructureViewer
        from automation.folder_navigator import FolderNavigatorMenu
        
        structure_viewer = StructureViewer()
        
        self.items = [
            MenuItem("GitHub Operations (Push/Pull/Status/Log)", lambda: GitMenu().run()),
            MenuItem("Initialize Git & Push to GitHub", lambda: GitInitMenu().run()),
            MenuItem("Git Recovery (Revert to Previous Commit)", lambda: GitRecoveryMenu().run()),
            MenuItem("Show Project Structure", lambda: structure_viewer.show_structure()),
            MenuItem("Navigate Folders", lambda: FolderNavigatorMenu().run()),
            MenuItem("Exit", lambda: self.exit_program())
        ]
    
    def exit_program(self):
        """Exit the program"""
        print("\n👋 Thanks for using Python Automation System!")
        print("Made with ❤️  for developers\n")
        return "exit"