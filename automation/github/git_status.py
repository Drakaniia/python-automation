"""
Git Status Module
Handles repository status checking and display
"""
import subprocess


class GitStatus:
    """Handles git status operations"""
    
    def __init__(self):
        pass
    
    def show_status(self):
        """Display current git status"""
        print("\n" + "="*70)
        print("📊 GIT STATUS")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        self._run_command(["git", "status"])
        input("\nPress Enter to continue...")
    
    def get_status_porcelain(self):
        """Get git status in machine-readable format"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def has_uncommitted_changes(self):
        """Check if there are uncommitted changes"""
        status = self.get_status_porcelain()
        return bool(status)
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command):
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
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