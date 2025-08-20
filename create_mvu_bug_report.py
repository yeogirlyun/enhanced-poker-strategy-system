#!/usr/bin/env python3
"""
MVU Infinite Rendering Loop Bug Report Creator
Creates a comprehensive bug report with all relevant source code for the MVU infinite rendering loop issue
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_mvu_bug_report(source_dir, output_dir, output_filename):
    """Create comprehensive bug report for MVU infinite rendering loop with all source code."""
    
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
    
    # Define file categories and their order - focused on MVU architecture
    file_categories = [
        ("BUG REPORT SUMMARY", [
            (source_path / "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md", "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md"),
        ]),
        ("MVU ARCHITECTURE - CORE FILES", [
            (source_path / "backend" / "ui" / "mvu" / "types.py", "mvu/types.py"),
            (source_path / "backend" / "ui" / "mvu" / "update.py", "mvu/update.py"),
            (source_path / "backend" / "ui" / "mvu" / "store.py", "mvu/store.py"),
            (source_path / "backend" / "ui" / "mvu" / "view.py", "mvu/view.py"),
            (source_path / "backend" / "ui" / "mvu" / "drivers.py", "mvu/drivers.py"),
            (source_path / "backend" / "ui" / "mvu" / "__init__.py", "mvu/__init__.py"),
        ]),
        ("MVU HANDS REVIEW IMPLEMENTATION", [
            (source_path / "backend" / "ui" / "mvu" / "hands_review_mvu.py", "mvu/hands_review_mvu.py"),
        ]),
        ("INTEGRATION AND APP SHELL", [
            (source_path / "backend" / "ui" / "app_shell.py", "app_shell.py"),
            (source_path / "backend" / "run_new_ui.py", "run_new_ui.py"),
        ]),
        ("DEPRECATED/LEGACY FILES (for reference)", [
            (source_path / "backend" / "ui" / "tabs" / "deprecated" / "hands_review_tab_legacy.py", "deprecated/hands_review_tab_legacy.py"),
        ]),
        ("TEST FILES", [
            (source_path / "backend" / "test_mvu_implementation.py", "test_mvu_implementation.py"),
            (source_path / "backend" / "test_mvu_simple.py", "test_mvu_simple.py"),
        ]),
        ("SUPPORTING SERVICES", [
            (source_path / "backend" / "ui" / "services" / "service_container.py", "services/service_container.py"),
            (source_path / "backend" / "ui" / "services" / "event_bus.py", "services/event_bus.py"),
            (source_path / "backend" / "ui" / "services" / "game_director.py", "services/game_director.py"),
            (source_path / "backend" / "ui" / "services" / "effect_bus.py", "services/effect_bus.py"),
            (source_path / "backend" / "ui" / "services" / "theme_manager.py", "services/theme_manager.py"),
        ]),
        ("ARCHITECTURE DOCUMENTATION", [
            (source_path / "docs" / "PROJECT_PRINCIPLES_v2.md", "PROJECT_PRINCIPLES_v2.md"),
            (source_path / "docs" / "PokerPro_Trainer_Complete_Architecture_v3.md", "PokerPro_Trainer_Complete_Architecture_v3.md"),
        ]),
        ("DEBUG LOGS AND OUTPUT", [
            # This will be added manually in the report
        ])
    ]
    
    print(f"🔧 Creating MVU infinite rendering loop bug report: {output_file}")
    print(f"📁 Source directory: {source_path}")
    print(f"📁 Output directory: {output_path}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("# 🚨 MVU INFINITE RENDERING LOOP - COMPREHENSIVE BUG REPORT\n\n")
        outfile.write("**Issue**: MVU (Model-View-Update) poker hands review tab stuck in infinite rendering loop\n\n")
        outfile.write("**Symptoms**: Application becomes unresponsive due to continuous alternating renders between 0 and 2 seats\n\n")
        outfile.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        outfile.write(f"**Source Directory**: `{source_path}`\n\n")
        outfile.write("---\n\n")
        
        # Add debug output section
        outfile.write("## 🔍 DEBUG OUTPUT PATTERN\n\n")
        outfile.write("The following infinite loop pattern was observed:\n\n")
        outfile.write("```\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 2 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 0 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("[Pattern repeats infinitely...]\n")
        outfile.write("```\n\n")
        outfile.write("**Key Observation**: Despite identical cursor and waiting state values, `Props equal: False` and `Seats equal: False` always, indicating object identity issues.\n\n")
        outfile.write("---\n\n")
        
        # Process each category
        for category_name, file_list in file_categories:
            if not file_list:  # Skip empty categories
                continue
                
            print(f"📂 Processing category: {category_name}")
            
            # Write category header
            outfile.write(f"## {category_name}\n\n")
            
            # Process each file in the category
            for file_path, display_name in file_list:
                if file_path.exists():
                    print(f"  📄 Adding: {display_name}")
                    
                    # Write file header
                    outfile.write(f"### {display_name}\n\n")
                    outfile.write(f"**Path**: `{file_path}`\n\n")
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
        
        # Add analysis section
        outfile.write("## 🎯 ROOT CAUSE ANALYSIS\n\n")
        outfile.write("### Primary Issue\n")
        outfile.write("The `TableRendererProps` objects are being recreated on every model update via `TableRendererProps.from_model(model)`, ")
        outfile.write("causing the equality check `self.current_props == props` to always fail, even when the actual data is identical.\n\n")
        
        outfile.write("### Key Problem Areas\n")
        outfile.write("1. **Fresh Object Creation**: `TableRendererProps.from_model()` creates new instances every time\n")
        outfile.write("2. **Nested Object Inequality**: The `seats` dictionary contains `SeatState` objects that may be recreated\n")
        outfile.write("3. **Model Update Frequency**: Frequent model updates trigger unnecessary re-renders\n")
        outfile.write("4. **Props Comparison Logic**: Dataclass equality fails due to nested mutable objects\n\n")
        
        outfile.write("### Reproduction Steps\n")
        outfile.write("1. Start application: `python3 backend/run_new_ui.py`\n")
        outfile.write("2. Navigate to 'Hands Review' tab\n")
        outfile.write("3. Observe infinite console output and unresponsive UI\n")
        outfile.write("4. Application must be terminated with Ctrl+C\n\n")
        
        outfile.write("---\n\n")
        
        # Add proposed solutions
        outfile.write("## 💡 PROPOSED SOLUTIONS\n\n")
        outfile.write("### Solution 1: Props Memoization\n")
        outfile.write("Cache `TableRendererProps` objects and only create new ones when underlying data actually changes:\n\n")
        outfile.write("```python\n")
        outfile.write("class MVUHandsReviewTab:\n")
        outfile.write("    def __init__(self, ...):\n")
        outfile.write("        self._cached_props = None\n")
        outfile.write("        self._last_model_hash = None\n")
        outfile.write("    \n")
        outfile.write("    def _on_model_changed(self, model: Model) -> None:\n")
        outfile.write("        # Create hash of relevant model data\n")
        outfile.write("        model_hash = hash((id(model.seats), model.review_cursor, model.waiting_for))\n")
        outfile.write("        \n")
        outfile.write("        # Only create new props if model actually changed\n")
        outfile.write("        if model_hash != self._last_model_hash:\n")
        outfile.write("            self._cached_props = TableRendererProps.from_model(model)\n")
        outfile.write("            self._last_model_hash = model_hash\n")
        outfile.write("        \n")
        outfile.write("        if self.table_renderer and self._cached_props:\n")
        outfile.write("            self.table_renderer.render(self._cached_props)\n")
        outfile.write("```\n\n")
        
        outfile.write("### Solution 2: Deep Equality Check\n")
        outfile.write("Implement proper deep comparison for `TableRendererProps`:\n\n")
        outfile.write("```python\n")
        outfile.write("@dataclass(frozen=True)\n")
        outfile.write("class TableRendererProps:\n")
        outfile.write("    # ... fields ...\n")
        outfile.write("    \n")
        outfile.write("    def __eq__(self, other):\n")
        outfile.write("        if not isinstance(other, TableRendererProps):\n")
        outfile.write("            return False\n")
        outfile.write("        \n")
        outfile.write("        return (\n")
        outfile.write("            self.seats == other.seats and\n")
        outfile.write("            self.board == other.board and\n")
        outfile.write("            self.pot == other.pot and\n")
        outfile.write("            # ... compare all fields\n")
        outfile.write("        )\n")
        outfile.write("```\n\n")
        
        outfile.write("### Solution 3: Selective Subscription\n")
        outfile.write("Only notify view subscribers when rendering-relevant fields actually change.\n\n")
        
        # Write footer
        outfile.write("---\n\n")
        outfile.write("## 📋 END OF MVU INFINITE RENDERING LOOP BUG REPORT\n\n")
        outfile.write("**Priority**: HIGH - Application completely unusable\n\n")
        outfile.write("**Environment**: Python 3.13.2, Tkinter, MVU Architecture, macOS\n\n")
        outfile.write("*This comprehensive report contains all source code and analysis needed to resolve the MVU infinite rendering loop issue.*\n")
    
    print(f"\n✅ MVU bug report created: {output_file}")
    
    # Get file size
    file_size = output_file.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Create comprehensive MVU infinite rendering loop bug report",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory containing all source files (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory for the bug report (default: current directory)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        default='MVU_INFINITE_RENDERING_LOOP_COMPREHENSIVE_BUG_REPORT.md',
        help='Output filename (default: MVU_INFINITE_RENDERING_LOOP_COMPREHENSIVE_BUG_REPORT.md)'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = create_mvu_bug_report(
            source_dir=args.source,
            output_dir=args.output,
            output_filename=args.filename
        )
        
        print(f"\n🎯 Success! MVU bug report created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating MVU bug report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
