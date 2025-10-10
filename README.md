# Python Automation System 🚀

A powerful, object-oriented Python automation toolkit for developers. Execute common development tasks with a simple command: `magic`

## Features ✨

- **GitHub Operations**: Push, pull, status, and log operations
- **Project Structure Viewer**: Visualize your project hierarchy
- **Extensible Architecture**: Easy to add new automation modules
- **OOP Design**: Clean, maintainable code structure
- **Global Access**: Run from anywhere with the `magic` command

## Project Structure 📁

```
python-automation/
├── main.py                    # Entry point
├── setup.sh                   # Installation script
├── README.md                  # This file
└── automation/                # Automation modules
    ├── __init__.py           # Package initialization
    ├── menu.py               # Menu system (base classes)
    ├── git_manager.py        # Git operations
    └── structure_viewer.py   # Project structure viewer
```

## Installation 🔧

1. **Clone or create the project structure:**
   ```bash
   mkdir -p python-automation/automation
   cd python-automation
   ```

2. **Create all the necessary files** (main.py, setup.sh, and automation module files)

3. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Activate the alias:**
   ```bash
   source ~/.bashrc  # or ~/.zshrc for Zsh users
   ```

## Usage 🎯

Simply type `magic` anywhere in your terminal:

```bash
magic
```

### Main Menu Options

1. **GitHub Operations**
   - Status: View current git status
   - Log: Show commit history
   - Pull: Pull latest changes from remote
   - Push: Add, commit, and push changes

2. **Show Project Structure**
   - Displays parent directory structure
   - Shows current project files with sizes
   - Highlights the current directory

3. **Exit**
   - Close the automation system

## Adding New Automation Modules 🔌

To add a new automation module:

1. Create a new file in the `automation/` directory:
   ```python
   # automation/my_module.py
   from automation.menu import Menu, MenuItem
   
   class MyAutomation:
       def do_something(self):
           print("Doing something awesome!")
   
   class MyMenu(Menu):
       def __init__(self):
           self.my_auto = MyAutomation()
           super().__init__("My Automation")
       
       def setup_items(self):
           self.items = [
               MenuItem("Do Something", lambda: self.my_auto.do_something()),
               MenuItem("Back", lambda: "exit")
           ]
   ```

2. Import and add to main menu in `automation/menu.py`:
   ```python
   from automation.my_module import MyMenu
   
   # In MainMenu.setup_items():
   MenuItem("My Automation", lambda: MyMenu().run()),
   ```

## Architecture 🏗️

### OOP Concepts Used

- **Abstract Base Classes**: `Menu` class defines the interface for all menus
- **Inheritance**: All specific menus inherit from `Menu`
- **Encapsulation**: Each module handles its own operations
- **Single Responsibility**: Each class has one clear purpose
- **Composition**: Menu items compose actions using callables

### Class Diagram

```
Menu (ABC)
├── MainMenu
├── GitMenu
└── [Your Custom Menu]

GitOperations
StructureViewer
MenuItem
```

## Requirements 📋

- Python 3.6+
- Git (for GitHub operations)
- Bash or Zsh shell

## Troubleshooting 🔍

**"magic: command not found"**
- Run `source ~/.bashrc` (or `~/.zshrc`)
- Make sure setup.sh completed successfully

**Git commands not working:**
- Ensure Git is installed: `git --version`
- Check if you're in a Git repository

**Permission denied:**
- Make main.py executable: `chmod +x main.py`

## Customization 🎨

### Change the Alias Name

Edit `setup.sh` and replace `magic` with your preferred command name:
```bash
echo "alias mycommand='python3 $MAIN_PY'" >> "$SHELL_CONFIG"
```

### Exclude Additional Directories

Edit `EXCLUDE_DIRS` in `automation/structure_viewer.py`:
```python
EXCLUDE_DIRS = {"__pycache__", ".git", "your_folder"}
```

## Contributing 🤝

Feel free to extend this automation system with your own modules!

## License 📄

MIT License - feel free to use and modify as needed.

---

**Made with ❤️ for developers who love automation**