"""
automation/github/changelog_generator.py
Simple, focused changelog generator without AI dependencies
Generates clean changelog entries from commit history
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class ChangelogGenerator:
    """
    Simple changelog generator focused on clarity and maintainability
    
    Features:
    - Categorizes commits by type (feature, fix, refactor, docs)
    - Groups changes by date
    - Tracks processed commits to avoid duplicates
    - Clean, readable markdown output
    """
    
    CONFIG = {
        'changelog_file': 'CHANGELOG.md',
        'commit_cache_file': '.commit_cache.json',
        'group_by_date': True,  # Group commits by date
        'show_author': True,     # Show commit authors
        'max_message_length': 72,  # Truncate long messages
    }
    
    # Commit type detection patterns
    COMMIT_TYPES = {
        'feature': {
            'keywords': ['add', 'new', 'feature', 'implement', 'create'],
            'emoji': '✨',
            'label': 'New Features'
        },
        'fix': {
            'keywords': ['fix', 'bug', 'patch', 'resolve', 'correct'],
            'emoji': '🐛',
            'label': 'Bug Fixes'
        },
        'refactor': {
            'keywords': ['refactor', 'restructure', 'reorganize', 'clean', 'improve'],
            'emoji': '♻️',
            'label': 'Code Refactoring'
        },
        'docs': {
            'keywords': ['doc', 'readme', 'comment', 'documentation'],
            'emoji': '📚',
            'label': 'Documentation'
        },
        'style': {
            'keywords': ['style', 'format', 'lint'],
            'emoji': '💄',
            'label': 'Style Changes'
        },
        'test': {
            'keywords': ['test', 'spec', 'testing'],
            'emoji': '✅',
            'label': 'Tests'
        },
        'chore': {
            'keywords': ['chore', 'update', 'upgrade', 'dependency'],
            'emoji': '🔧',
            'label': 'Maintenance'
        }
    }
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.processed_commits = self._load_commit_cache()
    
    # ========== Main Entry Points ==========
    
    def generate_changelog(self, num_commits: int = 1) -> bool:
        """
        Generate changelog entries for recent commits
        
        Args:
            num_commits: Number of recent commits to process
        
        Returns:
            True if successful, False otherwise
        """
        if not self._is_git_repo():
            print("❌ Not a git repository")
            return False
        
        print(f"\n📝 Generating changelog for last {num_commits} commit(s)...")
        
        # Get unprocessed commits
        commits = self._get_unprocessed_commits(num_commits)
        
        if not commits:
            print("✅ Changelog already up to date")
            return True
        
        # Group commits by date if configured
        if self.CONFIG['group_by_date']:
            grouped = self._group_commits_by_date(commits)
        else:
            grouped = {'All Changes': commits}
        
        # Generate entries for each group
        for date_label, commit_list in grouped.items():
            entry = self._generate_entry(date_label, commit_list)
            self._append_to_changelog(entry)
            
            # Mark commits as processed
            for commit in commit_list:
                self._mark_commit_processed(commit['hash'])
        
        print(f"✅ Changelog updated with {len(commits)} commit(s)!")
        return True
    
    def show_unprocessed_commits(self, limit: int = 10) -> None:
        """Show commits that haven't been added to changelog yet"""
        print("\n" + "="*70)
        print("📋 UNPROCESSED COMMITS")
        print("="*70 + "\n")
        
        if not self._is_git_repo():
            print("❌ Not a git repository")
            return
        
        commits = self._get_unprocessed_commits(limit)
        
        if not commits:
            print("✅ No unprocessed commits found")
            print("All commits have been added to the changelog.\n")
            return
        
        print(f"Found {len(commits)} unprocessed commit(s):\n")
        
        for i, commit in enumerate(commits, 1):
            commit_type = self._classify_commit(commit['message'])
            emoji = self.COMMIT_TYPES[commit_type]['emoji']
            
            print(f"{i}. {emoji} {commit['short_hash']} - {commit['message'][:60]}")
            print(f"   by {commit['author']} on {commit['date'][:10]}\n")
        
        print("="*70 + "\n")
    
    def reset_processed_commits(self) -> None:
        """Clear the processed commits cache"""
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        if cache_path.exists():
            cache_path.unlink()
            print("✅ Cleared processed commits cache")
        else:
            print("ℹ️  No cache file found")
    
    # ========== Commit Classification ==========
    
    def _classify_commit(self, message: str) -> str:
        """
        Classify commit by analyzing message
        
        Args:
            message: Commit message
        
        Returns:
            Commit type (feature, fix, refactor, etc.)
        """
        message_lower = message.lower()
        
        # Check each type's keywords
        for commit_type, config in self.COMMIT_TYPES.items():
            if any(keyword in message_lower for keyword in config['keywords']):
                return commit_type
        
        # Default to chore if no match
        return 'chore'
    
    def _group_commits_by_date(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Group commits by date"""
        grouped = defaultdict(list)
        
        for commit in commits:
            # Extract date (YYYY-MM-DD)
            date = commit['date'][:10]
            grouped[date].append(commit)
        
        return dict(grouped)
    
    # ========== Changelog Generation ==========
    
    def _generate_entry(self, date_label: str, commits: List[Dict]) -> str:
        """
        Generate changelog entry for a group of commits
        
        Args:
            date_label: Date or group label
            commits: List of commits in this group
        
        Returns:
            Formatted markdown entry
        """
        lines = []
        
        # Header
        lines.append(f"### {date_label}")
        lines.append("")
        
        # Categorize commits
        categorized = defaultdict(list)
        for commit in commits:
            commit_type = self._classify_commit(commit['message'])
            categorized[commit_type].append(commit)
        
        # Generate sections for each category
        for commit_type in ['feature', 'fix', 'refactor', 'docs', 'style', 'test', 'chore']:
            if commit_type not in categorized:
                continue
            
            type_config = self.COMMIT_TYPES[commit_type]
            commits_of_type = categorized[commit_type]
            
            lines.append(f"#### {type_config['emoji']} {type_config['label']}")
            lines.append("")
            
            for commit in commits_of_type:
                message = commit['message']
                
                # Truncate if too long
                if len(message) > self.CONFIG['max_message_length']:
                    message = message[:self.CONFIG['max_message_length']-3] + "..."
                
                # Build commit line
                commit_line = f"- {message} (`{commit['short_hash']}`)"
                
                if self.CONFIG['show_author']:
                    commit_line += f" - {commit['author']}"
                
                lines.append(commit_line)
            
            lines.append("")
        
        # Summary
        lines.append(f"**Total**: {len(commits)} commit(s)")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _append_to_changelog(self, entry: str) -> None:
        """Append entry to CHANGELOG.md"""
        changelog_path = self.current_dir / self.CONFIG['changelog_file']
        
        try:
            # Read existing content
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing = f.read()
            else:
                # Create new changelog with header
                existing = self._create_changelog_header()
            
            # Find insertion point (after header)
            if '---' in existing:
                # Insert after first separator
                parts = existing.split('---', 1)
                new_content = parts[0] + '---\n\n' + entry + parts[1]
            else:
                # No separator, append to end
                new_content = existing.rstrip() + '\n\n' + entry
            
            # Write back
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
        except Exception as e:
            print(f"❌ Failed to update changelog: {e}")
    
    def _create_changelog_header(self) -> str:
        """Create initial changelog header"""
        return """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

"""
    
    # ========== Commit Tracking ==========
    
    def _load_commit_cache(self) -> set:
        """Load set of processed commit hashes"""
        cache_path = self.current_dir / self.CONFIG['commit_cache_file']
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed', []))
            except (json.JSONDecodeError, Exception):
                return set()
        
        return set()
    
    def _mark_commit_processed(self, commit_hash: str) -> None:
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
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            cwd=self.current_dir
        )
        return result.returncode == 0


# ========== CLI Interface ==========

def main():
    """CLI entry point for testing"""
    import sys
    
    gen = ChangelogGenerator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'generate':
            num_commits = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            gen.generate_changelog(num_commits)
        
        elif command == 'show':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            gen.show_unprocessed_commits(limit)
        
        elif command == 'reset':
            gen.reset_processed_commits()
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python changelog_generator.py [generate|show|reset] [number]")
    
    else:
        print("Changelog Generator")
        print("==================")
        print("\nCommands:")
        print("  generate [N]  - Generate changelog for last N commits (default: 1)")
        print("  show [N]      - Show unprocessed commits (default: 10)")
        print("  reset         - Clear processed commits cache")
        print("\nExample:")
        print("  python changelog_generator.py generate 5")


if __name__ == '__main__':
    main()