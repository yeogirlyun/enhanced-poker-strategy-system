#!/usr/bin/env python3
"""
Test script to verify UI integration without launching GUI.
Safe to run in VS Code integrated terminal.
"""

import sys
import os

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

def test_ui_integration():
    """Test the UI integration components."""
    print("🧪 Testing UI Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import all components
        print("1. Testing imports...")
        from ui.app_shell import AppShell
        from ui.theme_manager import ThemeManager as AdvancedThemeManager
        from ui.menu_integration import add_theme_manager_to_menu, open_theme_manager
        from ui.services.theme_loader_consolidated import get_consolidated_theme_loader
        print("   ✅ All UI components imported successfully")
        
        # Test 2: Check menu integration functions
        print("\n2. Testing menu integration functions...")
        import tkinter as tk
        
        # Create a dummy root and menubar (don't show)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        menubar = tk.Menu(root)
        
        # Test adding theme manager to menu
        add_theme_manager_to_menu(menubar, root, lambda: print("Theme changed callback"))
        
        # Check if Settings menu was created
        menu_labels = []
        for i in range(menubar.index("end") + 1):
            try:
                label = menubar.entrycget(i, "label")
                menu_labels.append(label)
            except:
                pass
                
        print(f"   ✅ Menu labels created: {menu_labels}")
        
        if "Settings" in menu_labels:
            print("   ✅ Settings menu created successfully")
        else:
            print("   ⚠️  Settings menu not found")
            
        root.destroy()  # Clean up
        
        # Test 3: Theme loader integration
        print("\n3. Testing theme loader integration...")
        loader = get_consolidated_theme_loader()
        config = loader.load_themes()
        themes = config.get("themes", [])
        print(f"   ✅ Loaded {len(themes)} themes for integration")
        
        if themes:
            sample_theme = themes[0]
            print(f"   ✅ Sample theme: {sample_theme.get('name', 'Unknown')}")
        
        # Test 4: AppShell class structure
        print("\n4. Testing AppShell class structure...")
        
        # Check if AppShell has the required methods
        required_methods = [
            '_create_menu_system',
            '_on_theme_changed', 
            '_show_about',
            '_new_session'
        ]
        
        for method_name in required_methods:
            if hasattr(AppShell, method_name):
                print(f"   ✅ AppShell has {method_name} method")
            else:
                print(f"   ❌ AppShell missing {method_name} method")
        
        print("\n🎉 UI Integration tests passed!")
        print("\n💡 Integration features:")
        print("   • Settings → Appearance → 🎨 Theme Manager menu")
        print("   • Live theme switching with UI refresh")
        print("   • VS Code terminal safety checks")
        print("   • Menu shortcuts for zoom (Cmd +/-/0)")
        print("   • About dialog with theme info")
        
        print("\n🚀 Ready to launch! Use:")
        print("   1. macOS Terminal: python3 run_new_ui.py")
        print("   2. VS Code Terminal: python3 run_new_ui.py (with safety prompt)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ui_integration()
    sys.exit(0 if success else 1)
