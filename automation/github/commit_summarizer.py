"""
Enhanced Commit Summarizer Module
AI-powered changelog generator with deep diff analysis and Ollama integration
Generates detailed, context-aware changelog entries automatically
"""
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class EnhancedCommitSummarizer:
    """
    Intelligent commit summarizer with Ollama AI integration
    Generates detailed changelog entries with file-level analysis
    """
    
    CONFIG = {
        'use_ollama': True,  # Enable AI-powered summaries
        'ollama_model': 'tinydolphin',  # AI model to use
        'max_diff_lines': 500,  # Limit diff size for AI
        'detailed_line_ranges': True,  # Show affected line numbers
        'track_function_changes': True,  # Track function/class changes
        'max_recent_commits': 10,  # Prevent processing too many commits
        'changelog_file': 'CHANGELOG.md',
        'commit_cache_file': '.commit_cache.json',  # Track processed commits
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.processed_commits = self._load_commit_cache()
        self.ollama_available = self._check_ollama()
    
    # ========== Main Entry Points ==========
    
    def auto_generate_after_push(self, num_commits=1):
        """
        Automatically generate detailed changelog entry after a push
        Called by git_push_ai after successful push
        """
        if not self._is_git_repo():
            return False
        
        print("\n🧠 Generating intelligent changelog entry...")
        
        # Get recent commits that haven't been processed
        commits = self._get_unprocessed_commits(num_commits)
        
        if not commits:
            print("✅ Changelog already up to date")
            return True
        
        # Process each commit
        for commit in commits:
            if commit['hash'] in self.processed_commits:
                continue
            
            print(f"📝 Processing commit {commit['short_hash']}...")
            
            # Get detailed analysis
            analysis = self._analyze_commit_deeply(commit)
            
            # Generate changelog entry
            entry = self._generate_detailed_entry(commit, analysis)
            
            # Save to changelog
            self._append_to_changelog(entry)
            
            # Mark as processed
            self._mark_commit_processed(commit['hash'])
        
        print("✅ Changelog updated with detailed analysis!")
        return True
    
    def generate_commit_message_for_staged_changes(self):
        """
        Generate smart commit message from staged changes
        Used before commit is created
        """
        try:
            diff_output = self._get_staged_diff()
            
            if not diff_output:
                return "📝 Update files"
            
            changed_files = self._get_staged_files()
            analysis = self._analyze_diff(diff_output, changed_files)
            
            # Try AI-powered message first
            if self.ollama_available and self.CONFIG['use_ollama']:
                ai_message = self._generate_ai_commit_message(diff_output, analysis)
                if ai_message:
                    return ai_message
            
            # Fallback to heuristic
            return self._create_commit_message(analysis, changed_files)
        
        except Exception as e:
            print(f"⚠️  Error generating message: {e}")
            return "📝 Update files"
    
    # ========== Deep Commit Analysis ==========
    
    def _analyze_commit_deeply(self, commit: Dict) -> Dict:
        """
        Perform deep analysis of a commit
        Returns detailed breakdown of changes
        """
        commit_hash = commit['hash']
        
        analysis = {
            'files_changed': [],
            'total_stats': {'additions': 0, 'deletions': 0, 'files': 0},
            'file_details': {},
            'functions_changed': [],
            'summary': '',
            'intent': '',
            'breaking_changes': False
        }
        
        # Get diff with full context
        diff = self._get_commit_diff(commit_hash)
        
        if not diff:
            return analysis
        
        # Parse diff for each file
        file_diffs = self._split_diff_by_file(diff)
        
        for file_path, file_diff in file_diffs.items():
            file_analysis = self._analyze_file_diff(file_path, file_diff)
            analysis['file_details'][file_path] = file_analysis
            
            # Aggregate stats
            analysis['total_stats']['additions'] += file_analysis['additions']
            analysis['total_stats']['deletions'] += file_analysis['deletions']
            analysis['total_stats']['files'] += 1
            
            # Track changed functions
            if file_analysis['functions_changed']:
                analysis['functions_changed'].extend([
                    f"{file_path}::{func}" for func in file_analysis['functions_changed']
                ])
        
        # Generate AI-powered summary
        if self.ollama_available and self.CONFIG['use_ollama']:
            analysis['summary'] = self._generate_ai_summary(commit, diff, analysis)
            analysis['intent'] = self._infer_intent_with_ai(commit, diff)
        else:
            analysis['summary'] = self._generate_heuristic_summary(analysis)
            analysis['intent'] = self._infer_intent_heuristic(commit)
        
        # Detect breaking changes
        analysis['breaking_changes'] = self._detect_breaking_changes(diff)
        
        return analysis
    
    def _analyze_file_diff(self, file_path: str, diff: str) -> Dict:
        """
        Analyze changes in a single file
        Returns line ranges, functions changed, and change type
        """
        analysis = {
            'path': file_path,
            'change_type': 'modified',  # 'added', 'deleted', 'modified', 'renamed'
            'additions': 0,
            'deletions': 0,
            'line_ranges': [],
            'functions_changed': [],
            'classes_changed': [],
            'imports_changed': False,
            'significant_changes': []
        }
        
        # Detect change type
        if 'new file mode' in diff:
            analysis['change_type'] = 'added'
        elif 'deleted file mode' in diff:
            analysis['change_type'] = 'deleted'
        elif 'rename from' in diff:
            analysis['change_type'] = 'renamed'
        
        # Track line ranges
        current_range = None
        lines = diff.split('\n')
        
        for i, line in enumerate(lines):
            # Parse hunk headers: @@ -old_start,old_count +new_start,new_count @@
            if line.startswith('@@'):
                match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                if match:
                    old_start, new_start = int(match.group(1)), int(match.group(2))
                    
                    # Find end of this hunk
                    hunk_end = new_start
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith('@@') or lines[j].startswith('diff'):
                            break
                        if lines[j].startswith('+') and not lines[j].startswith('+++'):
                            hunk_end += 1
                    
                    if hunk_end > new_start:
                        analysis['line_ranges'].append((new_start, hunk_end))
            
            # Count changes
            if line.startswith('+') and not line.startswith('+++'):
                analysis['additions'] += 1
                
                # Detect function/class definitions
                if 'def ' in line:
                    func_match = re.search(r'def\s+(\w+)', line)
                    if func_match:
                        analysis['functions_changed'].append(func_match.group(1))
                
                if 'class ' in line:
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        analysis['classes_changed'].append(class_match.group(1))
                
                # Detect import changes
                if line.strip().startswith('import ') or 'from ' in line:
                    analysis['imports_changed'] = True
            
            elif line.startswith('-') and not line.startswith('---'):
                analysis['deletions'] += 1
        
        # Identify significant changes
        if analysis['additions'] + analysis['deletions'] > 50:
            analysis['significant_changes'].append('major_refactor')
        
        if analysis['imports_changed']:
            analysis['significant_changes'].append('dependencies_changed')
        
        if len(analysis['functions_changed']) > 5:
            analysis['significant_changes'].append('multiple_functions')
        
        return analysis
    
    def _split_diff_by_file(self, diff: str) -> Dict[str, str]:
        """Split unified diff into per-file diffs"""
        file_diffs = {}
        current_file = None
        current_diff = []
        
        for line in diff.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file
                if current_file:
                    file_diffs[current_file] = '\n'.join(current_diff)
                
                # Extract new file path
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    current_diff = [line]
            elif current_file:
                current_diff.append(line)
        
        # Save last file
        if current_file:
            file_diffs[current_file] = '\n'.join(current_diff)
        
        return file_diffs
    
    # ========== AI-Powered Analysis ==========
    
    def _generate_ai_summary(self, commit: Dict, diff: str, analysis: Dict) -> str:
        """Generate natural language summary using Ollama"""
        # Prepare context for AI
        file_list = list(analysis['file_details'].keys())
        stats = analysis['total_stats']
        
        # Truncate diff if too long
        truncated_diff = diff[:self.CONFIG['max_diff_lines'] * 80]  # ~80 chars per line
        
        prompt = f"""Analyze this git commit and provide a concise, technical summary (2-3 sentences max).

Commit: {commit['short_hash']} by {commit['author']}
Message: {commit['message']}

Files changed: {', '.join(file_list[:5])}
Stats: +{stats['additions']}/-{stats['deletions']} lines

Diff preview:
{truncated_diff}

Provide a clear summary of WHAT changed and WHY (infer the purpose). Be specific about technical details.
Summary:"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.CONFIG['ollama_model']],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0 and result.stdout.strip():
                summary = result.stdout.strip()
                # Clean up the response
                summary = self._clean_ai_output(summary)
                
                if len(summary) > 20 and len(summary) < 500:
                    return summary
        
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️  AI summary failed: {e}")
        
        # Fallback
        return self._generate_heuristic_summary(analysis)
    
    def _infer_intent_with_ai(self, commit: Dict, diff: str) -> str:
        """Use AI to infer the intent/purpose of changes"""
        prompt = f"""What was the developer's intent for this commit? Answer in 1 short sentence.

Commit message: {commit['message']}

Diff:
{diff[:1000]}

Intent (one sentence):"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.CONFIG['ollama_model']],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                intent = self._clean_ai_output(result.stdout.strip())
                if 10 < len(intent) < 200:
                    return intent
        
        except Exception:
            pass
        
        return self._infer_intent_heuristic(commit)
    
    def _generate_ai_commit_message(self, diff: str, analysis: Dict) -> Optional[str]:
        """Generate commit message using AI"""
        files = ', '.join(analysis.get('files', [])[:3])
        
        prompt = f"""Generate a git commit message (one line, max 60 chars) for these changes:

Files: {files}
Changes: +{analysis.get('additions', 0)}/-{analysis.get('deletions', 0)} lines

Diff:
{diff[:1500]}

Requirements:
- One line only
- Start with emoji and action verb
- Be specific and technical
- Format: [emoji] [verb] [scope]: [what]

Commit message:"""
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.CONFIG['ollama_model']],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                message = self._clean_ai_output(result.stdout.strip())
                if 10 < len(message) < 80:
                    return message
        
        except Exception:
            pass
        
        return None
    
    def _clean_ai_output(self, text: str) -> str:
        """Clean AI response"""
        # Remove common prefixes
        prefixes = ['summary:', 'intent:', 'message:', 'commit:', '> ', '• ', '- ']
        for prefix in prefixes:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove quotes
        text = text.strip('"\'`')
        
        # Take first line if multi-line
        text = text.split('\n')[0].strip()
        
        return text
    
    # ========== Heuristic Analysis (Fallback) ==========
    
    def _generate_heuristic_summary(self, analysis: Dict) -> str:
        """Generate summary using rules (fallback when AI unavailable)"""
        files = list(analysis['file_details'].keys())
        stats = analysis['total_stats']
        
        # Categorize changes
        categories = defaultdict(list)
        for file_path, details in analysis['file_details'].items():
            if details['change_type'] == 'added':
                categories['added'].append(file_path)
            elif details['change_type'] == 'deleted':
                categories['deleted'].append(file_path)
            elif details['significant_changes']:
                categories['major'].append(file_path)
            else:
                categories['modified'].append(file_path)
        
        # Build summary
        parts = []
        
        if categories['added']:
            parts.append(f"Added {len(categories['added'])} new file(s)")
        if categories['deleted']:
            parts.append(f"deleted {len(categories['deleted'])} file(s)")
        if categories['major']:
            parts.append(f"major changes to {', '.join(categories['major'][:2])}")
        if categories['modified']:
            parts.append(f"updated {len(categories['modified'])} file(s)")
        
        summary = '. '.join(parts).capitalize()
        summary += f". Total: +{stats['additions']}/-{stats['deletions']} lines."
        
        return summary
    
    def _infer_intent_heuristic(self, commit: Dict) -> str:
        """Infer intent from commit message (heuristic)"""
        msg = commit['message'].lower()
        
        if any(kw in msg for kw in ['fix', 'bug', 'patch']):
            return "Bug fix or error correction"
        elif any(kw in msg for kw in ['add', 'new', 'feature', 'implement']):
            return "New feature implementation"
        elif any(kw in msg for kw in ['refactor', 'clean', 'improve']):
            return "Code refactoring and improvements"
        elif any(kw in msg for kw in ['update', 'change', 'modify']):
            return "Updates to existing functionality"
        elif any(kw in msg for kw in ['doc', 'readme', 'comment']):
            return "Documentation updates"
        else:
            return "General code changes"
    
    def _detect_breaking_changes(self, diff: str) -> bool:
        """Detect if changes might be breaking"""
        breaking_indicators = [
            r'def\s+\w+.*\).*:',  # Function signature changes
            r'class\s+\w+',  # Class definition changes
            r'raise\s+\w+Error',  # New exceptions
            r'import\s+',  # Import changes
            r'from\s+.+\s+import',
        ]
        
        for pattern in breaking_indicators:
            if re.search(pattern, diff):
                # Check if it's a deletion (more likely breaking)
                lines = diff.split('\n')
                for line in lines:
                    if line.startswith('-') and re.search(pattern, line):
                        return True
        
        return False
    
    # ========== Changelog Generation ==========
    
    def _generate_detailed_entry(self, commit: Dict, analysis: Dict) -> str:
        """
        Generate detailed changelog entry with file-level analysis
        Format matches the requested example
        """
        lines = []
        
        # Header with commit info
        timestamp = datetime.fromisoformat(commit['date'].replace(' +', '+').replace(' -', '-'))
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M')
        
        lines.append(f"### Commit: {commit['short_hash']} ({formatted_time} by {commit['author']})")
        
        # Summary section
        lines.append(f"**Summary:** {commit['message']}")
        
        # AI-generated intent
        if analysis['intent']:
            lines.append(f"**Intent:** {analysis['intent']}")
        
        # Detailed analysis summary
        if analysis['summary']:
            lines.append(f"**Analysis:** {analysis['summary']}")
        
        # Breaking changes warning
        if analysis['breaking_changes']:
            lines.append("**⚠️  WARNING:** Potential breaking changes detected!")
        
        # Detailed file changes
        lines.append("**Details:**")
        
        for file_path, details in analysis['file_details'].items():
            # Format change type
            change_icon = {
                'added': '➕',
                'deleted': '➖',
                'modified': '📝',
                'renamed': '🔄'
            }.get(details['change_type'], '📝')
            
            # Build file description
            file_desc = [f"- {change_icon} `{file_path}`"]
            
            # Add change type if not modified
            if details['change_type'] != 'modified':
                file_desc.append(f"({details['change_type']})")
            
            # Add line ranges if available
            if self.CONFIG['detailed_line_ranges'] and details['line_ranges']:
                ranges = self._format_line_ranges(details['line_ranges'])
                file_desc.append(f"→ Lines {ranges}")
            
            # Add function changes
            if self.CONFIG['track_function_changes']:
                if details['functions_changed']:
                    funcs = ', '.join(details['functions_changed'][:3])
                    if len(details['functions_changed']) > 3:
                        funcs += f" (+{len(details['functions_changed'])-3} more)"
                    file_desc.append(f"→ Functions: {funcs}")
                
                if details['classes_changed']:
                    classes = ', '.join(details['classes_changed'][:2])
                    file_desc.append(f"→ Classes: {classes}")
            
            # Add stats
            file_desc.append(f"(+{details['additions']}/-{details['deletions']})")
            
            lines.append(' '.join(file_desc))
        
        # Overall stats
        stats = analysis['total_stats']
        lines.append(f"\n**Total Changes:** {stats['files']} files, +{stats['additions']}/-{stats['deletions']} lines")
        
        # Separator
        lines.append("\n---\n")
        
        return '\n'.join(lines)
    
    def _format_line_ranges(self, ranges: List[Tuple[int, int]]) -> str:
        """Format line ranges nicely"""
        if not ranges:
            return "N/A"
        
        # Merge overlapping ranges
        merged = []
        for start, end in sorted(ranges):
            if merged and start <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        
        # Format
        formatted = []
        for start, end in merged[:3]:  # Show max 3 ranges
            if end - start <= 1:
                formatted.append(str(start))
            else:
                formatted.append(f"{start}–{end}")
        
        if len(merged) > 3:
            formatted.append("...")
        
        return ', '.join(formatted)
    
    def _append_to_changelog(self, entry: str):
        """Append entry to CHANGELOG.md"""
        changelog_path = self.current_dir / self.CONFIG['changelog_file']
        
        try:
            # Read existing content
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing = f.read()
            else:
                existing = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            
            # Find insertion point (after header, before first entry)
            lines = existing.split('\n')
            insert_index = 0
            
            for i, line in enumerate(lines):
                if line.startswith('###') or line.startswith('##'):
                    insert_index = i
                    break
                elif i > 5:  # After reasonable header size
                    insert_index = i
                    break
            
            # Insert new entry
            if insert_index == 0:
                # No existing entries, append
                new_content = existing.rstrip() + '\n\n' + entry
            else:
                # Insert before first entry
                new_content = '\n'.join(lines[:insert_index]) + '\n\n' + entry + '\n'.join(lines[insert_index:])
            
            # Write back
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Changelog updated: {changelog_path}")
        
        except Exception as e:
            print(f"❌ Failed to update changelog: {e}")
    
    # ========== Commit Tracking ==========
    
    def _load_commit_cache(self) -> set:
        """Load set of already processed commit hashes"""
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed', []))
            except json.JSONDecodeError:
                return set()
        
        return set()
    
    def _mark_commit_processed(self, commit_hash: str):
        """Mark a commit as processed"""
        self.processed_commits.add(commit_hash)
        
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        try:
            data = {
                'processed': list(self.processed_commits),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"⚠️  Could not save commit cache: {e}")
    
    def _get_unprocessed_commits(self, limit: int) -> List[Dict]:
        """Get commits that haven't been processed yet"""
        all_commits = self._get_commit_history(limit)
        
        # Filter out already processed
        unprocessed = [c for c in all_commits if c['hash'] not in self.processed_commits]
        
        return unprocessed
    
    # ========== Git Operations ==========
    
    def _get_commit_history(self, limit: int) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = subprocess.run(
                ['git', 'log', f'-{limit}', '--pretty=format:%H|%an|%ai|%s'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commit_hash, author, date, message = parts
                        commits.append({
                            'hash': commit_hash,
                            'short_hash': commit_hash[:7],
                            'author': author,
                            'date': date,
                            'message': message
                        })
            
            return commits
        
        except subprocess.CalledProcessError:
            return []
    
    def _get_commit_diff(self, commit_hash: str) -> str:
        """Get full diff for a commit"""
        try:
            result = subprocess.run(
                ['git', 'show', commit_hash],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout
        except Exception:
            return ""
    
    def _get_staged_diff(self) -> str:
        """Get diff of staged changes"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def _get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            cwd=self.current_dir
        )
        return result.returncode == 0
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                timeout=3
            )
            available = result.returncode == 0
            
            if available and self.CONFIG['use_ollama']:
                print("✅ Ollama AI available for enhanced summaries")
            elif not available and self.CONFIG['use_ollama']:
                print("ℹ️  Ollama not available, using heuristic analysis")
            
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    # ========== Legacy Methods (for backward compatibility) ==========
    
    def _analyze_diff(self, diff_output: str, changed_files: List[str]) -> Dict:
        """Legacy method for basic diff analysis"""
        analysis = {
            'type': 'update',
            'scope': '',
            'files': changed_files,
            'additions': 0,
            'deletions': 0
        }
        
        for line in diff_output.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                analysis['additions'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                analysis['deletions'] += 1
        
        return analysis
    
    def _create_commit_message(self, analysis: Dict, changed_files: List[str]) -> str:
        """Legacy method for creating commit messages"""
        if not changed_files:
            return "📝 Update files"
        
        if len(changed_files) == 1:
            filename = Path(changed_files[0]).stem
            return f"🚀 Update {filename}"
        
        return f"🚀 Update {len(changed_files)} files"


# Backward compatibility
CommitSummarizer = EnhancedCommitSummarizer


if __name__ == '__main__':
    print("🧠 Enhanced Commit Summarizer Demo\n")
    print("="*70)
    
    summarizer = EnhancedCommitSummarizer()
    
    print("\n📋 Configuration:")
    for key, value in summarizer.CONFIG.items():
        print(f"  • {key}: {value}")
    
    print(f"\n🤖 Ollama Status: {'✅ Available' if summarizer.ollama_available else '❌ Not available'}")
    print(f"📝 Processed Commits: {len(summarizer.processed_commits)}")
    
    print("\n" + "="*70)
    print("\nTest: Generating changelog for recent commit...")
    
    success = summarizer.auto_generate_after_push(num_commits=1)
    
    if success:
        print("\n✅ Demo completed successfully!")
    else:
        print("\n⚠️  No commits to process or not a git repo")