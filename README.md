# 🚀 Python Automation System

A powerful, developer-friendly CLI automation toolkit with AI-powered Git operations, interactive navigation, and intelligent commit management.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

---

## ✨ Unique Features

### 🔧 Comprehensive Git Management

- **Repository Initialization**: One-command setup for new Git repositories with remote configuration
- **Smart Status Checking**: View detailed repository status with color-coded output
- **Commit Recovery**: Interactive interface to revert to previous commits
- **Multiple Reset Options**: Hard reset, soft reset, or create branches from any commit
- **Pull Operations**: Simple pull and pull-with-rebase functionality
- **Remote Management**: Easy configuration and updates of remote URLs

### 📊 Project Structure Visualization

- **AI-Readable Format**: Generates clean tree structures perfect for sharing with AI assistants
- **File Size Information**: Displays human-readable file sizes for each file
- **Smart Filtering**: Automatically excludes common unwanted directories (`__pycache__`, `.git`, `node_modules`)
- **Recursive Scanning**: Full project tree with nested directory support
- **Summary Statistics**: Shows total file and directory counts

### 🎯 Developer Experience

- **Single Command Access**: Just type `magic` anywhere in your terminal
- **Beautiful UI**: Clean, emoji-enhanced interface with clear visual hierarchy
- **Error Handling**: Graceful error messages with helpful suggestions
- **Permission Management**: Handles permission errors elegantly
- **Encoding Support**: Robust UTF-8 encoding with fallback handling

### 📝 Changelog Intelligence

- **Automatic Categorization**: Organizes commits into Features, Bug Fixes, Refactoring, and Documentation
- **Growth Analytics**: Tracks code growth/shrinkage with line counts
- **Contributor Recognition**: Lists all contributors for multi-author projects
- **Change Summaries**: Provides concise but comprehensive change descriptions
- **Historical Context**: Maintains full changelog history with timestamps

---

## 📦 Installation

### Prerequisites

- **Python 3.7 or higher**
- **Git** (for Git operations)
- **Bash shell** (Linux/macOS) or **Git Bash** (Windows)

### Quick Install

#### Option 1: Automated Setup (Recommended)

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/python-automation.git
cd python-automation
```

2. **Run the setup script**:

```bash
chmod +x setup.sh
./setup.sh
```

3. **Activate the alias**:

```bash
source ~/.bashrc  # or ~/.zshrc for Zsh users
```

4. **Start using it**:

```bash
magic
```

#### Option 2: Manual Setup

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/python-automation.git
cd python-automation
```

2. **Add alias to your shell configuration**:

For Bash (Linux/macOS):

```bash
echo 'alias magic="python3 /full/path/to/python-automation/main.py"' >> ~/.bashrc
source ~/.bashrc
```

For Zsh (macOS):

```bash
echo 'alias magic="python3 /full/path/to/python-automation/main.py"' >> ~/.zshrc
source ~/.zshrc
```

For Windows (Git Bash):

```bash
echo 'alias magic="python /full/path/to/python-automation/main.py"' >> ~/.bashrc
source ~/.bashrc
```

3. **Make the script executable** (Linux/macOS):

```bash
chmod +x main.py
```

4. **Run it**:

```bash
magic
```

---

## 🚀 Usage

### Starting the Program

Simply type `magic` anywhere in your terminal:

```bash
magic
```

### Main Menu Options

```
🚀 Python Automation System - Main Menu
══════════════════════════════════════════════════════════════════
  📍 Current Directory: /your/current/directory
══════════════════════════════════════════════════════════════════
  ► 1. GitHub Operations
    2. Show Project Structure
    3. Navigate Folders
    4. Exit
══════════════════════════════════════════════════════════════════
```

### Navigation

- **Arrow Keys**: Use ↑/↓ to navigate through options
- **Enter**: Select the highlighted option
- **Number Keys**: Directly select an option by typing its number

---

## 🔧 Feature Guides

### 1. AI-Powered Git Push

**What it does**: Analyzes your changes and generates an intelligent commit message automatically.

**Usage**:

1. Make changes to your files
2. Navigate to: `GitHub Operations` → `Push (Add, Commit & Push) 🤖 AI-Powered`
3. Review the AI-generated message
4. Confirm or edit the message
5. Automatically pushes and updates changelog

**Example**:

```
🧠 Generating AI-powered commit message...

════════════════════════════════════════════════════════════════
📝 Suggested Commit Message:
"🤖 Add AI: commit_summarizer module"
════════════════════════════════════════════════════════════════

Use this message? [Y/n]:
```

### 2. Interactive Folder Navigation

**What it does**: Navigate your file system with arrow keys and visual feedback.

**Usage**:

1. Select `Navigate Folders` from main menu
2. Use arrow keys to browse directories
3. Press → or Enter to enter a directory
4. Press ← to go back
5. Press Enter on empty line to confirm current directory

**Features**:

- Shows absolute and relative paths
- Displays all subdirectories
- Maintains navigation history
- Highlights current selection

### 3. Git Repository Initialization

**What it does**: Sets up a new Git repository and connects it to GitHub in one go.

**Usage**:

1. Navigate to your project directory
2. Select `GitHub Operations` → `Initialize Git & Push to GitHub`
3. Enter your GitHub repository URL
4. Automatically creates README, initializes Git, and pushes

**What it creates**:

- `.git` directory
- Initial commit
- `main` branch
- Remote origin connection
- First push to GitHub

### 4. Project Structure Viewer

**What it does**: Generates a clean, AI-readable tree structure of your project.

**Usage**:

1. Navigate to your project directory
2. Select `Show Project Structure`
3. Copy the output to share with AI assistants

**Example Output**:

