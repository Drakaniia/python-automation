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
git clone https://github.com/Drakaniia/python-automation.git
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
git clone https://github.com/Drakaniia/python-automation.git
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

