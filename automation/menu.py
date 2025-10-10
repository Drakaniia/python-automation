"""
Menu system for automation tools
"""
from abc import ABC, abstractmethod
from typing import List, Callable
import sys


class MenuItem:
    """Represents a single menu item"""
    def __init__(self, label: str, action: Callable):
        self.label = label
        self.action = action


class Menu(ABC):
    """Abstract base class for menus"""
    def __init__(self, title: str):
        self.title = title
        self.items: List[MenuItem] = []
        self.setup_items()
    
    @abstractmethod
    def setup_items(self):
        """Setup menu items - to be implemented by subclasses"""
        pass
    
    def display(self):
        """Display the menu"""
        print(f"\n{'='*50}")
        print(f"{self.title:^50}")
        print(f"{'='*50}\n")
        for i, item in enumerate(self.items, 1):
            print(f"  {i}. {item.label}")
        print()
    
    def run(self):
        """Run the menu loop"""
        while True:
            self.display()
            try:
                choice = input("Select an option: ").strip()
                if not choice:
                    continue
                
                idx = int(choice) - 1
                if 0 <= idx < len(self.items):
                    result = self.items[idx].action()
                    if result == "exit":
                        break
                else:
                    print(f"\n⚠️  Invalid choice. Please select 1-{len(self.items)}")
            except ValueError:
                print("\n⚠️  Please enter a number")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
            input("\nPress Enter to continue...")


class MainMenu(Menu):
    """Main menu for the automation system"""
    def setup_items(self):
        from automation.git_manager import GitMenu
        from automation.git_initializer import GitInitMenu
        from automation.structure_viewer import StructureViewer
        
        self.items = [
            MenuItem("GitHub Operations (Push/Pull/Status/Log)", lambda: GitMenu().run()),
            MenuItem("Initialize Git & Push to GitHub", lambda: GitInitMenu().run()),
            MenuItem("Show Project Structure", lambda: StructureViewer().show()),
            MenuItem("Exit", lambda: "exit")
        ]