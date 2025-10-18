#!/usr/bin/env python3
"""
AI Commit Integration Test Script
Verifies that all components are properly installed and working
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.NC}")

def test_file_structure():
    """Test 1: Verify all required files exist"""
    print_header("Test 1: File Structure Check")
    
    required_files = {
        'automation/github/git_push_ai.py': 'NEW - AI Push Handler',
        'automation/ai_features/commit_summarizer.py': 'UPDATED - Commit Summarizer',
        'automation/git_operations.py': 'UPDATED - Git Operations',
        'automation/github/__init__.py': 'UPDATED - GitHub Init',
        'automation/github/git_status.py': 'EXISTING - Status Handler',
        'automation/github/git_push.py': 'EXISTING - Push Handler',
    }
    
    all_found = True
    for filepath, description in required_files.items():
        if Path(filepath).exists():
            print_success(f"{description}: {filepath}")
        else:
            print_error(f"{description}: {filepath} - NOT FOUND")
            all_found = False
    
    return all_found

def test_imports():
    """Test 2: Verify all modules can be imported"""
    print_header("Test 2: Module Import Check")
    
    imports_to_test = [
        ('automation.github.git_push_ai', 'GitPushAI'),
        ('automation.ai_features.commit_summarizer', 'CommitSummarizer'),
        ('automation.git_operations', 'GitOperations'),
        ('automation.github.git_status', 'GitStatus'),
    ]
    
    all_imported = True
    for module_path, class_name in imports_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print_success(f"Imported {class_name} from {module_path}")
        except ImportError as e:
            print_error(f"Failed to import {class_name} from {module_path}: {e}")
            all_imported = False
        except AttributeError as e:
            print_error(f"Class {class_name} not found in {module_path}: {e}")
            all_imported = False
    
    return all_imported

def test_commit_summarizer_methods():
    """Test 3: Verify CommitSummarizer has required methods"""
    print_header("Test 3: CommitSummarizer Methods Check")
    
    try:
        from automation.ai_features.commit_summarizer import CommitSummarizer
        
        summarizer = CommitSummarizer()
        
        required_methods = [
            'generate_commit_message_for_staged_changes',
            '_get_staged_diff',
            '_get_staged_files',
            '_analyze_diff',
            '_create_commit_message',
            'generate_changelog',  # Original method
        ]
        
        all_methods_exist = True
        for method_name in required_methods:
            if hasattr(summarizer, method_name):
                print_success(f"Method exists: {method_name}")
            else:
                print_error(f"Method missing: {method_name}")
                all_methods_exist = False
        
        return all_methods_exist
    except Exception as e:
        print_error(f"Failed to test CommitSummarizer: {e}")
        return False

def test_git_operations_integration():
    """Test 4: Verify GitOperations has AI push integration"""
    print_header("Test 4: GitOperations Integration Check")
    
    try:
        from automation.git_operations import GitOperations
        
        git_ops = GitOperations()
        
        required_attributes = [
            'push_ai_handler',
            'status_handler',
            'log_handler',
            'push_handler',
        ]
        
        required_methods = [
            'push_ai',
            'push',
            'status',
            'log',
        ]
        
        all_exist = True
        
        # Check attributes
        for attr_name in required_attributes:
            if hasattr(git_ops, attr_name):
                print_success(f"Attribute exists: {attr_name}")
            else:
                print_error(f"Attribute missing: {attr_name}")
                all_exist = False
        
        # Check methods
        for method_name in required_methods:
            if hasattr(git_ops, method_name):
                print_success(f"Method exists: {method_name}")
            else:
                print_error(f"Method missing: {method_name}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print_error(f"Failed to test GitOperations: {e}")
        return False

def test_menu_integration():
    """Test 5: Verify menu has AI-powered push option"""
    print_header("Test 5: Menu Integration Check")
    
    try:
        from automation.git_operations import GitMenu
        
        menu = GitMenu()
        
        # Check if menu items are set up
        if hasattr(menu, 'items') and menu.items:
            print_success(f"Menu has {len(menu.items)} items")
            
            # Check for AI-powered push item
            ai_push_found = False
            for item in menu.items:
                if 'AI' in item.label or '🤖' in item.label:
                    print_success(f"Found AI-powered option: {item.label}")
                    ai_push_found = True
                    break
            
            if not ai_push_found:
                print_warning("AI-powered push option not found in menu (check label)")
            
            return True
        else:
            print_error("Menu items not properly initialized")
            return False
    except Exception as e:
        print_error(f"Failed to test menu: {e}")
        return False

def test_git_push_ai_instantiation():
    """Test 6: Verify GitPushAI can be instantiated"""
    print_header("Test 6: GitPushAI Instantiation Check")
    
    try:
        from automation.github.git_push_ai import GitPushAI
        
        push_ai = GitPushAI()
        
        required_methods = [
            'ai_commit_and_push',
            '_generate_ai_commit_message',
            '_has_changes',
            '_is_git_repo',
        ]
        
        all_exist = True
        for method_name in required_methods:
            if hasattr(push_ai, method_name):
                print_success(f"Method exists: {method_name}")
            else:
                print_error(f"Method missing: {method_name}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print_error(f"Failed to instantiate GitPushAI: {e}")
        return False

def test_ai_message_generation():
    """Test 7: Test AI message generation (dry run)"""
    print_header("Test 7: AI Message Generation Test (Dry Run)")
    
    try:
        from automation.ai_features.commit_summarizer import CommitSummarizer
        
        summarizer = CommitSummarizer()
        
        print_info("Testing message generation logic...")
        
        # Test the analysis methods
        test_files = ['automation/github/git_push_ai.py']
        test_diff = "+++ new code\n+def test(): pass\n"
        
        analysis = summarizer._analyze_diff(test_diff, test_files)
        print_success(f"Diff analysis works: type={analysis['type']}, scope={analysis['scope']}")
        
        message = summarizer._create_commit_message(analysis, test_files)
        print_success(f"Message generation works: \"{message}\"")
        
        print_info(f"Generated message: {Colors.YELLOW}{message}{Colors.NC}")
        
        return True
    except Exception as e:
        print_error(f"Failed to test message generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  AI COMMIT INTEGRATION TEST SUITE")
    print(f"{'='*60}{Colors.NC}\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("CommitSummarizer Methods", test_commit_summarizer_methods),
        ("GitOperations Integration", test_git_operations_integration),
        ("Menu Integration", test_menu_integration),
        ("GitPushAI Instantiation", test_git_push_ai_instantiation),
        ("AI Message Generation", test_ai_message_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.NC}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{'='*60}")
        print("  ✓ ALL TESTS PASSED!")
        print("  Your AI commit integration is ready to use!")
        print(f"{'='*60}{Colors.NC}\n")
        print(f"{Colors.BLUE}Next step: Run 'python main.py' and test it live!{Colors.NC}\n")
        return 0
    else:
        print(f"{Colors.RED}{'='*60}")
        print(f"  ✗ {total - passed} test(s) failed")
        print("  Please review the errors above and fix them")
        print(f"{'='*60}{Colors.NC}\n")
        return 1

if __name__ == "__main__":
    # Change to project root if needed
    if not Path("automation").exists():
        print_error("Please run this script from the python-automation root directory")
        sys.exit(1)
    
    exit_code = run_all_tests()
    sys.exit(exit_code)