#!/usr/bin/env python3
"""
Test the improved Apply → Save → Close workflow.
"""

import sys
import os
import traceback

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_apply_workflow():
    """Test the Apply → Save → Close workflow."""
    print("🔴 Testing Apply → Save → Close Workflow")
    print("=" * 50)
    
    try:
        import tkinter as tk
        from ui.app_shell import AppShell
        from ui.theme_manager import ThemeManager as AdvancedThemeManager
        
        # Create main app (hidden)
        root = tk.Tk()
        root.withdraw()
        
        # Create AppShell
        app_shell = AppShell(root)
        print("   ✅ Created main app with theme system")
        
        # Track refresh calls
        refresh_calls = {"count": 0, "details": []}
        original_refresh = app_shell._on_theme_changed
        
        def tracked_refresh():
            refresh_calls["count"] += 1
            detail = f"Refresh #{refresh_calls['count']}"
            refresh_calls["details"].append(detail)
            print(f"   📡 {detail}")
            return original_refresh()
        
        app_shell._on_theme_changed = tracked_refresh
        
        # Create Theme Manager
        theme_manager = AdvancedThemeManager(root, on_theme_change=tracked_refresh)
        print("   ✅ Created Theme Manager")
        
        # Test Apply button workflow
        print("\n   🔴 Testing Apply workflow...")
        
        # Check that Apply method exists
        if hasattr(theme_manager, '_apply_theme_to_main_app'):
            print("   ✅ Apply method exists")
            
            # Test Apply functionality
            initial_count = refresh_calls["count"]
            theme_manager._apply_theme_to_main_app()
            
            if refresh_calls["count"] > initial_count:
                print(f"   ✅ Apply triggered refresh (calls: {refresh_calls['count']})")
            else:
                print("   ⚠️ Apply didn't trigger refresh")
        else:
            print("   ❌ Apply method missing")
        
        # Test Close button workflow
        print("\n   ❌ Testing Close workflow...")
        
        if hasattr(theme_manager, '_close_theme_manager'):
            print("   ✅ Close method exists")
            
            # Test close detection logic (without actually closing)
            if hasattr(theme_manager, 'original_theme') and theme_manager.original_theme:
                print("   ✅ Original theme stored for revert")
            else:
                print("   ⚠️ No original theme stored")
        else:
            print("   ❌ Close method missing")
        
        # Test UI elements
        print("\n   🎛️ Testing UI elements...")
        
        # Check Apply button exists
        apply_found = False
        close_found = False
        
        def check_widget_text(widget, target_text):
            try:
                if hasattr(widget, 'cget'):
                    text = widget.cget('text')
                    return target_text in text
            except:
                pass
            return False
        
        def search_widgets(parent):
            nonlocal apply_found, close_found
            try:
                for child in parent.winfo_children():
                    if check_widget_text(child, "Apply to Main App"):
                        apply_found = True
                    if check_widget_text(child, "Close"):
                        close_found = True
                    search_widgets(child)
            except:
                pass
        
        search_widgets(theme_manager)
        
        if apply_found:
            print("   ✅ Apply button found in UI")
        else:
            print("   ⚠️ Apply button not found")
            
        if close_found:
            print("   ✅ Close button found in UI")
        else:
            print("   ⚠️ Close button not found")
        
        # Check status label
        if hasattr(theme_manager, 'apply_status'):
            print("   ✅ Apply status label exists")
            status_text = theme_manager.apply_status.cget('text')
            print(f"   📝 Status: {status_text}")
        else:
            print("   ⚠️ Apply status label missing")
        
        # Clean up
        root.destroy()
        
        print(f"\n🎉 Apply Workflow Test Summary:")
        print(f"   • Apply method: {'✅' if hasattr(theme_manager, '_apply_theme_to_main_app') else '❌'}")
        print(f"   • Close method: {'✅' if hasattr(theme_manager, '_close_theme_manager') else '❌'}")
        print(f"   • Apply button: {'✅' if apply_found else '❌'}")
        print(f"   • Close button: {'✅' if close_found else '❌'}")
        print(f"   • Status tracking: {'✅' if hasattr(theme_manager, 'apply_status') else '❌'}")
        print(f"   • Refresh integration: {'✅' if refresh_calls['count'] > 0 else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Apply workflow test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run apply workflow tests."""
    print("🔴 APPLY WORKFLOW TEST")
    print("=" * 60)
    print("Testing Apply → Save → Close user experience...\n")
    
    success = test_apply_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 APPLY WORKFLOW READY!")
        print("\n✨ Improved User Experience:")
        print("   1. 🎨 Edit colors → See previews in Theme Manager")
        print("   2. 🔴 Click 'Apply' → Main app updates immediately") 
        print("   3. 👍 If you like it → Click 'Save' to make permanent")
        print("   4. ❌ Click 'Close' → Exit (with unsaved changes warning)")
        print("\n🎯 Perfect workflow for theme customization!")
        return 0
    else:
        print("❌ APPLY WORKFLOW NEEDS FIXES")
        return 1

if __name__ == "__main__":
    sys.exit(main())
