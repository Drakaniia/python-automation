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
    
    def generate_changelog(self, target_dir=None, num_commits=10):
        """
        Generate changelog entry from recent commits
        
        Args:
            target_dir: Path to target directory (default: current directory)
            num_commits: Number of recent commits to analyze
        """
        if target_dir:
            self.current_dir = Path(target_dir)
        else:
            self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("🧾 COMMIT SUMMARIZER - AI-Powered Changelog Generator")
        print("="*70)
        print(f"\n📍 Target Directory: {self.current_dir}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}\n")
        
        # Step 1: Verify git repository
        if not self._is_git_repo():
            print("❌ Not a git repository. Please initialize git first.")
            input("\nPress Enter to continue...")
            return
        
        # Step 2: Get commit history
        print(f"📊 Analyzing last {num_commits} commits...")
        commits = self._get_commit_history(num_commits)
        
        if not commits:
            print("❌ No commits found in this repository.")
            input("\nPress Enter to continue...")
            return
        
        print(f"✅ Found {len(commits)} commits\n")
        
        # Step 3: Analyze commit patterns
        print("🔍 Analyzing commit patterns...")
        analysis = self._analyze_commits(commits)
        
        # Step 4: Generate changelog entry
        print("✍️  Generating changelog entry...\n")
        changelog_entry = self._generate_entry(commits, analysis)
        
        # Step 5: Preview and confirm
        print("="*70)
        print("📄 GENERATED CHANGELOG ENTRY")
        print("="*70)
        print(changelog_entry)
        print("="*70 + "\n")
        
        choice = input("Save this to CHANGELOG.md? (y/n): ").strip().lower()
        
        if choice == 'y':
            self._save_changelog(changelog_entry)
        else:
            print("\n❌ Changelog generation cancelled.")
        
        input("\nPress Enter to continue...")
    
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
        """Get detailed commit history"""
        try:
            # Format: hash|author|date|message
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ai|%s"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.current_dir
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
    
    def _get_commit_stats(self, commit_hash):
        """Get file change statistics for a commit"""
        try:
            result = subprocess.run(
                ["git", "show", "--stat", "--oneline", commit_hash],
                capture_output=True,
                text=True,
                cwd=self.current_dir
            )
            
            # Parse statistics
            stats = {
                'files_changed': 0,
                'insertions': 0,
                'deletions': 0,
                'files': []
            }
            
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip first line (commit message)
                if '|' in line:
                    # File change line
                    parts = line.split('|')
                    if len(parts) >= 2:
                        filename = parts[0].strip()
                        stats['files'].append(filename)
                        stats['files_changed'] += 1
                
                # Summary line: "X files changed, Y insertions(+), Z deletions(-)"
                if 'changed' in line:
                    match = re.search(r'(\d+) insertion', line)
                    if match:
                        stats['insertions'] += int(match.group(1))
                    match = re.search(r'(\d+) deletion', line)
                    if match:
                        stats['deletions'] += int(match.group(1))
            
            return stats
        except Exception:
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
        
        # Keywords for categorization
        feature_keywords = ['add', 'new', 'feature', 'implement', 'create']
        fix_keywords = ['fix', 'bug', 'patch', 'resolve', 'correct']
        refactor_keywords = ['refactor', 'clean', 'improve', 'optimize', 'update']
        doc_keywords = ['doc', 'readme', 'comment', 'documentation']
        
        for commit in commits:
            msg = commit['message'].lower()
            stats = commit['stats']
            
            # Update totals
            analysis['total_insertions'] += stats['insertions']
            analysis['total_deletions'] += stats['deletions']
            analysis['affected_files'].update(stats['files'])
            
            # Categorize commit
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
        # Get version or date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Choose a mood emoji based on changes
        mood = self._determine_mood(analysis)
        
        # Build entry
        lines = []
        lines.append(f"### {today} — {mood}")
        lines.append("")
        
        # Summary line
        total_commits = len(commits)
        files_count = len(analysis['affected_files'])
        net_changes = analysis['total_insertions'] - analysis['total_deletions']
        change_verb = "grew" if net_changes > 0 else "shrank" if net_changes < 0 else "evolved"
        
        lines.append(f"**{total_commits} commits** across **{files_count} files**. "
                    f"The codebase {change_verb} by {abs(net_changes)} lines.")
        lines.append("")
        
        # Features
        if analysis['features']:
            lines.append("#### ✨ New Features")
            for commit in analysis['features'][:5]:  # Limit to 5
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        # Fixes
        if analysis['fixes']:
            lines.append("#### 🐛 Bug Fixes")
            for commit in analysis['fixes'][:5]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        # Refactors
        if analysis['refactors']:
            lines.append("#### 🔧 Refactoring & Improvements")
            for commit in analysis['refactors'][:5]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        # Documentation
        if analysis['docs']:
            lines.append("#### 📚 Documentation")
            for commit in analysis['docs'][:3]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        # Other changes
        if analysis['other']:
            lines.append("#### 🔄 Other Changes")
            for commit in analysis['other'][:3]:
                lines.append(f"- {commit['message']} (`{commit['short_hash']}`)")
            lines.append("")
        
        # Contributors
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
            # Check if CHANGELOG exists
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Prepend new entry after header
                if existing_content.startswith('# '):
                    # Find end of header
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
                
                print(f"\n✅ Changelog entry added to: {changelog_path}")
            else:
                # Create new CHANGELOG
                with open(changelog_path, 'w', encoding='utf-8') as f:
                    f.write("# Changelog\n\n")
                    f.write("All notable changes to this project will be documented in this file.\n\n")
                    f.write(entry)
                
                print(f"\n✅ CHANGELOG.md created at: {changelog_path}")
        except Exception as e:
            print(f"❌ Error saving changelog: {e}")