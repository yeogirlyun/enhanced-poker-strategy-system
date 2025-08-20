#!/usr/bin/env python3
"""
Simple Compile Check - Focus on Critical Files

Checks the essential files for the PPSM hands review integration.
"""

import ast
import sys
from pathlib import Path

def check_file(file_path):
    """Check if a file compiles."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse AST to check syntax
        ast.parse(source, filename=str(path))
        
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check critical files."""
    print("🔍 Simple Compile Check for PPSM Integration")
    print("=" * 50)
    
    # Critical files (relative to backend/)
    files = [
        "ui/tabs/hands_review_tab_ppsm.py",
        "ui/app_shell.py",
        "run_new_ui.py"
    ]
    
    # Also check test file in project root
    test_file = "../test_hands_review_ppsm_ui.py"
    if Path(test_file).exists():
        files.append(test_file)
    
    all_good = True
    
    for file_path in files:
        print(f"🔍 {file_path}... ", end="")
        success, message = check_file(file_path)
        
        if success:
            print("✅ OK")
        else:
            print(f"❌ FAIL")
            print(f"   {message}")
            all_good = False
    
    print("\\n" + "=" * 50)
    if all_good:
        print("🎉 All critical files compile successfully!")
        print("🚀 Ready to run the GUI!")
        return 0
    else:
        print("❌ Some files have compile errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
