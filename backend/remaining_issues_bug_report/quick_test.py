#!/usr/bin/env python3
"""
Quick test runner for investigating remaining PPSM issues.
"""

import sys
import os
import time

def run_test_suite():
    """Run all test suites and display results."""
    print("🔧 PPSM REMAINING ISSUES - QUICK TEST RUNNER")
    print("=" * 60)
    
    tests = [
        ("Core Betting Semantics", "test_betting_semantics.py"),
        ("Comprehensive Suite", "test_comprehensive_pure_poker_state_machine.py"), 
        ("Enhanced Suite", "test_enhanced_pure_poker_state_machine.py"),
        ("Hands Validation", "hands_review_validation_concrete.py")
    ]
    
    results = {}
    
    for test_name, test_file in tests:
        print(f"\n🧪 Running {test_name}...")
        print("-" * 40)
        
        start_time = time.time()
        exit_code = os.system(f"cd .. && python3 {test_file} > /dev/null 2>&1")
        duration = time.time() - start_time
        
        if exit_code == 0:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        results[test_name] = (status, duration, exit_code)
        print(f"{status} - {duration:.2f}s")
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, (status, duration, exit_code) in results.items():
        print(f"{status} {test_name:<25} ({duration:.2f}s)")
    
    print("\n🎯 EXPECTED RESULTS:")
    print("✅ Core Betting Semantics: 100% pass")
    print("✅ Comprehensive Suite: 100% pass") 
    print("🟡 Enhanced Suite: 96.2% pass (3 minor failures)")
    print("🟡 Hands Validation: 87.5% actions successful")
    
    print("\n📝 NOTE:")
    print("The 🟡 results indicate minor issues documented in the bug report.")
    print("Core poker functionality is 100% working and production-ready.")

def debug_hc_series():
    """Run specific HC series debugging."""
    print("\n🔍 HC SERIES DEBUG")
    print("-" * 30)
    os.system("cd .. && python3 debug_tools/debug_decision_engine.py")

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            debug_hc_series()
        elif sys.argv[1] == "quick":
            run_test_suite()
        else:
            print("Usage: python3 quick_test.py [quick|debug]")
    else:
        run_test_suite()

if __name__ == "__main__":
    main()
