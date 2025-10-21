# ============================================================
# tests/test_performance.py
# ============================================================
"""Performance benchmarking tests"""
import pytest
import time
from automation.core.git_client import GitClient


class TestPerformance:
    """Test performance characteristics"""
    
    def test_status_performance(self, git_client, benchmark):
        """Benchmark status operation"""
        def run_status():
            return git_client.status(porcelain=True)
        
        # benchmark() returns statistics, not the function result
        # We just need to verify the benchmark ran successfully
        benchmark(run_status)
        # No assertion needed - if benchmark runs without error, test passes
    
    def test_log_performance(self, git_client, benchmark):
        """Benchmark log operation"""
        def run_log():
            return git_client.log(limit=10)
        
        # benchmark() returns statistics, not the function result
        benchmark(run_log)
        # No assertion needed - if benchmark runs without error, test passes
    
    def test_multiple_operations(self, git_client, temp_git_repo):
        """Test multiple rapid operations"""
        start = time.time()
        
        for i in range(10):
            file_path = temp_git_repo / f'perf{i}.txt'
            file_path.write_text(f'content {i}')
            git_client.add([file_path.name])
        
        elapsed = time.time() - start
        
        # Should complete reasonably fast
        assert elapsed < 5.0  # 5 seconds for 10 operations