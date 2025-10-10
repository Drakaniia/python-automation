"""
Menu System Module
Defines base menu classes and main menu
"""
from abc import ABC, abstractmethod
import os


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
    
    def display(self):
        """Display the menu"""
        self.clear_screen()
        print("=" * 70)
        print(f"  {self.title}")
        print("=" * 70)
        for i, item in enumerate(self.items, 1):
            print(f"  {i}. {item.label}")
        print("=" * 70)
    
    def get_choice(self):
        """Get user choice"""
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
                return len(self.items)  # Return last item (usually exit)
    
    def run(self):
        """Run the menu loop"""
        while True:
            self.display()
            choice = self.get_choice()
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
        from automation.structure_viewer import StructureViewer
        from automation.folder_navigator import FolderNavigatorMenu
        
        structure_viewer = StructureViewer()
        
        self.items = [
            MenuItem("GitHub Operations (Push/Pull/Status/Log)", lambda: GitMenu().run()),
            MenuItem("Initialize Git & Push to GitHub", lambda: GitInitMenu().run()),
            MenuItem("Show Project Structure", lambda: structure_viewer.show_structure()),
            MenuItem("Navigate Folders", lambda: FolderNavigatorMenu().run()),
            MenuItem("Exit", lambda: self.exit_program())
        ]
    
    def exit_program(self):
        """Exit the program"""
        print("\n👋 Thanks for using Python Automation System!")
        print("Made with ❤️  for developers\n")
        return "exit"