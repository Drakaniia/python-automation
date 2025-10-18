"""
Git Push AI Module - Code-Aware Enterprise Edition
Deeply analyzes actual code changes in your codebase to generate
precise, contextual commit messages based on what actually changed.
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


class CodeChangeAnalyzer:
    """Deep code analysis to understand what actually changed in the codebase"""
    
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
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def analyze_changes(self) -> Dict:
        """
        Perform deep analysis of actual code changes
        Returns detailed information about what changed in the codebase
        """
        # Get file changes
        file_changes = self._get_changed_files()
        
        if not file_changes:
            return {'files': [], 'summary': '', 'type': 'chore'}
        
        # Analyze each file's actual code changes
        analyzed_files = []
        for filepath, status in file_changes:
            file_analysis = self._analyze_file_changes(filepath, status)
            if file_analysis:
                analyzed_files.append(file_analysis)
        
        # Determine overall commit type and generate summary
        commit_info = self._synthesize_commit_info(analyzed_files)
        
        return commit_info
    
    def _get_changed_files(self) -> List[Tuple[str, str]]:
        """Get list of changed files with their status"""
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
    
    def _analyze_file_changes(self, filepath: str, status: str) -> Optional[Dict]:
        """Deeply analyze what changed in a specific file"""
        
        # Get the actual diff for this file
        diff = self._get_file_diff(filepath)
        
        if not diff and status != 'D':
            return None
        
        analysis = {
            'filepath': filepath,
            'filename': Path(filepath).name,
            'status': status,
            'changes': []
        }
        
        # Handle different statuses
        if status == 'A':
            # New file added
            analysis['changes'] = self._analyze_new_file(diff, filepath)
        elif status == 'D':
            # File deleted
            analysis['changes'] = [f"removed {Path(filepath).name}"]
        elif status == 'M':
            # Modified file - analyze what changed
            analysis['changes'] = self._analyze_modifications(diff, filepath)
        
        return analysis
    
    def _get_file_diff(self, filepath: str) -> str:
        """Get the actual diff content for a specific file"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", filepath],
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
    
    def _analyze_new_file(self, diff: str, filepath: str) -> List[str]:
        """Analyze a newly added file to understand its purpose"""
        changes = []
        filename = Path(filepath).name
        
        # Check file type
        if filename.endswith('.py'):
            # Analyze Python file
            
            # Look for class definitions
            classes = re.findall(r'^\+class\s+(\w+)', diff, re.MULTILINE)
            if classes:
                for cls in classes:
                    changes.append(f"new {cls} class for {self._infer_class_purpose(cls, diff)}")
            
            # Look for function definitions
            functions = re.findall(r'^\+def\s+(\w+)', diff, re.MULTILINE)
            if functions and not classes:
                changes.append(f"new module with {len(functions)} function(s): {', '.join(functions[:3])}")
            
            # Check for specific patterns
            if 'from gpt4all' in diff or 'import gpt4all' in diff:
                changes.append("AI model integration")
            
            if 'subprocess.run' in diff and 'git' in diff.lower():
                changes.append("Git operations handler")
            
            if 'class.*Menu' in diff or 'MenuItem' in diff:
                changes.append("menu system component")
        
        elif filename.endswith('.md'):
            if 'README' in filename.upper():
                changes.append("project documentation")
            elif 'CHANGELOG' in filename.upper():
                changes.append("changelog tracking")
            else:
                changes.append("documentation file")
        
        elif filename.endswith('.sh'):
            changes.append("shell script for automation")
        
        if not changes:
            changes.append(f"new {filename}")
        
        return changes
    
    def _analyze_modifications(self, diff: str, filepath: str) -> List[str]:
        """Analyze modifications to understand what actually changed"""
        changes = []
        filename = Path(filepath).name
        
        # Python file analysis
        if filename.endswith('.py'):
            
            # 1. New functions/methods added
            added_funcs = re.findall(r'^\+\s*def\s+(\w+)', diff, re.MULTILINE)
            if added_funcs:
                func_purposes = []
                for func in added_funcs[:3]:  # Limit to first 3
                    purpose = self._infer_function_purpose(func, diff)
                    func_purposes.append(f"{func}() for {purpose}")
                changes.append(f"added {', '.join(func_purposes)}")
            
            # 2. Functions/methods removed
            removed_funcs = re.findall(r'^-\s*def\s+(\w+)', diff, re.MULTILINE)
            if removed_funcs:
                changes.append(f"removed {', '.join(removed_funcs[:2])}() method(s)")
            
            # 3. New classes
            added_classes = re.findall(r'^\+class\s+(\w+)', diff, re.MULTILINE)
            if added_classes:
                for cls in added_classes:
                    purpose = self._infer_class_purpose(cls, diff)
                    changes.append(f"new {cls} class for {purpose}")
            
            # 4. Import changes (new dependencies)
            added_imports = re.findall(r'^\+(?:from|import)\s+([\w.]+)', diff, re.MULTILINE)
            if added_imports:
                unique_imports = list(set(added_imports))[:3]
                if 'gpt4all' in str(unique_imports):
                    changes.append("integrated GPT4All AI model")
                elif any('git' in imp for imp in unique_imports):
                    changes.append("added Git operation dependencies")
                elif unique_imports:
                    changes.append(f"added dependencies: {', '.join(unique_imports)}")
            
            # 5. Error handling improvements
            added_try = len(re.findall(r'^\+\s*try:', diff, re.MULTILINE))
            added_except = len(re.findall(r'^\+\s*except', diff, re.MULTILINE))
            if added_try > 0 or added_except > 0:
                changes.append("improved error handling with try-except blocks")
            
            # 6. Logging/debugging
            added_prints = len(re.findall(r'^\+.*print\(', diff, re.MULTILINE))
            if added_prints > 3:
                changes.append(f"enhanced logging with {added_prints} new debug statements")
            
            # 7. Check for algorithm changes
            if re.search(r'^\+.*for.*in', diff, re.MULTILINE):
                if re.search(r'^\+.*algorithm|^\+.*optimize|^\+.*performance', diff, re.MULTILINE | re.IGNORECASE):
                    changes.append("optimized algorithm implementation")
            
            # 8. Class attributes/constants
            added_constants = re.findall(r'^\+\s+([A-Z_]+)\s*=', diff, re.MULTILINE)
            if added_constants:
                changes.append(f"added configuration constants: {', '.join(added_constants[:3])}")
            
            # 9. Docstrings
            if '"""' in diff or "'''" in diff:
                added_docstrings = len(re.findall(r'^\+\s*"""', diff, re.MULTILINE))
                if added_docstrings > 0:
                    changes.append(f"added documentation strings to {added_docstrings} component(s)")
            
            # 10. Bug fix patterns
            if self._looks_like_bugfix(diff):
                changes.append("fixed logic error in implementation")
            
            # 11. Refactoring patterns
            if self._looks_like_refactor(diff):
                changes.append("refactored code structure for better maintainability")
        
        # Markdown file analysis
        elif filename.endswith('.md'):
            added_lines = [l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
            if len(added_lines) > 5:
                # Check what sections were added
                headers = re.findall(r'^\+#+ (.+)', diff, re.MULTILINE)
                if headers:
                    changes.append(f"updated documentation: {', '.join(headers[:2])}")
                else:
                    changes.append("expanded documentation content")
        
        # Configuration files
        elif filename.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
            changes.append("updated configuration settings")
        
        # Shell scripts
        elif filename.endswith('.sh'):
            changes.append("modified automation script")
        
        # Fallback analysis
        if not changes:
            # Count line changes
            added = len([l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')])
            removed = len([l for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')])
            
            if added > removed * 2:
                changes.append(f"expanded implementation (+{added} lines)")
            elif removed > added * 2:
                changes.append(f"simplified code (-{removed} lines)")
            else:
                changes.append("updated implementation logic")
        
        return changes
    
    def _infer_function_purpose(self, func_name: str, diff: str) -> str:
        """Infer the purpose of a function from its name and context"""
        name_lower = func_name.lower()
        
        # Common patterns
        if name_lower.startswith('get_'):
            return "retrieving data"
        elif name_lower.startswith('set_'):
            return "setting configuration"
        elif name_lower.startswith('check_') or name_lower.startswith('is_') or name_lower.startswith('has_'):
            return "validation"
        elif name_lower.startswith('parse_') or name_lower.startswith('extract_'):
            return "data parsing"
        elif name_lower.startswith('generate_') or name_lower.startswith('create_'):
            return "content generation"
        elif name_lower.startswith('analyze_'):
            return "analysis logic"
        elif name_lower.startswith('run_') or name_lower.startswith('execute_'):
            return "execution"
        elif name_lower.startswith('load_'):
            return "resource loading"
        elif name_lower.startswith('save_') or name_lower.startswith('write_'):
            return "data persistence"
        elif 'ai' in name_lower or 'model' in name_lower:
            return "AI processing"
        elif 'commit' in name_lower:
            return "commit handling"
        elif 'diff' in name_lower:
            return "diff analysis"
        else:
            return "processing"
    
    def _infer_class_purpose(self, class_name: str, diff: str) -> str:
        """Infer the purpose of a class from its name"""
        name_lower = class_name.lower()
        
        if 'analyzer' in name_lower:
            return "code analysis"
        elif 'handler' in name_lower or 'manager' in name_lower:
            return "operations management"
        elif 'generator' in name_lower:
            return "content generation"
        elif 'menu' in name_lower:
            return "user interface"
        elif 'git' in name_lower:
            return "Git operations"
        elif 'ai' in name_lower or 'model' in name_lower:
            return "AI functionality"
        elif 'viewer' in name_lower:
            return "data visualization"
        elif 'navigator' in name_lower:
            return "navigation logic"
        else:
            return "functionality"
    
    def _looks_like_bugfix(self, diff: str) -> bool:
        """Detect if changes look like a bug fix"""
        fix_keywords = ['fix', 'bug', 'error', 'issue', 'patch', 'correct', 'resolve']
        diff_lower = diff.lower()
        
        # Check for fix keywords in comments
        if any(kw in diff_lower for kw in fix_keywords):
            return True
        
        # Check for conditional logic changes
        if re.search(r'^-\s*if .+\n\+\s*if', diff, re.MULTILINE):
            return True
        
        return False
    
    def _looks_like_refactor(self, diff: str) -> bool:
        """Detect if changes look like refactoring"""
        # Similar number of additions and deletions
        added = len([l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')])
        removed = len([l for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')])
        
        if added > 0 and removed > 0:
            ratio = added / removed if removed > 0 else 0
            # If ratio is close to 1, likely refactoring
            if 0.7 <= ratio <= 1.3:
                return True
        
        return False
    
    def _synthesize_commit_info(self, analyzed_files: List[Dict]) -> Dict:
        """Synthesize all file analyses into a coherent commit message"""
        if not analyzed_files:
            return {'files': [], 'summary': '', 'type': 'chore'}
        
        # Determine commit type based on actual changes
        commit_type = self._determine_commit_type(analyzed_files)
        
        # Build detailed summary
        summary_parts = []
        
        for file_analysis in analyzed_files:
            filename = file_analysis['filename']
            changes = file_analysis['changes']
            
            if changes:
                # Format: filename: change1, change2
                change_text = '; '.join(changes)
                summary_parts.append(f"{filename}: {change_text}")
        
        return {
            'files': analyzed_files,
            'summary_parts': summary_parts,
            'type': commit_type
        }
    
    def _determine_commit_type(self, analyzed_files: List[Dict]) -> str:
        """Determine the primary commit type from analyzed changes"""
        
        type_indicators = {
            'feat': 0,
            'fix': 0,
            'refactor': 0,
            'docs': 0,
            'test': 0,
            'chore': 0
        }
        
        for file_analysis in analyzed_files:
            changes_text = ' '.join(file_analysis['changes']).lower()
            
            # New features
            if any(word in changes_text for word in ['new', 'added', 'implement', 'create']):
                type_indicators['feat'] += 2
            
            # Bug fixes
            if any(word in changes_text for word in ['fix', 'bug', 'error', 'resolve', 'correct']):
                type_indicators['fix'] += 3
            
            # Refactoring
            if any(word in changes_text for word in ['refactor', 'simplif', 'optimiz', 'restructur']):
                type_indicators['refactor'] += 2
            
            # Documentation
            if file_analysis['filename'].endswith('.md') or 'documentation' in changes_text:
                type_indicators['docs'] += 2
            
            # Tests
            if 'test' in file_analysis['filename'].lower():
                type_indicators['test'] += 2
        
        # Return type with highest score
        max_type = max(type_indicators, key=type_indicators.get)
        return max_type if type_indicators[max_type] > 0 else 'chore'


class GitPushAI:
    """AI-powered git push with deep code analysis"""
    
    _model_instance = None
    _model_loaded = False
    _loading_lock = threading.Lock()
    _model_error = None
    
    MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    MAX_TOKENS = 400
    TEMPERATURE = 0.5
    TOP_K = 30
    TOP_P = 0.9
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self._generation_interrupted = False
        self.analyzer = CodeChangeAnalyzer()
    
    @classmethod
    def _check_gpt4all_installed(cls):
        try:
            import gpt4all
            return True
        except ImportError:
            return False
    
    @classmethod
    def _check_model_exists(cls):
        models_dir = Path.cwd() / "models"
        model_path = models_dir / cls.MODEL_FILENAME
        return model_path.exists()
    
    @classmethod
    def _silent_load_model(cls):
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
    
    def _generate_code_aware_message(self, commit_info: Dict) -> str:
        """Generate commit message based on actual code analysis"""
        
        if not commit_info['summary_parts']:
            return "🔧 chore: update files"
        
        commit_type = commit_info['type']
        emoji = CodeChangeAnalyzer.COMMIT_TYPES.get(commit_type, '🔧')
        
        # Build subject line from first major change
        first_file = commit_info['files'][0]
        first_change = first_file['changes'][0] if first_file['changes'] else 'update'
        
        # Determine scope from filename
        scope = self._extract_scope(first_file['filepath'])
        
        # Create subject
        subject = f"{emoji} {commit_type}({scope}): {first_change}"
        
        # Truncate subject if too long
        if len(subject) > 72:
            subject = subject[:69] + "..."
        
        # Build body with all changes
        body_lines = []
        for part in commit_info['summary_parts'][:8]:  # Limit to 8 most important changes
            body_lines.append(f"• {part}")
        
        # Combine
        if body_lines:
            return f"{subject}\n\n" + "\n".join(body_lines)
        else:
            return subject
    
    def _extract_scope(self, filepath: str) -> str:
        """Extract scope from filepath"""
        parts = Path(filepath).parts
        
        # Check directory structure
        if 'github' in parts:
            return 'git'
        elif 'automation' in parts:
            if len(parts) > 1:
                return parts[parts.index('automation') + 1] if parts.index('automation') + 1 < len(parts) else 'core'
            return 'core'
        else:
            return Path(filepath).stem
    
    def _stream_generate_with_interrupt(self, prompt: str) -> Optional[str]:
        """Generate with AI model"""
        model = self._model_instance
        if model is None:
            return None
        
        try:
            print("💬 AI analyzing", end='', flush=True)
            
            generated_text = ""
            self._generation_interrupted = False
            
            def show_progress():
                dots = ['', '.', '..', '...']
                i = 0
                while not self._generation_interrupted:
                    print(f'\r💬 AI analyzing{dots[i % 4]}', end='', flush=True)
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
    
    def ai_commit_and_push(self):
        """Main entry point"""
        print("\n" + "="*70)
        print("⬆️  GIT PUSH (Code-Aware AI)")
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
        
        # Deep code analysis
        print("🔍 Analyzing code changes...")
        commit_info = self.analyzer.analyze_changes()
        
        if not commit_info['files']:
            print("⚠️  No changes to analyze")
            input("\nPress Enter to continue...")
            return
        
        print(f"✅ Analyzed {len(commit_info['files'])} file(s) with code-level inspection\n")
        
        # Generate message
        print("🤖 Generating Code-Aware Commit Message")
        print("─"*70)
        
        commit_message = self._generate_code_aware_message(commit_info)
        
        # Display
        print("\n" + "="*70)
        print("📝 Generated Commit Message (Based on Actual Code Changes):")
        print("─"*70)
        print(commit_message)
        print("="*70 + "\n")
        
        use_ai = input("Use this message? [Y/n/edit]: ").strip().lower()
        
        if use_ai in ("", "y", "yes"):
            pass
        elif use_ai in ("e", "edit"):
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
    
    def _auto_generate_changelog(self):
        try:
            from automation.github.commit_summarizer import CommitSummarizer
            summarizer = CommitSummarizer()
            summarizer.auto_generate_after_push(num_commits=1)
        except Exception as e:
            print(f"⚠️  Changelog generation skipped: {e}")
    
    def _has_changes(self) -> bool:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return bool(result.stdout.strip())
    
    def _is_git_repo(self) -> bool:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    
    def _run_command(self, command: List[str]) -> bool:
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