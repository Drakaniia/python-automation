"""
Enhanced AI Commit Message Generator
Intelligent commit message generation with multiple strategies:
- Advanced diff analysis with pattern recognition
- Rule-based heuristic engine
- Optional local LLM support (Ollama)
- Context learning from commit history
- Zero external API costs
"""
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class SmartCommitGenerator:
    """Intelligent commit message generator with multiple strategies"""
    
    # Configuration
    CONFIG = {
        'ai_mode': 'hybrid',  # 'heuristic', 'local_llm', 'hybrid'
        'llm_model': 'tinydolphin',  # Ollama model to use
        'max_diff_chars': 2000,  # Limit diff size for LLM
        'history_size': 50,  # Number of past commits to remember
        'min_confidence': 0.6,  # Minimum confidence to use generated message
    }
    
    HISTORY_FILE = '.ai_commit_history.json'
    
    # Smart pattern recognition
    CHANGE_PATTERNS = {
        'feature': [r'add', r'new', r'implement', r'create', r'introduce'],
        'fix': [r'fix', r'bug', r'patch', r'resolve', r'correct', r'repair'],
        'refactor': [r'refactor', r'clean', r'improve', r'optimize', r'simplify'],
        'docs': [r'doc', r'readme', r'comment', r'guide'],
        'test': [r'test', r'spec', r'mock', r'assert'],
        'style': [r'format', r'style', r'lint', r'prettier'],
        'perf': [r'performance', r'speed', r'optimize', r'cache'],
        'security': [r'security', r'auth', r'encrypt', r'sanitize'],
    }
    
    EMOJI_MAP = {
        'feature': '✨',
        'fix': '🐛',
        'refactor': '♻️',
        'docs': '📚',
        'test': '✅',
        'style': '🎨',
        'perf': '⚡',
        'security': '🔒',
        'config': '⚙️',
        'build': '🔧',
        'default': '🚀'
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.history = self._load_history()
    
    # ========== Main Entry Point ==========
    
    def generate_commit_message(self) -> str:
        """Generate intelligent commit message based on staged changes"""
        try:
            # Get diff data
            diff_text = self._get_git_diff()
            if not diff_text:
                return "📝 Update project files"
            
            # Analyze the diff
            analysis = self._analyze_diff(diff_text)
            
            # Choose generation strategy
            mode = self.CONFIG['ai_mode']
            
            if mode == 'local_llm':
                message = self._generate_with_llm(diff_text, analysis)
            elif mode == 'heuristic':
                message = self._generate_with_heuristics(analysis)
            else:  # hybrid
                message = self._generate_hybrid(diff_text, analysis)
            
            # Save to history
            self._save_to_history(message, analysis)
            
            return message
        
        except Exception as e:
            print(f"⚠️  Generation error: {e}")
            return "🚀 Update project files"
    
    # ========== Diff Analysis ==========
    
    def _get_git_diff(self) -> str:
        """Get staged diff with encoding handling"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout
        except Exception:
            return ""
    
    def _analyze_diff(self, diff_text: str) -> Dict:
        """Comprehensive diff analysis"""
        analysis = {
            'files': [],
            'stats': {'additions': 0, 'deletions': 0, 'files_changed': 0},
            'change_type': 'update',
            'scope': '',
            'confidence': 0.0,
            'keywords': [],
            'file_types': set(),
            'affected_modules': set()
        }
        
        # Extract files
        files = re.findall(r'diff --git a/(.*?) b/', diff_text)
        analysis['files'] = files
        analysis['stats']['files_changed'] = len(files)
        
        # Count line changes
        for line in diff_text.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                analysis['stats']['additions'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                analysis['stats']['deletions'] += 1
        
        # Detect file types and modules
        for file in files:
            ext = Path(file).suffix
            if ext:
                analysis['file_types'].add(ext)
            
            parts = file.split('/')
            if len(parts) > 1:
                analysis['affected_modules'].add(parts[0])
        
        # Detect change type using pattern recognition
        diff_lower = diff_text.lower()
        type_scores = {}
        
        for change_type, patterns in self.CHANGE_PATTERNS.items():
            score = sum(len(re.findall(pattern, diff_lower)) for pattern in patterns)
            if score > 0:
                type_scores[change_type] = score
        
        if type_scores:
            analysis['change_type'] = max(type_scores, key=type_scores.get)
            analysis['confidence'] = min(type_scores[analysis['change_type']] / 10, 1.0)
        
        # Detect scope
        analysis['scope'] = self._detect_scope(files, diff_text)
        
        # Extract keywords
        analysis['keywords'] = self._extract_keywords(diff_text)
        
        return analysis
    
    def _detect_scope(self, files: List[str], diff_text: str) -> str:
        """Detect the scope/area of changes"""
        scopes = {
            'core': ['core/', '__init__.py', 'base.py'],
            'ui': ['menu', 'interface', 'display'],
            'git': ['git', 'commit', 'push', 'pull'],
            'ai': ['ai', 'llm', 'generate', 'smart'],
            'config': ['config', 'settings', '.json', '.yaml'],
            'docs': ['.md', 'readme', 'changelog'],
            'tests': ['test_', 'tests/'],
            'build': ['setup', 'requirements', 'dockerfile'],
        }
        
        scope_scores = {}
        for scope, indicators in scopes.items():
            score = 0
            for indicator in indicators:
                for file in files:
                    if indicator.lower() in file.lower():
                        score += 1
                if indicator.lower() in diff_text.lower():
                    score += 0.5
            
            if score > 0:
                scope_scores[scope] = score
        
        if scope_scores:
            return max(scope_scores, key=scope_scores.get)
        return ''
    
    def _extract_keywords(self, diff_text: str) -> List[str]:
        """Extract important keywords from diff"""
        # Look for function/class names
        keywords = set()
        
        # Function definitions
        funcs = re.findall(r'def\s+(\w+)', diff_text)
        keywords.update(funcs[:3])
        
        # Class definitions
        classes = re.findall(r'class\s+(\w+)', diff_text)
        keywords.update(classes[:3])
        
        # Important words in comments
        comments = re.findall(r'#\s*(.+)', diff_text)
        for comment in comments[:5]:
            words = re.findall(r'\b[A-Z][a-z]+\b', comment)
            keywords.update(words[:2])
        
        return list(keywords)[:5]
    
    # ========== Heuristic Generation ==========
    
    def _generate_with_heuristics(self, analysis: Dict) -> str:
        """Generate message using rule-based heuristics"""
        emoji = self.EMOJI_MAP.get(analysis['change_type'], self.EMOJI_MAP['default'])
        
        # Build action verb
        action = self._get_action_verb(analysis)
        
        # Build description
        description = self._build_description(analysis)
        
        # Combine parts
        if analysis['scope']:
            message = f"{emoji} {action} {analysis['scope']}: {description}"
        else:
            message = f"{emoji} {action} {description}"
        
        # Truncate if needed
        if len(message) > 72:
            message = message[:69] + "..."
        
        return message
    
    def _get_action_verb(self, analysis: Dict) -> str:
        """Get appropriate action verb"""
        change_type = analysis['change_type']
        
        verbs = {
            'feature': 'Add',
            'fix': 'Fix',
            'refactor': 'Refactor',
            'docs': 'Update',
            'test': 'Improve',
            'style': 'Style',
            'perf': 'Optimize',
            'security': 'Secure',
            'config': 'Configure',
            'build': 'Build'
        }
        
        return verbs.get(change_type, 'Update')
    
    def _build_description(self, analysis: Dict) -> str:
        """Build description from analysis"""
        files = analysis['files']
        stats = analysis['stats']
        
        if not files:
            return "project files"
        
        # Single file
        if len(files) == 1:
            file_name = Path(files[0]).stem
            return f"{file_name}"
        
        # Multiple files - use scope or count
        if analysis['affected_modules']:
            modules = list(analysis['affected_modules'])[:2]
            if len(modules) == 1:
                return f"{modules[0]} module"
            return f"{', '.join(modules)} modules"
        
        # Fallback to file count
        return f"{len(files)} files"
    
    # ========== LLM Generation ==========
    
    def _generate_with_llm(self, diff_text: str, analysis: Dict) -> str:
        """Generate message using local LLM (Ollama)"""
        if not self._check_ollama_available():
            print("⚠️  Ollama not available, falling back to heuristics")
            return self._generate_with_heuristics(analysis)
        
        # Prepare context
        truncated_diff = diff_text[:self.CONFIG['max_diff_chars']]
        
        prompt = self._build_llm_prompt(truncated_diff, analysis)
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.CONFIG['llm_model']],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0 and result.stdout.strip():
                message = self._clean_llm_output(result.stdout)
                
                # Validate quality
                if len(message) > 10 and len(message) < 100:
                    # Add emoji if missing
                    if not any(emoji in message for emoji in self.EMOJI_MAP.values()):
                        emoji = self.EMOJI_MAP.get(analysis['change_type'], '🚀')
                        message = f"{emoji} {message}"
                    return message
            
        except subprocess.TimeoutExpired:
            print("⚠️  LLM timeout, using heuristics")
        except Exception as e:
            print(f"⚠️  LLM error: {e}")
        
        # Fallback
        return self._generate_with_heuristics(analysis)
    
    def _build_llm_prompt(self, diff_text: str, analysis: Dict) -> str:
        """Build prompt for LLM"""
        prompt = f"""Generate a concise git commit message (max 60 chars) for these changes:

Files changed: {', '.join(analysis['files'][:3])}
Type: {analysis['change_type']}
Stats: +{analysis['stats']['additions']}/-{analysis['stats']['deletions']}

Diff preview:
{diff_text}

Requirements:
- One line only
- Start with action verb (Add, Fix, Update, etc.)
- Be specific but brief
- No quotes or extra formatting

Commit message:"""
        
        return prompt
    
    def _clean_llm_output(self, output: str) -> str:
        """Clean LLM response"""
        # Remove common prefixes
        cleaned = output.strip()
        
        prefixes = ['commit message:', 'message:', '> ', '• ']
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove quotes
        cleaned = cleaned.strip('"\'')
        
        # Take first line
        cleaned = cleaned.split('\n')[0].strip()
        
        return cleaned
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is installed and model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    # ========== Hybrid Strategy ==========
    
    def _generate_hybrid(self, diff_text: str, analysis: Dict) -> str:
        """Hybrid: Use LLM for complex changes, heuristics for simple ones"""
        # Use heuristics for simple changes
        if (analysis['stats']['files_changed'] <= 2 and 
            analysis['stats']['additions'] + analysis['stats']['deletions'] < 50 and
            analysis['confidence'] > 0.7):
            return self._generate_with_heuristics(analysis)
        
        # Try LLM for complex changes
        if self._check_ollama_available():
            llm_message = self._generate_with_llm(diff_text, analysis)
            
            # Validate LLM output
            if self._validate_message(llm_message):
                return llm_message
        
        # Fallback to heuristics
        return self._generate_with_heuristics(analysis)
    
    def _validate_message(self, message: str) -> bool:
        """Validate generated message quality"""
        if not message or len(message) < 10:
            return False
        
        if len(message) > 100:
            return False
        
        # Check for common garbage patterns
        garbage = ['error', 'failed', 'sorry', 'cannot', "don't know"]
        if any(word in message.lower() for word in garbage):
            return False
        
        return True
    
    # ========== History Management ==========
    
    def _load_history(self) -> List[Dict]:
        """Load commit history from file"""
        history_path = self.current_dir / self.HISTORY_FILE
        
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        
        return []
    
    def _save_to_history(self, message: str, analysis: Dict):
        """Save commit to history"""
        entry = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'type': analysis['change_type'],
            'files': analysis['files'],
            'stats': analysis['stats']
        }
        
        self.history.append(entry)
        
        # Keep only recent entries
        self.history = self.history[-self.CONFIG['history_size']:]
        
        # Save to file
        history_path = self.current_dir / self.HISTORY_FILE
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save history: {e}")
    
    def get_history_stats(self) -> Dict:
        """Get statistics from commit history"""
        if not self.history:
            return {}
        
        types = {}
        for entry in self.history:
            change_type = entry.get('type', 'unknown')
            types[change_type] = types.get(change_type, 0) + 1
        
        return {
            'total_commits': len(self.history),
            'change_types': types,
            'most_common': max(types, key=types.get) if types else None
        }


# ========== Integration Function ==========

def generate_smart_commit_message() -> str:
    """
    Main function to generate smart commit message
    Can be called from git_push_ai.py
    """
    generator = SmartCommitGenerator()
    return generator.generate_commit_message()


# ========== Demo & Testing ==========

if __name__ == '__main__':
    print("🧠 Smart Commit Message Generator Demo\n")
    print("="*70)
    
    generator = SmartCommitGenerator()
    
    # Show configuration
    print("\n📋 Current Configuration:")
    for key, value in generator.CONFIG.items():
        print(f"  • {key}: {value}")
    
    # Check Ollama availability
    print("\n🔍 System Check:")
    ollama_available = generator._check_ollama_available()
    print(f"  • Ollama available: {'✅' if ollama_available else '❌'}")
    
    # Show history stats
    stats = generator.get_history_stats()
    if stats:
        print("\n📊 Commit History Stats:")
        print(f"  • Total commits: {stats['total_commits']}")
        print(f"  • Most common type: {stats['most_common']}")
    
    # Generate message for current staged changes
    print("\n🎯 Generating commit message for staged changes...")
    print("="*70)
    
    message = generator.generate_commit_message()
    
    print(f"\n✨ Generated Message:\n")
    print(f"  {message}")
    print("\n" + "="*70)
    
    print("\n💡 Tips:")
    print("  • Install Ollama: curl https://ollama.ai/install.sh | sh")
    print("  • Pull model: ollama pull tinydolphin")
    print("  • Change mode in CONFIG: 'heuristic', 'local_llm', 'hybrid'")