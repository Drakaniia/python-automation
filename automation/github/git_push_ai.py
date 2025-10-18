"""
Git Push AI Module
Handles AI-powered commit message generation and push operations
Now includes automatic changelog generation after successful push
"""
import subprocess
from pathlib import Path


class GitPushAI:
    """Handles AI-assisted git push operations with automatic changelog generation"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def ai_commit_and_push(self):
        """Add, commit with AI-generated message, and push changes"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (AI-Powered)")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        # Check for changes
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        # Stage all changes
        print("📦 Staging all changes...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        print("✅ Files staged\n")
        
        # Generate AI commit message
        print("🧠 Generating AI-powered commit message...")
        ai_message = self._generate_ai_commit_message()
        
        if not ai_message:
            print("❌ Failed to generate AI commit message. Falling back to manual input.")
            commit_message = input("\nEnter commit message manually: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            # Display AI-generated message
            print("\n" + "="*70)
            print(f"📝 Suggested Commit Message:")
            print(f'"{ai_message}"')
            print("="*70 + "\n")
            
            # Ask user for confirmation
            use_ai = input("Use this message? [Y/n]: ").strip().lower()
            
            if use_ai in ("", "y", "yes"):
                commit_message = ai_message
            else:
                commit_message = input("\nEnter custom commit message: ").strip()
                if not commit_message:
                    print("❌ Commit message cannot be empty")
                    input("\nPress Enter to continue...")
                    return
        
        # Commit with the chosen message
        print(f"\n💾 Committing with message: \"{commit_message}\"")
        if not self._run_command(["git", "commit", "-m", commit_message]):
            input("\nPress Enter to continue...")
            return
        print("✅ Commit created\n")
        
        # Push to remote
        print("📡 Pushing to remote...")
        push_success = self._run_command(["git", "push"])
        
        if push_success:
            print("\n✅ Successfully pushed to remote!")
            
            # ========== AUTOMATIC CHANGELOG GENERATION ==========
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n⚠️  Push failed. You may need to set up remote or pull first.")
        
        input("\nPress Enter to continue...")
    
    def _auto_generate_changelog(self):
        """
        Automatically generate and update changelog after successful push
        This is the new integration point for the AI Commit Summarizer
        """
        try:
            # Import from the correct location based on your file structure
            try:
                from automation.ai_features.commit_summarizer import CommitSummarizer
            except ImportError:
                # Fallback: try importing from readme_whisperer if that's where it is
                from automation.ai_features.readme_whisperer import CommitSummarizer
            
            summarizer = CommitSummarizer()
            
            # Generate changelog for the last commit (the one we just pushed)
            success = summarizer.auto_generate_after_push(num_commits=1)
            
            if not success:
                print("⚠️  Changelog generation skipped")
        except Exception as e:
            print(f"⚠️  Could not auto-generate changelog: {e}")
            print("   (This is non-critical - your push was successful)")
    
    def _generate_ai_commit_message(self):
        """Generate AI-powered commit message from staged changes"""
        try:
            # Import from the correct location based on your file structure
            try:
                from automation.ai_features.commit_summarizer import CommitSummarizer
            except ImportError:
                # Fallback: try importing from readme_whisperer if that's where it is
                from automation.ai_features.readme_whisperer import CommitSummarizer
            
            summarizer = CommitSummarizer()
            message = summarizer.generate_commit_message_for_staged_changes()
            return message
        except Exception as e:
            print(f"⚠️  Error generating AI message: {e}")
            return None
    
    def _has_changes(self):
        """Check if there are any changes (staged or unstaged)"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    
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