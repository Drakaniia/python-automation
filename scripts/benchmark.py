"""
Performance benchmarking script
Compare old vs new implementation
"""
import time
from automation.core import GitClient
import subprocess

def benchmark_old_method():
    """Benchmark old subprocess method"""
    start = time.time()
    for _ in range(100):
        subprocess.run(['git', 'status'], capture_output=True, text=True)
    return time.time() - start

def benchmark_new_method():
    """Benchmark new GitClient method"""
    client = GitClient()
    start = time.time()
    for _ in range(100):
        client.status()
    return time.time() - start

if __name__ == '__main__':
    print("Performance Benchmark")
    print("=" * 50)
    
    old_time = benchmark_old_method()
    new_time = benchmark_new_method()
    
    print(f"Old method: {old_time:.3f}s")
    print(f"New method: {new_time:.3f}s")
    print(f"Improvement: {((old_time - new_time) / old_time * 100):.1f}%")