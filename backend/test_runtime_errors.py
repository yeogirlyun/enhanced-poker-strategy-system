#!/usr/bin/env python3
"""
Test for actual runtime errors by bypassing safety checks.
This will attempt to initialize all components without showing GUI.
"""

import sys
import os
import traceback

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def test_app_initialization():
    """Test AppShell initialization without showing GUI."""
    print("🧪 Testing AppShell initialization...")
    
    try:
        import tkinter as tk
        from ui.app_shell import AppShell
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the window immediately
        
        print("   ✅ Root window created (hidden)")
        
        # Try to create AppShell
        app_shell = AppShell(root)
        print("   ✅ AppShell created successfully")
        
        # Test that services are initialized
        services = app_shell.services
        
        # Test each service
        event_bus = services.get_app("event_bus")
        print(f"   ✅ Event bus: {type(event_bus).__name__}")
        
        theme_manager = services.get_app("theme")
        print(f"   ✅ Theme manager: {type(theme_manager).__name__}")
        
        hands_repo = services.get_app("hands_repository")
        print(f"   ✅ Hands repository: {type(hands_repo).__name__}")
        
        store = services.get_app("store")
        print(f"   ✅ Store: {type(store).__name__}")
        
        # Test theme loading
        theme = theme_manager.get_theme()
        print(f"   ✅ Theme loaded with {len(theme)} properties")
        
        # Test menu system creation (this might be where errors occur)
        print("   🔍 Testing menu system...")
        
        # The menu should have been created in __init__
        menu = root.cget("menu")
        if menu:
            print("   ✅ Menu system created")
        else:
            print("   ⚠️  No menu found")
        
        # Clean up
        root.destroy()
        print("   ✅ Cleanup completed")
        
        return True, []
        
    except Exception as e:
        error_msg = f"AppShell initialization failed: {e}"
        print(f"   ❌ {error_msg}")
        traceback.print_exc()
        return False, [error_msg]

def test_theme_manager_creation():
    """Test creating the advanced Theme Manager."""
    print("\n🎨 Testing Theme Manager creation...")
    
    try:
        import tkinter as tk
        from ui.theme_manager import ThemeManager as AdvancedThemeManager
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Try to create Theme Manager (this is where errors might occur)
        theme_manager = AdvancedThemeManager(root)
        print("   ✅ Advanced Theme Manager created")
        
        # Test that it loaded themes
        if hasattr(theme_manager, 'themes') and theme_manager.themes:
            print(f"   ✅ Loaded {len(theme_manager.themes)} themes")
        else:
            print("   ⚠️  No themes loaded")
        
        # Clean up
        root.destroy()
        print("   ✅ Cleanup completed")
        
        return True, []
        
    except Exception as e:
        error_msg = f"Theme Manager creation failed: {e}"
        print(f"   ❌ {error_msg}")
        traceback.print_exc()
        return False, [error_msg]

def test_individual_components():
    """Test individual components that might have issues."""
    print("\n🔧 Testing individual components...")
    errors = []
    
    # Test theme loader
    try:
        from ui.services.theme_loader_consolidated import get_consolidated_theme_loader
        loader = get_consolidated_theme_loader()
        config = loader.load_themes()
        print("   ✅ Theme loader working")
    except Exception as e:
        error_msg = f"Theme loader failed: {e}"
        print(f"   ❌ {error_msg}")
        errors.append(error_msg)
    
    # Test existing theme manager
    try:
        from ui.services.theme_manager import ThemeManager
        tm = ThemeManager()
        theme = tm.get_theme()
        print("   ✅ Existing theme manager working")
    except Exception as e:
        error_msg = f"Existing theme manager failed: {e}"
        print(f"   ❌ {error_msg}")
        errors.append(error_msg)
    
    # Test hands repository
    try:
        from ui.services.hands_repository import HandsRepository
        repo = HandsRepository()
        hands = repo.get_filtered_hands()
        print("   ✅ Hands repository working")
    except Exception as e:
        error_msg = f"Hands repository failed: {e}"
        print(f"   ❌ {error_msg}")
        errors.append(error_msg)
    
    # Test store
    try:
        from ui.state.store import Store
        from ui.state.reducers import root_reducer
        store = Store({}, root_reducer)
        print("   ✅ Store working")
    except Exception as e:
        error_msg = f"Store failed: {e}"
        print(f"   ❌ {error_msg}")
        errors.append(error_msg)
    
    return len(errors) == 0, errors

def test_tab_creation():
    """Test tab creation which might have issues."""
    print("\n📑 Testing tab creation...")
    errors = []
    
    try:
        import tkinter as tk
        from tkinter import ttk
        from ui.tabs.hands_review_tab import HandsReviewTab
        from ui.services.service_container import ServiceContainer
        from ui.services.event_bus import EventBus
        from ui.services.theme_manager import ThemeManager
        from ui.services.hands_repository import HandsRepository
        from ui.state.store import Store
        from ui.state.reducers import root_reducer
        
        # Create hidden root and notebook
        root = tk.Tk()
        root.withdraw()
        notebook = ttk.Notebook(root)
        
        # Create services like AppShell does
        services = ServiceContainer()
        services.provide_app("event_bus", EventBus())
        services.provide_app("theme", ThemeManager())
        services.provide_app("hands_repository", HandsRepository())
        
        initial_state = {
            "table": {"dim": (0, 0)},
            "pot": {"amount": 0},
            "seats": [],
            "board": [],
            "dealer": 0,
            "active_tab": "",
            "review": {
                "hands": [],
                "filter": {},
                "loaded_hand": None,
                "study_mode": "replay",
                "collection": None
            }
        }
        services.provide_app("store", Store(initial_state, root_reducer))
        
        # Try to create HandsReviewTab
        tab = HandsReviewTab(notebook, services)
        print("   ✅ HandsReviewTab created successfully")
        
        # Clean up
        root.destroy()
        
    except Exception as e:
        error_msg = f"Tab creation failed: {e}"
        print(f"   ❌ {error_msg}")
        traceback.print_exc()
        errors.append(error_msg)
    
    return len(errors) == 0, errors

def main():
    """Run all runtime error tests."""
    print("🔍 RUNTIME ERROR DETECTION")
    print("=" * 50)
    print("This test bypasses safety checks to find actual runtime errors.\n")
    
    all_passed = True
    all_errors = []
    
    tests = [
        ("Individual Components", test_individual_components),
        ("Tab Creation", test_tab_creation),
        ("AppShell Initialization", test_app_initialization),
        ("Theme Manager Creation", test_theme_manager_creation)
    ]
    
    for test_name, test_func in tests:
        try:
            passed, errors = test_func()
            if passed:
                print(f"✅ {test_name}: PASSED\n")
            else:
                print(f"❌ {test_name}: FAILED\n")
                all_passed = False
                all_errors.extend(errors)
        except Exception as e:
            error_msg = f"{test_name} crashed: {e}"
            print(f"💥 {test_name}: CRASHED - {e}\n")
            traceback.print_exc()
            all_passed = False
            all_errors.append(error_msg)
    
    print("=" * 50)
    if all_passed:
        print("🎉 NO RUNTIME ERRORS DETECTED!")
        print("The issue might be:")
        print("   • VS Code terminal compatibility (use macOS Terminal)")
        print("   • GUI-specific issues that only appear when window is shown")
        print("   • Timing issues during actual GUI startup")
        return 0
    else:
        print(f"❌ {len(all_errors)} RUNTIME ERRORS FOUND:")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
