#!/usr/bin/env python3
"""
Compile Error Checker

This script checks for Python syntax and compile errors across all key files
in the PPSM hands review integration.
"""

import sys
import ast
import traceback
from pathlib import Path

def check_file_syntax(file_path):
    """Check if a Python file compiles without errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the AST
        ast.parse(source, filename=str(file_path))
        return True, None
        
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Error: {e}"

def check_file_import(file_path):
    """Check if a Python file can be imported."""
    try:
        # Add the directory to sys.path temporarily
        original_path = sys.path.copy()
        file_dir = str(file_path.parent)
        if file_dir not in sys.path:
            sys.path.insert(0, file_dir)
        
        # Get module name (remove .py extension)
        module_name = file_path.stem
        
        # Try to compile and execute (but not actually import to avoid side effects)
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, str(file_path), 'exec')
        return True, None
        
    except Exception as e:
        return False, f"ImportError: {e}"
    finally:
        # Restore original sys.path
        sys.path[:] = original_path

def main():
    """Main compile checker."""
    print("🔍 Python Compile Error Checker")
    print("=" * 50)
    
    # Key files to check
    key_files = [
        "ui/tabs/hands_review_tab_ppsm.py",
        "ui/app_shell.py", 
        "test_hands_review_ppsm_ui.py",
        "test_gto_hands_simple.py",
        "run_new_ui.py",
        "ui/state/store.py",
        "ui/services/event_bus.py",
        "ui/services/theme_manager.py",
        "core/pure_poker_state_machine.py",
        "core/hand_model.py",
        "core/hand_model_decision_engine.py"
    ]
    
    results = []
    
    for file_path in key_files:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  {file_path} - File not found")
            results.append((file_path, False, "File not found"))
            continue
        
        print(f"🔍 Checking {file_path}...")
        
        # Check syntax
        syntax_ok, syntax_error = check_file_syntax(path)
        if not syntax_ok:
            print(f"❌ {file_path} - SYNTAX ERROR")
            print(f"   {syntax_error}")
            results.append((file_path, False, syntax_error))
            continue
        
        # Check compilation
        compile_ok, compile_error = check_file_import(path)
        if not compile_ok:
            print(f"⚠️  {file_path} - COMPILE WARNING")
            print(f"   {compile_error}")
            results.append((file_path, True, f"Syntax OK, Import issues: {compile_error}"))
        else:
            print(f"✅ {file_path} - OK")
            results.append((file_path, True, "OK"))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for file_path, success, message in results:
        if success and message == "OK":
            status = "✅ PASS"
            passed += 1
        elif success:
            status = "⚠️  WARN"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} {file_path}")
        if message != "OK":
            print(f"     {message}")
    
    print(f"\\n🎯 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All files compile successfully!")
        return 0
    else:
        print("⚠️  Some files have issues that need fixing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
