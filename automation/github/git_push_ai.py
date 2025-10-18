"""
Git Push AI Module - Smart Commit Message Generation
Analyzes code changes to generate contextual commit messages
No external AI models required - uses pattern analysis
"""
import subprocess
from pathlib import Path
from typing import List


class GitPushAI:
    """Smart git push with automatic commit message generation"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def ai_commit_and_push(self):
        """Main entry point for smart commit and push"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (Smart Commit)")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        # Stage changes
        print("📦 Staging all changes...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        print("✅ Files staged\n")
        
        # Generate smart commit message
        print("🧠 Analyzing changes and generating commit message...")
        commit_message = self._generate_smart_commit_message()
        
        # Display generated message
        print("\n" + "="*70)
        print("📝 Generated Commit Message:")
        print("─"*70)
        print(commit_message)
        print("="*70 + "\n")
        
        use_message = input("Use this message? [Y/n/edit]: ").strip().lower()
        
        if use_message in ("", "y", "yes"):
            pass  # Use generated message
        elif use_message in ("e", "edit"):
            print(f"\nCurrent:\n{commit_message}\n")
            new_message = input("Enter edited message: ").strip()
            if new_message:
                commit_message = new_message
        else:
            commit_message = input("\nEnter custom message: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        
        # Commit
        print(f"\n💾 Creating commit...")
        if not self._run_command(["git", "commit", "-m", commit_message]):
            input("\nPress Enter to continue...")
            return
        print("✅ Commit created\n")
        
        # Push
        print("📡 Pushing to remote...")
        push_success = self._run_command(["git", "push"])
        
        if push_success:
            print("\n✅ Successfully pushed!")
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n⚠️  Push failed. Check remote configuration.")
        
        input("\nPress Enter to continue...")
    
    def _generate_smart_commit_message(self):
        """Generate commit message by analyzing changes"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            message = summarizer.generate_commit_message_for_staged_changes()
            return message
        except Exception as e:
            print(f"⚠️  Error generating message: {e}")
            return "🔧 Update project files"
    
    def _auto_generate_changelog(self):
        """Automatically generate changelog entry"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            summarizer.auto_generate_after_push(num_commits=1)
        except Exception as e:
            print(f"⚠️  Changelog generation skipped: {e}")
    
    def _has_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command: List[str]) -> bool:
        """Run a shell command and display output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='replace'
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
            print("❌ Git not found in PATH")
            return False