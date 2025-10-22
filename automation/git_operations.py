"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
"""
from pathlib import Path
from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_pull import GitPull
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.github.commit_summarizer import EnhancedCommitSummarizer
from automation.github.git_hooks import GitHooksManager
from automation.github.git_visualizations import GitVisualizations
from automation.menu import Menu, MenuItem


class GitOperations:
    """Unified Git operations orchestrator"""
    
    def __init__(self):
        self.current_path = Path.cwd()
        
        # Initialize all modular components
        self.status_handler = GitStatus()
        self.log_handler = GitLog()
        self.pull_handler = GitPull()
        self.push_handler = GitPush()
        self.initializer = GitInitializer()
        self.recovery_handler = GitRecover()
        self.commit_summarizer = EnhancedCommitSummarizer()
        self.hooks_manager = GitHooksManager()
        self.visualizations = GitVisualizations()
    
    # ========== BASIC GIT OPERATIONS ==========
    
    def status(self):
        """Show git status"""
        self.status_handler.show_status()
    
    def log(self):
        """Show git log"""
        self.log_handler.show_log(limit=10)
    
    def pull(self):
        """Pull from remote"""
        self.pull_handler.pull()
    
    def push(self):
        """Add, commit, and push changes"""
        self.push_handler.push()
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        self.initializer.initialize_and_push()
    
    # ========== GIT RECOVERY ==========
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        self.recovery_handler.show_recovery_menu(
            commit_history_func=self.log_handler.get_commit_history,
            commit_details_func=self.log_handler.get_commit_details,
            verify_commit_func=self.log_handler.verify_commit_exists
        )
    
    # ========== COMMIT SUMMARIZER ==========
    
    def show_commit_summarizer_menu(self):
        """Show commit summarizer options"""
        print("\n" + "="*70)
        print("🧠 COMMIT SUMMARIZER & CHANGELOG")
        print("="*70 + "\n")
        
        if not self.commit_summarizer._is_git_repo():
            print("❌ Not a git repository")
            input("\nPress Enter to continue...")
            return
        
        print("Available Options:")
        print("  1. Generate changelog for recent commits")
        print("  2. Generate commit message from staged changes")
        print("  3. View summarizer configuration")
        print("  4. Back to menu\n")
        
        choice = input("Your choice: ").strip()
        
        if choice == '1':
            self._generate_changelog()
        elif choice == '2':
            self._generate_commit_message()
        elif choice == '3':
            self._show_summarizer_config()
        elif choice == '4':
            return
        else:
            print("\n❌ Invalid choice")
            input("\nPress Enter to continue...")
    
    def _generate_changelog(self):
        """Generate changelog entries"""
        print("\n" + "="*70)
        print("📝 GENERATE CHANGELOG")
        print("="*70 + "\n")
        
        try:
            num_commits = input("How many recent commits to process? (default: 1): ").strip()
            num_commits = int(num_commits) if num_commits else 1
            
            if num_commits < 1 or num_commits > 50:
                print("❌ Please enter a number between 1 and 50")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n🔄 Processing {num_commits} commit(s)...\n")
            success = self.commit_summarizer.auto_generate_after_push(num_commits)
            
            if success:
                print("\n✅ Changelog generated successfully!")
                print(f"📄 Check CHANGELOG.md in your repository")
            else:
                print("\n⚠️  No new commits to process or error occurred")
        
        except ValueError:
            print("\n❌ Invalid number")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def _generate_commit_message(self):
        """Generate commit message from staged changes"""
        print("\n" + "="*70)
        print("💡 GENERATE COMMIT MESSAGE")
        print("="*70 + "\n")
        
        # Check for staged changes
        import subprocess
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("⚠️  No staged changes found")
            print("💡 Stage files first with: git add <files>")
            input("\nPress Enter to continue...")
            return
        
        print("📊 Staged files:")
        for line in result.stdout.strip().split('\n'):
            print(f"  • {line}")
        
        print("\n🧠 Generating commit message...\n")
        
        message = self.commit_summarizer.generate_commit_message_for_staged_changes()
        
        print("="*70)
        print("📝 Generated Commit Message:")
        print("="*70)
        print(f"\n{message}\n")
        print("="*70)
        
        use_message = input("\nUse this message for commit? (y/n): ").strip().lower()
        
        if use_message == 'y':
            try:
                result = subprocess.run(
                    ['git', 'commit', '-m', message],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("\n✅ Commit created successfully!")
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Commit failed: {e.stderr}")
        else:
            print("\n❌ Commit cancelled")
        
        input("\nPress Enter to continue...")
    
    def _show_summarizer_config(self):
        """Show summarizer configuration"""
        print("\n" + "="*70)
        print("⚙️  COMMIT SUMMARIZER CONFIGURATION")
        print("="*70 + "\n")
        
        config = self.commit_summarizer.CONFIG
        
        print("Current Configuration:")
        for key, value in config.items():
            print(f"  • {key:<30} : {value}")
        
        print(f"\n🤖 AI Status:")
        if self.commit_summarizer.ollama_available:
            print("  ✅ Ollama is available and enabled")
            print(f"  📦 Model: {config['ollama_model']}")
        else:
            print("  ⚠️  Ollama not available - using heuristic analysis")
            print("  💡 Install Ollama for AI-powered summaries")
        
        print(f"\n📝 Processed Commits: {len(self.commit_summarizer.processed_commits)}")
        
        input("\nPress Enter to continue...")
    
    # ========== GIT HOOKS MANAGER ==========
    
    def show_hooks_menu(self):
        """Show git hooks management menu"""
        print("\n" + "="*70)
        print("🔗 GIT HOOKS MANAGER")
        print("="*70 + "\n")
        
        if not self.hooks_manager.is_git_repo():
            print("❌ Not a git repository")
            input("\nPress Enter to continue...")
            return
        
        while True:
            print("\nAvailable Operations:")
            print("  1. List installed hooks")
            print("  2. Install pre-commit hook")
            print("  3. Install pre-push hook")
            print("  4. Install commit-msg hook")
            print("  5. Install post-commit hook")
            print("  6. Install post-merge hook")
            print("  7. Install all hooks")
            print("  8. Back to menu\n")
            
            choice = input("Your choice: ").strip()
            
            if choice == '1':
                self.hooks_manager.list_hooks()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.hooks_manager.install_hook('pre-commit')
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.hooks_manager.install_hook('pre-push')
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.hooks_manager.install_hook('commit-msg')
                input("\nPress Enter to continue...")
            elif choice == '5':
                self.hooks_manager.install_hook('post-commit')
                input("\nPress Enter to continue...")
            elif choice == '6':
                self.hooks_manager.install_hook('post-merge')
                input("\nPress Enter to continue...")
            elif choice == '7':
                self.hooks_manager.install_all_hooks()
                input("\nPress Enter to continue...")
            elif choice == '8':
                break
            else:
                print("\n❌ Invalid choice")
                input("\nPress Enter to continue...")
    
    # ========== GIT VISUALIZATIONS ==========
    
    def show_visualizations_menu(self):
        """Show git visualizations menu"""
        self.visualizations.show_visualizations_menu()


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
            MenuItem("Commit Summarizer & Changelog 🧠", lambda: self.git_ops.show_commit_summarizer_menu()),
            MenuItem("Git Hooks Manager 🔗", lambda: self.git_ops.show_hooks_menu()),
            MenuItem("Git Visualizations 📊", lambda: self.git_ops.show_visualizations_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]