#!/usr/bin/env python3
"""
Compile Error Checker for Poker Project
Checks all Python files for syntax errors without executing them.
"""

import os
import sys
import ast
from pathlib import Path

def check_file_compilation(file_path):
    """Check if a Python file compiles without syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the AST
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def check_directory(directory_path):
    """Recursively check all Python files in a directory."""
    errors = []
    total_files = 0
    
    for root, dirs, files in os.walk(directory_path):
        # Skip virtual environments and git directories
        if any(skip in root for skip in ['.venv', 'venv', '.git', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_files += 1
                
                success, error = check_file_compilation(file_path)
                if not success:
                    errors.append((file_path, error))
    
    return errors, total_files

def main():
    """Main function to check compilation errors."""
    print("🔍 Checking Python files for compile errors...")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Check the entire project
    errors, total_files = check_directory(project_root)
    
    print(f"📊 Results: {total_files} Python files checked")
    print("=" * 60)
    
    if not errors:
        print("✅ All Python files compile successfully!")
        return 0
    else:
        print(f"❌ Found {len(errors)} compilation errors:")
        print("=" * 60)
        
        for file_path, error in errors:
            # Make the path relative to project root
            relative_path = os.path.relpath(file_path, project_root)
            print(f"📁 {relative_path}")
            print(f"   {error}")
            print()
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