```
📁 PROJECT STRUCTURE (AI-Readable Format)
══════════════════════════════════════════════════════════════════

📍 Current Directory: /home/user/python-automation
📍 Absolute Path: /home/user/python-automation

```

python-automation/
├── automation/
│ ├── **init**.py (234B)
│ ├── folder_navigator.py (7.2KB)
│ ├── git_operations.py (3.1KB)
│ ├── menu.py (8.5KB)
│ └── github/
│ ├── **init**.py (156B)
│ ├── commit_summarizer.py (12.3KB)
│ └── git_push_ai.py (4.8KB)
├── main.py (456B)
└── README.md (8.9KB)

```

📊 Summary: 12 directories, 45 files
```

### 5. Commit Recovery

**What it does**: Safely revert to previous commits with multiple recovery options.

**Usage**:

1. Select `GitHub Operations` → `Git Recovery (Revert to Previous Commit)`
2. Choose a commit from the list or enter a commit ID
3. Select recovery method:
   - **Hard Reset**: Completely revert (destructive)
   - **Soft Reset**: Keep changes as uncommitted
   - **Create Branch**: Create new branch from that commit

**Safety Features**:

- Requires explicit confirmation for destructive operations
- Shows full commit details before reverting
- Provides multiple recovery strategies

### 6. Automatic Changelog

**What it does**: Maintains a beautiful, categorized changelog automatically.

**Generated Format**:

```markdown
### 2025-10-18 — 🚀 Feature Blast

**3 commits** across **8 files**. The codebase grew by 234 lines.

#### ✨ New Features

- Add AI-powered commit generation (`767fe68`)
- Implement smart file analysis (`aabbc61`)

#### 🐛 Bug Fixes

- Fix encoding issues in git operations (`8ed4705`)

#### 🔧 Refactoring & Improvements

- Consolidate Git operations into unified module (`9d18d76`)
```

---

## 📁 Project Structure

```
python-automation/
├── automation/                 # Main package
│   ├── __init__.py            # Package initialization
│   ├── folder_navigator.py    # Interactive folder navigation
│   ├── git_operations.py      # Git operations orchestrator
│   ├── menu.py                # Menu system and main menu
│   ├── structure_viewer.py    # Project structure viewer
│   └── github/                # Git-specific modules
│       ├── __init__.py
│       ├── commit_summarizer.py   # AI commit message generator
│       ├── git_initializer.py     # Repository initialization
│       ├── git_log.py             # Commit history viewer
│       ├── git_pull.py            # Pull operations
│       ├── git_push.py            # Traditional push
│       ├── git_push_ai.py         # AI-powered push
│       ├── git_recover.py         # Commit recovery
│       └── git_status.py          # Status operations
├── main.py                    # Entry point
├── setup.sh                   # Installation script
├── test_ai_commit.py          # Integration tests
├── README.md                  # This file
├── CHANGELOG.md               # Auto-generated changelog
└── FOLDER_STRUCTURE.MD        # Structure documentation
```

## 🎯 Common Use Cases

### Scenario 1: Starting a New Project

```bash
mkdir my-new-project
cd my-new-project
magic
# Select: Navigate Folders (confirm directory)
# Select: GitHub Operations → Initialize Git & Push to GitHub
# Enter repository URL
# Done! Project is on GitHub
```

### Scenario 2: Quick Commit with AI

```bash
cd my-project
# ... make changes ...
magic
# Select: GitHub Operations → Push (AI-Powered)
# Review AI message
# Confirm
# Done! Changes pushed with smart message and updated changelog
```

### Scenario 3: Exploring Project Structure

```bash
cd some-project
magic
# Select: Show Project Structure
# Copy output to share with team or AI
```

### Scenario 4: Recovering from Mistake

```bash
magic
# Select: GitHub Operations → Git Recovery
# Choose problematic commit
# Select: Soft Reset (keeps your changes)
# Fix issues
# Commit again
```

---

## ⚙️ Configuration

### Shell Compatibility

The system automatically detects your shell and configures accordingly:

- **Bash**: Uses `~/.bashrc`
- **Zsh**: Uses `~/.zshrc`
- **Git Bash (Windows)**: Uses `~/.bashrc`

### Python Version

The setup script automatically detects:

- `python3` command (preferred)
- `python` command (if it's Python 3)

---

## 🐛 Troubleshooting

### Issue: "magic: command not found"

**Solution**: Reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc
```

### Issue: Arrow keys not working

**Solution**: The system has fallback support. Use number keys instead:

- Type the number of your choice
- Press Enter

### Issue: "Not a git repository"

**Solution**: Initialize Git first:

```bash
magic
# Select: GitHub Operations → Initialize Git & Push to GitHub
```

### Issue: Permission denied

**Solution**: Make the script executable:

```bash
chmod +x /path/to/python-automation/main.py
```

### Issue: Encoding errors

**Solution**: The system has built-in UTF-8 encoding with fallback. If issues persist, ensure your terminal supports UTF-8:

```bash
export LANG=en_US.UTF-8
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Use the AI-powered commit: `magic` → Git Operations → AI Push
4. Push to your branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Drakaniia/python-automation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Drakaniia/python-automation/discussions)
- **Email**: alistairybaez574@gmail.com

---

## 👏 Acknowledgments

- Built with ❤️ for developers
- Inspired by the need for smarter Git workflows
- Special thanks to the Python and Git communities

---

## 🚀 Quick Start Reminder

```bash
# Install
git clone https://github.com/yourusername/python-automation.git
cd python-automation
./setup.sh
source ~/.bashrc

# Use
magic
```

**That's it! You're ready to automate! 🎉**

---

Made with ❤️ by [Eyabnyez](https://github.com/Drakaniia)
