"""
Git Push/Pull Module
Handles push, pull, and synchronization operations
"""
import subprocess


class GitPush:
    """Handles git push and pull operations"""
    
    def __init__(self):
        pass
    
    def pull(self):
        """Pull from remote repository"""
        print("\n" + "="*70)
        print("⬇️  GIT PULL")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        self._run_command(["git", "pull"])
        input("\nPress Enter to continue...")
    
    def push(self):
        """Add, commit, and push changes to remote"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
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
    
    def force_push(self, branch="main"):
        """Force push to remote (use with caution)"""
        print("\n⚠️  WARNING: Force push will overwrite remote history!")
        confirm = input("Type 'YES' to confirm: ").strip()
        
        if confirm == 'YES':
            print("\n🔧 Force pushing...")
            if self._run_command(["git", "push", "--force", "origin", branch]):
                print("\n✅ Force push completed!")
            else:
                print("\n❌ Force push failed!")
        else:
            print("\n❌ Force push cancelled.")
    
    def push_with_upstream(self, branch="main"):
        """Push and set upstream tracking"""
        print(f"\n⬆️  Pushing to origin/{branch} with upstream...")
        return self._run_command(["git", "push", "-u", "origin", branch])
    
    def get_remote_url(self):
        """Get the current remote URL"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def set_remote_url(self, url):
        """Set or update the remote URL"""
        # Check if remote exists
        if self.get_remote_url():
            print("⚠️  Remote 'origin' exists, updating URL...")
            return self._run_command(["git", "remote", "set-url", "origin", url])
        else:
            print("➕ Adding remote 'origin'...")
            return self._run_command(["git", "remote", "add", "origin", url])
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def _run_command(self, command):
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
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