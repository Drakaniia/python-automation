"""
Git Push AI Module - Smart Commit Message Generation
Analyzes code changes to generate contextual commit messages
No external AI models required - uses pattern analysis
Enhanced with automatic conflict resolution
"""
import subprocess
from pathlib import Path
from typing import List


class GitPushAI:
    """Smart git push with automatic commit message generation and conflict resolution"""
    
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
        
        # Push with automatic conflict resolution
        self._smart_push(commit_message)
    
    def _smart_push(self, commit_message: str):
        """Push with automatic conflict resolution"""
        print("📡 Pushing to remote...")
        push_result = self._run_command_silent(["git", "push"])
        
        if push_result['success']:
            print("\n✅ Successfully pushed!")
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
            input("\nPress Enter to continue...")
        else:
            # Check if it's a non-fast-forward error
            error_output = push_result['stderr'].lower()
            if "rejected" in error_output and ("non-fast-forward" in error_output or "behind" in error_output):
                self._handle_push_rejection(commit_message)
            else:
                print(f"\n❌ Push failed: {push_result['stderr']}")
                print("\n⚠️  Check your remote configuration and network connection.")
                input("\nPress Enter to continue...")
    
    def _handle_push_rejection(self, commit_message: str):
        """Handle push rejection due to non-fast-forward"""
        print("\n" + "="*70)
        print("⚠️  PUSH REJECTED - Remote has changes you don't have")
        print("="*70)
        print("\nThe remote repository has commits that you don't have locally.")
        print("You need to integrate those changes before pushing.\n")
        
        print("Choose a resolution strategy:\n")
        print("  1. Pull with merge (recommended)")
        print("     • Fetches remote changes and merges them")
        print("     • Creates a merge commit")
        print("     • Safest option, preserves all history\n")
        
        print("  2. Pull with rebase")
        print("     • Replays your commits on top of remote changes")
        print("     • Creates a linear history")
        print("     • Good for clean history\n")
        
        print("  3. Force push (⚠️  DANGEROUS)")
        print("     • Overwrites remote with your local changes")
        print("     • May lose remote commits")
        print("     • Only use if you're absolutely sure\n")
        
        print("  4. Cancel and resolve manually")
        print("="*70)
        
        choice = input("\nYour choice (1/2/3/4): ").strip()
        
        if choice == '1':
            self._resolve_with_pull_merge()
        elif choice == '2':
            self._resolve_with_pull_rebase()
        elif choice == '3':
            self._resolve_with_force_push()
        else:
            print("\n❌ Operation cancelled.")
            print("\n💡 You can resolve this manually by running:")
            print("   git pull          # or: git pull --rebase")
            print("   git push")
            input("\nPress Enter to continue...")
    
    def _resolve_with_pull_merge(self):
        """Resolve by pulling with merge strategy"""
        print("\n🔄 Pulling with merge strategy...")
        print("📥 Fetching remote changes...\n")
        
        result = self._run_command_silent(["git", "pull"])
        
        if not result['success']:
            error = result['stderr'].lower()
            if "conflict" in error or "merge conflict" in error:
                print("❌ Merge conflicts detected!")
                print("\n📝 Conflicted files:")
                self._run_command(["git", "status", "--short"])
                print("\n💡 To resolve:")
                print("   1. Open conflicted files and resolve conflicts")
                print("   2. git add <resolved-files>")
                print("   3. git commit")
                print("   4. Run 'magic' and push again")
            else:
                print(f"❌ Pull failed: {result['stderr']}")
            input("\nPress Enter to continue...")
            return
        
        print("✅ Successfully pulled and merged!\n")
        
        # Try pushing again
        print("📡 Attempting to push...")
        if self._run_command(["git", "push"]):
            print("\n✅ Successfully pushed!")
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n❌ Push still failed. Manual intervention required.")
        
        input("\nPress Enter to continue...")
    
    def _resolve_with_pull_rebase(self):
        """Resolve by pulling with rebase strategy"""
        print("\n🔄 Pulling with rebase strategy...")
        print("📥 Fetching and rebasing...\n")
        
        result = self._run_command_silent(["git", "pull", "--rebase"])
        
        if not result['success']:
            error = result['stderr'].lower()
            if "conflict" in error or "rebase" in error:
                print("❌ Rebase conflicts detected!")
                print("\n📝 Conflicted files:")
                self._run_command(["git", "status", "--short"])
                print("\n💡 To continue the rebase:")
                print("   1. Resolve conflicts in the files")
                print("   2. git add <resolved-files>")
                print("   3. git rebase --continue")
                print("\n💡 To abort the rebase:")
                print("   git rebase --abort")
            else:
                print(f"❌ Rebase failed: {result['stderr']}")
            input("\nPress Enter to continue...")
            return
        
        print("✅ Successfully pulled and rebased!\n")
        
        # Try pushing again
        print("📡 Attempting to push...")
        if self._run_command(["git", "push"]):
            print("\n✅ Successfully pushed!")
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n❌ Push still failed. Manual intervention required.")
        
        input("\nPress Enter to continue...")
    
    def _resolve_with_force_push(self):
        """Resolve by force pushing (dangerous)"""
        print("\n" + "="*70)
        print("⚠️  ⚠️  ⚠️  DANGER ZONE ⚠️  ⚠️  ⚠️")
        print("="*70)
        print("\nForce push will:")
        print("  • OVERWRITE all remote changes")
        print("  • PERMANENTLY DELETE remote commits you don't have")
        print("  • May cause SERIOUS PROBLEMS for collaborators")
        print("\nOnly do this if:")
        print("  • You're the only one working on this repository")
        print("  • You're absolutely sure the remote commits are wrong")
        print("  • You know what you're doing")
        print("\n" + "="*70)
        
        confirm = input("\nType 'FORCE' in ALL CAPS to confirm: ").strip()
        
        if confirm == 'FORCE':
            print("\n💪 Force pushing...")
            if self._run_command(["git", "push", "--force"]):
                print("\n✅ Successfully force pushed!")
                print("⚠️  Remote history has been rewritten.")
                print("⚠️  Collaborators will need to: git fetch && git reset --hard origin/main")
                print("\n" + "─"*70)
                self._auto_generate_changelog()
                print("─"*70)
            else:
                print("\n❌ Force push failed.")
        else:
            print("\n✅ Force push cancelled. Good choice!")
        
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
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
            return False
        except FileNotFoundError:
            print("❌ Git not found in PATH")
            return False
    
    def _run_command_silent(self, command: List[str]) -> dict:
        """Run a shell command silently and return result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except FileNotFoundError:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Git not found in PATH'
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e)
            }