#!/usr/bin/env python3
"""
Main entry point for GTO Integration Testing.

This is the primary script to run all GTO tests and validations.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("🎯 GTO INTEGRATION TESTING FRAMEWORK")
print("=" * 60)
print("🧠 Industry-strength GTO engine with PPSM integration")
print("🔧 Resolves interface mismatches and validates complete pipeline")
print()

try:
    from backend.gto.test_gto_integration import main
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()