"""
Git Initializer Module
Automates git repository initialization and first push to GitHub
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
        
        # Get repository URL
        print("📝 Enter your GitHub repository URL:")
        print("Example: https://github.com/username/repo-name.git")
        repo_url = input("Repository URL: ").strip()
        
        if not repo_url:
            print("\n❌ Repository URL cannot be empty")
            input("\nPress Enter to continue...")
            return
        
        print("\n🔧 Starting Git initialization...\n")
        
        # Step 1: Create README if it doesn't exist
        readme_path = Path("README.md")
        if not readme_path.exists():
            print("📄 Creating README.md...")
            try:
                with open(readme_path, "w") as f:
                    f.write(f"# {Path.cwd().name}\n\n")
                    f.write("This project was initialized using Python Automation System.\n")
                print("✅ README.md created\n")
            except Exception as e:
                print(f"❌ Error creating README.md: {e}\n")
                input("\nPress Enter to continue...")
                return
        else:
            print("📄 README.md already exists\n")
        
        # Step 2: Initialize git
        print("📦 Initializing git repository...")
        if not self._run_command(["git", "init"]):
            input("\nPress Enter to continue...")
            return
        print("✅ Git repository initialized\n")
        
        # Step 3: Add README
        print("➕ Adding README.md to staging...")
        if not self._run_command(["git", "add", "README.md"]):
            input("\nPress Enter to continue...")
            return
        print("✅ README.md added\n")
        
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
        print("✅ Branch renamed to 'main'\n")
        
        # Step 6: Add remote
        print(f"🔗 Adding remote origin: {repo_url}")
        if not self._run_command(["git", "remote", "add", "origin", repo_url]):
            # Remote might already exist, try to set URL instead
            print("⚠️  Remote already exists, updating URL...")
            if not self._run_command(["git", "remote", "set-url", "origin", repo_url]):
                input("\nPress Enter to continue...")
                return
        print("✅ Remote origin added\n")
        
        # Step 7: Push to GitHub
        print("⬆️  Pushing to GitHub...")
        if not self._run_command(["git", "push", "-u", "origin", "main"]):
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Repository initialized and pushed to GitHub!")
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