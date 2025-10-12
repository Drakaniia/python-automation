"""
Git Pull Module
Handles pull operations from remote repository
"""
import subprocess


class GitPull:
    """Handles git pull operations"""
    
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
            return False
        
        # Check if remote exists
        if not self._has_remote():
            print("❌ No remote repository configured.")
            print("💡 Use 'Initialize Git & Push to GitHub' to set up remote.")
            input("\nPress Enter to continue...")
            return False
        
        print("🔄 Pulling changes from remote...")
        success = self._run_command(["git", "pull"])
        
        if success:
            print("\n✅ Successfully pulled from remote!")
        else:
            print("\n❌ Pull failed. Check your network connection and remote configuration.")
        
        input("\nPress Enter to continue...")
        return success
    
    def pull_with_rebase(self):
        """Pull with rebase strategy"""
        print("\n" + "="*70)
        print("⬇️  GIT PULL (with rebase)")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return False
        
        print("🔄 Pulling with rebase...")
        success = self._run_command(["git", "pull", "--rebase"])
        
        if success:
            print("\n✅ Successfully pulled with rebase!")
        
        input("\nPress Enter to continue...")
        return success
    
    def fetch(self):
        """Fetch from remote without merging"""
        print("\n📥 Fetching from remote...")
        return self._run_command(["git", "fetch"])
    
    def get_remote_info(self):
        """Get information about remote repository"""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def _has_remote(self):
        """Check if remote repository is configured"""
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
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