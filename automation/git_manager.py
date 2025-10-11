"""
Git Manager Module
Handles GitHub operations: push, pull, status, log
"""
import subprocess
from automation.menu import Menu, MenuItem


class GitOperations:
    """Handles Git operations"""
    
    def status(self):
        """Show git status"""
        print("\n" + "="*70)
        print("📊 GIT STATUS")
        print("="*70 + "\n")
        self._run_command(["git", "status"])
        input("\nPress Enter to continue...")
    
    def log(self):
        """Show git log"""
        print("\n" + "="*70)
        print("📜 GIT LOG (Last 10 commits)")
        print("="*70 + "\n")
        self._run_command(["git", "log", "--oneline", "-10"])
        input("\nPress Enter to continue...")
    
    def pull(self):
        """Pull from remote"""
        print("\n" + "="*70)
        print("⬇️  GIT PULL")
        print("="*70 + "\n")
        self._run_command(["git", "pull"])
        input("\nPress Enter to continue...")
    
    def push(self):
        """Add, commit, and push changes"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH")
        print("="*70 + "\n")
        
        commit_msg = input("Enter commit message: ").strip()
        if not commit_msg:
            print("❌ Commit message cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        print("\n🔧 Adding files...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        
        print("\n💾 Creating commit...")
        if not self._run_command(["git", "commit", "-m", commit_msg]):
            input("\nPress Enter to continue...")
            return
        
        print("\n⬆️  Pushing to remote...")
        if self._run_command(["git", "push"]):
            print("\n✅ Successfully pushed to remote!")
        
        input("\nPress Enter to continue...")
    
    def _run_command(self, command):
        """Run a shell command and return success status"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False


class GitMenu(Menu):
    """Menu for Git operations"""
    
    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("🔧 GitHub Operations")
    
    def setup_items(self):
        """Setup menu items"""
        self.items = [
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Log (Last 10 commits)", lambda: self.git_ops.log()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Push", lambda: self.git_ops.push()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]
