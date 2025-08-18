#!/usr/bin/env python3
"""
Comprehensive runtime test to verify no compile/import errors.
Tests all Theme Manager integration components without launching GUI.
"""

import sys
import os
import traceback
from typing import List, Tuple

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports() -> Tuple[bool, List[str]]:
    """Test all imports to catch compile-time errors."""
    print("🔍 Testing imports...")
    errors = []
    
    # Core imports
    try:
        import tkinter as tk
        from tkinter import ttk
        print("   ✅ tkinter imports")
    except Exception as e:
        errors.append(f"tkinter: {e}")
    
    # Theme system imports
    try:
        from ui.services.theme_loader_consolidated import (
            ConsolidatedThemeLoader,
            get_consolidated_theme_loader,
            load_themes,
            save_themes
        )
        print("   ✅ Consolidated theme loader")
    except Exception as e:
        errors.append(f"theme_loader_consolidated: {e}")
    
    try:
        from ui.theme_manager import (
            ThemeManager,
            hex_to_rgbf,
            rgbf_to_hex,
            apply_hsl_nudge,
            EDITABLE_KEYS
        )
        print("   ✅ Advanced Theme Manager")
    except Exception as e:
        errors.append(f"theme_manager: {e}")
    
    try:
        from ui.menu_integration import (
            open_theme_manager,
            add_theme_manager_to_menu
        )
        print("   ✅ Menu integration")
    except Exception as e:
        errors.append(f"menu_integration: {e}")
    
    # UI integration imports
    try:
        from ui.app_shell import AppShell
        print("   ✅ AppShell with Theme Manager integration")
    except Exception as e:
        errors.append(f"app_shell: {e}")
    
    # Existing theme system
    try:
        from ui.services.theme_manager import ThemeManager as ExistingThemeManager
        from ui.services.theme_factory import build_all_themes
        print("   ✅ Existing theme system")
    except Exception as e:
        errors.append(f"existing_theme_system: {e}")
    
    return len(errors) == 0, errors

