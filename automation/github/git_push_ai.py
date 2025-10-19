"""
Git Push AI Module - Enhanced Smart Commit Generation
Integrates advanced commit message generation with multiple strategies
No external APIs required - uses local analysis and optional local LLM
"""
import subprocess
from pathlib import Path
from typing import List


class GitPushAI:
    """Smart git push with enhanced AI-powered commit generation"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def ai_commit_and_push(self):
        """Main entry point for smart commit and push"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (Enhanced Smart Commit)")
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
        
        # Generate enhanced smart commit message
        print("🧠 Analyzing changes with enhanced AI...")
        commit_message, analysis = self._generate_enhanced_commit_message()
        
        # Display analysis and generated message
        self._display_analysis(analysis, commit_message)
        
        # Get user confirmation
        use_message = input("\nUse this message? [Y/n/edit/config]: ").strip().lower()
        
        if use_message == 'config':
            self._show_config_menu()
            return self.ai_commit_and_push()  # Restart with new config
        elif use_message in ("", "y", "yes"):
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
    
    def _generate_enhanced_commit_message(self):
        """Generate commit message using enhanced smart generator"""
        try:
            # Try to import the enhanced generator
            try:
                from automation.github.smart_commit_generator import SmartCommitGenerator
                
                generator = SmartCommitGenerator()
                message = generator.generate_commit_message()
                
                # Get analysis for display
                diff_text = generator._get_git_diff()
                analysis = generator._analyze_diff(diff_text)
                
                return message, analysis
            except ImportError:
                # Enhanced generator not available yet
                print("ℹ️  Using basic commit generator")
                return self._generate_basic_message(), {}
        
        except Exception as e:
            print(f"⚠️  Generation error: {e}")
            return self._generate_basic_message(), {}
    
    def _generate_basic_message(self):
        """Basic fallback message generation"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            return summarizer.generate_commit_message_for_staged_changes()
        except Exception:
            return "🚀 Update project files"
    
    def _display_analysis(self, analysis: dict, message: str):
        """Display detailed analysis of changes"""
        print("\n" + "="*70)
        print("📊 CHANGE ANALYSIS")
        print("="*70)
        
        if analysis:
            stats = analysis.get('stats', {})
            print(f"\n📝 Files Changed: {stats.get('files_changed', 'N/A')}")
            print(f"➕ Additions: {stats.get('additions', 'N/A')}")
            print(f"➖ Deletions: {stats.get('deletions', 'N/A')}")
            
            if analysis.get('change_type'):
                print(f"🏷️  Change Type: {analysis['change_type']}")
            
            if analysis.get('scope'):
                print(f"🎯 Scope: {analysis['scope']}")
            
            if analysis.get('confidence'):
                confidence = analysis['confidence'] * 100
                print(f"📈 Confidence: {confidence:.0f}%")
            
            if analysis.get('affected_modules'):
                modules = ', '.join(list(analysis['affected_modules'])[:3])
                print(f"📦 Modules: {modules}")
        
        print("\n" + "─"*70)
        print("✨ GENERATED MESSAGE:")
        print("─"*70)
        print(f"{message}")
        print("="*70)
    
    def _show_config_menu(self):
        """Show configuration options"""
        print("\n" + "="*70)
        print("⚙️  COMMIT GENERATOR CONFIGURATION")
        print("="*70)
        
        try:
            from automation.github.smart_commit_generator import SmartCommitGenerator
            generator = SmartCommitGenerator()
            
            print("\n📋 Current Settings:")
            for key, value in generator.CONFIG.items():
                print(f"  {key}: {value}")
            
            print("\n🔧 Available Modes:")
            print("  1. heuristic  - Rule-based analysis (fast, no dependencies)")
            print("  2. local_llm  - Local AI model (requires Ollama)")
            print("  3. hybrid     - Smart mix of both (recommended)")
            
            print("\n💡 Tips:")
            print("  • Heuristic: Best for quick commits, no setup needed")
            print("  • Local LLM: Most intelligent, requires: ollama pull tinydolphin")
            print("  • Hybrid: Automatically chooses best strategy")
            
            choice = input("\nSelect mode (1/2/3) or press Enter to keep current: ").strip()
            
            mode_map = {'1': 'heuristic', '2': 'local_llm', '3': 'hybrid'}
            if choice in mode_map:
                new_mode = mode_map[choice]
                generator.CONFIG['ai_mode'] = new_mode
                print(f"\n✅ Mode changed to: {new_mode}")
                print("⚠️  Note: This change is temporary (session only)")
            
        except ImportError:
            print("\n⚠️  Enhanced generator not available")
            print("💡 Add smart_commit_generator.py to automation/github/")
        
        input("\nPress Enter to continue...")
    
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