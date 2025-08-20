#!/usr/bin/env python3
"""
Comprehensive Bug Report Creator
Concatenates all bug report files into one comprehensive file
Accepts command-line parameters for flexibility
"""

import os
import sys
import argparse
from pathlib import Path

def create_comprehensive_bug_report(source_dir, output_dir, output_filename):
    """Create one comprehensive bug report file with all source code."""
    
    # Convert to Path objects
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()
    
    # Ensure source directory exists
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    # Ensure output directory exists
    output_path.mkdir(exist_ok=True)
    
    # Define the output file
    output_file = output_path / output_filename
    
    # Define file categories and their order with correct paths
    file_categories = [
        ("BUG REPORT DOCUMENTATION", [
            (source_path / "COMPREHENSIVE_UI_BUG_REPORT.md", "COMPREHENSIVE_UI_BUG_REPORT.md"),
            (source_path / "COMPREHENSIVE_UI_BUG_REPORT_README.md", "COMPREHENSIVE_UI_BUG_REPORT_README.md")
        ]),
        ("CORE SOURCE CODE", [
            (source_path / "backend" / "ui" / "services" / "effect_bus.py", "effect_bus.py"),
            (source_path / "backend" / "ui" / "services" / "hands_review_session_manager.py", "hands_review_session_manager.py"),
            (source_path / "backend" / "ui" / "tabs" / "hands_review_tab.py", "hands_review_tab.py"),
            (source_path / "backend" / "ui" / "app_shell.py", "app_shell.py"),
            (source_path / "backend" / "sounds" / "poker_sound_config.json", "poker_sound_config.json"),
            (source_path / "backend" / "core" / "poker_types.py", "poker_types.py"),
            (source_path / "backend" / "core" / "hand_model.py", "hand_model.py"),
            (source_path / "backend" / "fix_runtime_errors.py", "fix_runtime_errors.py"),
            (source_path / "backend" / "run_new_ui.py", "run_new_ui.py")
        ]),
        ("UI COMPONENT SYSTEM", [
            (source_path / "backend" / "ui" / "tableview" / "components" / "chip_animations.py", "chip_animations.py"),
            (source_path / "backend" / "ui" / "tableview" / "components" / "chip_graphics.py", "chip_graphics.py"),
            (source_path / "backend" / "ui" / "tableview" / "components" / "token_driven_renderer.py", "token_driven_renderer.py"),
            (source_path / "backend" / "ui" / "tableview" / "components" / "enhanced_cards.py", "enhanced_cards.py"),
            (source_path / "backend" / "ui" / "tableview" / "components" / "premium_chips.py", "premium_chips.py")
        ]),
        ("THEME SYSTEM", [
            (source_path / "backend" / "ui" / "services" / "theme_manager.py", "theme_manager.py"),
            (source_path / "backend" / "ui" / "services" / "theme_factory.py", "theme_factory.py"),
            (source_path / "backend" / "ui" / "services" / "theme_loader_consolidated.py", "theme_loader_consolidated.py"),
            (source_path / "backend" / "ui" / "services" / "theme_utils.py", "theme_utils.py"),
            (source_path / "backend" / "ui" / "services" / "state_styler.py", "state_styler.py"),
            (source_path / "backend" / "ui" / "services" / "theme_derive.py", "theme_derive.py"),
            (source_path / "backend" / "ui" / "services" / "theme_manager_clean.py", "theme_manager_clean.py")
        ]),
        ("ARCHITECTURE DOCUMENTATION", [
            (source_path / "docs" / "PokerPro_Trainer_Complete_Architecture_v3.md", "PokerPro_Trainer_Complete_Architecture_v3.md"),
            (source_path / "docs" / "PokerPro_UI_Implementation_Handbook_v1.1.md", "PokerPro_UI_Implementation_Handbook_v1.1.md"),
            (source_path / "docs" / "PROJECT_PRINCIPLES_v2.md", "PROJECT_PRINCIPLES_v2.md"),
            (source_path / "backend" / "RUNTIME_FIXES_README.md", "RUNTIME_FIXES_README.md")
        ])
    ]
    
    print(f"🔧 Creating comprehensive bug report: {output_file}")
    print(f"📁 Source directory: {source_path}")
    print(f"📁 Output directory: {output_path}")
    print(f"📁 Working directory: {Path.cwd()}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("# 🚨 COMPREHENSIVE UI BUG REPORT - ALL IN ONE\n\n")
        outfile.write("This file contains the complete bug report, all source code, and documentation in one comprehensive file.\n\n")
        outfile.write(f"**Source Directory:** `{source_path}`\n")
        outfile.write("**Generated:** $(date)\n\n")
        outfile.write("---\n\n")
        
        # Process each category
        for category_name, file_list in file_categories:
            print(f"📂 Processing category: {category_name}")
            
            # Write category header
            outfile.write(f"## {category_name}\n\n")
            
            # Process each file in the category
            for file_path, display_name in file_list:
                if file_path.exists():
                    print(f"  📄 Adding: {display_name}")
                    
                    # Write file header
                    outfile.write(f"### {display_name}\n\n")
                    outfile.write("```")
                    
                    # Determine file extension for syntax highlighting
                    if display_name.endswith('.py'):
                        outfile.write("python")
                    elif display_name.endswith('.json'):
                        outfile.write("json")
                    elif display_name.endswith('.md'):
                        outfile.write("markdown")
                    else:
                        outfile.write("text")
                    
                    outfile.write("\n")
                    
                    # Read and write file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        outfile.write(f"ERROR READING FILE: {e}")
                    
                    outfile.write("\n```\n\n")
                    outfile.write("---\n\n")
                else:
                    print(f"  ⚠️  File not found: {display_name} at {file_path}")
        
        # Write footer
        outfile.write("## 📋 END OF COMPREHENSIVE BUG REPORT\n\n")
        outfile.write("*This file contains all the information needed to resolve the UI coordination issues while maintaining architecture compliance.*\n")
    
    print(f"\n✅ Comprehensive bug report created: {output_file}")
    
    # Get file size
    file_size = output_file.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Create a comprehensive bug report with all source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create bug report from current directory to bug_report folder
  python3 create_comprehensive_bug_report.py
  
  # Create bug report from specific source directory
  python3 create_comprehensive_bug_report.py --source /path/to/source
  
  # Create bug report with custom output location and filename
  python3 create_comprehensive_bug_report.py --source /path/to/source --output /path/to/output --filename my_bug_report.md
  
  # Use default Poker project structure
  python3 create_comprehensive_bug_report.py --poker-default
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory containing all source files (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='bug_report',
        help='Output directory for the bug report (default: bug_report)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        default='COMPREHENSIVE_BUG_REPORT_ALL_IN_ONE.md',
        help='Output filename (default: COMPREHENSIVE_BUG_REPORT_ALL_IN_ONE.md)'
    )
    
    parser.add_argument(
        '--poker-default', '-p',
        action='store_true',
        help='Use default Poker project structure (source: current dir, output: bug_report/)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.poker_default:
            # Use default Poker project structure
            current_dir = Path.cwd()
            poker_root = current_dir
            
            # Find the Poker project root (look for backend folder)
            while poker_root != poker_root.parent and not (poker_root / "backend").exists():
                poker_root = poker_root.parent
            
            if not (poker_root / "backend").exists():
                raise FileNotFoundError("Could not find Poker project root directory")
            
            source_dir = poker_root
            output_dir = poker_root / "bug_report"
            print(f"🎯 Using Poker project defaults:")
            print(f"   Source: {source_dir}")
            print(f"   Output: {output_dir}")
        else:
            source_dir = args.source
            output_dir = args.output
        
        output_file = create_comprehensive_bug_report(
            source_dir=source_dir,
            output_dir=output_dir,
            output_filename=args.filename
        )
        
        print(f"\n🎯 Success! Comprehensive bug report created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating comprehensive bug report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
