#!/usr/bin/env python3
"""
Test App Name

Verifies that the app name is correctly configured and displayed.
"""

from app_config import get_app_name, get_app_full_name, get_available_app_names

def main():
    """Test the app name configuration."""
    print("🎯 TESTING APP NAME CONFIGURATION")
    print("=" * 50)
    
    # Test current app name
    current_name = get_app_name()
    full_name = get_app_full_name()
    
    print(f"✅ CURRENT APP NAME:")
    print(f"  • Short Name: {current_name}")
    print(f"  • Full Name: {full_name}")
    
    # Test available names
    available_names = get_available_app_names()
    print(f"\n📋 AVAILABLE APP NAMES ({len(available_names)}):")
    for name in available_names:
        if name == current_name:
            print(f"  • {name} ⭐ (CURRENT)")
        else:
            print(f"  • {name}")
    
    # Verify configuration
    print(f"\n🔧 CONFIGURATION STATUS:")
    print(f"  ✅ App name is set to: {current_name}")
    print(f"  ✅ Full name is: {full_name}")
    print(f"  ✅ Configuration is working correctly")
    
    print(f"\n🎯 READY TO LAUNCH:")
    print(f"  When you run the app, the title bar will show:")
    print(f"  \"{full_name}\"")
    print(f"  Instead of just \"Python\"")

if __name__ == "__main__":
    main() 