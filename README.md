# Python Automation System 🚀

A powerful, object-oriented Python automation toolkit for developers. Execute common development tasks with a simple command: **`magic`**

## ✨ New Features

### 🎯 Arrow Key Navigation
Navigate through all menus using **↑** and **↓** arrow keys! The selected option is highlighted in cyan. Press **Enter** to execute. You can still type numbers for quick access.

### 🔄 Git Commit Recovery
View your complete commit history and recover to any previous state:
- Browse commits by number or search by ID
- See commit timestamps, IDs, and messages
- Three recovery modes:
  - **Hard Reset**: Roll back completely (destructive)
  - **Soft Reset**: Keep changes as uncommitted
  - **Create Branch**: Safely explore old commits

### 📍 Persistent Working Directory
Navigate to any folder and **stay there**! All Git operations, structure views, and initializations now work in your currently navigated directory. No more jumping back to the root!

## Features ✨

- **GitHub Operations**: Push, pull, status, and log operations
- **Git Repository Initialization**: Initialize and push new repos to GitHub with one command
- **Git Commit Recovery**: View history and revert to any previous commit
- **Project Structure Viewer**: Visualize current directory structure in AI-readable format
- **Folder Navigator**: Interactive directory navigation with persistent location
- **Arrow Key Menu Navigation**: Smooth, intuitive menu control
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
    ├── menu.py                 # Menu system (base classes + arrow navigation)
    ├── git_manager.py          # Git operations (push/pull/status/log)
    ├── git_initializer.py      # Git init & first push automation
    ├── git_recovery.py         # Git commit recovery & rollback ✨NEW
    ├── structure_viewer.py     # Project structure viewer (AI-readable)
    └── folder_navigator.py     # Interactive folder navigation
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
touch automation/{__init__.py,magic.py,menu.py,git_manager.py,git_initializer.py,git_recovery.py,structure_viewer.py,folder_navigator.py}
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

You should see the main menu with arrow key navigation! 🎉

## Usage 🎯

Simply type `magic` anywhere in your terminal:

```bash
magic
```

### Main Menu Options

Use **↑/↓ arrow keys** to navigate, **Enter** to select (or type numbers):

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

3. **Git Recovery (Revert to Previous Commit)** ✨NEW
   - View complete numbered commit history
   - See commit IDs, timestamps, and messages
   - Select commits by number or ID
   - Three recovery options:
     - **Hard Reset**: ⚠️ Destructive - permanently removes all commits after selected point
     - **Soft Reset**: Keeps changes as uncommitted (safe)
     - **Create Branch**: Create new branch from old commit (safest)
   
   **Example session:**
   ```
   📜 Commit History:
   
   #     Commit ID    Date & Time               Message
   ----------------------------------------------------------------------
   1     a1b2c3d4e5   2025-10-10 14:32:15      Added new feature
   2     f6g7h8i9j0   2025-10-09 09:21:43      Fixed bug in login
   3     k1l2m3n4o5   2025-10-08 16:45:22      Initial commit
   
   Your choice: 1
   
   Recovery Options:
     1. Hard Reset (loses all changes after this commit)
     2. Soft Reset (keeps changes as uncommitted)
     3. Create new branch from this commit
     4. Cancel
   ```

4. **Show Project Structure** 📊
   - Displays **current directory** structure (respects navigation!)
   - AI-readable format (easy to copy/paste to AI assistants)
   - Shows file sizes
   - Clean tree visualization with proper indentation
   - Example output:
     ```
     python-automation/
     ├── main.py (1.2KB)
     ├── setup.sh (3.4KB)
     ├── README.md (12.1KB)
     └── automation/
         ├── __init__.py (0.1KB)
         ├── magic.py (0.5KB)
         ├── menu.py (4.8KB)
         ├── git_manager.py (4.1KB)
         ├── git_initializer.py (3.8KB)
         ├── git_recovery.py (8.3KB) ✨NEW
         ├── structure_viewer.py (2.9KB)
         └── folder_navigator.py (4.5KB)
     ```

5. **Navigate Folders** 🗂️
   - Interactive directory navigation with **persistent location**
   - View all subdirectories in current location
   - Navigate by entering directory number
   - Working directory persists across all operations!
   - Commands:
     - **Number (1, 2, 3...)**: Enter that directory
     - **`back` or `..`**: Go up one level
     - **`home`**: Jump to home directory
     - **`exit` or `q`**: Return to main menu (stays in current directory)
   
   **Example session:**
   ```
   📍 Current Location: /c/projects
   
   📁 Available Directories:
   1. python-automation/
   2. web-projects/
   3. data-science/
   
   Your choice: 1
   ✅ Entered: python-automation/
   
   [Navigate to main menu - you're still in python-automation/]
   [All Git operations now work in python-automation/]
   ```

