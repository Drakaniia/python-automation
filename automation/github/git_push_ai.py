"""
Git Push AI Module
Handles AI-powered commit message generation using GPT4All (offline) and push operations
IMPROVED: Better error handling, user feedback, and model management
"""
import subprocess
from pathlib import Path
import sys
import os
import warnings
import threading
import time


class GitPushAI:
    """Handles AI-assisted git push operations with GPT4All local model"""
    
    # Class-level model cache (singleton pattern)
    _model_instance = None
    _model_loaded = False
    _loading_lock = threading.Lock()
    _model_error = None
    
    # Optimized model configuration
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    
    # Performance tuning
    MAX_TOKENS = 25
    TEMPERATURE = 0.3
    TOP_K = 10
    TOP_P = 0.8
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self._generation_interrupted = False
    
    @classmethod
    def _check_gpt4all_installed(cls):
        """Check if gpt4all is installed"""
        try:
            import gpt4all
            return True
        except ImportError:
            return False
    
    @classmethod
    def _check_model_exists(cls):
        """Check if the model file exists"""
        models_dir = Path.cwd() / "models"
        model_path = models_dir / cls.MODEL_FILENAME
        return model_path.exists()
    
    @classmethod
    def _silent_load_model(cls):
        """
        Silently load model in background
        Returns True if successful, False otherwise
        """
        with cls._loading_lock:
            if cls._model_loaded:
                return cls._model_instance is not None
            
            # Check if gpt4all is installed
            if not cls._check_gpt4all_installed():
                cls._model_error = "gpt4all not installed"
                cls._model_loaded = True
                return False
            
            # Check if model exists
            if not cls._check_model_exists():
                cls._model_error = "model file not found"
                cls._model_loaded = True
                return False
            
            try:
                # Silence mode
                os.environ['GPT4ALL_VERBOSE'] = '0'
                os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())
                warnings.filterwarnings('ignore')
                
                from gpt4all import GPT4All
                
                models_dir = Path.cwd() / "models"
                model_path = models_dir / cls.MODEL_FILENAME
                
                # Suppress output
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                
                try:
                    sys.stdout = open(os.devnull, 'w')
                    sys.stderr = open(os.devnull, 'w')
                    
                    # OS-level suppression on Windows
                    if sys.platform == 'win32':
                        old_stderr = os.dup(2)
                        old_stdout = os.dup(1)
                        devnull_fd = os.open(os.devnull, os.O_WRONLY)
                        os.dup2(devnull_fd, 2)
                        os.dup2(devnull_fd, 1)
                        os.close(devnull_fd)
                    
                    # Load model
                    cls._model_instance = GPT4All(
                        model_name=cls.MODEL_FILENAME,
                        model_path=str(models_dir),
                        allow_download=False,
                        device='cpu',
                        verbose=False,
                        n_threads=os.cpu_count()
                    )
                    
                finally:
                    # Restore output
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
                cls._model_error = None
                return True
                
            except Exception as e:
                cls._model_error = str(e)
                cls._model_loaded = True
                return False
    
    def _show_ai_setup_help(self):
        """Display helpful information about AI setup"""
        print("\n" + "="*70)
        print("🤖 AI Model Setup Required")
        print("="*70)
        
        if self._model_error == "gpt4all not installed":
            print("\n📦 The gpt4all library is not installed.\n")
            print("To enable AI-powered commits, install it:")
            print("  pip install gpt4all")
        
        elif self._model_error == "model file not found":
            print(f"\n📥 Model file not found: {self.MODEL_FILENAME}\n")
            print("To enable AI-powered commits:")
            print("  1. Create a 'models' directory in your project root")
            print(f"  2. Download {self.MODEL_FILENAME} from:")
            print("     https://gpt4all.io/models/models3.json")
            print(f"  3. Place it in: {Path.cwd() / 'models' / self.MODEL_FILENAME}")
        
        else:
            print(f"\n⚠️  AI model failed to load: {self._model_error}\n")
            print("Using fallback commit message generator instead.")
        
        print("\n💡 The tool will continue using rule-based commit messages.")
        print("="*70 + "\n")
    
    def _stream_generate_with_interrupt(self, prompt):
        """Generate with streaming and interrupt support"""
        model = self._model_instance
        if model is None:
            return None
        
        try:
            print("💬 Generating", end='', flush=True)
            
            generated_text = ""
            self._generation_interrupted = False
            
            def show_progress():
                dots = ['', '.', '..', '...']
                i = 0
                while not self._generation_interrupted and len(generated_text) < self.MAX_TOKENS:
                    print(f'\r💬 Generating{dots[i % 4]}', end='', flush=True)
                    i += 1
                    time.sleep(0.3)
            
            progress_thread = threading.Thread(target=show_progress, daemon=True)
            progress_thread.start()
            
            try:
                for token in model.generate(
                    prompt,
                    max_tokens=self.MAX_TOKENS,
                    temp=self.TEMPERATURE,
                    top_p=self.TOP_P,
                    top_k=self.TOP_K,
                    streaming=True
                ):
                    if self._generation_interrupted:
                        break
                    generated_text += token
                    
                    if '\n' in generated_text:
                        break
            except KeyboardInterrupt:
                self._generation_interrupted = True
                print("\r💬 Generation interrupted by user" + " "*20)
                return None
            
            self._generation_interrupted = True
            progress_thread.join(timeout=0.5)
            
            print("\r" + " "*40 + "\r", end='', flush=True)
            
            if generated_text:
                return generated_text.strip()
            return None
            
        except KeyboardInterrupt:
            print("\r💬 Generation cancelled" + " "*20 + "\r", end='', flush=True)
            return None
        except Exception:
            return None
    
    def _generate_ai_commit_message(self, changed_files):
        """Generate commit message with AI"""
        # Load model if needed
        if not self._model_loaded:
            print("🧠 Initializing AI model (first time only)...", flush=True)
            success = self._silent_load_model()
            
            if not success:
                # Show setup help on first failure
                self._show_ai_setup_help()
                return None
            else:
                print("✅ AI model loaded successfully!\n")
        
        if self._model_instance is None:
            return None
        
        try:
            # Create prompt
            if not changed_files:
                hint = "files"
            elif len(changed_files) == 1:
                hint = Path(changed_files[0]).stem
            else:
                hint = f"{len(changed_files)} files"
            
            prompt = f"""Git commit for {hint}.
Format: <emoji> <type>: <what>
Emojis: 🚀=feat 🐛=fix 📚=docs ♻️=refactor
Max 50 chars.

"""
            
            # Generate with streaming
            response = self._stream_generate_with_interrupt(prompt)
            
            if response is None:
                return None
            
            # Clean up
            message = response.split('\n')[0].strip()
            
            for prefix in ["Message:", "Commit:", '"', "'", "-", "*", ">"]:
                if message.startswith(prefix):
                    message = message[len(prefix):].strip()
            
            for suffix in ['"', "'", ".", "!"]:
                if message.endswith(suffix):
                    message = message[:-1].strip()
            
            # Ensure emoji
            emojis = ['🚀', '🐛', '📚', '♻️', '🎨', '✅', '🔧', '✨']
            if not any(message.startswith(e) for e in emojis):
                msg_lower = message.lower()
                if 'fix' in msg_lower or 'bug' in msg_lower:
                    message = '🐛 ' + message
                elif 'add' in msg_lower or 'feat' in msg_lower:
                    message = '🚀 ' + message
                elif 'doc' in msg_lower:
                    message = '📚 ' + message
                elif 'refactor' in msg_lower:
                    message = '♻️ ' + message
                else:
                    message = '🔧 ' + message
            
            if len(message) > 72:
                message = message[:69] + "..."
            
            if 10 < len(message) < 80:
                return message
            return None
                
        except KeyboardInterrupt:
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
        
        # Stage changes
        print("📦 Staging all changes...")
        if not self._run_command(["git", "add", "."]):
            input("\nPress Enter to continue...")
            return
        print("✅ Files staged\n")
        
        # Get changed files
        changed_files = self._get_staged_files()
        
        # Try AI generation
        print("🤖 AI Commit Message Generation")
        print("─"*70)
        print("💡 Tip: Press Ctrl+C during generation to enter manual mode\n")
        
        ai_message = None
        try:
            ai_message = self._generate_ai_commit_message(changed_files)
        except KeyboardInterrupt:
            print("\n⚠️  AI generation cancelled by user")
            ai_message = None
        
        # Fallback if AI fails
        if not ai_message:
            print("⚠️  Using fallback analyzer...")
            ai_message = self._generate_fallback_commit_message()
        
        # Manual input if everything fails
        if not ai_message:
            print("\n📝 Manual commit message required")
            commit_message = input("Enter commit message: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            # Display and confirm
            print("\n" + "="*70)
            print(f"📝 Suggested Message:")
            print(f"   \"{ai_message}\"")
            print("="*70 + "\n")
            
            use_ai = input("Use this? [Y/n/edit]: ").strip().lower()
            
            if use_ai in ("", "y", "yes"):
                commit_message = ai_message
            elif use_ai in ("e", "edit"):
                print(f"\nCurrent: {ai_message}")
                commit_message = input("Edit message: ").strip()
                if not commit_message:
                    commit_message = ai_message
            else:
                commit_message = input("\nEnter custom message: ").strip()
                if not commit_message:
                    print("❌ Commit message cannot be empty")
                    input("\nPress Enter to continue...")
                    return
        
        # Commit
        print(f"\n💾 Committing: \"{commit_message}\"")
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
    
    def _generate_fallback_commit_message(self):
        """Fast rule-based fallback"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            return summarizer.generate_commit_message_for_staged_changes()
        except Exception:
            return None
    
    def _auto_generate_changelog(self):
        """Generate changelog after push"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            summarizer.auto_generate_after_push(num_commits=1)
        except Exception as e:
            print(f"⚠️  Changelog error: {e}")
    
    def _get_staged_files(self):
        """Get staged files list"""
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
            print("❌ Git not found in PATH")
            return False