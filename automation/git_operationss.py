"""
Consolidated Git Operations Module
Handles all Git operations: push, pull, status, log, initialization, and recovery
"""
import subprocess
from pathlib import Path
from datetime import datetime
from automation.menu import Menu, MenuItem


class GitOperations:
    """Unified Git operations handler"""
    
    def __init__(self):
        self.current_path = Path.cwd()
    
    # ========== BASIC GIT OPERATIONS ==========
    
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
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        print("\n" + "="*70)
        print("🚀 Git Repository Initialization & First Push")
        print("="*70 + "\n")
        
        # Show current directory
        current_dir = Path.cwd()
        print(f"📍 Current Directory: {current_dir}")
        print(f"📍 Absolute Path: {current_dir.absolute()}\n")
        
        # Confirm this is the right directory
        confirm = input("Is this the correct project directory? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n❌ Operation cancelled. Please navigate to the correct directory first.")
            input("\nPress Enter to continue...")
            return
        
        # Check if .git exists
        git_exists = (current_dir / ".git").exists()
        
        if git_exists:
            print("\n⚠️  Git repository already exists in this directory.")
            print("This will configure remote and push existing commits.\n")
            
            # Show current status
            print("📊 Current Git Status:")
            self._run_command(["git", "status", "--short"])
            print()
            
            choice = input("Continue? (y/n): ").strip().lower()
            if choice != 'y':
                print("\n❌ Operation cancelled.")
                input("\nPress Enter to continue...")
                return
        
        # Get repository URL
        print("\n📝 Enter your GitHub repository URL:")
        print("Example: https://github.com/username/repo-name.git")
        repo_url = input("Repository URL: ").strip()
        
        if not repo_url:
            print("\n❌ Repository URL cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        print("\n🔧 Starting Git setup...\n")
        
        # If git doesn't exist, initialize it
        if not git_exists:
            # Step 1: Create README if it doesn't exist
            readme_path = Path("README.md")
            if not readme_path.exists():
                print("📄 Creating README.md...")
                try:
                    with open(readme_path, "w") as f:
                        f.write(f"# {current_dir.name}\n\n")
                        f.write("This project was initialized using Python Automation System.\n")
                    print("✅ README.md created\n")
                except Exception as e:
                    print(f"❌ Error creating README.md: {e}\n")
                    input("\nPress Enter to continue...")
                    return
            
            # Step 2: Initialize git
            print("📦 Initializing git repository...")
            if not self._run_command(["git", "init"]):
                input("\nPress Enter to continue...")
                return
            print("✅ Git repository initialized\n")
            
            # Step 3: Add files
            print("➕ Adding files to staging...")
            if not self._run_command(["git", "add", "."]):
                input("\nPress Enter to continue...")
                return
            print("✅ Files added\n")
            
            # Step 4: First commit
            print("💾 Creating first commit...")
            if not self._run_command(["git", "commit", "-m", "Initial commit"]):
                input("\nPress Enter to continue...")
                return
            print("✅ First commit created\n")
            
            # Step 5: Set branch to main
            print("🌿 Setting branch to 'main'...")
            if not self._run_command(["git", "branch", "-M", "main"]):
                input("\nPress Enter to continue...")
                return
            print("✅ Branch set to 'main'\n")
        else:
            # Repository exists, check if there are uncommitted changes
            print("🔍 Checking for uncommitted changes...")
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print("\n⚠️  You have uncommitted changes:")
                print(result.stdout)
                
                commit_choice = input("\nDo you want to commit these changes first? (y/n): ").strip().lower()
                if commit_choice == 'y':
                    commit_msg = input("Enter commit message: ").strip()
                    if not commit_msg:
                        commit_msg = "Update files before push"
                    
                    print("\n➕ Adding files...")
                    if not self._run_command(["git", "add", "."]):
                        input("\nPress Enter to continue...")
                        return
                    
                    print("💾 Committing changes...")
                    if not self._run_command(["git", "commit", "-m", commit_msg]):
                        input("\nPress Enter to continue...")
                        return
                    print("✅ Changes committed\n")
            else:
                print("✅ No uncommitted changes\n")
            
            # Ensure we're on main branch
            print("🌿 Checking current branch...")
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            if current_branch != "main":
                print(f"📌 Current branch: {current_branch}")
                switch = input("Switch to 'main' branch? (y/n): ").strip().lower()
                if switch == 'y':
                    # Check if main exists
                    result = subprocess.run(
                        ["git", "rev-parse", "--verify", "main"],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        # main exists, switch to it
                        if not self._run_command(["git", "checkout", "main"]):
                            input("\nPress Enter to continue...")
                            return
                    else:
                        # main doesn't exist, rename current branch
                        if not self._run_command(["git", "branch", "-M", "main"]):
                            input("\nPress Enter to continue...")
                            return
                    print("✅ Switched to 'main'\n")
        
        # Step 6: Add/Update remote
        print(f"🔗 Configuring remote origin: {repo_url}")
        
        # Check if remote exists
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Remote exists, update it
            print("⚠️  Remote 'origin' exists, updating URL...")
            if not self._run_command(["git", "remote", "set-url", "origin", repo_url]):
                input("\nPress Enter to continue...")
                return
        else:
            # Add new remote
            if not self._run_command(["git", "remote", "add", "origin", repo_url]):
                input("\nPress Enter to continue...")
                return
        print("✅ Remote origin configured\n")
        
        # Step 7: Push to GitHub
        print("⬆️  Pushing to GitHub...")
        if not self._run_command(["git", "push", "-u", "origin", "main"]):
            print("\n⚠️  Push failed. This might be because:")
            print("  • The remote repository doesn't exist")
            print("  • You don't have permission to push")
            print("  • The remote has commits you don't have locally")
            print("\nTry: git push -u origin main --force (if you're sure)")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Repository pushed to GitHub!")
        print(f"🌐 Your repository: {repo_url.replace('.git', '')}")
        print("="*70 + "\n")
        
        input("Press Enter to continue...")
    
    # ========== GIT RECOVERY ==========
    
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
    
    # ========== UTILITY METHODS ==========
    
    def _run_command(self, command):
        """Run a shell command and return success status"""
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


class GitMenu(Menu):
    """Unified menu for all Git operations"""
    
    def __init__(self):
        self.git_ops = GitOperations()
        super().__init__("🔧 GitHub Operations")
    
    def setup_items(self):
        """Setup menu items with all Git operations"""
        self.items = [
            MenuItem("Status", lambda: self.git_ops.status()),
            MenuItem("Log (Last 10 commits)", lambda: self.git_ops.log()),
            MenuItem("Pull", lambda: self.git_ops.pull()),
            MenuItem("Push (Add, Commit & Push)", lambda: self.git_ops.push()),
            MenuItem("Initialize Git & Push to GitHub", lambda: self.git_ops.initialize_and_push()),
            MenuItem("Git Recovery (Revert to Previous Commit)", lambda: self.git_ops.show_recovery_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]