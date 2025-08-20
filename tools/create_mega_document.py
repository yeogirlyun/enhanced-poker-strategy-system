#!/usr/bin/env python3
"""
🔧 **UNIVERSAL MEGA DOCUMENT GENERATOR**

A configurable tool to create comprehensive mega documents for different purposes:
- Bug Reports with source code analysis
- Requirements documents with implementation details
- Architecture documentation with code examples
- Feature specifications with complete source
- Testing documentation with test cases

Supports JSON configuration files for different document types and templates.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

class MegaDocumentGenerator:
    """Universal mega document generator with configurable templates."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize with optional configuration file."""
        self.templates = self._load_default_templates()
        if config_file:
            self.load_config(config_file)
    
    def _load_default_templates(self) -> Dict[str, Any]:
        """Load default document templates."""
        return {
            "bug_report": {
                "title": "🚨 **COMPREHENSIVE BUG REPORT - ALL IN ONE**",
                "description": "Complete bug analysis with source code, reproduction steps, and resolution details.",
                "output_dir": "bug_report",
                "filename": "COMPREHENSIVE_BUG_REPORT_WITH_SOURCE.md",
                "categories": [
                    {
                        "name": "BUG ANALYSIS",
                        "files": [
                            "*.md|**/BUG*.md",
                            "**/ANALYSIS*.md",
                            "**/ERROR*.md"
                        ]
                    },
                    {
                        "name": "AFFECTED SOURCE CODE",
                        "files": [
                            "backend/ui/**/*.py",
                            "backend/core/**/*.py",
                            "backend/services/**/*.py"
                        ]
                    },
                    {
                        "name": "CONFIGURATION FILES",
                        "files": [
                            "**/*.json|config",
                            "**/*.yaml",
                            "**/requirements.txt"
                        ]
                    },
                    {
                        "name": "TEST CASES",
                        "files": [
                            "**/test_*.py",
                            "**/tests/**/*.py"
                        ]
                    }
                ]
            },
            "requirements": {
                "title": "📋 **COMPREHENSIVE REQUIREMENTS DOCUMENT**",
                "description": "Complete requirements specification with implementation details and source code.",
                "output_dir": "req_requests",
                "filename": "REQUIREMENTS_MEGA_DOCUMENT.md",
                "categories": [
                    {
                        "name": "REQUIREMENTS SPECIFICATION",
                        "files": [
                            "*REQUIREMENTS*.md",
                            "*REQ*.md",
                            "*SPEC*.md"
                        ]
                    },
                    {
                        "name": "ARCHITECTURE DOCUMENTATION",
                        "files": [
                            "docs/*ARCHITECTURE*.md",
                            "docs/*DESIGN*.md",
                            "docs/PROJECT_PRINCIPLES*.md"
                        ]
                    },
                    {
                        "name": "IMPLEMENTATION SOURCE",
                        "files": [
                            "backend/ui/**/*.py",
                            "backend/core/**/*.py"
                        ]
                    },
                    {
                        "name": "CONFIGURATION & DATA",
                        "files": [
                            "backend/data/**/*.json",
                            "**/theme*.json",
                            "**/config*.json"
                        ]
                    }
                ]
            },
            "architecture": {
                "title": "🏗️ **COMPREHENSIVE ARCHITECTURE DOCUMENT**",
                "description": "Complete system architecture with implementation examples and design patterns.",
                "output_dir": "docs",
                "filename": "ARCHITECTURE_MEGA_DOCUMENT.md",
                "categories": [
                    {
                        "name": "ARCHITECTURE DOCUMENTATION",
                        "files": [
                            "docs/**/*.md"
                        ]
                    },
                    {
                        "name": "CORE IMPLEMENTATION",
                        "files": [
                            "backend/core/**/*.py",
                            "backend/services/**/*.py"
                        ]
                    },
                    {
                        "name": "UI IMPLEMENTATION",
                        "files": [
                            "backend/ui/**/*.py"
                        ]
                    },
                    {
                        "name": "TESTING FRAMEWORK",
                        "files": [
                            "**/test_*.py",
                            "**/tests/**/*.py"
                        ]
                    }
                ]
            },
            "feature": {
                "title": "🚀 **COMPREHENSIVE FEATURE DOCUMENT**",
                "description": "Complete feature specification with implementation and testing details.",
                "output_dir": "features",
                "filename": "FEATURE_MEGA_DOCUMENT.md",
                "categories": [
                    {
                        "name": "FEATURE SPECIFICATION",
                        "files": [
                            "*FEATURE*.md",
                            "*SPEC*.md"
                        ]
                    },
                    {
                        "name": "IMPLEMENTATION CODE",
                        "files": [
                            "backend/**/*.py"
                        ]
                    },
                    {
                        "name": "UI COMPONENTS",
                        "files": [
                            "backend/ui/**/*.py"
                        ]
                    },
                    {
                        "name": "TESTING SUITE",
                        "files": [
                            "**/test_*.py"
                        ]
                    }
                ]
            },
            "mvu": {
                "title": "🔄 **MVU ARCHITECTURE MEGA DOCUMENT**",
                "description": "Complete MVU implementation with infinite loop prevention and best practices.",
                "output_dir": "mvu_docs",
                "filename": "MVU_COMPLETE_IMPLEMENTATION.md",
                "categories": [
                    {
                        "name": "MVU ARCHITECTURE GUIDE",
                        "files": [
                            "docs/*MVU*.md",
                            "docs/*ARCHITECTURE*.md"
                        ]
                    },
                    {
                        "name": "MVU IMPLEMENTATION",
                        "files": [
                            "backend/ui/mvu/**/*.py"
                        ]
                    },
                    {
                        "name": "MODEL & TYPES",
                        "files": [
                            "**/types.py",
                            "**/store.py",
                            "**/update.py"
                        ]
                    },
                    {
                        "name": "VIEW RENDERING",
                        "files": [
                            "**/view.py",
                            "**/renderer*.py"
                        ]
                    },
                    {
                        "name": "INFINITE LOOP PREVENTION",
                        "files": [
                            "**/test_mvu*.py",
                            "**/*BUG_REPORT*.md"
                        ]
                    }
                ]
            }
        }
    
    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.templates.update(config.get('templates', {}))
        except FileNotFoundError:
            print(f"⚠️ Config file not found: {config_file}. Using defaults.")
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in config file: {e}. Using defaults.")
    
    def _find_files(self, source_path: Path, pattern: str) -> List[Path]:
        """Find files matching a pattern with glob support."""
        files = []
        
        # Handle special syntax: "pattern|keyword" means files matching pattern AND containing keyword
        if '|' in pattern:
            glob_pattern, keyword = pattern.split('|', 1)
            potential_files = list(source_path.glob(glob_pattern))
            for file_path in potential_files:
                if keyword.lower() in str(file_path).lower():
                    files.append(file_path)
        else:
            files.extend(source_path.glob(pattern))
        
        return [f for f in files if f.is_file()]
    
    def _get_file_language(self, filename: str) -> str:
        """Determine syntax highlighting language from filename."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql',
            '.sh': 'bash',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml'
        }
        
        suffix = Path(filename).suffix.lower()
        return ext_map.get(suffix, 'text')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"
    
    def _handle_large_file(self, file_path: Path, max_lines: int = 100) -> str:
        """Handle large files by truncating or summarizing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if len(lines) <= max_lines:
                return ''.join(lines)
            
            # For large files, show first part and summary
            first_part = ''.join(lines[:max_lines//2])
            last_part = ''.join(lines[-max_lines//2:])
            
            summary = f"\n\n# FILE TRUNCATED FOR BREVITY\n"
            summary += f"# Showing first {max_lines//2} and last {max_lines//2} lines\n"
            summary += f"# Total lines: {len(lines)}\n"
            summary += f"# File size: {self._format_file_size(file_path.stat().st_size)}\n\n"
            
            return first_part + summary + last_part
            
        except Exception as e:
            return f"ERROR READING FILE: {e}"
    
    def generate_document(self, 
                         template_name: str,
                         source_dir: str = ".",
                         output_dir: Optional[str] = None,
                         filename: Optional[str] = None,
                         max_file_lines: int = 1000) -> Path:
        """Generate a mega document using the specified template."""
        
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.templates.keys())}")
        
        template = self.templates[template_name]
        
        # Convert to Path objects
        source_path = Path(source_dir).resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source_path}")
        
        # Determine output directory and filename
        output_dir = output_dir or template["output_dir"]
        filename = filename or template["filename"]
        
        output_path = Path(output_dir).resolve()
        output_path.mkdir(exist_ok=True)
        
        output_file = output_path / filename
        
        print(f"🔧 Creating {template_name} mega document: {output_file}")
        print(f"📁 Source directory: {source_path}")
        print(f"📁 Output directory: {output_path}")
        
        # Statistics
        total_files = 0
        total_size = 0
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Write header
            outfile.write(f"# {template['title']}\n\n")
            outfile.write("## 📋 **DOCUMENT OVERVIEW**\n\n")
            outfile.write(f"{template['description']}\n\n")
            outfile.write(f"**Template**: {template_name}\n\n")
            outfile.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            outfile.write(f"**Source Directory**: `{source_path}`\n\n")
            outfile.write(f"**Output Directory**: `{output_path}`\n\n")
            outfile.write("---\n\n")
            
            # Process each category
            for category in template["categories"]:
                category_name = category["name"]
                file_patterns = category["files"]
                
                print(f"📂 Processing category: {category_name}")
                outfile.write(f"## {category_name}\n\n")
                
                # Collect all files for this category
                category_files = []
                for pattern in file_patterns:
                    found_files = self._find_files(source_path, pattern)
                    category_files.extend(found_files)
                
                # Remove duplicates and sort
                category_files = sorted(list(set(category_files)))
                
                if not category_files:
                    print(f"  ⚠️  No files found for category: {category_name}")
                    outfile.write(f"*No files found matching patterns: {', '.join(file_patterns)}*\n\n")
                    continue
                
                # Process each file in the category
                for file_path in category_files:
                    display_name = file_path.name
                    relative_path = file_path.relative_to(source_path)
                    
                    print(f"  📄 Adding: {display_name}")
                    
                    # Write file header
                    outfile.write(f"### {display_name}\n\n")
                    outfile.write(f"**Path**: `{relative_path}`\n\n")
                    outfile.write(f"**Size**: {self._format_file_size(file_path.stat().st_size)}\n\n")
                    
                    # Write file content with syntax highlighting
                    language = self._get_file_language(display_name)
                    outfile.write(f"```{language}\n")
                    
                    # Handle large files
                    if file_path.stat().st_size > 500 * 1024:  # 500KB
                        content = self._handle_large_file(file_path, max_file_lines)
                    else:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                        except Exception as e:
                            content = f"ERROR READING FILE: {e}"
                    
                    outfile.write(content)
                    if not content.endswith('\n'):
                        outfile.write('\n')
                    
                    outfile.write("```\n\n")
                    outfile.write("---\n\n")
                    
                    # Update statistics
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            # Write footer with statistics
            outfile.write("## 📊 **DOCUMENT STATISTICS**\n\n")
            outfile.write(f"- **Total Files Included**: {total_files}\n")
            outfile.write(f"- **Total Source Size**: {self._format_file_size(total_size)}\n")
            outfile.write(f"- **Categories Processed**: {len(template['categories'])}\n")
            outfile.write(f"- **Generation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            outfile.write("## 📋 **END OF MEGA DOCUMENT**\n\n")
            outfile.write(f"*This comprehensive {template_name} document contains all relevant information and source code.*\n")
        
        # Final statistics
        output_size = output_file.stat().st_size
        print(f"\n✅ {template_name.title()} mega document created: {output_file}")
        print(f"📊 Output size: {self._format_file_size(output_size)}")
        print(f"📊 Files included: {total_files}")
        print(f"📊 Source size: {self._format_file_size(total_size)}")
        
        return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="🔧 Universal Mega Document Generator - Create comprehensive documents with source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 **AVAILABLE TEMPLATES:**

  bug_report     - Comprehensive bug analysis with source code
  requirements   - Requirements specification with implementation
  architecture   - System architecture with code examples  
  feature        - Feature specification with implementation
  mvu            - MVU architecture with infinite loop prevention

📝 **EXAMPLES:**

  # Create bug report in bug_report/ folder
  python3 create_mega_document.py bug_report
  
  # Create requirements document in req_requests/ folder  
  python3 create_mega_document.py requirements
  
  # Create architecture document in docs/ folder
  python3 create_mega_document.py architecture
  
  # Create MVU documentation with custom output
  python3 create_mega_document.py mvu --output ./mvu_analysis --filename MVU_DEEP_DIVE.md
  
  # Use custom source directory
  python3 create_mega_document.py feature --source /path/to/project
  
  # List available templates
  python3 create_mega_document.py --list-templates

🔧 **ADVANCED USAGE:**

  # Use custom configuration file
  python3 create_mega_document.py bug_report --config my_templates.json
  
  # Control file size limits
  python3 create_mega_document.py architecture --max-lines 500
        """
    )
    
    parser.add_argument(
        'template',
        nargs='?',
        help='Document template to use (bug_report, requirements, architecture, feature, mvu)'
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory containing all source files (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output directory for the document (default: template-specific)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        help='Output filename (default: template-specific)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='JSON configuration file with custom templates'
    )
    
    parser.add_argument(
        '--max-lines',
        type=int,
        default=1000,
        help='Maximum lines to include from large files (default: 1000)'
    )
    
    parser.add_argument(
        '--list-templates', '-l',
        action='store_true',
        help='List available templates and exit'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize generator
        generator = MegaDocumentGenerator(args.config)
        
        # List templates if requested
        if args.list_templates:
            print("🎯 **AVAILABLE DOCUMENT TEMPLATES:**\n")
            for name, template in generator.templates.items():
                print(f"  📋 **{name}**")
                print(f"     {template['description']}")
                print(f"     Output: {template['output_dir']}/{template['filename']}")
                print()
            return
        
        if not args.template:
            print("❌ Error: Template name required. Use --list-templates to see available options.")
            sys.exit(1)
        
        # Generate document
        output_file = generator.generate_document(
            template_name=args.template,
            source_dir=args.source,
            output_dir=args.output,
            filename=args.filename,
            max_file_lines=args.max_lines
        )
        
        print(f"\n🎯 Success! Mega document created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating mega document: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
