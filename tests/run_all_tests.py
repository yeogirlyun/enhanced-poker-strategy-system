#!/usr/bin/env python3
"""
Test Runner for Poker Strategy System

Runs all tests in the tests directory and provides a comprehensive test report.
"""

import sys
import os
import subprocess
import time
from typing import List, Dict

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRunner:
    """Runs all tests and generates reports."""
    
    def __init__(self):
        self.test_files = [
            "test_enhanced_evaluator.py",
            "test_poker_table.py", 
            "comprehensive_test_suite.py"
        ]
        self.results = {}
    
    def run_test(self, test_file: str) -> Dict:
        """Run a single test file and return results."""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_file}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Import and run the test
            test_module = __import__(test_file.replace('.py', ''))
            
            # Run the main test function if it exists
            if hasattr(test_module, 'test_hand_evaluation'):
                test_module.test_hand_evaluation()
            
            if hasattr(test_module, 'test_preflop_strengths'):
                test_module.test_preflop_strengths()
            
            if hasattr(test_module, 'test_complete_hand_flow'):
                test_module.test_complete_hand_flow()
            
            if hasattr(test_module, 'test_poker_table'):
                test_module.test_poker_table()
            
            execution_time = time.time() - start_time
            
            return {
                "status": "PASS",
                "execution_time": execution_time,
                "error": None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                "status": "FAIL",
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run all tests and generate a comprehensive report."""
        print("🎯 POKER STRATEGY SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"📅 Test Run: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Test Directory: {os.path.abspath('.')}")
        print(f"🔧 Backend Path: {os.path.abspath('../backend')}")
        print("=" * 60)
        
        total_tests = len(self.test_files)
        passed_tests = 0
        failed_tests = 0
        total_time = 0
        
        for test_file in self.test_files:
            result = self.run_test(test_file)
            self.results[test_file] = result
            
            if result["status"] == "PASS":
                passed_tests += 1
                print(f"✅ {test_file}: PASS ({result['execution_time']:.2f}s)")
            else:
                failed_tests += 1
                print(f"❌ {test_file}: FAIL ({result['execution_time']:.2f}s)")
                print(f"   Error: {result['error']}")
            
            total_time += result["execution_time"]
        
        # Generate summary report
        self._print_summary(passed_tests, failed_tests, total_tests, total_time)
    
    def _print_summary(self, passed: int, failed: int, total: int, total_time: float):
        """Print test summary report."""
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY REPORT")
        print(f"{'='*60}")
        
        print(f"🎯 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        print(f"⏱️  Total Execution Time: {total_time:.2f}s")
        print(f"⏱️  Average Time per Test: {total_time/total:.2f}s")
        
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_file, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {status_icon} {test_file}: {result['status']} ({result['execution_time']:.2f}s)")
    
    def run_specific_test(self, test_name: str):
        """Run a specific test by name."""
        if test_name in self.test_files:
            print(f"🎯 Running specific test: {test_name}")
            result = self.run_test(test_name)
            print(f"\n📊 Result: {result['status']}")
            if result["error"]:
                print(f"Error: {result['error']}")
        else:
            print(f"❌ Test '{test_name}' not found. Available tests:")
            for test in self.test_files:
                print(f"   • {test}")


def main():
    """Main test runner function."""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        runner.run_specific_test(test_name)
    else:
        # Run all tests
        runner.run_all_tests()


if __name__ == "__main__":
    main() 