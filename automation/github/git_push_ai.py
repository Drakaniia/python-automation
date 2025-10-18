"""
Git Push AI Module
Handles AI-powered commit message generation using GPT4All (offline) and push operations
Includes automatic changelog generation after successful push
ULTRA-OPTIMIZED: Fast inference with aggressive performance tuning
"""
import subprocess
from pathlib import Path
import sys
import os
import warnings


class GitPushAI:
    """Handles AI-assisted git push operations with GPT4All local model"""
    
    # Class-level model cache (singleton pattern)
    _model_instance = None
    _model_loaded = False
    
    # Optimized model configuration
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    
    # Performance tuning parameters
    MAX_TOKENS = 32  # Reduced from 50 for faster generation
    TEMPERATURE = 0.5  # Lower = more deterministic = faster
    TOP_K = 20  # Reduced from 40 for speed
    TOP_P = 0.85  # Slightly reduced
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    @classmethod
    def _init_ai_model(cls):
        """
        Initialize GPT4All model (singleton - loads once per session)
        Returns the model instance or None if loading fails
        """
        # Return cached instance if already loaded
        if cls._model_loaded:
            return cls._model_instance
        
        try:
            # Suppress GPT4All's verbose logging
            os.environ['GPT4ALL_VERBOSE'] = '0'
            
            # Enable performance optimizations
            os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())  # Use all CPU cores
            
            # Suppress warnings about DLL loading
            warnings.filterwarnings('ignore', category=UserWarning)
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            
            from gpt4all import GPT4All
            
            # Define model path
            models_dir = Path.cwd() / "models"
            models_dir.mkdir(exist_ok=True)
            model_path = models_dir / cls.MODEL_FILENAME
            
            # CRITICAL: Redirect ALL stderr output (including C++ library errors)
            # This suppresses DLL loading errors from the native library
            import io
            import contextlib
            
            # Check if model exists
            if not model_path.exists():
                print(f"📥 Downloading {cls.MODEL_FILENAME} (first time only)...")
                print("   This may take a few minutes...")
                
                # Redirect stderr during download too
                stderr_buffer = io.StringIO()
                with contextlib.redirect_stderr(stderr_buffer):
                    cls._model_instance = GPT4All(
                        model_name=cls.MODEL_FILENAME,
                        model_path=str(models_dir),
                        allow_download=True,
                        device='cpu',
                        verbose=False,
                        # Performance optimizations
                        n_threads=os.cpu_count()  # Use all threads
                    )
                print("✅ Model downloaded and ready!")
            else:
                # Load existing model with clean output
                print(f"🔍 Loading AI model: {cls.MODEL_FILENAME}...", end=' ', flush=True)
                
                # Open devnull for complete stderr suppression
                import tempfile
                
                # Save original stderr
                original_stderr = sys.stderr
                
                try:
                    # Redirect Python's stderr AND OS-level stderr (fd 2)
                    sys.stderr = open(os.devnull, 'w')
                    
                    # Also suppress OS-level stderr on Windows
                    if sys.platform == 'win32':
                        import msvcrt
                        old_stderr = os.dup(2)  # Duplicate stderr file descriptor
                        devnull_fd = os.open(os.devnull, os.O_WRONLY)
                        os.dup2(devnull_fd, 2)  # Redirect stderr to devnull
                        os.close(devnull_fd)
                    
                    # Load model (DLL errors now suppressed) with performance settings
                    cls._model_instance = GPT4All(
                        model_name=cls.MODEL_FILENAME,
                        model_path=str(models_dir),
                        allow_download=False,
                        device='cpu',
                        verbose=False,
                        # CRITICAL PERFORMANCE SETTINGS
                        n_threads=os.cpu_count()  # Use all available CPU threads
                    )
                    
                finally:
                    # Restore stderr
                    if sys.platform == 'win32':
                        try:
                            os.dup2(old_stderr, 2)
                            os.close(old_stderr)
                        except:
                            pass
                    
                    sys.stderr.close()
                    sys.stderr = original_stderr
                
                print("✅ Model ready!")
            
            cls._model_loaded = True
            return cls._model_instance
            
        except ImportError:
            print("❌ Error: GPT4All not installed")
            print("   Install with: pip install gpt4all")
            cls._model_loaded = True
            return None
        except FileNotFoundError:
            print(f"❌ Error: Model file not found")
            print(f"   Expected: {models_dir / cls.MODEL_FILENAME}")
            print(f"   Tip: Place {cls.MODEL_FILENAME} in the /models folder")
            cls._model_loaded = True
            return None
        except Exception as e:
            print(f"❌ Error loading AI model: {e}")
            print("   Falling back to rule-based commit messages")
            cls._model_loaded = True
            return None
    
    def _generate_ai_commit_message_with_gpt4all(self, changed_files):
        """
        Generate commit message using GPT4All local model
        OPTIMIZED: Ultra-fast generation with minimal prompt
        """
        model = self._init_ai_model()
        
        if model is None:
            return None
        
        try:
            # Show generation progress
            print("⚡ Generating message...", end=' ', flush=True)
            
            # Prepare ultra-concise file summary
            if not changed_files:
                file_hint = "multiple files"
            elif len(changed_files) == 1:
                file_hint = Path(changed_files[0]).name
            else:
                file_hint = f"{len(changed_files)} files"
            
            # ULTRA-MINIMAL PROMPT for speed
            # Shorter prompt = faster generation
            prompt = f"""Write a git commit message for: {file_hint}

Format: <emoji> <type>: <what changed>
Emojis: 🚀=feature 🐛=fix 📚=docs ♻️=refactor
Max 50 chars. No period.

Message:"""
            
            # Generate with AGGRESSIVE performance settings
            response = model.generate(
                prompt,
                max_tokens=self.MAX_TOKENS,  # Reduced token count
                temp=self.TEMPERATURE,       # Lower temperature = faster
                top_p=self.TOP_P,
                top_k=self.TOP_K,            # Reduced top_k
                repeat_penalty=1.1,          # Slight penalty to avoid repetition
                n_batch=8,                   # Batch size for processing
                streaming=False              # Non-streaming for simpler code
            )
            
            print("✅")  # Complete the progress line
            
            # Clean up the response aggressively
            message = response.strip()
            
            # Remove everything after first newline
            message = message.split('\n')[0].strip()
            
            # Remove common prefixes/suffixes
            prefixes = ["Message:", "Commit:", "Git:", "**", "```", '"', "'", ">", "-", "*"]
            for prefix in prefixes:
                if message.startswith(prefix):
                    message = message[len(prefix):].strip()
            
            for suffix in ['"', "'", "**", "```", ".", "!"]:
                if message.endswith(suffix):
                    message = message[:-len(suffix)].strip()
            
            # Ensure it starts with an emoji
            emojis = ['🚀', '🐛', '📚', '♻️', '🎨', '✅', '🔧', '✨', '🔥', '📝']
            if not any(message.startswith(e) for e in emojis):
                # Try to infer emoji from content
                msg_lower = message.lower()
                if any(word in msg_lower for word in ['fix', 'bug', 'error']):
                    message = '🐛 ' + message
                elif any(word in msg_lower for word in ['add', 'new', 'feature']):
                    message = '🚀 ' + message
                elif any(word in msg_lower for word in ['doc', 'readme', 'comment']):
                    message = '📚 ' + message
                elif any(word in msg_lower for word in ['refactor', 'clean', 'improve']):
                    message = '♻️ ' + message
                else:
                    message = '🔧 ' + message
            
            # Enforce length limit
            if len(message) > 72:
                message = message[:69] + "..."
            
            # Validate message quality
            if len(message) > 10 and len(message) < 80:
                return message
            else:
                return None
                
        except Exception as e:
            print(f"\n⚠️  Generation error: {e}")
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
        
        # Get changed files for context
        changed_files = self._get_staged_files()
        
        # Generate AI commit message
        print("🧠 AI-Powered Commit Message Generation")
        print("─"*70)
        
        # Try GPT4All first (now optimized for speed)
        ai_message = self._generate_ai_commit_message_with_gpt4all(changed_files)
        
        # Fallback to rule-based AI
        if not ai_message:
            print("\n⚠️  Using fallback generator...")
            ai_message = self._generate_fallback_commit_message()
        
        if not ai_message:
            print("❌ Failed to generate commit message. Manual input required.")
            commit_message = input("\nEnter commit message: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            # Display AI-generated message
            print("\n" + "="*70)
            print(f"📝 Suggested Commit Message:")
            print(f'   "{ai_message}"')
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
        print(f"\n💾 Committing: \"{commit_message}\"")
        if not self._run_command(["git", "commit", "-m", commit_message]):
            input("\nPress Enter to continue...")
            return
        print("✅ Commit created\n")
        
        # Push to remote
        print("📡 Pushing to remote...")
        push_success = self._run_command(["git", "push"])
        
        if push_success:
            print("\n✅ Successfully pushed to remote!")
            
            # Automatic changelog generation
            print("\n" + "─"*70)
            self._auto_generate_changelog()
            print("─"*70)
        else:
            print("\n⚠️  Push failed. You may need to set up remote or pull first.")
        
        input("\nPress Enter to continue...")
    
    def _generate_fallback_commit_message(self):
        """Fallback rule-based commit message generation"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            
            summarizer = CommitSummarizer()
            message = summarizer.generate_commit_message_for_staged_changes()
            return message
        except Exception as e:
            print(f"⚠️  Fallback error: {e}")
            return "chore: update repository"
    
    def _auto_generate_changelog(self):
        """Automatically generate and update changelog after successful push"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            
            summarizer = CommitSummarizer()
            success = summarizer.auto_generate_after_push(num_commits=1)
            
            if not success:
                print("⚠️  Changelog generation skipped")
        except Exception as e:
            print(f"⚠️  Could not auto-generate changelog: {e}")
            print("   (This is non-critical - your push was successful)")
    
    def _get_staged_files(self):
        """Get list of staged files"""
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
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            return files
        except:
            return []
    
    def _has_changes(self):
        """Check if there are any changes (staged or unstaged)"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command):
        """Run a shell command and display output with proper encoding handling"""
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
            print("❌ Git is not installed or not in PATH")
            return False