"""
Git Push AI Module
Handles AI-powered commit message generation using GPT4All (offline) and push operations
ULTRA-OPTIMIZED: Silent loading, accurate messages, fast generation, proper Ctrl+C support
"""
import subprocess
from pathlib import Path
import sys
import os
import warnings
import signal
import time


class GitPushAI:
    """Handles AI-assisted git push operations with GPT4All local model"""
    
    # Class-level model cache (singleton pattern)
    _model_instance = None
    _model_loaded = False
    
    # Use SMALLEST available model for speed
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    
    # Ultra-aggressive performance tuning
    MAX_TOKENS = 20  # Very short
    TEMPERATURE = 0.1  # Almost deterministic for speed
    TOP_K = 5  # Minimal sampling
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self._interrupted = False
    
    @classmethod
    def _silent_load_model(cls):
        """Silently load model (no output at all)"""
        if cls._model_loaded:
            return cls._model_instance is not None
        
        try:
            # Complete silence
            os.environ['GPT4ALL_VERBOSE'] = '0'
            os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())
            warnings.filterwarnings('ignore')
            
            from gpt4all import GPT4All
            
            models_dir = Path.cwd() / "models"
            model_path = models_dir / cls.MODEL_FILENAME
            
            if not model_path.exists():
                cls._model_loaded = True
                return False
            
            # Suppress all output
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            try:
                sys.stdout = open(os.devnull, 'w')
                sys.stderr = open(os.devnull, 'w')
                
                if sys.platform == 'win32':
                    old_stderr = os.dup(2)
                    old_stdout = os.dup(1)
                    devnull_fd = os.open(os.devnull, os.O_WRONLY)
                    os.dup2(devnull_fd, 2)
                    os.dup2(devnull_fd, 1)
                    os.close(devnull_fd)
                
                cls._model_instance = GPT4All(
                    model_name=cls.MODEL_FILENAME,
                    model_path=str(models_dir),
                    allow_download=False,
                    device='cpu',
                    verbose=False,
                    n_threads=os.cpu_count()
                )
                
            finally:
                if sys.platform == 'win32':
                    try:
                        os.dup2(old_stderr, 2)
                        os.dup2(old_stdout, 1)
                        os.close(old_stderr)
                        os.close(old_stdout)
                    except:
                        pass
                
                sys.stdout.close()
                sys.stderr.close()
                sys.stdout = original_stdout
                sys.stderr = original_stderr
            
            cls._model_loaded = True
            return True
            
        except Exception:
            cls._model_loaded = True
            return False
    
    def _get_diff_summary(self):
        """Get actual diff to understand what changed"""
        try:
            # Get diff with context
            result = subprocess.run(
                ["git", "diff", "--cached", "--stat"],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip()
        except:
            return ""
    
    def _analyze_changes(self, changed_files):
        """Analyze actual changes to create accurate context"""
        if not changed_files:
            return "multiple files", "update"
        
        # Get file types and changes
        file_types = set()
        change_type = "update"
        
        for file in changed_files:
            ext = Path(file).suffix.lower()
            name = Path(file).name.lower()
            
            if '.py' in ext:
                file_types.add('Python')
            elif ext in ['.md', '.txt', '.rst']:
                file_types.add('docs')
            elif ext in ['.json', '.yaml', '.yml', '.toml']:
                file_types.add('config')
            elif ext in ['.sh', '.bat']:
                file_types.add('scripts')
            elif ext in ['.html', '.css', '.js']:
                file_types.add('web')
            
            # Detect change type from git status
            try:
                status = subprocess.run(
                    ["git", "status", "--porcelain", file],
                    capture_output=True,
                    text=True,
                    cwd=self.current_dir,
                    encoding='utf-8',
                    errors='replace'
                ).stdout.strip()
                
                if status.startswith('A'):
                    change_type = "add"
                elif status.startswith('D'):
                    change_type = "remove"
                elif status.startswith('M'):
                    change_type = "update"
            except:
                pass
        
        # Create context
        if len(changed_files) == 1:
            context = Path(changed_files[0]).stem
        elif file_types:
            context = " and ".join(file_types)
        else:
            context = f"{len(changed_files)} files"
        
        return context, change_type
    
    def _generate_with_timeout(self, prompt, timeout=8):
        """Generate with timeout and Ctrl+C support"""
        model = self._model_instance
        if model is None:
            return None
        
        result = [None]
        self._interrupted = False
        
        def generate():
            try:
                response = model.generate(
                    prompt,
                    max_tokens=self.MAX_TOKENS,
                    temp=self.TEMPERATURE,
                    top_k=self.TOP_K,
                    top_p=0.7,
                    streaming=False  # Faster for short outputs
                )
                result[0] = response
            except:
                pass
        
        # Setup Ctrl+C handler
        def signal_handler(sig, frame):
            self._interrupted = True
            print("\n⚠️  Generation cancelled (Ctrl+C pressed)")
            raise KeyboardInterrupt
        
        old_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            import threading
            thread = threading.Thread(target=generate, daemon=True)
            thread.start()
            
            # Wait with animation
            dots = ['', '.', '..', '...']
            start = time.time()
            i = 0
            
            while thread.is_alive() and (time.time() - start) < timeout:
                if self._interrupted:
                    return None
                print(f'\r💬 Generating{dots[i % 4]}', end='', flush=True)
                time.sleep(0.3)
                i += 1
            
            thread.join(timeout=0.1)
            print('\r' + ' ' * 40 + '\r', end='', flush=True)
            
            return result[0]
            
        except KeyboardInterrupt:
            print('\r' + ' ' * 40 + '\r', end='', flush=True)
            return None
        finally:
            signal.signal(signal.SIGINT, old_handler)
    
    def _generate_ai_commit_message(self, changed_files):
        """Generate accurate commit message based on actual changes"""
        # Silent load
        if not self._model_loaded:
            if not self._silent_load_model():
                return None
        
        if self._model_instance is None:
            return None
        
        try:
            # Analyze actual changes
            context, change_type = self._analyze_changes(changed_files)
            
            # Get diff summary for accuracy
            diff_summary = self._get_diff_summary()
            
            # Create focused prompt with actual file info
            file_list = ", ".join([Path(f).name for f in changed_files[:3]])
            if len(changed_files) > 3:
                file_list += f" and {len(changed_files)-3} more"
            
            # More specific prompt for accuracy
            prompt = f"""Write a git commit message.

Files changed: {file_list}
Change type: {change_type}
Context: {context}

Format: <emoji> <action>: <what changed>
Example: 🐛 fix: resolve error in parser
Example: 🚀 feat: add new feature
Example: 📚 docs: update README

Be specific about what changed. Max 50 chars.

Commit message:"""
            
            # Generate with timeout and interrupt support
            response = self._generate_with_timeout(prompt, timeout=10)
            
            if response is None or self._interrupted:
                return None
            
            # Clean response
            message = response.strip().split('\n')[0].strip()
            
            # Remove common prefixes
            prefixes = ["Commit message:", "Message:", "Commit:", "Output:", 
                       '"', "'", ">", "-", "*", "•", "Example:"]
            for prefix in prefixes:
                if message.lower().startswith(prefix.lower()):
                    message = message[len(prefix):].strip()
            
            # Remove trailing punctuation/quotes
            message = message.rstrip('."\'!,;')
            
            # Ensure proper format
            emojis = ['🚀', '🐛', '📚', '♻️', '🎨', '✅', '🔧', '✨', '🔥', '📝', '⚡', '💚']
            has_emoji = any(message.startswith(e) for e in emojis)
            
            if not has_emoji:
                # Add appropriate emoji based on change type
                msg_lower = message.lower()
                if change_type == "add" or "add" in msg_lower or "new" in msg_lower:
                    message = '✨ ' + message
                elif "fix" in msg_lower or "bug" in msg_lower or "error" in msg_lower:
                    message = '🐛 ' + message
                elif "doc" in msg_lower or "readme" in msg_lower:
                    message = '📚 ' + message
                elif "refactor" in msg_lower or "clean" in msg_lower:
                    message = '♻️ ' + message
                elif "test" in msg_lower:
                    message = '✅ ' + message
                else:
                    message = '🔧 ' + message
            
            # Ensure conventional commit format
            if ':' not in message:
                parts = message.split(' ', 2)
                if len(parts) >= 2:
                    emoji = parts[0] if parts[0] in emojis else '🔧'
                    action = parts[1] if len(parts) > 1 else 'update'
                    desc = parts[2] if len(parts) > 2 else context
                    message = f"{emoji} {action}: {desc}"
            
            # Length limit
            if len(message) > 72:
                message = message[:69] + "..."
            
            # Validate quality
            if 15 < len(message) < 80 and ':' in message:
                return message
            
            return None
                
        except KeyboardInterrupt:
            self._interrupted = True
            return None
        except Exception:
            return None
    
    def ai_commit_and_push(self):
        """Add, commit with AI-generated message, and push changes"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (AI-Powered)")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        if not self._has_changes():
            print("ℹ️  No changes detected. Working directory is clean.")
            input("\nPress Enter to continue...")
            return
        
        print("📦 Staging all changes...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        print("✅ Files staged\n")
        
        changed_files = self._get_staged_files()
        
        print("🤖 AI Commit Message Generation")
        print("─"*70)
        print("💡 Press Ctrl+C during generation to enter manual mode\n")
        
        ai_message = None
        try:
            ai_message = self._generate_ai_commit_message(changed_files)
        except KeyboardInterrupt:
            print("⚠️  Generation cancelled by user\n")
            ai_message = None
        
        # Fallback to rule-based
        if not ai_message and not self._interrupted:
            print("⚠️  AI unavailable, using fallback...")
            ai_message = self._generate_fallback_commit_message()
        
        # Manual input
        if not ai_message or self._interrupted:
            print("📝 Manual commit message")
            commit_message = input("Enter message: ").strip()
            if not commit_message:
                print("❌ Message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            print("="*70)
            print(f"📝 Suggested:")
            print(f"   {ai_message}")
            print("="*70 + "\n")
            
            use_ai = input("Use this? [Y/n/edit]: ").strip().lower()
            
            if use_ai in ("", "y", "yes"):
                commit_message = ai_message
            elif use_ai in ("e", "edit"):
                print(f"\nCurrent: {ai_message}")
                edited = input("Edit: ").strip()
                commit_message = edited if edited else ai_message
            else:
                commit_message = input("\nEnter message: ").strip()
                if not commit_message:
                    print("❌ Message cannot be empty")
                    input("\nPress Enter to continue...")
                    return
        
        print(f"\n💾 Committing: \"{commit_message}\"")
        if not self._run_command(["git", "commit", "-m", commit_message]):
            input("\nPress Enter to continue...")
            return
        print("✅ Commit created\n")
        
        print("📡 Pushing to remote...")
        push_success = self._run_command(["git", "push"])
        
        if push_success:
            print("\n✅ Successfully pushed!")
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n⚠️  Push failed.")
        
        input("\nPress Enter to continue...")
    
    def _generate_fallback_commit_message(self):
        """Fast rule-based fallback"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            return summarizer.generate_commit_message_for_staged_changes()
        except Exception:
            return None
    
    def _auto_generate_changelog(self):
        """Generate changelog"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            summarizer.auto_generate_after_push(num_commits=1)
        except Exception:
            pass
    
    def _get_staged_files(self):
        """Get staged files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except:
            return []
    
    def _has_changes(self):
        """Check for changes"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
    def _is_git_repo(self):
        """Check if git repo"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command):
        """Run git command"""
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
            print("❌ Git not found")
            return False