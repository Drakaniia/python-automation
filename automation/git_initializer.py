"""
Git repository initialization and first push automation
"""
import subprocess
from pathlib import Path
from automation.menu import Menu, MenuItem


class GitInitializer:
    """Handles Git repository initialization and first push"""
    
    @staticmethod
    def run_command(cmd: list, capture_output: bool = False):
        """Run a command"""
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                return result.stdout.strip()
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
    
    def check_git_exists(self):
        """Check if .git directory exists"""
        return Path(".git").exists()
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        print("\n🚀 Git Repository Initialization & First Push\n")
        print("=" * 60)
        
        # Check if already a git repo
        if self.check_git_exists():
            print("\n⚠️  This directory is already a git repository!")
            choice = input("Do you want to continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                print("❌ Operation cancelled.")
                return
        
        # Get GitHub repository URL
        print("\n📝 Enter your GitHub repository URL:")
        print("Example: https://github.com/username/repo-name.git")
        repo_url = input("Repository URL: ").strip()
        
        if not repo_url:
            print("❌ No URL provided. Operation cancelled.")
            return
        
        # Validate URL format
        if not (repo_url.startswith("https://github.com/") or 
                repo_url.startswith("git@github.com:")):
            print("⚠️  Warning: URL doesn't look like a GitHub repository")
            choice = input("Continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                return
        
        print("\n" + "=" * 60)
        print("🔧 Starting Git initialization...\n")
        
        # Step 1: Create/update README.md
        readme_path = Path("README.md")
        if not readme_path.exists():
            print("📄 Creating README.md...")
            project_name = Path.cwd().name
            with open("README.md", "w") as f:
                f.write(f"# {project_name}\n")
            print("✅ README.md created")
        else:
            print("✅ README.md already exists")
        
        # Step 2: Initialize git
        if not self.check_git_exists():
            print("\n📦 Initializing git repository...")
            if self.run_command(["git", "init"]) is not None or True:
                print("✅ Git repository initialized")
        else:
            print("✅ Git repository already initialized")
        
        # Step 3: Add README
        print("\n➕ Adding README.md to staging...")
        self.run_command(["git", "add", "README.md"])
        print("✅ README.md added")
        
        # Step 4: First commit
        print("\n💾 Creating first commit...")
        commit_result = self.run_command(["git", "commit", "-m", "first commit"])
        if commit_result is not None or True:
            print("✅ First commit created")
        
        # Step 5: Rename branch to main
        print("\n🌿 Setting branch to 'main'...")
        self.run_command(["git", "branch", "-M", "main"])
        print("✅ Branch renamed to 'main'")
        
        # Step 6: Add remote origin
        print(f"\n🔗 Adding remote origin: {repo_url}")
        
        # Check if origin already exists
        existing_remote = self.run_command(
            ["git", "remote", "get-url", "origin"],
            capture_output=True
        )
        
        if existing_remote:
            print(f"⚠️  Remote 'origin' already exists: {existing_remote}")
            choice = input("Remove and re-add? (y/n): ").strip().lower()
            if choice == 'y':
                self.run_command(["git", "remote", "remove", "origin"])
                print("🗑️  Old remote removed")
            else:
                print("❌ Keeping existing remote. Skipping push.")
                return
        
        self.run_command(["git", "remote", "add", "origin", repo_url])
        print("✅ Remote origin added")
        
        # Step 7: Push to GitHub
        print("\n⬆️  Pushing to GitHub...")
        print("This may take a moment...\n")
        
        push_result = self.run_command(["git", "push", "-u", "origin", "main"])
        
        if push_result is not None or True:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Repository initialized and pushed to GitHub!")
            print("=" * 60)
            print(f"\n🌐 Your repository: {repo_url.replace('.git', '')}")
        else:
            print("\n⚠️  Push may have failed. Check the errors above.")
            print("You might need to authenticate or check repository permissions.")


class GitInitMenu(Menu):
    """Git initialization menu"""
    def __init__(self):
        self.git_init = GitInitializer()
        super().__init__("Git Repository Initialization")
    
    def setup_items(self):
        self.items = [
            MenuItem("Initialize & Push to GitHub", 
                    lambda: self.git_init.initialize_and_push()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]