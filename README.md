# Python Automation System 🚀

A powerful, object-oriented Python automation toolkit for developers. Execute common development tasks with a simple command: **`magic`**

## Features ✨

- **GitHub Operations**: Push, pull, status, and log operations
- **Git Repository Initialization**: Initialize and push new repos to GitHub with one command
- **Project Structure Viewer**: Visualize your project hierarchy
- **Extensible Architecture**: Easy to add new automation modules
- **OOP Design**: Clean, maintainable code structure
- **Global Access**: Run from anywhere with the `magic` command

## Project Structure 📁

```
python-automation/
├── main.py                      # Entry point
├── setup.sh                     # Installation script
├── README.md                    # This file
└── automation/                  # Automation modules
    ├── __init__.py             # Package initialization
    ├── magic.py                # CLI entry point for `magic`
    ├── menu.py                 # Menu system (base classes)
    ├── git_manager.py          # Git operations (push/pull/status/log)
    ├── git_initializer.py      # Git init & first push automation
    └── structure_viewer.py     # Project structure viewer
```

## Installation 🔧

### 1. Prerequisites

Ensure Python 3.13+ is installed:

```bash
python --version
```

**Windows Users**: If you see a Microsoft Store message, disable the Windows App Execution Alias:
- Settings → Apps → Advanced app settings → App execution aliases
- Turn OFF the Python aliases

Add Python to your `~/.bashrc`:

```bash
export PATH="/c/Users/<YourUser>/AppData/Local/Programs/Python/Python313:$PATH"
alias python="py"
```

### 2. Create Project Structure

```bash
mkdir -p python-automation/automation
cd python-automation
```

### 3. Create Required Files

```bash
touch main.py setup.sh README.md
touch automation/{__init__.py,magic.py,menu.py,git_manager.py,git_initializer.py,structure_viewer.py}
```

Copy the code from each artifact into its respective file.

### 4. Set Up the Global `magic` Alias

Add this to your `~/.bashrc`:

```bash
echo 'alias magic="cd /c/projectfiles/python-automation && python -m automation.magic"' >> ~/.bashrc
source ~/.bashrc
```

**Replace** `/c/projectfiles/python-automation` with your actual project path.

### 5. Verify Installation

```bash
magic
```

You should see the main menu! 🎉

## Usage 🎯

Simply type `magic` anywhere in your terminal:

```bash
magic
```

### Main Menu Options

1. **GitHub Operations (Push/Pull/Status/Log)**
   - **Status**: View current git status
   - **Log**: Show commit history (last 10 commits)
   - **Pull**: Pull latest changes from remote
   - **Push**: Add, commit, and push changes

2. **Initialize Git & Push to GitHub** 🆕
   - Creates README.md (if needed)
   - Initializes git repository
   - Creates first commit
   - Sets branch to `main`
   - Adds remote origin (you provide the URL)
   - Pushes to GitHub
   
   **Example workflow:**
   ```
   Select option 2
   → Enter: https://github.com/username/repo-name.git
   → Automated: git init, add, commit, push!
   ```

3. **Show Project Structure**
   - Displays parent directory structure
   - Shows current project files with sizes
   - Highlights the current directory

4. **Exit**
   - Close the automation system

## Git Initialization Example 📝

When you select **"Initialize Git & Push to GitHub"**:

```
🚀 Git Repository Initialization & First Push

📝 Enter your GitHub repository URL:
Example: https://github.com/username/repo-name.git
Repository URL: https://github.com/Drakaniia/python-automation.git

🔧 Starting Git initialization...

📄 Creating README.md...
✅ README.md created

📦 Initializing git repository...
✅ Git repository initialized

➕ Adding README.md to staging...
✅ README.md added

💾 Creating first commit...
✅ First commit created

🌿 Setting branch to 'main'...
✅ Branch renamed to 'main'

🔗 Adding remote origin: https://github.com/Drakaniia/python-automation.git
✅ Remote origin added

⬆️  Pushing to GitHub...

✅ SUCCESS! Repository initialized and pushed to GitHub!
🌐 Your repository: https://github.com/Drakaniia/python-automation
```

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
├── GitInitMenu
└── [Your Custom Menu]

GitOperations
GitInitializer
StructureViewer
MenuItem
```

## Requirements 📋

- Python 3.6+ (tested on 3.13.7)
- Git (`git --version`)
- Bash, Zsh, or Git Bash terminal

## Troubleshooting 🔍

**`magic: command not found`**
- Run `source ~/.bashrc`
- Verify alias: `type magic`

**`ModuleNotFoundError: No module named 'automation'`**
- Ensure your alias uses:
  ```bash
  alias magic="cd /path/to/python-automation && python -m automation.magic"
  ```

**Git commands not working**
- Check Git installation: `git --version`
- Ensure you're in a Git repository (for Push/Pull/Status/Log)

**Permission denied**
- Make scripts executable:
  ```bash
  chmod +x setup.sh main.py
  ```

**Push to GitHub fails**
- Check GitHub authentication (SSH keys or Personal Access Token)
- Verify repository URL is correct
- Ensure repository exists on GitHub

## Customization 🎨

### Change the Alias Name

Edit your `.bashrc`:
```bash
alias mycmd="cd /c/projectfiles/python-automation && python -m automation.magic"
```

### Exclude Additional Directories

Edit `EXCLUDE_DIRS` in `automation/structure_viewer.py`:
```python
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv"}
```

## Contributing 🤝

Pull requests and new automation modules are welcome! Follow the OOP structure and menu patterns for consistency.

## License 📄

MIT License — free to use, modify, and share.

---

**Made with ❤️ for developers who love automation and clean tooling**