"""
Git Recovery Module
Handles commit recovery, rollback, and history management
"""
import subprocess


class GitRecover:
    """Handles git commit recovery and rollback operations"""
    
    def __init__(self):
        pass
    
    def show_recovery_menu(self, commit_history_func, commit_details_func, verify_commit_func):
        """
        Show the commit recovery interface
        
        Args:
            commit_history_func: Function to get commit history
            commit_details_func: Function to get commit details by ID
            verify_commit_func: Function to verify commit exists
        """
        print("\n" + "="*70)
        print("🔄 GIT COMMIT RECOVERY")
        print("="*70 + "\n")
        
        # Check if we're in a git repository
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        # Get commit history
        commits = commit_history_func()
        
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
            self._select_by_id(commit_details_func, verify_commit_func)
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
    
    def _select_by_id(self, commit_details_func, verify_commit_func):
        """Select commit by entering commit ID"""
        commit_id = input("\nEnter commit ID (hash): ").strip()
        
        if not commit_id:
            print("\n❌ Commit ID cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        # Verify commit exists
        if not verify_commit_func(commit_id):
            print(f"\n❌ Commit '{commit_id}' not found.")
            input("\nPress Enter to continue...")
            return
        
        # Get commit details
        commit_info = commit_details_func(commit_id)
        if commit_info:
            self._confirm_and_revert(commit_info)
        else:
            print(f"\n❌ Could not retrieve details for commit '{commit_id}'.")
            input("\nPress Enter to continue...")
    
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
            self.hard_reset(commit['hash'])
        elif choice == '2':
            self.soft_reset(commit['hash'])
        elif choice == '3':
            self.create_branch(commit['hash'])
        elif choice == '4':
            print("\n❌ Operation cancelled.")
            input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    
    def hard_reset(self, commit_hash):
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
    
    def soft_reset(self, commit_hash):
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
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\n❌ Error: {result.stderr}")
        
        input("\nPress Enter to continue...")
    
    def create_branch(self, commit_hash):
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
            if result.stdout:
                print(result.stdout)
        else:
            print(f"\n❌ Error: {result.stderr}")
        
        input("\nPress Enter to continue...")
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0