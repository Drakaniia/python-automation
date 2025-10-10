"""
Git operations manager
"""
import subprocess
from pathlib import Path
from automation.menu import Menu, MenuItem


class GitOperations:
    """Handles Git operations"""
    
    @staticmethod
    def run_command(cmd: list, capture_output: bool = False):
        """Run a git command"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                return result.stdout
            else:
                subprocess.run(cmd, check=True)
                return None
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Command failed: {' '.join(cmd)}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return None
        except FileNotFoundError:
            print("\n❌ Git is not installed or not in PATH")
            return None
    
    def status(self):
        """Show git status"""
        print("\n📊 Git Status:\n")
        self.run_command(["git", "status"])
    
    def log(self):
        """Show git log"""
        print("\n📜 Git Log (last 10 commits):\n")
        self.run_command([
            "git", "log", 
            "--oneline", 
            "--graph", 
            "--decorate", 
            "-n", "10"
        ])
    
    def pull(self):
        """Pull from remote"""
        print("\n⬇️  Pulling from remote...\n")
        branch = self.run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True
        )
        if branch:
            branch = branch.strip()
            print(f"Current branch: {branch}")
            self.run_command(["git", "pull", "origin", branch])
            print("\n✅ Pull completed")
    
    def push(self):
        """Push to remote"""
        print("\n📤 Push Operation\n")
        
        # Check if there are changes to commit
        status = self.run_command(
            ["git", "status", "--porcelain"],
            capture_output=True
        )
        
        if status and status.strip():
            print("Uncommitted changes detected:\n")
            self.run_command(["git", "status", "-s"])
            
            commit = input("\nCommit changes? (y/n): ").strip().lower()
            if commit == 'y':
                msg = input("Commit message: ").strip()
                if msg:
                    self.run_command(["git", "add", "."])
                    self.run_command(["git", "commit", "-m", msg])
                else:
                    print("❌ Commit cancelled - no message provided")
                    return
        
        # Push
        branch = self.run_command(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True
        )
        if branch:
            branch = branch.strip()
            print(f"\n⬆️  Pushing to origin/{branch}...\n")
            self.run_command(["git", "push", "origin", branch])
            print("\n✅ Push completed")


class GitMenu(Menu):
    """Git operations menu"""
    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("GitHub Operations")
    
    def setup_items(self):
        self.items = [
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Log", lambda: self.git_ops.log()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Push", lambda: self.git_ops.push()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]