6. **Exit**
   - Close the automation system

## Git Recovery Examples 📝

### Example 1: Undo Last Commit (Keep Changes)

```
Select option 3: Git Recovery
→ Shows commit list
→ Select commit #2 (before your mistake)
→ Choose "Soft Reset"
→ Your changes are now uncommitted - edit and recommit!
```

### Example 2: Roll Back to Stable Version

```
Select option 3: Git Recovery
→ Shows commit list
→ Select commit #5 (last known good state)
→ Choose "Hard Reset"
→ Type 'YES' to confirm
→ Repository is now at that exact state
```

### Example 3: Explore Old Code Safely

```
Select option 3: Git Recovery
→ Shows commit list
→ Select commit #10 (interesting old feature)
→ Choose "Create new branch"
→ Enter branch name: "explore-old-feature"
→ Safely explore without affecting main branch
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
- **State Management**: Persistent working directory across operations

### Class Diagram

```
Menu (ABC)
├── MainMenu
├── GitMenu
├── GitInitMenu
├── GitRecoveryMenu ✨NEW
└── FolderNavigatorMenu

GitOperations
GitInitializer
GitRecovery ✨NEW
StructureViewer
FolderNavigator
MenuItem
```

## Requirements 📋

- Python 3.6+ (tested on 3.13.7)
- Git (`git --version`)
- Bash, Zsh, or Git Bash terminal
- Unix/Linux/Mac (for arrow key navigation)
  - Windows Git Bash also supported

## Troubleshooting 🔍

**`magic: command not found`**
- Run `source ~/.bashrc`
- Verify alias: `type magic`

**`ModuleNotFoundError: No module named 'automation'`**
- Ensure your alias uses:
  ```bash
  alias magic="cd /path/to/python-automation && python -m automation.magic"
  ```

**Arrow keys not working**
- Ensure you're using a Unix-like terminal (Git Bash on Windows)
- You can still type numbers to select options

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

**Folder navigator can't access directory**
- Check directory permissions
- Some system directories may be restricted

**Git Recovery not showing commits**
- Ensure you're in a git repository
- Check that commits exist: `git log`

## Customization 🎨

### Change the Alias Name

Edit your `.bashrc`:
```bash
alias mycmd="cd /c/projectfiles/python-automation && python -m automation.magic"
```

### Exclude Additional Directories in Structure Viewer

Edit `EXCLUDE_DIRS` in `automation/structure_viewer.py`:
```python
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules", "venv", "build", "dist"}
```

### Customize Menu Colors

Edit the ANSI color codes in `automation/menu.py`:
```python
# Change from cyan (46) to green (42), red (41), etc.
print(f"  \033[1;42m► {i + 1}. {item.label}\033[0m")
```

## Tips & Tricks 💡

### Persistent Navigation Workflow

1. Run `magic` from anywhere
2. Select "Navigate Folders"
3. Browse to your project directory
4. Return to main menu
5. All operations now work in that directory!
6. Push code, view structure, recover commits - all in your chosen location

### AI-Readable Structure Output

The "Show Project Structure" feature outputs in a format optimized for AI assistants:
- Clean tree structure with proper indentation
- File sizes included
- Easy to copy/paste into ChatGPT, Claude, or other AI tools
- Helps AI understand your project layout quickly

### Safe Git Recovery

Before using Hard Reset:
1. Always create a backup branch first
2. Or use "Create Branch" option to explore safely
3. Use Soft Reset if you want to keep your changes
4. Hard Reset is permanent - use with caution!

### Quick Menu Navigation

- Use arrow keys for browsing all options
- Type numbers for quick access to known options
- Press Ctrl+C to exit at any time

## Contributing 🤝

Pull requests and new automation modules are welcome! Follow the OOP structure and menu patterns for consistency.

## License 📄

MIT License — free to use, modify, and share.

---

**Made with ❤️ for developers who love automation and clean tooling**

### Changelog

**v2.0.0** (Latest)
- ✨ Added arrow key navigation for all menus
- ✨ Added Git Commit Recovery system
- ✨ Persistent working directory across operations
- 🐛 Fixed folder navigation not persisting directory
- 🎨 Enhanced menu display with current directory indicator
- 📝 Comprehensive documentation updates

**v1.0.0**
- Initial release with core features