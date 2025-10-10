"""
Git Initializer Module (IMPROVED)
Automates git repository initialization and first push to GitHub
Now with better error handling and status checking
"""
import subprocess
from pathlib import Path
from automation.menu import Menu, MenuItem


class GitInitializer:
    """Handles git initialization and first push"""
    
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
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH")
            return False


class GitInitMenu(Menu):
    """Menu for Git initialization"""
    
    def __init__(self):
        self.git_init = GitInitializer()
        super().__init__("🚀 Initialize Git & Push to GitHub")
    
    def setup_items(self):
        """Setup menu items"""
        self.items = [
            MenuItem("Initialize & Push", lambda: self.git_init.initialize_and_push()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]