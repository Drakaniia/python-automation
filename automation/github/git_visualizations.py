"""
Git Visualizations Module
Provides visual representations of Git history, branches, and statistics
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess


class GitVisualizations:
    """Generate visual representations of Git data"""
    
    def __init__(self):
        self.repo_path = Path.cwd()
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def show_visualizations_menu(self):
        """Display visualizations menu"""
        print("\n" + "="*70)
        print("📊 GIT VISUALIZATIONS")
        print("="*70 + "\n")
        
        if not self.is_git_repo():
            print("❌ Not a Git repository")
            input("\nPress Enter to continue...")
            return
        
        while True:
            print("\n📈 Available Visualizations:")
            print("  1. Commit Activity Graph")
            print("  2. Branch Tree")
            print("  3. Author Statistics")
            print("  4. File Change Heatmap")
            print("  5. Commit Size Distribution")
            print("  6. Timeline View")
            print("  7. Repository Summary")
            print("  8. Back to menu\n")
            
            choice = input("Your choice: ").strip()
            
            if choice == '1':
                self.show_commit_activity()
            elif choice == '2':
                self.show_branch_tree()
            elif choice == '3':
                self.show_author_stats()
            elif choice == '4':
                self.show_file_heatmap()
            elif choice == '5':
                self.show_commit_sizes()
            elif choice == '6':
                self.show_timeline()
            elif choice == '7':
                self.show_repository_summary()
            elif choice == '8':
                break
            else:
                print("\n❌ Invalid choice")
    
    def show_commit_activity(self):
        """Display commit activity graph"""
        print("\n" + "="*70)
        print("📊 COMMIT ACTIVITY (Last 30 Days)")
        print("="*70 + "\n")
        
        # Get commits from last 30 days
        commits_by_date = self._get_commits_by_date(days=30)
        
        if not commits_by_date:
            print("No commits found in the last 30 days")
            input("\nPress Enter to continue...")
            return
        
        # Find max commits for scaling
        max_commits = max(commits_by_date.values())
        bar_width = 50
        
        # Display graph
        for date, count in sorted(commits_by_date.items()):
            bar_length = int((count / max_commits) * bar_width) if max_commits > 0 else 0
            bar = '█' * bar_length
            print(f"{date} │ {bar} {count}")
        
        # Statistics
        total_commits = sum(commits_by_date.values())
        avg_commits = total_commits / len(commits_by_date) if commits_by_date else 0
        
        print("\n" + "-"*70)
        print(f"Total commits: {total_commits}")
        print(f"Average per day: {avg_commits:.1f}")
        print(f"Most active day: {max(commits_by_date.values())} commits")
        
        input("\nPress Enter to continue...")
    
    def show_branch_tree(self):
        """Display branch structure as tree"""
        print("\n" + "="*70)
        print("🌳 BRANCH TREE")
        print("="*70 + "\n")
        
        try:
            # Get branches
            result = subprocess.run(
                ['git', 'branch', '-a', '-vv'],
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = result.stdout.strip().split('\n')
            
            print("📌 Local Branches:")
            for branch in branches:
                if 'remotes/' not in branch:
                    is_current = branch.startswith('*')
                    branch_clean = branch.strip('* ')
                    
                    if is_current:
                        print(f"  ► {branch_clean} 🎯")
                    else:
                        print(f"  ├─ {branch_clean}")
            
            print("\n🌐 Remote Branches:")
            for branch in branches:
                if 'remotes/' in branch:
                    branch_clean = branch.strip('* ').replace('remotes/', '')
                    print(f"  └─ {branch_clean}")
            
            # Show graph view
            print("\n📊 Branch Graph:")
            result = subprocess.run(
                ['git', 'log', '--graph', '--oneline', '--all', '--decorate', '-15'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_author_stats(self):
        """Display author contribution statistics"""
        print("\n" + "="*70)
        print("👥 AUTHOR STATISTICS")
        print("="*70 + "\n")
        
        # Get author stats
        authors = self._get_author_stats()
        
        if not authors:
            print("No commit data found")
            input("\nPress Enter to continue...")
            return
        
        # Sort by commit count
        sorted_authors = sorted(authors.items(), key=lambda x: x[1]['commits'], reverse=True)
        
        # Display stats
        print(f"{'Author':<30} {'Commits':<10} {'Insertions':<12} {'Deletions':<12}")
        print("-"*70)
        
        for author, stats in sorted_authors:
            author_short = author[:28] + '..' if len(author) > 30 else author
            print(f"{author_short:<30} {stats['commits']:<10} "
                  f"+{stats['insertions']:<11} -{stats['deletions']:<11}")
        
        # Total statistics
        total_commits = sum(s['commits'] for s in authors.values())
        total_insertions = sum(s['insertions'] for s in authors.values())
        total_deletions = sum(s['deletions'] for s in authors.values())
        
        print("-"*70)
        print(f"{'TOTAL':<30} {total_commits:<10} +{total_insertions:<11} -{total_deletions:<11}")
        
        # Contribution percentage
        print("\n📊 Contribution Percentage:")
        for author, stats in sorted_authors[:5]:  # Top 5
            percentage = (stats['commits'] / total_commits * 100) if total_commits > 0 else 0
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = '█' * bar_length
            author_short = author[:20] + '..' if len(author) > 22 else author
            print(f"{author_short:<22} │ {bar} {percentage:.1f}%")
        
        input("\nPress Enter to continue...")
    
    def show_file_heatmap(self):
        """Display file change frequency heatmap"""
        print("\n" + "="*70)
        print("🔥 FILE CHANGE HEATMAP (Top 20)")
        print("="*70 + "\n")
        
        # Get file change counts
        file_changes = self._get_file_changes()
        
        if not file_changes:
            print("No file changes found")
            input("\nPress Enter to continue...")
            return
        
        # Sort by change count
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Find max for scaling
        max_changes = max(file_changes.values())
        bar_width = 40
        
        print(f"{'File':<40} {'Changes':<10} {'Heatmap'}")
        print("-"*70)
        
        for file, count in sorted_files:
            file_short = file[-37:] if len(file) > 40 else file
            bar_length = int((count / max_changes) * bar_width) if max_changes > 0 else 0
            
            # Color intensity based on change count
            if count >= max_changes * 0.7:
                bar = '🔴' * (bar_length // 2)
            elif count >= max_changes * 0.4:
                bar = '🟠' * (bar_length // 2)
            elif count >= max_changes * 0.2:
                bar = '🟡' * (bar_length // 2)
            else:
                bar = '🟢' * (bar_length // 2)
            
            print(f"{file_short:<40} {count:<10} {bar}")
        
        input("\nPress Enter to continue...")
    
    def show_commit_sizes(self):
        """Display commit size distribution"""
        print("\n" + "="*70)
        print("📏 COMMIT SIZE DISTRIBUTION")
        print("="*70 + "\n")
        
        # Get commit sizes
        sizes = self._get_commit_sizes()
        
        if not sizes:
            print("No commit data found")
            input("\nPress Enter to continue...")
            return
        
        # Categorize sizes
        categories = {
            'Tiny (1-10 lines)': 0,
            'Small (11-50 lines)': 0,
            'Medium (51-200 lines)': 0,
            'Large (201-500 lines)': 0,
            'Huge (500+ lines)': 0
        }
        
        for size in sizes:
            total_lines = size['insertions'] + size['deletions']
            if total_lines <= 10:
                categories['Tiny (1-10 lines)'] += 1
            elif total_lines <= 50:
                categories['Small (11-50 lines)'] += 1
            elif total_lines <= 200:
                categories['Medium (51-200 lines)'] += 1
            elif total_lines <= 500:
                categories['Large (201-500 lines)'] += 1
            else:
                categories['Huge (500+ lines)'] += 1
        
        # Display distribution
        total_commits = len(sizes)
        max_count = max(categories.values())
        bar_width = 40
        
        for category, count in categories.items():
            percentage = (count / total_commits * 100) if total_commits > 0 else 0
            bar_length = int((count / max_count) * bar_width) if max_count > 0 else 0
            bar = '█' * bar_length
            
            print(f"{category:<25} │ {bar} {count} ({percentage:.1f}%)")
        
        # Statistics
        avg_insertions = sum(s['insertions'] for s in sizes) / len(sizes) if sizes else 0
        avg_deletions = sum(s['deletions'] for s in sizes) / len(sizes) if sizes else 0
        
        print("\n" + "-"*70)
        print(f"Average insertions per commit: +{avg_insertions:.1f}")
        print(f"Average deletions per commit: -{avg_deletions:.1f}")
        
        input("\nPress Enter to continue...")
    
    def show_timeline(self):
        """Display commit timeline"""
        print("\n" + "="*70)
        print("⏰ COMMIT TIMELINE (Last 20 Commits)")
        print("="*70 + "\n")
        
        try:
            result = subprocess.run(
                ['git', 'log', '-20', '--pretty=format:%h|%an|%ar|%s', '--date=relative'],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = result.stdout.strip().split('\n')
            
            for i, commit in enumerate(commits):
                parts = commit.split('|', 3)
                if len(parts) == 4:
                    hash_short, author, time_ago, message = parts
                    
                    # Tree structure
                    if i == 0:
                        tree = "┌─"
                    elif i == len(commits) - 1:
                        tree = "└─"
                    else:
                        tree = "├─"
                    
                    author_short = author[:15] + '..' if len(author) > 17 else author
                    message_short = message[:40] + '...' if len(message) > 43 else message
                    
                    print(f"{tree} {hash_short} │ {author_short:<17} │ {time_ago:<15} │ {message_short}")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_repository_summary(self):
        """Display comprehensive repository summary"""
        print("\n" + "="*70)
        print("📋 REPOSITORY SUMMARY")
        print("="*70 + "\n")
        
        try:
            # Basic info
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True
            )
            repo_name = Path(result.stdout.strip()).name
            
            # Commit count
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True
            )
            total_commits = int(result.stdout.strip()) if result.stdout.strip() else 0
            
            # Branch count
            result = subprocess.run(
                ['git', 'branch', '-a'],
                capture_output=True,
                text=True
            )
            branches = len([b for b in result.stdout.split('\n') if b.strip()])
            
            # Contributors
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                capture_output=True,
                text=True
            )
            contributors = len([c for c in result.stdout.split('\n') if c.strip()])
            
            # First and last commit
            result = subprocess.run(
                ['git', 'log', '--reverse', '--pretty=format:%ai', '-1'],
                capture_output=True,
                text=True
            )
            first_commit = result.stdout.strip()[:10] if result.stdout else "Unknown"
            
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%ai', '-1'],
                capture_output=True,
                text=True
            )
            last_commit = result.stdout.strip()[:10] if result.stdout else "Unknown"
            
            # Repository size
            result = subprocess.run(
                ['git', 'count-objects', '-vH'],
                capture_output=True,
                text=True
            )
            size_info = result.stdout
            
            # Display summary
            print(f"📦 Repository: {repo_name}")
            print(f"📊 Total Commits: {total_commits}")
            print(f"🌿 Branches: {branches}")
            print(f"👥 Contributors: {contributors}")
            print(f"📅 First Commit: {first_commit}")
            print(f"📅 Last Commit: {last_commit}")
            print(f"\n💾 Repository Size:")
            
            for line in size_info.split('\n'):
                if line.strip():
                    print(f"   {line}")
            
            # Recent activity
            print("\n🔥 Recent Activity (Last 7 Days):")
            recent_commits = self._get_commits_by_date(days=7)
            recent_total = sum(recent_commits.values())
            print(f"   Commits: {recent_total}")
            print(f"   Average per day: {recent_total / 7:.1f}")
            
            # Top contributors
            print("\n🏆 Top 3 Contributors:")
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all', 'HEAD'],
                capture_output=True,
                text=True
            )
            
            lines = [l.strip() for l in result.stdout.split('\n') if l.strip()]
            for i, line in enumerate(lines[:3], 1):
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    count, author = parts
                    print(f"   {i}. {author} ({count} commits)")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    # Helper methods
    
    def _get_commits_by_date(self, days: int = 30) -> Dict[str, int]:
        """Get commit counts grouped by date"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            result = subprocess.run(
                ['git', 'log', '--since', since_date, '--pretty=format:%ai'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout:
                return {}
            
            # Count commits per date
            commits_by_date = defaultdict(int)
            for line in result.stdout.strip().split('\n'):
                if line:
                    date = line[:10]  # YYYY-MM-DD
                    commits_by_date[date] += 1
            
            # Fill in missing dates with 0
            start_date = datetime.now() - timedelta(days=days)
            for i in range(days):
                date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                if date not in commits_by_date:
                    commits_by_date[date] = 0
            
            return dict(commits_by_date)
        
        except subprocess.CalledProcessError:
            return {}
    
    def _get_author_stats(self) -> Dict[str, Dict]:
        """Get statistics per author"""
        try:
            # Get commit counts
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                capture_output=True,
                text=True,
                check=True
            )
            
            authors = {}
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split('\t', 1)
                    if len(parts) == 2:
                        count, author = parts
                        authors[author] = {
                            'commits': int(count),
                            'insertions': 0,
                            'deletions': 0
                        }
            
            # Get insertions/deletions per author
            for author in authors.keys():
                result = subprocess.run(
                    ['git', 'log', '--author', author, '--pretty=tformat:', '--numstat'],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                insertions = int(parts[0]) if parts[0] != '-' else 0
                                deletions = int(parts[1]) if parts[1] != '-' else 0
                                authors[author]['insertions'] += insertions
                                authors[author]['deletions'] += deletions
                            except ValueError:
                                continue
            
            return authors
        
        except subprocess.CalledProcessError:
            return {}
    
    def _get_file_changes(self) -> Dict[str, int]:
        """Get file change frequency"""
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            
            file_changes = defaultdict(int)
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    file_changes[line.strip()] += 1
            
            return dict(file_changes)
        
        except subprocess.CalledProcessError:
            return {}
    
    def _get_commit_sizes(self) -> List[Dict]:
        """Get size of each commit"""
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%H', '--shortstat', '-100'],
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            current_commit = None
            
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith(' '):
                    current_commit = {'hash': line, 'insertions': 0, 'deletions': 0}
                    commits.append(current_commit)
                elif line.strip() and current_commit:
                    # Parse shortstat line
                    if 'insertion' in line:
                        parts = line.split(',')
                        for part in parts:
                            if 'insertion' in part:
                                try:
                                    current_commit['insertions'] = int(part.split()[0])
                                except (ValueError, IndexError):
                                    pass
                            if 'deletion' in part:
                                try:
                                    current_commit['deletions'] = int(part.split()[0])
                                except (ValueError, IndexError):
                                    pass
            
            return commits
        
        except subprocess.CalledProcessError:
            return []