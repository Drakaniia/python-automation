#!/usr/bin/env python3
"""
run_dev_tests.py
Script to run all dev_mode tests with proper reporting
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all dev_mode tests"""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    print("=" * 70)
    print("🧪 RUNNING DEV MODE TESTS")
    print("=" * 70)
    print()
    
    # Test commands to run
    test_commands = [
        # Basic test run
        {
            'name': 'All Dev Mode Tests',
            'cmd': ['pytest', 'tests/test_dev_mode/', '-v'],
            'description': 'Run all tests in test_dev_mode directory'
        },
        # Individual test files
        {
            'name': 'Menu Routing Tests',
            'cmd': ['pytest', 'tests/test_dev_mode/test_menu_routing.py', '-v'],
            'description': 'Test menu structure and command loading'
        },
        {
            'name': 'Create Frontend Tests',
            'cmd': ['pytest', 'tests/test_dev_mode/test_create_frontend_noninteractive.py', '-v'],
            'description': 'Test frontend project creation'
        },
        {
            'name': 'Other Modules Tests',
            'cmd': ['pytest', 'tests/test_dev_mode/test_other_modules.py', '-v'],
            'description': 'Test run_project, install_deps, format_code, docker_quick'
        },
    ]
    
    results = []
    
    for test_config in test_commands:
        print(f"\n{'=' * 70}")
        print(f"📋 {test_config['name']}")
        print(f"   {test_config['description']}")
        print(f"{'=' * 70}\n")
        
        try:
            result = subprocess.run(
                test_config['cmd'],
                cwd=project_root,
                capture_output=False,
                text=True
            )
            
            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            results.append({
                'name': test_config['name'],
                'status': status,
                'returncode': result.returncode
            })
            
            print(f"\n{status}: {test_config['name']}")
            
        except FileNotFoundError:
            print("❌ ERROR: pytest not found. Install it with:")
            print("   pip install pytest pytest-mock")
            results.append({
                'name': test_config['name'],
                'status': "❌ SKIPPED",
                'returncode': -1
            })
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                'name': test_config['name'],
                'status': "❌ ERROR",
                'returncode': -1
            })
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for result in results:
        print(f"  {result['status']}: {result['name']}")
    
    passed = sum(1 for r in results if r['returncode'] == 0)
    failed = sum(1 for r in results if r['returncode'] != 0)
    
    print("\n" + "=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


def show_options():
    """Show available test options"""
    print("=" * 70)
    print("🧪 DEV MODE TEST RUNNER")
    print("=" * 70)
    print()
    print("Available Options:")
    print()
    print("  1. Run all tests                    pytest tests/test_dev_mode/ -v")
    print("  2. Run menu routing tests          pytest tests/test_dev_mode/test_menu_routing.py -v")
    print("  3. Run create frontend tests       pytest tests/test_dev_mode/test_create_frontend_noninteractive.py -v")
    print("  4. Run other modules tests         pytest tests/test_dev_mode/test_other_modules.py -v")
    print("  5. Run with coverage               pytest tests/test_dev_mode/ -v --cov=automation/dev_mode")
    print("  6. Run specific test               pytest tests/test_dev_mode/test_file.py::TestClass::test_method -v")
    print()
    print("Additional Options:")
    print("  -v    Verbose output")
    print("  -vv   Very verbose output")
    print("  -s    Show print statements")
    print("  -x    Stop on first failure")
    print("  -k    Run tests matching pattern:  pytest -k 'test_name'")
    print()
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_options()
        sys.exit(0)
    
    exit_code = run_tests()
    sys.exit(exit_code)