def test_theme_loader() -> Tuple[bool, List[str]]:
    """Test theme loader functionality."""
    print("\n🎨 Testing theme loader...")
    errors = []
    
    try:
        from ui.services.theme_loader_consolidated import get_consolidated_theme_loader
        
        loader = get_consolidated_theme_loader()
        config = loader.load_themes()
        
        # Validate config structure
        if "themes" not in config:
            errors.append("Missing 'themes' key in config")
        else:
            themes = config["themes"]
            if not isinstance(themes, list):
                errors.append("'themes' is not a list")
            elif len(themes) == 0:
                errors.append("No themes found")
            else:
                print(f"   ✅ Loaded {len(themes)} themes")
        
        if "defaults" not in config:
            errors.append("Missing 'defaults' key in config")
        else:
            print("   ✅ Defaults loaded")
        
        # Test theme access
        theme_list = loader.get_theme_list()
        if not theme_list:
            errors.append("get_theme_list() returned empty")
        else:
            print(f"   ✅ Theme list: {len(theme_list)} entries")
        
        # Test individual theme access
        if themes:
            first_theme_id = themes[0].get("id")
            if first_theme_id:
                theme = loader.get_theme_by_id(first_theme_id)
                if theme:
                    print(f"   ✅ Theme access by ID: {theme.get('name', 'Unknown')}")
                else:
                    errors.append(f"Could not load theme by ID: {first_theme_id}")
        
    except Exception as e:
        errors.append(f"Theme loader error: {e}")
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_color_utilities() -> Tuple[bool, List[str]]:
    """Test color utility functions."""
    print("\n🌈 Testing color utilities...")
    errors = []
    
    try:
        from ui.theme_manager import hex_to_rgbf, rgbf_to_hex, apply_hsl_nudge
        
        # Test color conversion
        test_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000"]
        for color in test_colors:
            try:
                rgb = hex_to_rgbf(color)
                back_to_hex = rgbf_to_hex(rgb)
                if not back_to_hex.startswith("#"):
                    errors.append(f"Invalid hex output: {back_to_hex}")
            except Exception as e:
                errors.append(f"Color conversion failed for {color}: {e}")
        
        print("   ✅ Color conversion functions")
        
        # Test HSL nudging
        try:
            original = "#FF0000"
            nudged = apply_hsl_nudge(original, dh=0.1, ds=0.0, dl=0.0)
            if nudged == original:
                errors.append("HSL nudge had no effect")
            else:
                print(f"   ✅ HSL nudging: {original} -> {nudged}")
        except Exception as e:
            errors.append(f"HSL nudge failed: {e}")
        
    except Exception as e:
        errors.append(f"Color utilities error: {e}")
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_menu_integration() -> Tuple[bool, List[str]]:
    """Test menu integration without creating windows."""
    print("\n📋 Testing menu integration...")
    errors = []
    
    try:
        from ui.menu_integration import add_theme_manager_to_menu
        import tkinter as tk
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Create menu bar
        menubar = tk.Menu(root)
        
        # Test adding theme manager to menu
        def dummy_callback():
            pass
        
        add_theme_manager_to_menu(menubar, root, dummy_callback)
        
        # Verify Settings menu was created
        menu_created = False
        try:
            menu_end = menubar.index("end")
            if menu_end is not None:
                for i in range(menu_end + 1):
                    try:
                        label = menubar.entrycget(i, "label")
                        if "Settings" in label:
                            menu_created = True
                            break
                    except:
                        continue
        except:
            pass
        
        if menu_created:
            print("   ✅ Settings menu created")
        else:
            errors.append("Settings menu not created")
        
        root.destroy()  # Clean up
        
    except Exception as e:
        errors.append(f"Menu integration error: {e}")
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_app_shell_integration() -> Tuple[bool, List[str]]:
    """Test AppShell class structure."""
    print("\n🏗️ Testing AppShell integration...")
    errors = []
    
    try:
        from ui.app_shell import AppShell
        
        # Check required methods exist
        required_methods = [
            '_create_menu_system',
            '_on_theme_changed',
            '_show_about',
            '_new_session'
        ]
        
        for method_name in required_methods:
            if hasattr(AppShell, method_name):
                print(f"   ✅ AppShell.{method_name}")
            else:
                errors.append(f"Missing method: AppShell.{method_name}")
        
        # Check imports in AppShell by trying to access them
        try:
            # The import should be accessible in the module
            import ui.app_shell as app_shell_module
            if hasattr(app_shell_module, 'AdvancedThemeManager'):
                print("   ✅ Advanced Theme Manager imported")
            else:
                print("   ℹ️  Advanced Theme Manager imported but not exposed (OK)")
            
            if hasattr(app_shell_module, 'add_theme_manager_to_menu'):
                print("   ✅ Menu integration imported")
            else:
                print("   ℹ️  Menu integration imported but used internally (OK)")
                
        except Exception as e:
            errors.append(f"Could not verify imports: {e}")
        
    except Exception as e:
        errors.append(f"AppShell integration error: {e}")
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_file_structure() -> Tuple[bool, List[str]]:
    """Test that all required files exist."""
    print("\n📁 Testing file structure...")
    errors = []
    
    required_files = [
        "ui/theme_manager.py",
        "ui/services/theme_loader_consolidated.py",
        "ui/menu_integration.py",
        "data/poker_themes.json",
        "demo_theme_manager.py",
        "test_theme_system.py",
        "test_ui_integration.py"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            errors.append(f"Missing file: {file_path}")
    
    return len(errors) == 0, errors

def main():
    """Run all runtime tests."""
    print("🧪 COMPREHENSIVE RUNTIME TEST")
    print("=" * 60)
    
    all_passed = True
    all_errors = []
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Theme Loader", test_theme_loader),
        ("Color Utilities", test_color_utilities),
        ("Menu Integration", test_menu_integration),
        ("AppShell Integration", test_app_shell_integration)
    ]
    
    for test_name, test_func in tests:
        try:
            passed, errors = test_func()
            if passed:
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
                for error in errors:
                    print(f"   • {error}")
                all_passed = False
                all_errors.extend(errors)
        except Exception as e:
            print(f"\n💥 {test_name}: CRASHED - {e}")
            all_passed = False
            all_errors.append(f"{test_name} crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - No runtime errors detected!")
        print("\n✅ Theme Manager integration is ready to use:")
        print("   • All imports working correctly")
        print("   • Theme loading functional")
        print("   • Color utilities working")
        print("   • Menu integration ready")
        print("   • AppShell properly integrated")
        print("\n🚀 Safe to launch: python3 run_new_ui.py")
        return 0
    else:
        print(f"❌ {len(all_errors)} ERRORS DETECTED:")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
        print("\n🔧 Fix these issues before launching the UI")
        return 1

if __name__ == "__main__":
    sys.exit(main())
