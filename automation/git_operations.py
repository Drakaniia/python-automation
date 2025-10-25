"""
Consolidated Git Operations Module
Main orchestrator for all Git operations using modular components
UPDATED: Now uses ChangelogGenerator instead of CommitSummarizer
"""
from pathlib import Path
from automation.github.git_status import GitStatus
from automation.github.git_log import GitLog
from automation.github.git_pull import GitPull
from automation.github.git_push import GitPush
from automation.github.git_initializer import GitInitializer
from automation.github.git_recover import GitRecover
from automation.menu import Menu, MenuItem
from automation.core.git_client import get_git_client
from automation.github.changelog_generator import ChangelogGenerator


class GitOperations:
    """Unified Git operations orchestrator with dynamic directory detection"""
    
    def __init__(self):
        # Don't cache components - create fresh for each operation
        pass
    
    def _get_current_path(self):
        """Get current working directory (updates dynamically)"""
        return Path.cwd()
    
    def _refresh_git_client(self):
        """Get fresh GitClient for current directory"""
        return get_git_client(working_dir=self._get_current_path())
    
    # ========== BASIC GIT OPERATIONS ==========
    
    def status(self):
        """Show git status"""
        status_handler = GitStatus()
        status_handler.show_status()
    
    def log(self):
        """Show git log"""
        log_handler = GitLog()
        log_handler.show_log(limit=10)
    
    def pull(self):
        """Pull from remote"""
        pull_handler = GitPull()
        pull_handler.pull()
    
    def push(self):
        """Add, commit, and push changes"""
        # Create fresh push handler for current directory
        push_handler = GitPush()
        push_handler.push()
    
    # ========== GIT INITIALIZATION ==========
    
    def initialize_and_push(self):
        """Initialize git repo and push to GitHub"""
        initializer = GitInitializer()
        initializer.initialize_and_push()
    
    # ========== GIT RECOVERY ==========
    
    def show_recovery_menu(self):
        """Show the commit recovery interface"""
        log_handler = GitLog()
        recovery_handler = GitRecover()
        recovery_handler.show_recovery_menu(
            commit_history_func=log_handler.get_commit_history,
            commit_details_func=log_handler.get_commit_details,
            verify_commit_func=log_handler.verify_commit_exists
        )
    
    def show_changelog_generator_menu(self):
        """Show changelog generator options"""
        # Create fresh generator for current directory
        changelog_gen = ChangelogGenerator()
        
        print("\n" + "="*70)
        print("📝 CHANGELOG GENERATOR")
        print("="*70 + "\n")
        
        if not changelog_gen._is_git_repo():
            print("❌ Not a git repository")
            input("\nPress Enter to continue...")
            return
        
        print("Generate clean changelog entries from recent commits.")
        print("\nOptions:")
        print("  1. Generate changelog for recent commits")
        print("  2. Show unprocessed commits")
        print("  3. Reset processed commits cache")
        print("  4. View generator configuration")
        print("  5. Back to menu\n")
        
        choice = input("Your choice: ").strip()
        
        if choice == '1':
            self._generate_changelog_interactive(changelog_gen)
        elif choice == '2':
            self._show_unprocessed_commits(changelog_gen)
        elif choice == '3':
            self._reset_changelog_cache(changelog_gen)
        elif choice == '4':
            self._show_generator_config(changelog_gen)
        elif choice == '5':
            return
        else:
            print("\n❌ Invalid choice")
            input("\nPress Enter to continue...")
    
    def _generate_changelog_interactive(self, changelog_gen):
        """Interactive changelog generation"""
        print("\n" + "="*70)
        print("📝 GENERATE CHANGELOG")
        print("="*70 + "\n")
        
        try:
            num_commits = input("How many recent commits to process? (default: 1): ").strip()
            num_commits = int(num_commits) if num_commits else 1
            
            if num_commits < 1 or num_commits > 100:
                print("❌ Please enter a number between 1 and 100")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n🔄 Processing {num_commits} commit(s)...\n")
            success = changelog_gen.generate_changelog(num_commits)
            
            if success:
                print("\n✅ Changelog generated successfully!")
                print(f"📄 Check {changelog_gen.CONFIG['changelog_file']} in your repository")
            else:
                print("\n⚠️  No new commits to process or error occurred")
        
        except ValueError:
            print("\n❌ Invalid number")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def _show_unprocessed_commits(self, changelog_gen):
        """Show unprocessed commits"""
        changelog_gen.show_unprocessed_commits(limit=20)
        input("Press Enter to continue...")
    
    def _reset_changelog_cache(self, changelog_gen):
        """Reset the processed commits cache"""
        print("\n" + "="*70)
        print("⚠️  RESET CHANGELOG CACHE")
        print("="*70 + "\n")
        
        print("This will clear the record of processed commits.")
        print("All commits will be treated as unprocessed.\n")
        
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            changelog_gen.reset_processed_commits()
            print()
        else:
            print("\n❌ Operation cancelled")
        
        input("\nPress Enter to continue...")
    
    def _show_generator_config(self, changelog_gen):
        """Show generator configuration"""
        print("\n" + "="*70)
        print("⚙️  CHANGELOG GENERATOR CONFIGURATION")
        print("="*70 + "\n")
        
        config = changelog_gen.CONFIG
        
        print("Current Configuration:")
        for key, value in config.items():
            print(f"  • {key:<25} : {value}")
        
        print(f"\n📝 Processed Commits: {len(changelog_gen.processed_commits)}")
        
        print("\n📋 Supported Commit Types:")
        for commit_type, type_config in changelog_gen.COMMIT_TYPES.items():
            print(f"  {type_config['emoji']} {commit_type:<12} - {type_config['label']}")
            keywords = ', '.join(type_config['keywords'][:3])
            if len(type_config['keywords']) > 3:
                keywords += '...'
            print(f"     Keywords: {keywords}")
        
        input("\nPress Enter to continue...")


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
            MenuItem("Generate Changelog", lambda: self.git_ops.show_changelog_generator_menu()),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]