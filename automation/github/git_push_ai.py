"""
Git Push AI Module
Handles AI-powered commit message generation using GPT4All (offline) and push operations
Includes automatic changelog generation after successful push
OPTIMIZED: Fast single-model loading with clean output
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
    
    # Fixed model configuration
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    
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
            
            # Suppress warnings about DLL loading
            warnings.filterwarnings('ignore', category=UserWarning)
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            
            from gpt4all import GPT4All
            
            # Define model path
            models_dir = Path.cwd() / "models"
            models_dir.mkdir(exist_ok=True)
            model_path = models_dir / cls.MODEL_FILENAME
            
            # Check if model exists
            if not model_path.exists():
                print(f"📥 Downloading {cls.MODEL_FILENAME} (first time only)...")
                print("   This may take a few minutes...")
                
                cls._model_instance = GPT4All(
                    model_name=cls.MODEL_FILENAME,
                    model_path=str(models_dir),
                    allow_download=True,
                    device='cpu',
                    verbose=False
                )
                print("✅ Model downloaded and ready!")
            else:
                # Load existing model with clean output
                print(f"🔍 Loading AI model: {cls.MODEL_FILENAME}...")
                
                # Redirect stderr temporarily to suppress DLL warnings
                import io
                import contextlib
                
                stderr_buffer = io.StringIO()
                
                with contextlib.redirect_stderr(stderr_buffer):
                    cls._model_instance = GPT4All(
                        model_name=cls.MODEL_FILENAME,
                        model_path=str(models_dir),
                        allow_download=False,
                        device='cpu',
                        verbose=False
                    )
                
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
        Uses cached model instance for fast generation
        """
        model = self._init_ai_model()
        
        if model is None:
            return None
        
        try:
            # Prepare file information
            if not changed_files:
                file_summary = "multiple files"
            elif len(changed_files) == 1:
                file_summary = f"'{changed_files[0]}'"
            elif len(changed_files) <= 3:
                file_summary = ", ".join(f"'{f}'" for f in changed_files)
            else:
                file_summary = f"{len(changed_files)} files"
            
            # Create concise prompt
            prompt = f"""You are a Git commit message expert. Write a short, professional commit message (max 60 characters).

Changed files: {file_summary}

Rules:
- Start with an emoji (🚀 feature, 🐛 fix, 📚 docs, ♻️ refactor, 🎨 style, ✅ test)
- Use conventional commits format: <emoji> <type>: <description>
- Be specific but concise
- No periods at the end

Commit message:"""
            
            # Generate with GPT4All (fast after first load)
            response = model.generate(
                prompt,
                max_tokens=50,
                temp=0.7,
                top_p=0.9,
                top_k=40
            )
            
            # Clean up the response
            message = response.strip()
            
            # Remove common prefixes
            for prefix in ["Commit message:", "Message:", "**", "```", '"', "'"]:
                if message.startswith(prefix):
                    message = message[len(prefix):].strip()
                if message.endswith(prefix):
                    message = message[:-len(prefix)].strip()
            
            # Take only first line
            message = message.split('\n')[0].strip()
            
            # Remove quotes if present
            message = message.strip('"\'')
            
            # Ensure reasonable length
            if len(message) > 72:
                message = message[:69] + "..."
            
            # Validate message has content
            if message and len(message) > 5:
                return message
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  AI generation error: {e}")
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
        print("🧠 Generating AI-powered commit message...\n")
        
        # Try GPT4All first
        ai_message = self._generate_ai_commit_message_with_gpt4all(changed_files)
        
        # Fallback to rule-based AI
        if not ai_message:
            print("⚠️  Local AI unavailable. Using fallback analyzer...\n")
            ai_message = self._generate_fallback_commit_message()
        
        if not ai_message:
            print("❌ Failed to generate commit message. Falling back to manual input.")
            commit_message = input("\nEnter commit message manually: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            # Display AI-generated message
            print("="*70)
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
            print(f"⚠️  Fallback analyzer error: {e}")
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