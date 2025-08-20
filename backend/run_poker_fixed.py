#!/usr/bin/env python3
"""
Fixed Poker Launcher - Automatically applies runtime fixes before launching.
This ensures the application runs without console errors.
"""


def main():
    """Main launcher function."""
    print("🎯 Fixed Poker Launcher Starting...")
    
    # Apply runtime fixes first
    try:
        print("🔧 Applying runtime fixes...")
        from fix_runtime_errors import main as apply_fixes
        apply_fixes()
        print("✅ Runtime fixes applied successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not apply runtime fixes: {e}")
        print("🎯 Continuing anyway...")
    
    # Now launch the main application
    try:
        print("🚀 Launching poker application...")
        from run_new_ui import main as launch_app
        launch_app()
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        print("💡 Try running 'python3 fix_runtime_errors.py' first, then "
              "'python3 run_new_ui.py'")


if __name__ == "__main__":
    main()
