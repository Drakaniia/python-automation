"""
automation/github/git_visualizations.py
Modern Interactive CLI Dashboard for Repository Health Metrics
"""
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import sys
import os

# Try to import rich for enhanced visuals
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.text import Text
    from rich.live import Live
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️  Install 'rich' for enhanced dashboard: pip install rich")

# Try to import psutil for system stats
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class DashboardCache:
    """Cache for expensive operations"""
    def __init__(self):
        self.data = {}
        self.timestamps = {}
        self.ttl = 60  # Cache TTL in seconds
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value if not expired"""
        if key in self.data:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.data[key]
        return None
    
    def set(self, key: str, value: any):
        """Cache a value"""
        self.data[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache"""
        self.data.clear()
        self.timestamps.clear()


class GitDashboard:
    """
    Modern Interactive CLI Dashboard for Git Repository Health
    Features: Real-time metrics, commit activity, coverage, security integration
    """
    
    # ASCII Logo
    LOGO = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🚀 PYTHON AUTOMATION SYSTEM - REPOSITORY DASHBOARD 🚀       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    
    def __init__(self):
        self.repo_path = Path.cwd()
        self.cache = DashboardCache()
        self.console = Console() if HAS_RICH else None
        self.last_refresh = None
        
    # ========== MAIN DASHBOARD ==========
    
    def show_dashboard(self, interactive: bool = True):
        """Display main dashboard with all metrics"""
        if not self.is_git_repo():
            self._print_error("Not a Git repository")
            return
        
        if HAS_RICH:
            self._show_rich_dashboard(interactive)
        else:
            self._show_basic_dashboard()
    
    def _show_rich_dashboard(self, interactive: bool):
        """Rich-enhanced dashboard with live updates"""
        if interactive:
            self._interactive_dashboard()
        else:
            self._static_rich_dashboard()
    
    def _interactive_dashboard(self):
        """Interactive dashboard with keyboard controls"""
        self.console.clear()
        
        while True:
            # Render dashboard
            layout = self._create_dashboard_layout()
            
            # Display
            self.console.clear()
            self.console.print(layout)
            
            # Show controls
            self._show_controls()
            
            # Get user input (non-blocking)
            self.console.print("\n[dim]Press key or wait...[/dim]", end="")
            
            try:
                # Use getch for instant response
                key = self._getch_with_timeout(5.0)
                
                if key:
                    key = key.lower()
                    
                    if key == 'q':
                        self._exit_dashboard()
                        break
                    elif key == 'r':
                        self.cache.clear()
                        continue
                    elif key == 'l':
                        self._show_detailed_logs()
                    elif key == 's':
                        self._run_security_scan()
                    elif key == 'e':
                        self._export_report()
                    elif key == 'h':
                        self._show_help()
                
                # Auto-refresh after 5 seconds
                self.cache.clear()
                
            except KeyboardInterrupt:
                self._exit_dashboard()
                break
    
    def _static_rich_dashboard(self):
        """Static dashboard (one-time render)"""
        layout = self._create_dashboard_layout()
        self.console.print(layout)
    
    def _create_dashboard_layout(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header: Logo and refresh time
        layout["header"].update(self._render_header())
        
        # Body: Split into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left column: Overview, Activity, Stats
        layout["left"].split_column(
            Layout(name="overview", size=8),
            Layout(name="activity", size=15),
            Layout(name="stats", size=12)
        )
        
        # Right column: Coverage, Security, Automation
        layout["right"].split_column(
            Layout(name="coverage", size=10),
            Layout(name="security", size=10),
            Layout(name="automation", size=15)
        )
        
        # Populate sections
        layout["overview"].update(self._render_overview())
        layout["activity"].update(self._render_commit_activity())
        layout["stats"].update(self._render_repo_stats())
        layout["coverage"].update(self._render_coverage())
        layout["security"].update(self._render_security())
        layout["automation"].update(self._render_automation_health())
        layout["footer"].update(self._render_footer())
        
        return layout
    
    # ========== HEADER & FOOTER ==========
    
    def _render_header(self) -> Panel:
        """Render dashboard header"""
        refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header_text = Text()
        header_text.append("🚀 PYTHON AUTOMATION SYSTEM ", style="bold cyan")
        header_text.append("• ", style="dim")
        header_text.append("Repository Dashboard", style="bold white")
        header_text.append(f"\n Last refresh: {refresh_time}", style="dim italic")
        
        return Panel(
            header_text,
            border_style="cyan",
            box=box.DOUBLE
        )
    
    def _render_footer(self) -> Panel:
        """Render dashboard footer with system stats"""
        footer_text = Text()
        
        # System stats (if available)
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            
            footer_text.append(f"💻 CPU: {cpu:.1f}%  ", style="cyan")
            footer_text.append(f"🧠 Memory: {memory:.1f}%  ", style="magenta")
        
        # Repository path
        footer_text.append(f"📁 {self.repo_path}", style="dim")
        
        return Panel(
            footer_text,
            border_style="blue",
            box=box.ROUNDED
        )
    
    def _show_controls(self):
        """Show keyboard controls"""
        controls = (
            "[cyan]R[/cyan]=Refresh  "
            "[green]L[/green]=Logs  "
            "[yellow]S[/yellow]=Security  "
            "[magenta]E[/magenta]=Export  "
            "[blue]H[/blue]=Help  "
            "[red]Q[/red]=Quit"
        )
        self.console.print(f"\n{controls}")
    
    # ========== OVERVIEW SECTION ==========
    
    def _render_overview(self) -> Panel:
        """Render repository overview"""
        # Get cached or fetch data
        cached = self.cache.get('overview')
        if cached:
            return cached
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Label", style="cyan bold")
        table.add_column("Value", style="white")
        
        try:
            # Repository name
            repo_name = self.repo_path.name
            table.add_row("📦 Repository", repo_name)
            
            # Current branch
            branch = self._get_current_branch()
            table.add_row("🌿 Branch", branch)
            
            # Total commits
            total_commits = self._get_total_commits()
            table.add_row("📝 Total Commits", str(total_commits))
            
            # Last commit
            last_commit = self._get_last_commit()
            if last_commit:
                table.add_row("👤 Last Author", last_commit['author'])
                table.add_row("🕐 Last Commit", last_commit['date'])
            
            # Health status
            health = self._calculate_health_status()
            table.add_row("💚 Health", health)
            
            # Contributors
            contributors = self._get_contributor_count()
            table.add_row("👥 Contributors", str(contributors))
            
        except Exception as e:
            table.add_row("⚠️  Error", str(e))
        
        panel = Panel(
            table,
            title="[bold cyan]📊 Repository Overview[/bold cyan]",
            border_style="cyan"
        )
        
        self.cache.set('overview', panel)
        return panel
    
    def _calculate_health_status(self) -> str:
        """Calculate repository health indicator"""
        score = 0
        max_score = 5
        
        # Check 1: Clean working directory
        if not self._has_uncommitted_changes():
            score += 1
        
        # Check 2: Recent activity (commits in last 7 days)
        recent_commits = self._get_commits_in_days(7)
        if len(recent_commits) > 0:
            score += 1
        
        # Check 3: Has remote configured
        if self._has_remote():
            score += 1
        
        # Check 4: Coverage > 70% (if available)
        coverage = self._get_coverage_percentage()
        if coverage and coverage > 70:
            score += 1
        
        # Check 5: No security issues
        security_score = self._get_security_score()
        if security_score and security_score > 80:
            score += 1
        
        # Generate health indicator
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            return "🟢 Excellent"
        elif percentage >= 60:
            return "🟡 Good"
        elif percentage >= 40:
            return "🟠 Fair"
        else:
            return "🔴 Needs Attention"
    
    # ========== COMMIT ACTIVITY ==========
    
    def _render_commit_activity(self) -> Panel:
        """Render commit activity heatmap"""
        cached = self.cache.get('activity')
        if cached:
            return cached
        
        table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
        table.add_column("Date", style="cyan")
        table.add_column("Commits", justify="right", style="yellow")
        table.add_column("Activity", style="green")
        
        try:
            # Get last 30 days
            commits_by_date = self._get_commits_by_date(days=30)
            
            if not commits_by_date:
                table.add_row("No data", "0", "")
            else:
                max_commits = max(commits_by_date.values())
                
                # Show last 14 days for cleaner display
                dates = sorted(commits_by_date.keys())[-14:]
                
                for date in dates:
                    count = commits_by_date[date]
                    
                    # Create activity bar
                    bar_length = int((count / max_commits) * 20) if max_commits > 0 else 0
                    bar = "█" * bar_length
                    
                    # Color based on activity
                    if count == 0:
                        bar_style = "dim"
                    elif count >= max_commits * 0.7:
                        bar_style = "bright_green"
                    elif count >= max_commits * 0.4:
                        bar_style = "green"
                    else:
                        bar_style = "yellow"
                    
                    table.add_row(
                        date,
                        str(count),
                        Text(bar, style=bar_style)
                    )
        
        except Exception as e:
            table.add_row("⚠️  Error", str(e), "")
        
        panel = Panel(
            table,
            title="[bold green]📈 Commit Activity (Last 14 Days)[/bold green]",
            border_style="green"
        )
        
        self.cache.set('activity', panel)
        return panel
    
    # ========== REPOSITORY STATS ==========
    
    def _render_repo_stats(self) -> Panel:
        """Render codebase statistics"""
        cached = self.cache.get('stats')
        if cached:
            return cached
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="magenta bold")
        table.add_column("Value", style="white")
        
        try:
            # Count lines of code
            loc_data = self._count_lines_of_code()
            table.add_row("📝 Lines of Code", f"{loc_data['total']:,}")
            
            # File counts
            table.add_row("📄 Total Files", str(loc_data['files']))
            table.add_row("🐍 Python Files", str(loc_data['python_files']))
            
            # Top 3 largest files
            largest = self._get_largest_files(3)
            if largest:
                table.add_row("", "")  # Separator
                table.add_row("[bold]🔝 Largest Modules[/bold]", "")
                for i, (file, size) in enumerate(largest, 1):
                    table.add_row(f"  {i}. {file[:30]}", f"{size:,} lines")
            
            # Code ratio
            if loc_data['python_lines'] > 0:
                ratio = (loc_data['python_lines'] / loc_data['total']) * 100
                table.add_row("", "")
                table.add_row("🐍 Python Ratio", f"{ratio:.1f}%")
        
        except Exception as e:
            table.add_row("⚠️  Error", str(e))
        
        panel = Panel(
            table,
            title="[bold magenta]📊 Codebase Statistics[/bold magenta]",
            border_style="magenta"
        )
        
        self.cache.set('stats', panel)
        return panel
    
    # ========== COVERAGE ==========
    
    def _render_coverage(self) -> Panel:
        """Render test coverage summary"""
        cached = self.cache.get('coverage')
        if cached:
            return cached
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="blue bold")
        table.add_column("Value")
        
        try:
            coverage_pct = self._get_coverage_percentage()
            
            if coverage_pct is not None:
                # Coverage percentage
                table.add_row("📊 Coverage", f"{coverage_pct:.1f}%")
                
                # Visual bar
                bar_length = int(coverage_pct / 5)  # Scale to 20 chars
                bar_filled = "█" * bar_length
                bar_empty = "░" * (20 - bar_length)
                
                # Color based on coverage
                if coverage_pct >= 80:
                    bar_style = "bright_green"
                    status = "🟢 Excellent"
                elif coverage_pct >= 60:
                    bar_style = "green"
                    status = "🟡 Good"
                elif coverage_pct >= 40:
                    bar_style = "yellow"
                    status = "🟠 Fair"
                else:
                    bar_style = "red"
                    status = "🔴 Poor"
                
                bar_text = Text(bar_filled, style=bar_style)
                bar_text.append(bar_empty, style="dim")
                
                table.add_row("Progress", bar_text)
                table.add_row("Status", status)
                
                # Additional stats
                coverage_data = self._parse_coverage_data()
                if coverage_data:
                    table.add_row("", "")
                    table.add_row("Files Tested", str(coverage_data.get('files', 'N/A')))
                    table.add_row("Statements", str(coverage_data.get('statements', 'N/A')))
            else:
                table.add_row("⚠️  No coverage data", "Run tests first")
        
        except Exception as e:
            table.add_row("⚠️  Error", str(e))
        
        panel = Panel(
            table,
            title="[bold blue]🧪 Test Coverage[/bold blue]",
            border_style="blue"
        )
        
        self.cache.set('coverage', panel)
        return panel
    
    # ========== SECURITY ==========
    
    def _render_security(self) -> Panel:
        """Render security metrics"""
        cached = self.cache.get('security')
        if cached:
            return cached
        
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="red bold")
        table.add_column("Value")
        
        try:
            security_score = self._get_security_score()
            
            if security_score is not None:
                table.add_row("🔒 Security Score", f"{security_score}/100")
                
                # Status indicator
                if security_score >= 90:
                    status = "🟢 Secure"
                    style = "bright_green"
                elif security_score >= 70:
                    status = "🟡 Moderate"
                    style = "yellow"
                else:
                    status = "🔴 At Risk"
                    style = "red"
                
                table.add_row("Status", Text(status, style=style))
                
                # Last scan
                last_scan = self._get_last_security_scan()
                if last_scan:
                    table.add_row("Last Scan", last_scan)
            else:
                table.add_row("ℹ️  Security", "Not configured")
                table.add_row("Action", "Press 'S' to scan")
        
        except Exception as e:
            table.add_row("⚠️  Error", str(e))
        
        panel = Panel(
            table,
            title="[bold red]🔐 Security Status[/bold red]",
            border_style="red"
        )
        
        self.cache.set('security', panel)
        return panel
    
    # ========== AUTOMATION HEALTH ==========
    
    def _render_automation_health(self) -> Panel:
        """Render automation task health"""
        cached = self.cache.get('automation')
        if cached:
            return cached
        
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("Task", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Last Run", style="dim")
        
        try:
            # Get recent automation tasks
            tasks = self._get_recent_tasks()
            
            if tasks:
                for task in tasks:
                    status = "✅" if task['success'] else "❌"
                    table.add_row(
                        task['name'],
                        status,
                        task['timestamp']
                    )
            else:
                table.add_row("No recent tasks", "—", "—")
        
        except Exception as e:
            table.add_row("⚠️  Error", str(e), "—")
        
        panel = Panel(
            table,
            title="[bold yellow]⚙️  Automation Health[/bold yellow]",
            border_style="yellow"
        )
        
        self.cache.set('automation', panel)
        return panel
    
    # ========== BASIC DASHBOARD (Fallback) ==========
    
    def _show_basic_dashboard(self):
        """Basic dashboard without rich library"""
        print("\n" + "="*70)
        print(self.LOGO)
        print("="*70 + "\n")
        
        print("📊 REPOSITORY OVERVIEW")
        print("-" * 70)
        print(f"Repository: {self.repo_path.name}")
        print(f"Branch: {self._get_current_branch()}")
        print(f"Total Commits: {self._get_total_commits()}")
        print(f"Health: {self._calculate_health_status()}")
        print()
        
        print("📈 COMMIT ACTIVITY (Last 7 Days)")
        print("-" * 70)
        commits_by_date = self._get_commits_by_date(days=7)
        for date, count in sorted(commits_by_date.items()):
            bar = "█" * count
            print(f"{date} │ {bar} {count}")
        print()
        
        print("📊 CODEBASE STATS")
        print("-" * 70)
        loc_data = self._count_lines_of_code()
        print(f"Lines of Code: {loc_data['total']:,}")
        print(f"Python Files: {loc_data['python_files']}")
        print()
        
        print("🧪 TEST COVERAGE")
        print("-" * 70)
        coverage = self._get_coverage_percentage()
        if coverage:
            bar_length = int(coverage / 5)
            bar = "#" * bar_length + "-" * (20 - bar_length)
            print(f"[{bar}] {coverage:.1f}%")
        else:
            print("No coverage data available")
        print()
        
        print("="*70)
        input("\nPress Enter to continue...")
    
    # ========== HELPER METHODS ==========
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a Git repository"""
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def _get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip() or "Unknown"
        except:
            return "Unknown"
    
    def _get_total_commits(self) -> int:
        """Get total commit count"""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except:
            return 0
    
    def _get_last_commit(self) -> Optional[Dict]:
        """Get last commit info"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%an|%ar'],
                capture_output=True,
                text=True,
                check=True
            )
            parts = result.stdout.strip().split('|')
            if len(parts) == 2:
                return {'author': parts[0], 'date': parts[1]}
        except:
            pass
        return None
    
    def _has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def _has_remote(self) -> bool:
        """Check if remote is configured"""
        try:
            result = subprocess.run(
                ['git', 'remote'],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False
    
    def _get_contributor_count(self) -> int:
        """Get number of contributors"""
        try:
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                capture_output=True,
                text=True
            )
            return len([l for l in result.stdout.split('\n') if l.strip()])
        except:
            return 0
    
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
            
            commits_by_date = defaultdict(int)
            for line in result.stdout.strip().split('\n'):
                if line:
                    date = line[:10]
                    commits_by_date[date] += 1
            
            # Fill missing dates
            start_date = datetime.now() - timedelta(days=days)
            for i in range(days):
                date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                if date not in commits_by_date:
                    commits_by_date[date] = 0
            
            return dict(commits_by_date)
        except:
            return {}
    
    def _get_commits_in_days(self, days: int) -> List[str]:
        """Get commits in last N days"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'log', '--since', since_date, '--oneline'],
                capture_output=True,
                text=True
            )
            return [l for l in result.stdout.split('\n') if l.strip()]
        except:
            return []
    
    def _count_lines_of_code(self) -> Dict:
        """Count lines of code"""
        total_lines = 0
        python_lines = 0
        total_files = 0
        python_files = 0
        
        try:
            for file in self.repo_path.rglob('*'):
                if file.is_file() and not self._should_exclude_file(file):
                    try:
                        lines = len(file.read_text(encoding='utf-8', errors='ignore').splitlines())
                        total_lines += lines
                        total_files += 1
                        
                        if file.suffix == '.py':
                            python_lines += lines
                            python_files += 1
                    except:
                        pass
        except:
            pass
        
        return {
            'total': total_lines,
            'python_lines': python_lines,
            'files': total_files,
            'python_files': python_files
        }
    
    def _get_largest_files(self, limit: int = 3) -> List[Tuple[str, int]]:
        """Get largest files by line count"""
        file_sizes = []
        
        try:
            for file in self.repo_path.rglob('*.py'):
                if not self._should_exclude_file(file):
                    try:
                        lines = len(file.read_text(encoding='utf-8', errors='ignore').splitlines())
                        file_sizes.append((file.name, lines))
                    except:
                        pass
            
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            return file_sizes[:limit]
        except:
            return []
    
    def _should_exclude_file(self, file: Path) -> bool:
        """Check if file should be excluded"""
        exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', 'htmlcov'}
        return any(excluded in file.parts for excluded in exclude_dirs)
    
    def _get_coverage_percentage(self) -> Optional[float]:
        """Get test coverage percentage"""
        # Try htmlcov/status.json first
        status_json = self.repo_path / 'htmlcov' / 'status.json'
        if status_json.exists():
            try:
                data = json.loads(status_json.read_text())
                return float(data.get('totals', {}).get('percent_covered', 0))
            except:
                pass
        
        # Try .coverage file
        coverage_file = self.repo_path / '.coverage'
        if coverage_file.exists():
            try:
                # Parse coverage data (simplified)
                result = subprocess.run(
                    ['coverage', 'report'],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path
                )
                
                # Extract percentage from last line
                for line in result.stdout.split('\n'):
                    if 'TOTAL' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            return float(parts[-1].rstrip('%'))
            except:
                pass
        
        return None
    
    def _parse_coverage_data(self) -> Optional[Dict]:
        """Parse detailed coverage data"""
        status_json = self.repo_path / 'htmlcov' / 'status.json'
        if status_json.exists():
            try:
                data = json.loads(status_json.read_text())
                totals = data.get('totals', {})
                return {
                    'files': totals.get('num_statements', 0),
                    'statements': totals.get('num_statements', 0),
                    'covered': totals.get('covered_lines', 0)
                }
            except:
                pass
        return None
    
    def _get_security_score(self) -> Optional[int]:
        """Get security score from security_integrity module"""
        try:
            # Try to import and run security check
            security_file = self.repo_path / 'automation' / 'security_integrity.py'
            if security_file.exists():
                # Check if there's a cached score
                score_cache = self.repo_path / '.security_score.json'
                if score_cache.exists():
                    data = json.loads(score_cache.read_text())
                    return int(data.get('score', 0))
        except:
            pass
        return None
    
    def _get_last_security_scan(self) -> Optional[str]:
        """Get last security scan timestamp"""
        try:
            score_cache = self.repo_path / '.security_score.json'
            if score_cache.exists():
                data = json.loads(score_cache.read_text())
                timestamp = data.get('timestamp')
                if timestamp:
                    dt = datetime.fromisoformat(timestamp)
                    return dt.strftime('%Y-%m-%d %H:%M')
        except:
            pass
        return None
    
    def _get_recent_tasks(self) -> List[Dict]:
        """Get recent automation tasks"""
        tasks = []
        
        try:
            # Check git log for automation commits
            result = subprocess.run(
                ['git', 'log', '-10', '--pretty=format:%s|%ar'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n')[:5]:
                if '|' in line:
                    message, time_ago = line.split('|', 1)
                    
                    # Determine task type
                    task_name = "Unknown"
                    success = True
                    
                    if 'push' in message.lower():
                        task_name = "Push"
                    elif 'pull' in message.lower():
                        task_name = "Pull"
                    elif 'merge' in message.lower():
                        task_name = "Merge"
                    elif 'commit' in message.lower():
                        task_name = "Commit"
                    elif 'fix' in message.lower() or 'bug' in message.lower():
                        task_name = "Bug Fix"
                        success = True
                    elif 'feature' in message.lower() or 'add' in message.lower():
                        task_name = "Feature"
                        success = True
                    
                    tasks.append({
                        'name': task_name,
                        'success': success,
                        'timestamp': time_ago
                    })
        except:
            pass
        
        return tasks
    
    # ========== INTERACTIVE COMMANDS ==========
    
    def _show_detailed_logs(self):
        """Show detailed commit logs"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]📜 Commit History (Last 20)[/bold cyan]",
            border_style="cyan"
        ))
        
        try:
            result = subprocess.run(
                ['git', 'log', '-20', '--pretty=format:%h|%an|%ar|%s', '--date=relative'],
                capture_output=True,
                text=True,
                check=True
            )
            
            table = Table(show_header=True, box=box.ROUNDED)
            table.add_column("Hash", style="cyan")
            table.add_column("Author", style="yellow")
            table.add_column("Time", style="magenta")
            table.add_column("Message", style="white")
            
            for line in result.stdout.split('\n'):
                if '|' in line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        hash_short, author, time_ago, message = parts
                        table.add_row(
                            hash_short,
                            author[:20],
                            time_ago,
                            message[:50] + ('...' if len(message) > 50 else '')
                        )
            
            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]⚠️  Error: {e}[/red]")
        
        input("\nPress Enter to return to dashboard...")
    
    def _run_security_scan(self):
        """Run security scan"""
        self.console.clear()
        self.console.print(Panel(
            "[bold red]🔐 Running Security Scan[/bold red]",
            border_style="red"
        ))
        
        try:
            # Check if security module exists
            security_file = self.repo_path / 'automation' / 'security_integrity.py'
            
            if security_file.exists():
                self.console.print("\n[cyan]Scanning repository...[/cyan]")
                
                # Run security check
                result = subprocess.run(
                    ['python', str(security_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.repo_path
                )
                
                if result.returncode == 0:
                    self.console.print("\n[green]✅ Security scan completed![/green]")
                    self.console.print(result.stdout)
                else:
                    self.console.print("\n[yellow]⚠️  Scan completed with warnings[/yellow]")
                    self.console.print(result.stderr)
                
                # Clear cache to refresh security section
                self.cache.clear()
            else:
                self.console.print("\n[yellow]⚠️  Security module not found[/yellow]")
                self.console.print("Create automation/security_integrity.py to enable security scanning")
        
        except subprocess.TimeoutExpired:
            self.console.print("\n[red]❌ Scan timed out[/red]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
        
        input("\nPress Enter to return to dashboard...")
    
    def _export_report(self):
        """Export dashboard as markdown report"""
        self.console.clear()
        self.console.print(Panel(
            "[bold magenta]📄 Exporting Report[/bold magenta]",
            border_style="magenta"
        ))
        
        try:
            report_path = self.repo_path / 'REPO_HEALTH.md'
            
            # Generate markdown report
            report = self._generate_markdown_report()
            
            report_path.write_text(report, encoding='utf-8')
            
            self.console.print(f"\n[green]✅ Report exported to: {report_path}[/green]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
        
        input("\nPress Enter to return to dashboard...")
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown version of dashboard"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Repository Health Report

**Generated:** {timestamp}  
**Repository:** {self.repo_path.name}  
**Path:** {self.repo_path}

---

## 📊 Overview

- **Branch:** {self._get_current_branch()}
- **Total Commits:** {self._get_total_commits()}
- **Contributors:** {self._get_contributor_count()}
- **Health Status:** {self._calculate_health_status()}

"""
        
        # Last commit
        last_commit = self._get_last_commit()
        if last_commit:
            report += f"- **Last Commit:** {last_commit['date']} by {last_commit['author']}\n"
        
        report += "\n---\n\n## 📈 Commit Activity (Last 30 Days)\n\n"
        
        commits_by_date = self._get_commits_by_date(days=30)
        report += "| Date | Commits | Activity |\n"
        report += "|------|---------|----------|\n"
        
        for date, count in sorted(commits_by_date.items())[-14:]:
            bar = "█" * count
            report += f"| {date} | {count} | {bar} |\n"
        
        report += "\n---\n\n## 📊 Codebase Statistics\n\n"
        
        loc_data = self._count_lines_of_code()
        report += f"- **Total Lines:** {loc_data['total']:,}\n"
        report += f"- **Python Lines:** {loc_data['python_lines']:,}\n"
        report += f"- **Total Files:** {loc_data['files']}\n"
        report += f"- **Python Files:** {loc_data['python_files']}\n"
        
        if loc_data['python_lines'] > 0:
            ratio = (loc_data['python_lines'] / loc_data['total']) * 100
            report += f"- **Python Ratio:** {ratio:.1f}%\n"
        
        # Largest files
        largest = self._get_largest_files(5)
        if largest:
            report += "\n### 🔝 Largest Modules\n\n"
            for i, (file, size) in enumerate(largest, 1):
                report += f"{i}. **{file}** - {size:,} lines\n"
        
        report += "\n---\n\n## 🧪 Test Coverage\n\n"
        
        coverage = self._get_coverage_percentage()
        if coverage:
            report += f"- **Coverage:** {coverage:.1f}%\n"
            
            bar_length = int(coverage / 5)
            bar = "#" * bar_length + "-" * (20 - bar_length)
            report += f"- **Progress:** `[{bar}]`\n"
            
            if coverage >= 80:
                report += "- **Status:** 🟢 Excellent\n"
            elif coverage >= 60:
                report += "- **Status:** 🟡 Good\n"
            elif coverage >= 40:
                report += "- **Status:** 🟠 Fair\n"
            else:
                report += "- **Status:** 🔴 Poor\n"
        else:
            report += "*No coverage data available*\n"
        
        report += "\n---\n\n## 🔐 Security Status\n\n"
        
        security_score = self._get_security_score()
        if security_score:
            report += f"- **Security Score:** {security_score}/100\n"
            
            if security_score >= 90:
                report += "- **Status:** 🟢 Secure\n"
            elif security_score >= 70:
                report += "- **Status:** 🟡 Moderate\n"
            else:
                report += "- **Status:** 🔴 At Risk\n"
            
            last_scan = self._get_last_security_scan()
            if last_scan:
                report += f"- **Last Scan:** {last_scan}\n"
        else:
            report += "*Security scanning not configured*\n"
        
        report += "\n---\n\n## ⚙️ Recent Automation Tasks\n\n"
        
        tasks = self._get_recent_tasks()
        if tasks:
            report += "| Task | Status | Time |\n"
            report += "|------|--------|------|\n"
            
            for task in tasks:
                status = "✅" if task['success'] else "❌"
                report += f"| {task['name']} | {status} | {task['timestamp']} |\n"
        else:
            report += "*No recent tasks*\n"
        
        # System stats
        if HAS_PSUTIL:
            report += "\n---\n\n## 💻 System Resources\n\n"
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage(str(self.repo_path)).percent
            
            report += f"- **CPU Usage:** {cpu:.1f}%\n"
            report += f"- **Memory Usage:** {memory:.1f}%\n"
            report += f"- **Disk Usage:** {disk:.1f}%\n"
        
        report += "\n---\n\n*Report generated by Python Automation System*\n"
        
        return report
    
    def _show_help(self):
        """Show help screen"""
        self.console.clear()
        
        help_text = """
[bold cyan]🔧 Dashboard Help[/bold cyan]

[bold]Keyboard Controls:[/bold]

  [cyan]R[/cyan] - Refresh dashboard (clear cache and reload data)
  [green]L[/green] - View detailed commit logs (last 20 commits)
  [yellow]S[/yellow] - Run security scan (requires security module)
  [magenta]E[/magenta] - Export report as REPO_HEALTH.md
  [blue]H[/blue] - Show this help screen
  [red]Q[/red] - Quit dashboard

[bold]Features:[/bold]

  • Real-time repository metrics
  • Commit activity heatmap (30 days)
  • Test coverage visualization
  • Security status monitoring
  • Automation task tracking
  • System resource monitoring

[bold]Dashboard Sections:[/bold]

  📊 [cyan]Overview[/cyan] - Repository name, branch, commits, health
  📈 [green]Activity[/green] - Commit frequency over time
  📊 [magenta]Statistics[/magenta] - Lines of code, file counts
  🧪 [blue]Coverage[/blue] - Test coverage percentage
  🔐 [red]Security[/red] - Security score and last scan
  ⚙️  [yellow]Automation[/yellow] - Recent task status

[bold]Requirements:[/bold]

  • Git repository
  • Python 3.7+
  • rich library (pip install rich)
  • psutil for system stats (optional)
  • coverage for test metrics (optional)

[bold]Cache:[/bold]

  Dashboard caches data for 60 seconds to improve performance.
  Press 'R' to force refresh all sections.
        """
        
        self.console.print(Panel(help_text, border_style="blue"))
        input("\nPress Enter to return to dashboard...")
    
    def _exit_dashboard(self):
        """Clean exit from dashboard"""
        if HAS_RICH:
            self.console.clear()
            self.console.print(Panel(
                "[bold green]👋 Thanks for using Python Automation System![/bold green]\n"
                "Dashboard closed successfully.",
                border_style="green"
            ))
        else:
            print("\n👋 Dashboard closed. Goodbye!")
    
    def _getch_with_timeout(self, timeout: float) -> Optional[str]:
        """Get character with timeout (cross-platform)"""
        # Windows support
        if sys.platform == 'win32':
            import msvcrt
            import time
            
            start = time.time()
            while time.time() - start < timeout:
                if msvcrt.kbhit():
                    return msvcrt.getch().decode('utf-8', errors='ignore')
                time.sleep(0.1)
            return None
        
        # Unix/Linux/Mac support
        else:
            import select
            import tty
            import termios
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                
                if rlist:
                    return sys.stdin.read(1)
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _print_error(self, message: str):
        """Print error message"""
        if HAS_RICH:
            self.console.print(f"[red]❌ {message}[/red]")
        else:
            print(f"❌ {message}")


# ========== BACKWARD COMPATIBILITY ==========

class GitVisualizations(GitDashboard):
    """
    Backward compatible class maintaining old interface
    while adding new dashboard functionality
    """
    
    def show_visualizations_menu(self):
        """Show visualizations menu (legacy method)"""
        print("\n" + "="*70)
        print("📊 GIT VISUALIZATIONS")
        print("="*70 + "\n")
        
        if not self.is_git_repo():
            print("❌ Not a Git repository")
            input("\nPress Enter to continue...")
            return
        
        while True:
            print("\n📈 Available Visualizations:")
            print("  1. Interactive Dashboard (New!)")
            print("  2. Static Dashboard Report")
            print("  3. Commit Activity Graph")
            print("  4. Repository Summary")
            print("  5. Export Health Report")
            print("  6. Back to menu\n")
            
            choice = input("Your choice: ").strip()
            
            if choice == '1':
                self.show_dashboard(interactive=True)
            elif choice == '2':
                self.show_dashboard(interactive=False)
                input("\nPress Enter to continue...")
            elif choice == '3':
                self._show_commit_activity_only()
            elif choice == '4':
                self._show_summary_only()
            elif choice == '5':
                self._export_report()
            elif choice == '6':
                break
            else:
                print("\n❌ Invalid choice")
    
    def _show_commit_activity_only(self):
        """Show only commit activity graph"""
        print("\n" + "="*70)
        print("📈 COMMIT ACTIVITY (Last 30 Days)")
        print("="*70 + "\n")
        
        commits_by_date = self._get_commits_by_date(days=30)
        
        if not commits_by_date:
            print("No commits found in the last 30 days")
        else:
            max_commits = max(commits_by_date.values())
            bar_width = 50
            
            for date, count in sorted(commits_by_date.items())[-14:]:
                bar_length = int((count / max_commits) * bar_width) if max_commits > 0 else 0
                bar = '█' * bar_length
                print(f"{date} │ {bar} {count}")
            
            total_commits = sum(commits_by_date.values())
            avg_commits = total_commits / len(commits_by_date) if commits_by_date else 0
            
            print("\n" + "-"*70)
            print(f"Total commits: {total_commits}")
            print(f"Average per day: {avg_commits:.1f}")
            print(f"Most active day: {max(commits_by_date.values())} commits")
        
        input("\nPress Enter to continue...")
    
    def _show_summary_only(self):
        """Show only repository summary"""
        print("\n" + "="*70)
        print("📋 REPOSITORY SUMMARY")
        print("="*70 + "\n")
        
        try:
            print(f"📦 Repository: {self.repo_path.name}")
            print(f"🌿 Branch: {self._get_current_branch()}")
            print(f"📝 Total Commits: {self._get_total_commits()}")
            print(f"👥 Contributors: {self._get_contributor_count()}")
            print(f"💚 Health: {self._calculate_health_status()}")
            
            last_commit = self._get_last_commit()
            if last_commit:
                print(f"\n👤 Last Commit:")
                print(f"   Author: {last_commit['author']}")
                print(f"   Time: {last_commit['date']}")
            
            print(f"\n📊 Codebase:")
            loc_data = self._count_lines_of_code()
            print(f"   Lines of Code: {loc_data['total']:,}")
            print(f"   Python Files: {loc_data['python_files']}")
            print(f"   Total Files: {loc_data['files']}")
            
            coverage = self._get_coverage_percentage()
            if coverage:
                print(f"\n🧪 Test Coverage: {coverage:.1f}%")
            
            security_score = self._get_security_score()
            if security_score:
                print(f"\n🔐 Security Score: {security_score}/100")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")


# ========== MAIN ENTRY POINT ==========

if __name__ == '__main__':
    dashboard = GitDashboard()
    
    if HAS_RICH:
        dashboard.show_dashboard(interactive=True)
    else:
        print("\n⚠️  Install 'rich' for interactive dashboard:")
        print("    pip install rich")
        print("\nFalling back to basic dashboard...\n")
        dashboard.show_dashboard(interactive=False)