#!/usr/bin/env python3
"""
MVU Persistent Infinite Loop Bug Report Generator
Creates a comprehensive bug report for the still-occurring infinite rendering loop
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

def create_persistent_loop_bug_report(source_dir, output_dir, output_filename):
    """Create comprehensive bug report for persistent MVU infinite rendering loop."""
    
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
    
    # Define file categories - focused on the persistent loop issue
    file_categories = [
        ("BUG DESCRIPTION AND EVIDENCE", [
            # This will be written manually in the report
        ]),
        ("CURRENT MVU IMPLEMENTATION (POST-FIX)", [
            (source_path / "backend" / "ui" / "mvu" / "types.py", "mvu/types.py"),
            (source_path / "backend" / "ui" / "mvu" / "update.py", "mvu/update.py"),
            (source_path / "backend" / "ui" / "mvu" / "store.py", "mvu/store.py"),
            (source_path / "backend" / "ui" / "mvu" / "view.py", "mvu/view.py"),
            (source_path / "backend" / "ui" / "mvu" / "hands_review_mvu.py", "mvu/hands_review_mvu.py"),
        ]),
        ("DEBUGGING AND LOGS", [
            # This will be added manually
        ]),
        ("RELATED INFRASTRUCTURE", [
            (source_path / "backend" / "ui" / "mvu" / "drivers.py", "mvu/drivers.py"),
            (source_path / "backend" / "ui" / "app_shell.py", "app_shell.py"),
            (source_path / "backend" / "run_new_ui.py", "run_new_ui.py"),
        ]),
        ("PREVIOUS FIX ATTEMPTS", [
            (source_path / "MVU_INFINITE_LOOP_FIX_SUMMARY.md", "MVU_INFINITE_LOOP_FIX_SUMMARY.md"),
            (source_path / "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md", "MVU_INFINITE_RENDERING_LOOP_BUG_REPORT.md"),
        ]),
        ("ARCHITECTURE REFERENCES", [
            (source_path / "docs" / "PROJECT_PRINCIPLES_v2.md", "PROJECT_PRINCIPLES_v2.md"),
        ])
    ]
    
    print(f"🔧 Creating persistent MVU loop bug report: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("# 🚨 MVU PERSISTENT INFINITE RENDERING LOOP - CRITICAL BUG\n\n")
        outfile.write("**Status**: UNRESOLVED - Loop persists despite multiple fix attempts\n\n")
        outfile.write("**Severity**: CRITICAL - Application completely unusable\n\n")
        outfile.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        outfile.write("---\n\n")
        
        # Add the persistent issue description
        outfile.write("## 🔥 PERSISTENT ISSUE DESCRIPTION\n\n")
        outfile.write("Despite implementing the following fixes:\n")
        outfile.write("- ✅ Value-equal dataclasses with `@dataclass(frozen=True, eq=True, slots=True)`\n")
        outfile.write("- ✅ Proper props memoization with early-out comparison\n")
        outfile.write("- ✅ Removed UpdateUI command entirely\n")
        outfile.write("- ✅ Immutable data structures (tuples instead of lists)\n\n")
        outfile.write("**THE INFINITE LOOP STILL PERSISTS!**\n\n")
        
        # Add debug evidence
        outfile.write("## 🔍 CURRENT DEBUG EVIDENCE\n\n")
        outfile.write("The following pattern continues to occur infinitely:\n\n")
        outfile.write("```\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 0 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("🎨 MVUPokerTableRenderer: Rendering with 2 seats\n")
        outfile.write("🔍 Props changed: old_props is None: False\n")
        outfile.write("🔍 Props equal: False\n")
        outfile.write("🔍 Seats equal: False\n")
        outfile.write("🔍 Review cursor: 0 -> 0\n")
        outfile.write("🔍 Waiting for: NONE -> NONE\n")
        outfile.write("[REPEATS INFINITELY]\n")
        outfile.write("```\n\n")
        
        # Key observations
        outfile.write("## 🧐 KEY OBSERVATIONS\n\n")
        outfile.write("1. **Props Equality Still Failing**: Despite dataclass equality, `Props equal: False`\n")
        outfile.write("2. **Seats Equality Failing**: `Seats equal: False` even with identical cursor/state\n")
        outfile.write("3. **Values Are Identical**: `Review cursor: 0 -> 0` and `Waiting for: NONE -> NONE`\n")
        outfile.write("4. **Alternating Pattern**: Switches between 0 seats and 2 seats consistently\n")
        outfile.write("5. **Dataclass Equality Not Working**: The `==` operator is not behaving as expected\n\n")
        
        # Hypothesis
        outfile.write("## 🎯 NEW HYPOTHESIS\n\n")
        outfile.write("The issue may be deeper than just dataclass equality:\n\n")
        outfile.write("### Potential Root Causes:\n")
        outfile.write("1. **Nested Dictionary Mutation**: The `seats: Dict[int, SeatState]` may be getting mutated\n")
        outfile.write("2. **Set Equality Issues**: `legal_actions: Set[str]` may not be comparing correctly\n")
        outfile.write("3. **Hidden State Changes**: Something is modifying the model between comparisons\n")
        outfile.write("4. **Dataclass Hash Collision**: Frozen dataclasses might have hash issues with mutable containers\n")
        outfile.write("5. **Timing Race Condition**: Multiple threads/events firing simultaneously\n")
        outfile.write("6. **Scale Widget Callback**: The review scale might still be triggering callbacks\n")
        outfile.write("7. **Model Creation Logic**: The `from_model()` method might be creating different objects\n\n")
        
        # Investigation needed
        outfile.write("## 🔍 INVESTIGATION NEEDED\n\n")
        outfile.write("### Immediate Debug Steps:\n")
        outfile.write("1. **Deep Inspection**: Add logging to show exact object contents being compared\n")
        outfile.write("2. **Hash Analysis**: Check if hash values are consistent for 'equal' objects\n")
        outfile.write("3. **Mutation Detection**: Add immutability checks to detect if objects are being modified\n")
        outfile.write("4. **Thread Analysis**: Verify all UI updates happen on main thread\n")
        outfile.write("5. **Event Tracing**: Log all dispatch calls to find the trigger source\n")
        outfile.write("6. **Memory Analysis**: Check if objects are being garbage collected unexpectedly\n\n")
        
        # Reproduction
        outfile.write("## 📋 REPRODUCTION\n\n")
        outfile.write("1. Run: `python3 backend/run_new_ui.py`\n")
        outfile.write("2. Navigate to 'Hands Review' tab\n")
        outfile.write("3. Infinite loop starts immediately\n")
        outfile.write("4. CPU usage spikes to 100%\n")
        outfile.write("5. Application becomes unresponsive\n\n")
        
        outfile.write("---\n\n")
        
        # Process each category
        for category_name, file_list in file_categories:
            if not file_list:  # Skip empty categories for now
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
        
        # Add urgent action items
        outfile.write("## 🚨 URGENT ACTION ITEMS\n\n")
        outfile.write("1. **Add Deep Debug Logging**: Instrument the props comparison to show exact differences\n")
        outfile.write("2. **Isolate the Trigger**: Find what's causing the initial model change\n")
        outfile.write("3. **Test Dataclass Equality**: Create minimal test case for TableRendererProps equality\n")
        outfile.write("4. **Check Object Identity**: Verify if objects are being recreated unnecessarily\n")
        outfile.write("5. **Review Scale Widget**: Ensure review scale callbacks are truly disabled\n")
        outfile.write("6. **Memory Profiling**: Check for memory leaks or object pooling issues\n\n")
        
        # Potential emergency solutions
        outfile.write("## 🆘 EMERGENCY WORKAROUNDS\n\n")
        outfile.write("If the issue cannot be resolved quickly:\n\n")
        outfile.write("1. **Revert to Legacy Tab**: Temporarily restore the old HandsReviewTab\n")
        outfile.write("2. **Disable MVU Tab**: Remove MVU tab from main app until fixed\n")
        outfile.write("3. **Add Rate Limiting**: Limit renders to max 1 per 100ms as emergency brake\n")
        outfile.write("4. **Force Early Return**: Add counter-based early return after N renders\n\n")
        
        # Write footer
        outfile.write("---\n\n")
        outfile.write("## 📋 END OF PERSISTENT LOOP BUG REPORT\n\n")
        outfile.write("**Priority**: CRITICAL - Application completely broken\n\n")
        outfile.write("**Next Step**: Immediate deep debugging session required\n\n")
        outfile.write("*This report documents the failure of initial fix attempts and provides direction for deeper investigation.*\n")
    
    print(f"\n✅ Persistent loop bug report created: {output_file}")
    
    # Get file size
    file_size = output_file.stat().st_size
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    return output_file


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Create persistent MVU infinite loop bug report"
    )
    
    parser.add_argument(
        '--source', '-s',
        default='.',
        help='Source directory (default: current directory)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '--filename', '-f',
        default='MVU_PERSISTENT_INFINITE_LOOP_BUG_REPORT.md',
        help='Output filename'
    )
    
    args = parser.parse_args()
    
    try:
        output_file = create_persistent_loop_bug_report(
            source_dir=args.source,
            output_dir=args.output,
            output_filename=args.filename
        )
        
        print(f"\n🎯 Critical bug report created: {output_file}")
        print(f"📁 Location: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating bug report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
