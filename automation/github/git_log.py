"""
Git Log Module
Handles commit history viewing and log operations
"""
import subprocess
from datetime import datetime


class GitLog:
    """Handles git log and commit history operations"""
    
    def __init__(self):
        pass
    
    def show_log(self, limit=10):
        """Display git commit log"""
        print("\n" + "="*70)
        print(f"📜 GIT LOG (Last {limit} commits)")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        self._run_command(["git", "log", "--oneline", f"-{limit}"])
        input("\nPress Enter to continue...")
    
    def get_commit_history(self, limit=50):
        """Get detailed commit history with metadata"""
        try:
            # Format: hash|author|date|message
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ai|%s"],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commit_hash, author, date, message = parts
                        # Parse and format date
                        try:
                            dt = datetime.fromisoformat(date.replace(' +', '+').replace(' -', '-'))
                            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            formatted_date = date[:19]  # Fallback
                        
                        commits.append({
                            'hash': commit_hash,
                            'author': author,
                            'date': formatted_date,
                            'message': message
                        })
            
            return commits
        except subprocess.CalledProcessError:
            return []
        except FileNotFoundError:
            return []
    
    def get_commit_details(self, commit_id):
        """Get details for a specific commit"""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ai|%s", commit_id],
                capture_output=True,
                text=True,
                check=True
            )
            
            parts = result.stdout.strip().split('|', 3)
            if len(parts) == 4:
                commit_hash, author, date, message = parts
                try:
                    dt = datetime.fromisoformat(date.replace(' +', '+').replace(' -', '-'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = date[:19]
                
                return {
                    'hash': commit_hash,
                    'author': author,
                    'date': formatted_date,
                    'message': message
                }
        except:
            pass
        
        return None
    
    def verify_commit_exists(self, commit_id):
        """Verify if a commit exists in the repository"""
        result = subprocess.run(
            ["git", "cat-file", "-t", commit_id],
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