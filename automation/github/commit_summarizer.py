"""
Commit Summarizer Module
AI-powered changelog generator from git commits
Transforms commit diffs into elegant, human-readable changelog entries
"""
import subprocess
from pathlib import Path
from datetime import datetime
import re


class CommitSummarizer:
    """Generates changelog entries from git commit history"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
    
    def auto_generate_after_push(self, num_commits=1):
        """
        Automatically generate changelog entry after a push
        This is called internally by git push operations
        
        Args:
            num_commits: Number of recent commits to summarize (default: 1 for last commit)
        """
        if not self._is_git_repo():
            return False
        
        print("\n🧠 Generating automatic changelog entry...")
        
        # Get recent commits
        commits = self._get_commit_history(num_commits)
        
        if not commits:
            print("⚠️  No commits found to summarize")
            return False
        
        # Analyze commit patterns
        analysis = self._analyze_commits(commits)
        
        # Generate changelog entry
        changelog_entry = self._generate_entry(commits, analysis)
        
        # Save to changelog
        self._save_changelog(changelog_entry)
        
        print("✅ Changelog automatically updated!")
        return True
    
    def generate_commit_message_for_staged_changes(self):
        """
        Generate a smart commit message from currently staged changes
        Returns a formatted commit message string
        """
        try:
            # Get staged diff
            diff_output = self._get_staged_diff()
            
            if not diff_output:
                return "📝 Update files"
            
            # Get list of changed files
            changed_files = self._get_staged_files()
            
            # Analyze the changes
            analysis = self._analyze_diff(diff_output, changed_files)
            
            # Generate commit message
            message = self._create_commit_message(analysis, changed_files)
            
            return message
        except Exception as e:
            print(f"Debug: Error in generate_commit_message_for_staged_changes: {e}")
            return "📝 Update files"
    
    # ========== AI COMMIT MESSAGE GENERATION ==========
    
    def _get_staged_diff(self):
        """Get diff of staged changes with proper encoding handling"""
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
        except subprocess.CalledProcessError:
            return ""
        except Exception:
            return ""
    
    def _get_staged_files(self):
        """Get list of staged files with proper encoding handling"""
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
        except subprocess.CalledProcessError:
            return []
        except Exception:
            return []
    
    def _analyze_diff(self, diff_output, changed_files):
        """Analyze diff to determine what kind of changes were made"""
        analysis = {
            'type': 'update',
            'scope': '',
            'is_new_file': False,
            'is_deletion': False,
            'is_ai_feature': False,
            'is_fix': False,
            'is_refactor': False,
            'line_changes': {'additions': 0, 'deletions': 0}
        }
        
        # Count line changes
        for line in diff_output.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                analysis['line_changes']['additions'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                analysis['line_changes']['deletions'] += 1
        
        # Determine scope from file paths
        if changed_files:
            first_file = changed_files[0]
            if 'ai_features' in first_file or 'ai' in first_file.lower():
                analysis['is_ai_feature'] = True
                analysis['scope'] = 'AI'
            elif 'github' in first_file or 'git' in first_file:
                analysis['scope'] = 'Git'
            elif 'menu' in first_file:
                analysis['scope'] = 'UI'
            elif 'test' in first_file.lower():
                analysis['scope'] = 'Tests'
            elif any(ext in first_file for ext in ['.md', 'README', 'CHANGELOG']):
                analysis['scope'] = 'Docs'
        
        # Check for new files
        if 'new file mode' in diff_output:
            analysis['is_new_file'] = True
            analysis['type'] = 'add'
        
        # Check for deletions
        if 'deleted file mode' in diff_output:
            analysis['is_deletion'] = True
            analysis['type'] = 'remove'
        
        # Check for fix patterns
        fix_keywords = ['fix', 'bug', 'error', 'issue', 'patch', 'correct']
        if any(kw in diff_output.lower() for kw in fix_keywords):
            analysis['is_fix'] = True
            analysis['type'] = 'fix'
        
        # Check for refactor patterns
        refactor_keywords = ['refactor', 'clean', 'reorganize', 'restructure']
        if any(kw in diff_output.lower() for kw in refactor_keywords):
            analysis['is_refactor'] = True
            analysis['type'] = 'refactor'
        
        return analysis
    
    def _create_commit_message(self, analysis, changed_files):
        """Create a formatted commit message based on analysis"""
        # Select emoji based on change type
        emoji = self._select_emoji(analysis)
        
        # Determine action verb
        if analysis['is_new_file']:
            action = "Add"
        elif analysis['is_deletion']:
            action = "Remove"
        elif analysis['is_fix']:
            action = "Fix"
        elif analysis['is_refactor']:
            action = "Refactor"
        else:
            action = "Update"
        
        # Create description based on files
        description = self._create_description(changed_files, analysis)
        
        # Add scope if available
        if analysis['scope']:
            message = f"{emoji} {action} {analysis['scope']}: {description}"
        else:
            message = f"{emoji} {action} {description}"
        
        # Limit message length
        if len(message) > 72:
            message = message[:69] + "..."
        
        return message
    
    def _select_emoji(self, analysis):
        """Select appropriate emoji based on change type"""
        if analysis['is_ai_feature']:
            return "🤖"
        elif analysis['is_new_file']:
            return "✨"
        elif analysis['is_fix']:
            return "🐛"
        elif analysis['is_refactor']:
            return "♻️"
        elif analysis['scope'] == 'Docs':
            return "📚"
        elif analysis['scope'] == 'Tests':
            return "✅"
        elif analysis['scope'] == 'UI':
            return "🎨"
        elif analysis['scope'] == 'Git':
            return "🔧"
        else:
            return "🚀"
    
    def _create_description(self, changed_files, analysis):
        """Create a concise description of changes"""
        if not changed_files:
            return "project files"
        
        # If single file, use its name
        if len(changed_files) == 1:
            filename = Path(changed_files[0]).stem
            return f"{filename} module"
        
        # Multiple files - categorize
        file_types = set()
        for f in changed_files:
            if '.py' in f:
                file_types.add('Python modules')
            elif '.md' in f:
                file_types.add('documentation')
            elif '.json' in f or '.yaml' in f:
                file_types.add('configuration')
            else:
                file_types.add('project files')
        
        if len(file_types) == 1:
            return list(file_types)[0]
        else:
            return f"{len(changed_files)} files"
    
    # ========== CHANGELOG GENERATION ==========
    
    def _is_git_repo(self):
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=self.current_dir
        )
        return result.returncode == 0
    
    def _get_commit_history(self, limit):
        """Get detailed commit history with proper encoding support"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ai|%s"],
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
                        
                        # Get diff stats for this commit
                        stats = self._get_commit_stats(commit_hash)
                        
                        commits.append({
                            'hash': commit_hash,
                            'short_hash': commit_hash[:7],
                            'author': author,
                            'date': date,
                            'message': message,
                            'stats': stats
                        })
            
            return commits
        except subprocess.CalledProcessError:
            return []
        except Exception as e:
            print(f"Debug: Error getting commit history: {e}")
            return []
    
    def _get_commit_stats(self, commit_hash):
        """Get file change statistics for a commit with proper encoding support"""
        try:
            result = subprocess.run(
                ["git", "show", "--stat", "--oneline", commit_hash],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            stats = {
                'files_changed': 0,
                'insertions': 0,
                'deletions': 0,
                'files': []
            }
            
            if not result.stdout:
                return stats
            
            lines = result.stdout.split('\n')
            for line in lines[1:]:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        filename = parts[0].strip()
                        stats['files'].append(filename)
                        stats['files_changed'] += 1
                
                if 'changed' in line:
                    match = re.search(r'(\d+) insertion', line)
                    if match:
                        stats['insertions'] += int(match.group(1))
                    match = re.search(r'(\d+) deletion', line)
                    if match:
                        stats['deletions'] += int(match.group(1))
            
            return stats
        except Exception as e:
            print(f"Debug: Error getting commit stats: {e}")
            return {'files_changed': 0, 'insertions': 0, 'deletions': 0, 'files': []}
    
    def _analyze_commits(self, commits):
        """Analyze commit patterns and categorize changes"""
        analysis = {
            'features': [],
            'fixes': [],
            'refactors': [],
            'docs': [],
            'other': [],
            'total_insertions': 0,
            'total_deletions': 0,
            'affected_files': set()
        }
        
        feature_keywords = ['add', 'new', 'feature', 'implement', 'create']
        fix_keywords = ['fix', 'bug', 'patch', 'resolve', 'correct']
        refactor_keywords = ['refactor', 'clean', 'improve', 'optimize', 'update']
        doc_keywords = ['doc', 'readme', 'comment', 'documentation']
        
        for commit in commits:
            msg = commit['message'].lower()
            stats = commit['stats']
            
            analysis['total_insertions'] += stats['insertions']
            analysis['total_deletions'] += stats['deletions']
            analysis['affected_files'].update(stats['files'])
            
            categorized = False
            
            if any(kw in msg for kw in feature_keywords):
                analysis['features'].append(commit)
                categorized = True
            elif any(kw in msg for kw in fix_keywords):
                analysis['fixes'].append(commit)
                categorized = True
            elif any(kw in msg for kw in refactor_keywords):
                analysis['refactors'].append(commit)
                categorized = True
            elif any(kw in msg for kw in doc_keywords):
                analysis['docs'].append(commit)
                categorized = True
            
            if not categorized:
                analysis['other'].append(commit)
        
        return analysis
    
    def _generate_entry(self, commits, analysis):
        """Generate formatted changelog entry"""
        today = datetime.now().strftime('%Y-%m-%d')
        mood = self._determine_mood(analysis)
        
        lines = []
        lines.append(f"### {today} — {mood}")
        lines.append("")
        
        total_commits = len(commits)
        files_count = len(analysis['affected_files'])
        net_changes = analysis['total_insertions'] - analysis['total_deletions']
        change_verb = "grew" if net_changes > 0 else "shrank" if net_changes < 0 else "evolved"
        
        lines.append(f"**{total_commits} commits** across **{files_count} files**. "
                    f"The codebase {change_verb} by {abs(net_changes)} lines.")
        lines.append("")
        
        if analysis['features']:
            lines.append("#### ✨ New Features")
            for commit in analysis['features'][:5]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        if analysis['fixes']:
            lines.append("#### 🐛 Bug Fixes")
            for commit in analysis['fixes'][:5]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        if analysis['refactors']:
            lines.append("#### 🔧 Refactoring & Improvements")
            for commit in analysis['refactors'][:5]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        if analysis['docs']:
            lines.append("#### 📚 Documentation")
            for commit in analysis['docs'][:3]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        if analysis['other']:
            lines.append("#### 🔄 Other Changes")
            for commit in analysis['other'][:3]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        authors = set(c['author'] for c in commits)
        if len(authors) > 1:
            lines.append(f"**Contributors:** {', '.join(sorted(authors))}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _determine_mood(self, analysis):
        """Determine mood emoji based on change analysis"""
        features = len(analysis['features'])
        fixes = len(analysis['fixes'])
        refactors = len(analysis['refactors'])
        
        if features > fixes and features > refactors:
            return "🚀 Feature Blast"
        elif fixes > features:
            return "🔧 Bug Squashing Session"
        elif refactors > features and refactors > fixes:
            return "♻️ Cleanup Spree"
        elif analysis['total_insertions'] > analysis['total_deletions'] * 2:
            return "📈 Growth Spurt"
        elif analysis['total_deletions'] > analysis['total_insertions'] * 2:
            return "🧹 Spring Cleaning"
        else:
            return "⚡ Steady Progress"
    
    def _save_changelog(self, entry):
        """Save or append to CHANGELOG.md"""
        changelog_path = self.current_dir / "CHANGELOG.md"
        
        try:
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                if existing_content.startswith('# '):
                    lines = existing_content.split('\n')
                    header_end = 0
                    for i, line in enumerate(lines):
                        if line.startswith('# '):
                            header_end = i + 1
                            break
                    
                    new_content = '\n'.join(lines[:header_end + 1]) + '\n\n' + entry + '\n\n' + '\n'.join(lines[header_end + 1:])
                else:
                    new_content = entry + '\n\n' + existing_content
                
                with open(changelog_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Changelog entry added to: {changelog_path}")
            else:
                with open(changelog_path, 'w', encoding='utf-8') as f:
                    f.write("# Changelog\n\n")
                    f.write("All notable changes to this project will be documented in this file.\n\n")
                    f.write(entry)
                
                print(f"✅ CHANGELOG.md created at: {changelog_path}")
        except Exception as e:
            print(f"❌ Error saving changelog: {e}")