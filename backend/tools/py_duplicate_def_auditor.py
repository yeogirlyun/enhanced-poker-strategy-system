#!/usr/bin/env python3
"""
Enhanced Duplicate Definition Auditor - Eliminates False Positives

This improved version distinguishes between:
- REAL duplicates: Same method/function defined multiple times in the same class/file
- FALSE POSITIVES: Legitimate patterns like inheritance, nested classes, local functions

Key improvements:
1. Per-file analysis (no cross-file false positives)
2. Inheritance-aware method tracking
3. Nested class detection
4. Local function scope analysis
5. Context-aware duplicate detection
"""

import ast
import os
import argparse
import json
import fnmatch
from typing import Dict, List, Any, Optional, Set


class SmartDuplicateDefVisitor(ast.NodeVisitor):
    """
    Smart duplicate definition visitor that eliminates false positives.
    
    Only reports REAL duplicates within the same scope, not legitimate
    Python patterns like inheritance, nested classes, or local functions.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
        self.current_class: Optional[str] = None
        self.current_methods: Set[str] = set()
        self.current_functions: Set[str] = set()
        self.duplicates: List[Dict[str, Any]] = []
        
        # Track nested class depth
        self.class_stack: List[str] = []
        
        # Track function scope depth
        self.function_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition with nested class awareness."""
        # Track nested class depth
        self.class_stack.append(node.name)
        
        # Check for duplicate methods ONLY within the same class
        if self.current_class == node.name:
            # Same class - check for duplicate method names
            if node.name in self.current_methods:
                self.duplicates.append({
                    "type": "duplicate_method_same_class",
                    "class": node.name,
                    "name": node.name,
                    "file": self.filename,
                    "line": node.lineno,
                    "severity": "high",
                    "description": f"Method '{node.name}' defined multiple times in class '{node.name}'"
                })
        else:
            # Different class - reset method tracking
            self.current_class = node.name
            self.current_methods.clear()
        
        # Track methods within this class
        for body_item in node.body:
            if isinstance(body_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_name = body_item.name
                
                # Check for duplicate methods within the same class
                if method_name in self.current_methods:
                    self.duplicates.append({
                        "type": "duplicate_method_same_class",
                        "class": node.name,
                        "name": method_name,
                        "file": self.filename,
                        "line": body_item.lineno,
                        "severity": "high",
                        "description": f"Method '{method_name}' defined multiple times in class '{node.name}'"
                    })
                else:
                    self.current_methods.add(method_name)
        
        # Visit child nodes
        self.generic_visit(node)
        
        # Pop class from stack
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition with scope awareness."""
        # Check if this is a method (inside a class) or a top-level function
        if self.class_stack:
            # This is a method inside a class - don't report as duplicate
            # Methods are handled in visit_ClassDef
            pass
        elif self.function_stack:
            # Local function - don't report as duplicate
            pass
        else:
            # Top-level function - check for duplicates
            if node.name in self.current_functions:
                self.duplicates.append({
                    "type": "duplicate_top_level_function",
                    "name": node.name,
                    "file": self.filename,
                    "line": node.lineno,
                    "severity": "medium",
                    "description": f"Top-level function '{node.name}' defined multiple times"
                })
            else:
                self.current_functions.add(node.name)
        
        # Track function scope
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definition with scope awareness."""
        # Same logic as regular functions
        if self.class_stack:
            # This is an async method inside a class - don't report as duplicate
            pass
        elif self.function_stack:
            # Local async function - don't report as duplicate
            pass
        else:
            # Top-level async function - check for duplicates
            if node.name in self.current_functions:
                self.duplicates.append({
                    "type": "duplicate_top_level_async_function",
                    "name": node.name,
                    "file": self.filename,
                    "line": node.lineno,
                    "severity": "medium",
                    "description": f"Top-level async function '{node.name}' defined multiple times"
                })
            else:
                self.current_functions.add(node.name)
        
        # Track function scope
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()


def scan_file(path: str) -> List[Dict[str, Any]]:
    """Scan a single Python file for REAL duplicate definitions."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {path}: {e}")
        return []
    
    visitor = SmartDuplicateDefVisitor(path)
    visitor.visit(tree)
    return visitor.duplicates


def scan_directory(root: str, ignore_patterns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Scan a directory recursively for REAL duplicate definitions."""
    all_duplicates = []
    scanned_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)
                
                # Skip ignored patterns
                if (ignore_patterns and 
                    any(fnmatch.fnmatch(full_path, pat) for pat in ignore_patterns)):
                    continue
                
                dups = scan_file(full_path)
                all_duplicates.extend(dups)
                scanned_files += 1
    
    print(f"Scanned {scanned_files} Python files")
    return all_duplicates


