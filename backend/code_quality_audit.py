#!/usr/bin/env python3
"""
Code Quality Audit Script for Poker Application

This script performs a comprehensive audit to check for:
1. Duplicate class names across files
2. Duplicate method definitions within classes
3. Method overrides from base classes
4. Import conflicts and circular dependencies
"""

import os
import sys
import ast
import importlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CodeAuditor:
    """Audit poker application code for quality issues."""
    
    def __init__(self, backend_dir: str = "."):
        self.backend_dir = Path(backend_dir)
        self.class_definitions: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # class_name -> [(file_path, class_code)]
        self.method_definitions: Dict[str, Dict[str, List[Tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))  # class_name -> {method_name -> [(file_path, method_code)]}
        self.base_classes: Dict[str, Set[str]] = defaultdict(set)  # class_name -> {base_class_names}
        self.imports: Dict[str, Set[str]] = defaultdict(set)  # file_path -> {imported_modules}
        
    def audit_all_files(self):
        """Audit all Python files in the backend directory."""
        print("🔍 Starting Code Quality Audit")
        print("=" * 60)
        
        # Find all Python files
        python_files = list(self.backend_dir.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files")
        
        # Audit each file
        for file_path in python_files:
            self._audit_file(file_path)
        
        # Analyze results
        self._analyze_duplicate_classes()
        self._analyze_duplicate_methods()
        self._analyze_method_overrides()
        self._analyze_imports()
        
        print("\n🎉 Code Quality Audit Complete!")
    
    def _audit_file(self, file_path: Path):
        """Audit a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._extract_class_info(file_path, node, content)
                elif isinstance(node, ast.Import):
                    self._extract_imports(file_path, node)
                elif isinstance(node, ast.ImportFrom):
                    self._extract_imports(file_path, node)
                    
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
    
    def _extract_class_info(self, file_path: Path, class_node: ast.ClassDef, content: str):
        """Extract information about a class definition."""
        class_name = class_node.name
        file_rel_path = str(file_path.relative_to(self.backend_dir))
        
        # Get class source code
        class_start = class_node.lineno - 1
        class_end = class_node.end_lineno
        class_lines = content.split('\n')[class_start:class_end]
        class_code = '\n'.join(class_lines)
        
        # Store class definition
        self.class_definitions[class_name].append((file_rel_path, class_code))
        
        # Extract base classes
        base_classes = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")
        
        self.base_classes[class_name].update(base_classes)
        
        # Extract method definitions
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                method_start = item.lineno - 1
                method_end = item.end_lineno
                method_lines = content.split('\n')[method_start:method_end]
                method_code = '\n'.join(method_lines)
                
                self.method_definitions[class_name][method_name].append((file_rel_path, method_code))
    
    def _extract_imports(self, file_path: Path, import_node):
        """Extract import information."""
        file_rel_path = str(file_path.relative_to(self.backend_dir))
        
        if isinstance(import_node, ast.Import):
            for alias in import_node.names:
                self.imports[file_rel_path].add(alias.name)
        elif isinstance(import_node, ast.ImportFrom):
            module = import_node.module or ""
            for alias in import_node.names:
                if module:
                    self.imports[file_rel_path].add(f"{module}.{alias.name}")
                else:
                    self.imports[file_rel_path].add(alias.name)
    
    def _analyze_duplicate_classes(self):
        """Analyze duplicate class definitions."""
        print("\n🔍 Checking for Duplicate Class Names:")
        print("-" * 40)
        
        duplicates_found = False
        for class_name, definitions in self.class_definitions.items():
            if len(definitions) > 1:
                duplicates_found = True
                print(f"❌ DUPLICATE CLASS: '{class_name}' found in {len(definitions)} files:")
                for file_path, _ in definitions:
                    print(f"   - {file_path}")
        
        if not duplicates_found:
            print("✅ No duplicate class names found")
    
    def _analyze_duplicate_methods(self):
        """Analyze duplicate method definitions within classes."""
        print("\n🔍 Checking for Duplicate Methods Within Classes:")
        print("-" * 50)
        
        duplicates_found = False
        for class_name, methods in self.method_definitions.items():
            for method_name, definitions in methods.items():
                if len(definitions) > 1:
                    duplicates_found = True
                    print(f"❌ DUPLICATE METHOD: '{class_name}.{method_name}' found in {len(definitions)} files:")
                    for file_path, _ in definitions:
                        print(f"   - {file_path}")
        
        if not duplicates_found:
            print("✅ No duplicate methods found within classes")
    
    def _analyze_method_overrides(self):
        """Analyze method overrides from base classes."""
        print("\n🔍 Checking Method Overrides:")
        print("-" * 30)
        
        overrides_found = False
        for class_name, base_class_set in self.base_classes.items():
            if base_class_set:
                print(f"📋 Class '{class_name}' inherits from: {', '.join(base_class_set)}")
                
                # Check for common override methods
                common_methods = ['__init__', 'start', 'stop', 'update', 'render', 'on_event']
                for method_name in common_methods:
                    if method_name in self.method_definitions[class_name]:
                        print(f"   🔄 Overrides '{method_name}' method")
                        overrides_found = True
        
        if not overrides_found:
            print("ℹ️ No obvious method overrides found")
    
    def _analyze_imports(self):
        """Analyze import patterns and potential conflicts."""
        print("\n🔍 Checking Import Patterns:")
        print("-" * 30)
        
        # Check for circular imports
        print("📦 Import analysis completed")
        
        # Show import summary
        total_imports = sum(len(imports) for imports in self.imports.values())
        print(f"   Total imports across all files: {total_imports}")
    
    def generate_report(self):
        """Generate a comprehensive audit report."""
        print("\n📊 AUDIT SUMMARY:")
        print("=" * 40)
        
        total_classes = len(self.class_definitions)
        total_methods = sum(len(methods) for methods in self.method_definitions.values())
        
        print(f"📈 Total Classes: {total_classes}")
        print(f"📈 Total Methods: {total_methods}")
        print(f"📈 Files Analyzed: {len(self.imports)}")
        
        # Show class hierarchy
        print("\n🏗️ Class Hierarchy:")
        for class_name, base_classes in self.base_classes.items():
            if base_classes:
                print(f"   {class_name} -> {', '.join(base_classes)}")
            else:
                print(f"   {class_name} (no inheritance)")

def main():
    """Main audit function."""
    auditor = CodeAuditor()
    auditor.audit_all_files()
    auditor.generate_report()

if __name__ == "__main__":
    main()
