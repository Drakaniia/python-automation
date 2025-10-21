# ============================================================
# tests/test_git_hooks.py (FIXED for Windows)
# ============================================================
"""Performance benchmarking tests"""
import pytest
import time
from automation.core.git_client import GitClient


# Mark tests that require pytest-benchmark
pytest_benchmark_available = pytest.mark.skipif(
    not hasattr(pytest, 'benchmark'),
    reason="pytest-benchmark not installed"
)


class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.skipif(True, reason="Requires pytest-benchmark plugin")
    def test_status_performance(self, git_client, benchmark):
        """Benchmark status operation (requires pytest-benchmark)"""
        def run_status():
            return git_client.status(porcelain=True)
        
        benchmark(run_status)
    
    @pytest.mark.skipif(True, reason="Requires pytest-benchmark plugin")
    def test_log_performance(self, git_client, benchmark):
        """Benchmark log operation (requires pytest-benchmark)"""
        def run_log():
            return git_client.log(limit=10)
        
        benchmark(run_log)
    
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
    
    def test_status_speed(self, git_client):
        """Test status operation completes quickly"""
        start = time.time()
        git_client.status(porcelain=True)
        elapsed = time.time() - start
        
        # Should be very fast
        assert elapsed < 1.0
    
    def test_log_speed(self, git_client):
        """Test log operation completes quickly"""
        start = time.time()
        git_client.log(limit=10)
        elapsed = time.time() - start
        
        # Should be fast
        assert elapsed < 2.0