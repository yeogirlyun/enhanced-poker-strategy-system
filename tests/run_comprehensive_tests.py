#!/usr/bin/env python3
"""
Comprehensive Test Runner

This script runs all comprehensive tests with coverage reporting
to ensure system integrity and prevent regressions.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests_with_coverage():
    """Run all comprehensive tests with coverage reporting."""
    print("🧪 RUNNING COMPREHENSIVE POKER STATE MACHINE TESTS")
    print("=" * 60)
    
    # Get the tests directory
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Run pytest with coverage
    cmd = [
        "python3", "-m", "pytest",
        str(tests_dir / "test_poker_state_machine_comprehensive.py"),
        "-v",
        "--cov=backend/core",
        "--cov-report=term-missing",
        "--cov-report=html:tests/coverage_html",
        "--cov-fail-under=70"  # Fail if coverage is below 70%
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ ALL TESTS PASSED!")
            print("📊 Coverage report generated in tests/coverage_html/")
        else:
            print("\n❌ SOME TESTS FAILED!")
            print("Please review the test output above.")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_quick_tests():
    """Run quick tests for basic functionality."""
    print("🧪 RUNNING QUICK FUNCTIONALITY TESTS")
    print("=" * 60)
    
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    os.chdir(project_root)
    
    # Run basic tests
    basic_tests = [
        "test_ui_call_amount_fix.py",
        "test_ui_state_machine_integration.py",
        "test_comprehensive_poker_state_machine.py"
    ]
    
    all_passed = True
    
    for test_file in basic_tests:
        test_path = tests_dir / test_file
        if test_path.exists():
            print(f"\nRunning {test_file}...")
            try:
                result = subprocess.run(
                    ["python3", str(test_path)],
                    capture_output=False,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                else:
                    print(f"❌ {test_file} FAILED")
                    all_passed = False
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                all_passed = False
        else:
            print(f"⚠️  {test_file} not found, skipping")
    
    return all_passed


def main():
    """Main test runner."""
    print("🎯 POKER STATE MACHINE COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("This will run all tests to ensure system integrity.")
    print()
    
    # Run quick tests first
    quick_success = run_quick_tests()
    
    print("\n" + "=" * 60)
    
    # Run comprehensive tests
    comprehensive_success = run_tests_with_coverage()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if quick_success and comprehensive_success:
        print("✅ ALL TESTS PASSED!")
        print("🎉 System integrity verified.")
        print("🛡️  No regressions detected.")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please review and fix failing tests.")
        print("⚠️  System integrity may be compromised.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 