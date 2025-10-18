"""
Git Push AI Module - Enterprise Edition
Generates detailed, contextual, enterprise-grade commit messages
with file-specific analysis and structured summaries.
"""
import subprocess
from pathlib import Path
import sys
import os
import warnings
import threading
import time
import re
from typing import List, Dict, Tuple, Optional


class EnterpriseCommitAnalyzer:
    """Analyzes git changes and generates enterprise-grade commit messages"""
    
    # Conventional commit types with emojis
    COMMIT_TYPES = {
        'feat': '✨',
        'fix': '🐛',
        'refactor': '♻️',
        'docs': '📚',
        'style': '🎨',
        'test': '✅',
        'chore': '🔧',
        'perf': '⚡',
        'build': '🏗️',
        'ci': '👷',
        'revert': '⏪'
    }
    
    # File patterns for scope detection
    SCOPE_PATTERNS = {
        'ai': ['ai', 'gpt', 'model', 'intelligence'],
        'git': ['git_', 'commit', 'push', 'pull', 'status', 'log'],
        'ui': ['menu', 'navigator', 'viewer', 'display'],
        'core': ['main', '__init__', 'operations'],
        'utils': ['helper', 'util', 'tool'],
        'docs': ['readme', 'changelog', 'documentation'],
        'test': ['test_', 'spec_'],
        'config': ['setup', 'config', '.ini', '.yaml', '.toml']
    }
    
    # Keywords for change type detection
    CHANGE_KEYWORDS = {
        'feat': ['add', 'new', 'create', 'implement', 'introduce', 'feature'],
        'fix': ['fix', 'bug', 'error', 'issue', 'resolve', 'patch', 'correct'],
        'refactor': ['refactor', 'clean', 'reorganize', 'restructure', 'improve', 'optimize'],
        'docs': ['document', 'readme', 'comment', 'docs', 'guide'],
        'perf': ['performance', 'optimize', 'speed', 'faster', 'cache'],
        'style': ['format', 'style', 'lint', 'prettier'],
        'test': ['test', 'spec', 'coverage'],
        'chore': ['update', 'dependency', 'maintenance', 'version']
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def analyze_staged_changes(self) -> Dict:
        """
        Comprehensive analysis of staged changes
        Returns structured data about what changed and why
        """
        # Get file changes with status
        file_changes = self._get_file_changes_with_status()
        
        # Get detailed diff content
        diff_content = self._get_staged_diff()
        
        # Analyze each file
        file_analyses = []
        for file_path, status in file_changes:
            analysis = self._analyze_single_file(file_path, status, diff_content)
            file_analyses.append(analysis)
        
        # Aggregate analysis
        return self._aggregate_analysis(file_analyses)
    
    def _get_file_changes_with_status(self) -> List[Tuple[str, str]]:
        """Get list of changed files with their status (M, A, D, R)"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, filepath = parts
                        changes.append((filepath, status))
            
            return changes
        except:
            return []
    
    def _get_staged_diff(self) -> str:
        """Get full diff of staged changes"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout
        except:
            return ""
    
    def _analyze_single_file(self, filepath: str, status: str, diff_content: str) -> Dict:
        """Analyze a single file's changes"""
        path = Path(filepath)
        
        analysis = {
            'filepath': filepath,
            'filename': path.name,
            'status': status,
            'status_text': self._get_status_text(status),
            'scope': self._detect_scope(filepath),
            'type': self._detect_change_type(filepath, diff_content, status),
            'additions': 0,
            'deletions': 0,
            'summary': ''
        }
        
        # Count line changes for this file
        file_diff = self._extract_file_diff(filepath, diff_content)
        analysis['additions'], analysis['deletions'] = self._count_line_changes(file_diff)
        
        # Generate file-specific summary
        analysis['summary'] = self._generate_file_summary(analysis, file_diff)
        
        return analysis
    
    def _get_status_text(self, status: str) -> str:
        """Convert git status code to readable text"""
        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'T': 'type changed'
        }
        return status_map.get(status[0], 'changed')
    
    def _detect_scope(self, filepath: str) -> str:
        """Detect the scope/component from filepath"""
        filepath_lower = filepath.lower()
        
        for scope, patterns in self.SCOPE_PATTERNS.items():
            if any(pattern in filepath_lower for pattern in patterns):
                return scope
        
        # Default to directory name
        parts = Path(filepath).parts
        if len(parts) > 1:
            return parts[-2] if parts[-2] != 'automation' else parts[-1].split('.')[0]
        
        return 'core'
    
    def _detect_change_type(self, filepath: str, diff_content: str, status: str) -> str:
        """Detect the type of change (feat, fix, refactor, etc.)"""
        # Status-based detection
        if status == 'A':
            return 'feat'
        elif status == 'D':
            return 'chore'
        
        # Content-based detection
        content_lower = diff_content.lower()
        filepath_lower = filepath.lower()
        
        # Check for test files
        if 'test' in filepath_lower:
            return 'test'
        
        # Check for documentation
        if any(ext in filepath_lower for ext in ['.md', 'readme', 'changelog', 'doc']):
            return 'docs'
        
        # Check diff content for keywords
        scores = {}
        for change_type, keywords in self.CHANGE_KEYWORDS.items():
            score = sum(content_lower.count(kw) for kw in keywords)
            scores[change_type] = score
        
        if scores:
            max_type = max(scores, key=scores.get)
            if scores[max_type] > 0:
                return max_type
        
        return 'chore'
    
    def _extract_file_diff(self, filepath: str, full_diff: str) -> str:
        """Extract diff section for specific file"""
        pattern = f"diff --git a/{re.escape(filepath)} b/{re.escape(filepath)}"
        parts = full_diff.split('diff --git')
        
        for part in parts:
            if filepath in part:
                return part
        
        return ""
    
    def _count_line_changes(self, file_diff: str) -> Tuple[int, int]:
        """Count additions and deletions in file diff"""
        additions = 0
        deletions = 0
        
        for line in file_diff.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        return additions, deletions
    
    def _generate_file_summary(self, analysis: Dict, file_diff: str) -> str:
        """Generate a human-readable summary for a single file"""
        filepath = analysis['filepath']
        filename = analysis['filename']
        status = analysis['status_text']
        
        # For new files
        if analysis['status'] == 'A':
            purpose = self._infer_file_purpose(filename, file_diff)
            return f"{filename}: {purpose}"
        
        # For deletions
        if analysis['status'] == 'D':
            return f"{filename}: removed obsolete file"
        
        # For modifications
        adds = analysis['additions']
        dels = analysis['deletions']
        
        # Try to infer what changed
        changes = self._infer_modification_details(file_diff, filename)
        
        if changes:
            return f"{filename}: {changes}"
        
        # Fallback to generic summary
        if adds > dels * 2:
            return f"{filename}: expanded functionality ({adds} additions)"
        elif dels > adds * 2:
            return f"{filename}: simplified code ({dels} deletions)"
        else:
            return f"{filename}: improved implementation"
    
    def _infer_file_purpose(self, filename: str, diff: str) -> str:
        """Infer purpose of a new file from its content"""
        diff_lower = diff.lower()
        
        if 'class' in diff_lower:
            class_match = re.search(r'class\s+(\w+)', diff)
            if class_match:
                return f"new {class_match.group(1)} class implementation"
        
        if 'def ' in diff_lower:
            return "new module with utility functions"
        
        if filename.endswith('.md'):
            return "documentation file"
        
        return "new file added"
    
    def _infer_modification_details(self, diff: str, filename: str) -> str:
        """Infer specific details about what was modified"""
        diff_lower = diff.lower()
        
        # Function/method changes
        added_funcs = re.findall(r'\+\s*def\s+(\w+)', diff)
        removed_funcs = re.findall(r'-\s*def\s+(\w+)', diff)
        
        if added_funcs:
            return f"added {', '.join(added_funcs[:2])} method(s)"
        
        if removed_funcs:
            return f"removed {', '.join(removed_funcs[:2])} method(s)"
        
        # Class changes
        if '+class ' in diff:
            return "added new class implementation"
        
        # Import changes
        if '+import ' in diff or '+from ' in diff:
            return "updated dependencies"
        
        # Error handling
        if 'try:' in diff_lower or 'except' in diff_lower:
            return "improved error handling"
        
        # Logging
        if 'print(' in diff or 'log' in diff_lower:
            return "enhanced logging"
        
        # Performance
        if any(kw in diff_lower for kw in ['cache', 'optimize', 'performance']):
            return "performance optimizations"
        
        return "code improvements"
    
    def _aggregate_analysis(self, file_analyses: List[Dict]) -> Dict:
        """Aggregate individual file analyses into overall summary"""
        if not file_analyses:
            return {
                'type': 'chore',
                'scope': 'core',
                'files': [],
                'total_additions': 0,
                'total_deletions': 0
            }
        
        # Determine primary type (most common)
        type_counts = {}
        for analysis in file_analyses:
            t = analysis['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        primary_type = max(type_counts, key=type_counts.get)
        
        # Determine primary scope
        scope_counts = {}
        for analysis in file_analyses:
            s = analysis['scope']
            scope_counts[s] = scope_counts.get(s, 0) + 1
        
        primary_scope = max(scope_counts, key=scope_counts.get)
        
        # Calculate totals
        total_additions = sum(a['additions'] for a in file_analyses)
        total_deletions = sum(a['deletions'] for a in file_analyses)
        
        return {
            'type': primary_type,
            'scope': primary_scope,
            'files': file_analyses,
            'total_additions': total_additions,
            'total_deletions': total_deletions
        }


class GitPushAI:
    """Enterprise-grade AI-assisted git push with detailed commit messages"""
    
    _model_instance = None
    _model_loaded = False
    _loading_lock = threading.Lock()
    _model_error = None
    
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    MAX_TOKENS = 300
    TEMPERATURE = 0.4
    TOP_K = 20
    TOP_P = 0.85
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self._generation_interrupted = False
        self.analyzer = EnterpriseCommitAnalyzer()
    
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
        """Silently load model in background"""
        with cls._loading_lock:
            if cls._model_loaded:
                return cls._model_instance is not None
            
            if not cls._check_gpt4all_installed():
                cls._model_error = "gpt4all not installed"
                cls._model_loaded = True
                return False
            
            if not cls._check_model_exists():
                cls._model_error = "model file not found"
                cls._model_loaded = True
                return False
            
            try:
                os.environ['GPT4ALL_VERBOSE'] = '0'
                os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())
                warnings.filterwarnings('ignore')
                
                from gpt4all import GPT4All
                
                models_dir = Path.cwd() / "models"
                
                # Suppress output
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
                cls._model_error = None
                return True
                
            except Exception as e:
                cls._model_error = str(e)
                cls._model_loaded = True
                return False
    
    def _generate_enterprise_commit_message(self, analysis: Dict) -> Optional[str]:
        """Generate enterprise-grade commit message from analysis"""
        
        # Build structured prompt for AI
        prompt = self._build_enterprise_prompt(analysis)
        
        # Try AI generation
        if not self._model_loaded:
            print("🧠 Initializing AI model (first time only)...")
            success = self._silent_load_model()
            if success:
                print("✅ AI model loaded successfully!\n")
        
        ai_message = None
        if self._model_instance:
            try:
                ai_message = self._stream_generate_with_interrupt(prompt)
            except KeyboardInterrupt:
                print("\n⚠️  AI generation cancelled by user")
                ai_message = None
        
        # Use rule-based fallback if AI fails
        if not ai_message:
            return self._generate_fallback_enterprise_message(analysis)
        
        # Clean and validate AI response
        cleaned = self._clean_ai_response(ai_message, analysis)
        return cleaned
    
    def _build_enterprise_prompt(self, analysis: Dict) -> str:
        """Build detailed prompt for AI model"""
        commit_type = analysis['type']
        scope = analysis['scope']
        files = analysis['files']
        
        # Build file summary
        file_list = "\n".join([
            f"  • {f['status_text'].upper()}: {f['filepath']} (+{f['additions']}/-{f['deletions']})"
            for f in files[:5]  # Limit to 5 files
        ])
        
        prompt = f"""You are an enterprise Git commit message generator.
Generate a concise, professional commit message following Conventional Commits.

Changes Summary:
{file_list}

Type: {commit_type}
Scope: {scope}
Total: +{analysis['total_additions']}/-{analysis['total_deletions']} lines

Format:
<emoji> <type>(<scope>): <clear summary under 50 chars>

• <specific change 1>
• <specific change 2>

Keep it professional and actionable. Use the appropriate emoji for {commit_type}.
"""
        
        return prompt
    
    def _stream_generate_with_interrupt(self, prompt: str) -> Optional[str]:
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
            except KeyboardInterrupt:
                self._generation_interrupted = True
                return None
            
            self._generation_interrupted = True
            progress_thread.join(timeout=0.5)
            
            print("\r" + " "*40 + "\r", end='', flush=True)
            
            return generated_text.strip() if generated_text else None
            
        except:
            return None
    
    def _clean_ai_response(self, response: str, analysis: Dict) -> str:
        """Clean and format AI-generated response"""
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove common prefixes
                for prefix in ["Message:", "Commit:", "Output:", '"', "'", "-", "*", ">"]:
                    if line.startswith(prefix):
                        line = line[len(prefix):].strip()
                
                # Remove trailing quotes/periods
                for suffix in ['"', "'", ".", "!"]:
                    if line.endswith(suffix):
                        line = line[:-1].strip()
                
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # Ensure it has an emoji
        if not any(emoji in result for emoji in EnterpriseCommitAnalyzer.COMMIT_TYPES.values()):
            emoji = EnterpriseCommitAnalyzer.COMMIT_TYPES.get(analysis['type'], '🔧')
            result = f"{emoji} {result}"
        
        return result
    
    def _generate_fallback_enterprise_message(self, analysis: Dict) -> str:
        """Generate enterprise message using rules (fallback)"""
        commit_type = analysis['type']
        scope = analysis['scope']
        files = analysis['files']
        emoji = EnterpriseCommitAnalyzer.COMMIT_TYPES.get(commit_type, '🔧')
        
        # Generate subject line
        if len(files) == 1:
            subject = f"{emoji} {commit_type}({scope}): {files[0]['summary']}"
        else:
            action = self._get_action_verb(commit_type)
            subject = f"{emoji} {commit_type}({scope}): {action} {len(files)} files across {scope} module"
        
        # Keep subject under 72 chars
        if len(subject) > 72:
            subject = subject[:69] + "..."
        
        # Generate body with file details
        body_lines = []
        for file_analysis in files[:5]:  # Limit to 5 files
            summary = file_analysis['summary']
            body_lines.append(f"• {summary}")
        
        if len(files) > 5:
            body_lines.append(f"• ...and {len(files) - 5} more files")
        
        # Combine
        if body_lines:
            return f"{subject}\n\n" + "\n".join(body_lines)
        else:
            return subject
    
    def _get_action_verb(self, commit_type: str) -> str:
        """Get action verb for commit type"""
        verbs = {
            'feat': 'implement',
            'fix': 'resolve',
            'refactor': 'improve',
            'docs': 'document',
            'style': 'format',
            'test': 'add tests for',
            'chore': 'update',
            'perf': 'optimize',
            'build': 'configure',
            'ci': 'update'
        }
        return verbs.get(commit_type, 'update')
    
    def ai_commit_and_push(self):
        """Main entry point: analyze, generate message, commit, and push"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (Enterprise AI-Powered)")
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
        
        # Analyze changes
        print("🔍 Analyzing changes...")
        analysis = self.analyzer.analyze_staged_changes()
        
        if not analysis['files']:
            print("⚠️  No staged changes to analyze")
            input("\nPress Enter to continue...")
            return
        
        print(f"✅ Analyzed {len(analysis['files'])} file(s)\n")
        
        # Generate commit message
        print("🤖 Enterprise AI Commit Generation")
        print("─"*70)
        print("💡 Generating detailed, file-specific commit message...")
        print("💡 Press Ctrl+C during generation to switch to manual mode\n")
        
        try:
            commit_message = self._generate_enterprise_commit_message(analysis)
        except KeyboardInterrupt:
            print("\n⚠️  Generation cancelled by user")
            commit_message = None
        
        # Manual input if needed
        if not commit_message:
            print("\n📝 Manual commit message required")
            commit_message = input("Enter commit message: ").strip()
            if not commit_message:
                print("❌ Commit message cannot be empty")
                input("\nPress Enter to continue...")
                return
        else:
            # Display and confirm
            print("\n" + "="*70)
            print("📝 Generated Enterprise Commit Message:")
            print("─"*70)
            print(commit_message)
            print("="*70 + "\n")
            
            use_ai = input("Use this message? [Y/n/edit]: ").strip().lower()
            
            if use_ai in ("", "y", "yes"):
                pass  # Use as-is
            elif use_ai in ("e", "edit"):
                print(f"\nCurrent message:\n{commit_message}\n")
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
    
    def _auto_generate_changelog(self):
        """Generate changelog after push"""
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            summarizer.auto_generate_after_push(num_commits=1)
        except Exception as e:
            print(f"⚠️  Changelog generation skipped: {e}")
    
    def _has_changes(self) -> bool:
        """Check if there are changes to commit"""
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
        """Run git command and display output"""
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