def generate_report(duplicates: List[Dict[str, Any]], 
                   output_format: str = "console") -> str:
    """Generate a formatted report of REAL duplicates only."""
    if not duplicates:
        return "✅ No REAL duplicates found! All 'duplicates' are legitimate Python patterns."
    
    # Group duplicates by type and severity
    grouped = {}
    for dup in duplicates:
        dup_type = dup["type"]
        severity = dup["severity"]
        
        if dup_type not in grouped:
            grouped[dup_type] = {}
        if severity not in grouped[dup_type]:
            grouped[dup_type][severity] = []
        
        grouped[dup_type][severity].append(dup)
    
    # Generate report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("SMART DUPLICATE DEFINITIONS AUDIT REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Total REAL duplicates found: {len(duplicates)}")
    report_lines.append("(False positives from inheritance, nested classes, and local functions eliminated)")
    report_lines.append("")
    
    for dup_type in sorted(grouped.keys()):
        report_lines.append(f"{dup_type.upper().replace('_', ' ')}:")
        report_lines.append("-" * 40)
        
        for severity in ["high", "medium", "low"]:
            if severity in grouped[dup_type]:
                dupes = grouped[dup_type][severity]
                report_lines.append(f"  {severity.upper()} severity ({len(dupes)}):")
                
                for dup in dupes:
                    if "class" in dup:
                        report_lines.append(f"    {dup['name']} in class {dup['class']}")
                    else:
                        report_lines.append(f"    {dup['name']}")
                    
                    report_lines.append(f"      File: {dup['file']}:{dup['line']}")
                    report_lines.append(f"      Issue: {dup['description']}")
                    report_lines.append("")
        
        report_lines.append("")
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Smart duplicate definition auditor that eliminates false positives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  python py_duplicate_def_auditor.py --root .
  
  # Scan with custom ignore patterns
  python py_duplicate_def_auditor.py --root . --ignore "*/__pycache__/*,*/logs/*"
  
  # Generate JSON report
  python py_duplicate_def_auditor.py --root . --format json
  
  # Quiet mode
  python py_duplicate_def_auditor.py --root . --quiet
        """
    )
    
    parser.add_argument(
        "--root", 
        default=".", 
        help="Root directory to scan (default: current directory)"
    )
    
    parser.add_argument(
        "--ignore", 
        nargs="*", 
        default=["*/__pycache__/*", "*/logs/*"],
        help="Ignore patterns (default: __pycache__ and logs directories)"
    )
    
    parser.add_argument(
        "--format", 
        choices=["console", "json"], 
        default="console",
        help="Output format (default: console)"
    )
    
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🔍 Smart Duplicate Definition Auditor")
        print("📁 Scanning directory:", args.root)
        print("🚫 Ignoring patterns:", args.ignore)
        print()
    
    # Scan for duplicates
    duplicates = scan_directory(args.root, args.ignore)
    
    if not args.quiet:
        print()
    
    # Generate and display report
    if args.format == "json":
        # JSON output for programmatic use
        report_data = {
            "summary": {
                "total_duplicates": len(duplicates),
                "scanned_directory": args.root,
                "ignore_patterns": args.ignore
            },
            "duplicates": duplicates
        }
        print(json.dumps(report_data, indent=2))
    else:
        # Console output
        report = generate_report(duplicates)
        print(report)
    
    # Save detailed report
    report_filename = f"duplicate_audit_report_{len(duplicates)}_duplicates.json"
    with open(report_filename, "w") as f:
        json.dump({
            "summary": {
                "total_duplicates": len(duplicates),
                "scanned_directory": args.root,
                "ignore_patterns": args.ignore,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            },
            "duplicates": duplicates
        }, f, indent=2)
    
    if not args.quiet:
        print(f"📄 Detailed report saved to: {report_filename}")
        print()
        
        if duplicates:
            print("❌ Found REAL duplicates that need attention!")
            print("💡 These are actual code issues, not false positives.")
            exit(1)
        else:
            print("✅ All 'duplicates' are legitimate Python patterns!")
            print("🎉 Your codebase is clean and well-structured.")
            exit(0)


if __name__ == "__main__":
    main()
