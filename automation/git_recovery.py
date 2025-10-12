"""
Git Recovery Module
Allows users to view commit history and revert to previous commits
"""
import subprocess
from datetime import datetime
from automation.menu import Menu, MenuItem


class GitRecovery:
    """Handles git commit history and recovery operations"""
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        print("\n" + "="*70)
        print("🔄 GIT COMMIT RECOVERY")
        print("="*70 + "\n")
        
        # Check if we're in a git repository
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        # Get commit history
        commits = self._get_commit_history()
        
        if not commits:
            print("❌ No commits found in this repository.")
            input("\nPress Enter to continue...")
            return
        
        # Display commits
        print("📜 Commit History:\n")
        print(f"{'#':<5} {'Commit ID':<12} {'Date & Time':<25} {'Message'}")
        print("-" * 70)
        
        for idx, commit in enumerate(commits, 1):
            commit_id = commit['hash'][:10]
            timestamp = commit['date']
            message = commit['message'][:40] + "..." if len(commit['message']) > 40 else commit['message']
            print(f"{idx:<5} {commit_id:<12} {timestamp:<25} {message}")
        
        print("-" * 70 + "\n")
        
        # Ask user how they want to select
        print("How would you like to select a commit?")
        print("  1. By commit number (from the list above)")
        print("  2. By entering commit ID directly")
        print("  3. Cancel and return to menu\n")
        
        choice = input("Your choice (1/2/3): ").strip()
        
        if choice == '1':
            self._select_by_number(commits)
        elif choice == '2':
            self._select_by_id()
        elif choice == '3':
            print("\n❌ Operation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    
    def _select_by_number(self, commits):
        """Select commit by number from list"""
        try:
            num = input("\nEnter commit number to recover: ").strip()
            num = int(num)
            
            if 1 <= num <= len(commits):
                commit = commits[num - 1]
                self._confirm_and_revert(commit)
            else:
                print(f"\n❌ Invalid number. Please enter between 1 and {len(commits)}")
                input("\nPress Enter to continue...")
        except ValueError:
            print("\n❌ Invalid input. Please enter a number.")
            input("\nPress Enter to continue...")
    
    def _select_by_id(self):
        """Select commit by entering commit ID"""
        commit_id = input("\nEnter commit ID (hash): ").strip()
        
        if not commit_id:
            print("\n❌ Commit ID cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        # Verify commit exists
        result = subprocess.run(
            ["git", "cat-file", "-t", commit_id],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n❌ Commit '{commit_id}' not found.")
            input("\nPress Enter to continue...")
            return
        
        # Get commit details
        commit_info = self._get_commit_details(commit_id)
        self._confirm_and_revert(commit_info)
    
    def _confirm_and_revert(self, commit):
        """Confirm and perform the revert operation"""
        print("\n" + "="*70)
        print("⚠️  COMMIT RECOVERY CONFIRMATION")
        print("="*70)
        print(f"\nCommit ID:  {commit['hash']}")
        print(f"Date:       {commit['date']}")
        print(f"Author:     {commit['author']}")
        print(f"Message:    {commit['message']}\n")
        
        print("Recovery Options:")
        print("  1. Hard Reset (⚠️  DESTRUCTIVE - loses all changes after this commit)")
        print("  2. Soft Reset (keeps changes as uncommitted)")
        print("  3. Create new branch from this commit")
        print("  4. Cancel\n")
        
        choice = input("Your choice (1/2/3/4): ").strip()
        
        if choice == '1':
            self._hard_reset(commit['hash'])
        elif choice == '2':
            self._soft_reset(commit['hash'])
        elif choice == '3':
            self._create_branch(commit['hash'])
        elif choice == '4':
            print("\n❌ Operation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    
    def _hard_reset(self, commit_hash):
        """Perform hard reset to commit"""
        print("\n⚠️  WARNING: This will permanently delete all commits after this point!")
        print("⚠️  Are you absolutely sure?")
        confirm = input("Type 'YES' to confirm: ").strip()
        
        if confirm == 'YES':
            print("\n🔧 Performing hard reset...")
            result = subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("\n✅ Successfully reset to commit!")
                print(result.stdout)
                print("\n⚠️  Note: Use 'git push --force' to update remote (if needed)")
            else:
                print(f"\n❌ Error: {result.stderr}")
            
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Operation cancelled.")
            input("\nPress Enter to continue...")
    
    def _soft_reset(self, commit_hash):
        """Perform soft reset to commit"""
        print("\n🔧 Performing soft reset...")
        result = subprocess.run(
            ["git", "reset", "--soft", commit_hash],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Successfully reset to commit!")
            print("Your changes are now uncommitted and staged.")
            print(result.stdout)
        else:
            print(f"\n❌ Error: {result.stderr}")
        
        input("\nPress Enter to continue...")
    
    def _create_branch(self, commit_hash):
        """Create a new branch from commit"""
        branch_name = input("\nEnter new branch name: ").strip()
        
        if not branch_name:
            print("\n❌ Branch name cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n🔧 Creating branch '{branch_name}' from commit...")
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name, commit_hash],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ Successfully created and switched to branch '{branch_name}'!")
            print(result.stdout)
        else:
            print(f"\n❌ Error: {result.stderr}")
        
        input("\nPress Enter to continue...")
    
    def _get_commit_history(self, limit=50):
        """Get commit history with details"""
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
    
    def _get_commit_details(self, commit_id):
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
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0


class GitRecoveryMenu(Menu):
    """Menu for Git recovery operations"""
    
    def __init__(self):
        self.git_recovery = GitRecovery()
        super().__init__("🔄 Git Commit Recovery")
    
    def setup_items(self):
        """Setup menu items"""
        self.items = [
            MenuItem("View & Recover Commits", lambda: self.git_recovery.show_recovery_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]